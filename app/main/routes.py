import sqlalchemy as sa
from flask import current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.models import Comment, User, Post

from .forms import CommentForm, EditProfileForm, EmptyForm, PostForm


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        current_user.following_posts(),
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.prev_num else None
    return render_template(
        'main/index.html',
        title='Home',
        form=form,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/user/<username>')
def user(username):
    form = EmptyForm()
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts_query = user.posts.select().order_by(Post.created_at.desc())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        posts_query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.prev_num else None
    return render_template(
        'main/user.html',
        title=f'{user.username}',
        form=form,
        user=user,
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data.strip().lower()
        current_user.about_me = form.about_me.data.strip()
        db.session.commit()
        return redirect(
            url_for('main.user', username=current_user.username)
        )
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template(
        'main/edit_profile.html', title='Edit profile', form=form
    )


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        if user is None:
            flash('User not found')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You can not follow yourself.')
            return redirect(url_for('main.user', username=user.username))

        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {user.username}')
        return redirect(url_for('main.user', username=user.username))

    return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username)
        )

        if user is None:
            flash('User not found')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You can not unfollow yourself.')
            return redirect(url_for('main.user', username=user.username))

        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {user.username}')
        return redirect(url_for('main.user', username=user.username))

    return redirect(url_for('main.index'))


@bp.route('/explore')
@login_required
def explore():
    query = sa.select(Post).order_by(Post.created_at.desc())
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(
        query,
        page=page,
        per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.prev_num else None
    return render_template(
        'main/index.html',
        title='Explore',
        posts=posts,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/post/<post_id>')
def post(post_id):
    query = sa.select(Post).where(Post.id == post_id)
    post = db.first_or_404(query)
    page = request.args.get('page', 1, type=int)
    comments = db.paginate(
        post.comments.select().order_by(Comment.created_at.desc()),
        page=page,
        per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    form = CommentForm()
    next_url = (
        url_for('main.post', post_id=post_id, page=comments.next_num)
        if comments.next_num else None
    )
    prev_url = (
        url_for('main.post', post_id=post_id, page=comments.prev_num)
        if comments.prev_num else None
    )
    return render_template(
        'main/post.html',
        title=post.body,
        form=form,
        post=post,
        comments=comments,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/post/<post_id>/comment', methods=['POST'])
@login_required
def comment(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        query = sa.select(Post).where(Post.id == post_id)
        post = db.first_or_404(query)
        comment = Comment(body=form.body.data, author=current_user)
        post.comments.add(comment)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))

    return redirect(url_for('main.index'))
