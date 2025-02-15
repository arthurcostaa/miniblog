from flask import render_template
from flask_login import login_required

from app.main import bp


@bp.route('/')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'Arthur'},
            'body': 'Uma vez Flamengo, sempre Flamengo!',
        },
        {
            'author': {'username': 'John'},
            'body': 'Muita chuva em Natal.',
        }
    ]
    return render_template('main/index.html', title='Home', posts=posts)
