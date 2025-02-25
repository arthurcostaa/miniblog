import sqlalchemy as sa
import sqlalchemy.orm as so

from app import create_app, db
from app.models import Comment, Post, User

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'sa': sa,
        'so': so,
        'db': db,
        'Comment': Comment,
        'Post': Post,
        'User': User,
    }
