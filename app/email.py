from threading import Thread

from flask import current_app
from flask_mail import Message

from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(
    subject: str,
    sender: str,
    recipients: list[str],
    text_body: str,
    text_html: str
) -> None:
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = text_html
    Thread(
        target=send_async_email,
        args=(current_app._get_current_object(), msg)
    ).start()
