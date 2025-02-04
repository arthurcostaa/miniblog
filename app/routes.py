from flask import render_template

from app import app


@app.route('/')
def index():
    user = {'username': 'Arthur'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)
