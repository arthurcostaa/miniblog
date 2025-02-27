from datetime import datetime
from hashlib import md5
from time import time

from flask import current_app
import jwt
import sqlalchemy as sa
import sqlalchemy.orm as so
from jwt.exceptions import DecodeError, ExpiredSignatureError
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, login


followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column(
        'follower_id',
        sa.Integer,
        sa.ForeignKey('user.id'),
        primary_key=True
    ),
    sa.Column(
        'followed_id',
        sa.Integer,
        sa.ForeignKey('user.id'),
        primary_key=True
    )
)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(
        sa.String(64), index=True, unique=True
    )
    email: so.Mapped[str] = so.mapped_column(
        sa.String(120), index=True, unique=True
    )
    password_hash: so.Mapped[str | None] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(
        back_populates='author'
    )
    comments: so.WriteOnlyMapped['Comment'] = so.relationship(
        back_populates='author'
    )
    about_me: so.Mapped[str | None] = so.mapped_column(sa.String(140))
    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )

    def __repr__(self) -> str:
        return f'<User {self.username}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def is_following(self, user):
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)

        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(
                sa.or_(Follower.id == self.id, Author.id == self.id)
            )
            .group_by(Post)
            .order_by(Post.created_at.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    @staticmethod
    def verify_reset_password(token):
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = payload['reset_password']
        except (DecodeError, ExpiredSignatureError):
            return

        return db.session.get(User, user_id)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=sa.func.now(), index=True
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.now()
    )
    user_id: so.Mapped[int]  = so.mapped_column(
        sa.ForeignKey(User.id), index=True
    )
    author: so.Mapped[User] = so.relationship(back_populates='posts')
    comments: so.WriteOnlyMapped['Comment'] = so.relationship(
        back_populates='post'
    )

    def __repr__(self) -> str:
        return f'<Post {self.body}>'

    def comments_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.comments.select().subquery()
        )
        return db.session.scalar(query)


class Comment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(256))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True
    )
    post_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(Post.id)
    )
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),default=sa.func.now(), index=True
    )
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=sa.func.now(),
        onupdate=sa.func.now()
    )
    author: so.Mapped[User] = so.relationship(back_populates='comments')
    post: so.Mapped[Post] = so.relationship(back_populates='comments')

    def __repr__(self):
        return f'<Comment {self.body}>'


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))
