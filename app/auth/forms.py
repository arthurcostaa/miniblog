import sqlalchemy as sa
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    EmailField,
    PasswordField,
    StringField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from app import db
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Register')

    def validate_username(self, username):
        if username.data.strip().count(' ') > 0:
            raise ValidationError('Username cannot contain whitespaces')

        user = db.session.scalar(
            sa.select(User).where(User.username == username.data)
        )
        if user is not None:
            raise ValidationError('Please enter a different username.')

    def validate_email(self, email):
        user = db.session.scalar(
            sa.select(User).where(User.email == email.data)
        )
        if user is not None:
            raise ValidationError('Please enter a different email.')
