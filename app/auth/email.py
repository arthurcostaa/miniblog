from flask import current_app, render_template

from app.email import send_mail


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_mail(
        '[Miniblog] Reset Password Email',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template(
            'email/reset_password.txt', user=user, token=token
        ),
        text_html=render_template(
            'email/reset_password.html', user=user, token=token
        )
    )
