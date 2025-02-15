import sqlalchemy as sa
from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.models import User

from .forms import EditProfileForm


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


@bp.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    posts = posts = [
        {'author': user, 'body': 'First post'},
        {'author': user, 'body': 'Second post'},
    ]
    return render_template('main/user.html', user=user, posts=posts)


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
