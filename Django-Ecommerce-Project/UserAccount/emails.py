from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from celery import shared_task


@shared_task
def send_welcome_email(user_id):

    user = User.objects.get(id=user_id)

    html_message = render_to_string('reg_email.html', {"user":user})
    # plain_message = strip_tags(html_message)
    send_mail(
        "Welcome to Smart Shops","Thankyou for registration...",
        settings.EMAIL_HOST_USER, [user.email], fail_silently=False,
        html_message=html_message
        )

    return True

@shared_task
def send_reset_password_email(user_id):

    user = User.objects.get(id=user_id)

    html_message = render_to_string('reg_email.html', {"user":user})
    # plain_message = strip_tags(html_message)
    send_mail(
        "Reset password","Please reset your password with following link (...))",
        settings.EMAIL_HOST_USER, [user.email], fail_silently=False,
        html_message=html_message
        )

    return True
