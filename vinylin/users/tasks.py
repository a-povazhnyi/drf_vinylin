from django.core.mail import EmailMessage

from vinylin.celery import celery_app
from users.emails import EmailConfirmMessage


@celery_app.task
def send_confirm_email_task(token, email):
    EmailConfirmMessage(code=token, to=[email]).send(fail_silently=True)


@celery_app.task
def send_password_reset_email_task(token, email):
    password_reset_email = EmailConfirmMessage(
        code=token,
        to=[email]
    )
    password_reset_email.subject = 'Reset your password!'
    password_reset_email.body = (
        f'Here is your password reset code: \n{token}'
    )
    password_reset_email.send(fail_silently=True)


@celery_app.task
def send_site_reminder_task(email):
    email = EmailMessage(
        subject='Welcome to Vinylin!',
        body='You recently registered on the Vinylin. Come see us more often!',
        to=[email]
    )
    email.send(fail_silently=True)
