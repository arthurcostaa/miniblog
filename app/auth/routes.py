from urllib.parse import urlsplit

import sqlalchemy as sa
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        if next_page is None or urlsplit(next_page).netloc != '':
            return redirect(url_for('main.index'))
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data.strip().lower()
        user.email = form.email.data.strip().lower()
        user.set_password(form.password.data)

        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)
