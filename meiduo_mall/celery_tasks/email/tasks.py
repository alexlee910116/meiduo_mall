from django.core.mail import send_mail
from celery_tasks.main import celery_app


@celery_app.task(name='celery_send_email')
def celery_send_email(subject, message, from_email, recipient_list, html_message):
    send_mail(subject=subject,
              message=message,
              from_email=from_email,
              recipient_list=recipient_list,
              html_message=html_message)
