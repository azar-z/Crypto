from django.core.mail import EmailMessage

from celery import shared_task


@shared_task
def send_email_task(subject, msg_html, to):
    email = EmailMessage(subject, msg_html, to=to)
    email.send()
    return 'emails were sent'
