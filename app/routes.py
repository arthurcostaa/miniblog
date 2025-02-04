from flask import flash, render_template, redirect, url_for

from app import app
from app.forms import LoginForm


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login requested for {form.username.data} (remember_me={form.remember_me.data})')
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
