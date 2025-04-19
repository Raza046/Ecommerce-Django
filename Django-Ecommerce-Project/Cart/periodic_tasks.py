import json

from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings
from django.utils import timezone

from Cart.models import Cart
from celery import shared_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask



# Create a dummy interval schedule to run the tasks once.
interval_schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)


def email_reminder_to_complete_an_order_job(cart_id) -> bool:

    # Get the current time
    now = timezone.now()

    # Calculate the times for 48 hours, 24 hours, and 2 hours before the session
    after_a_day = now + timezone.timedelta(hours=24)
    after_three_days = now - timezone.timedelta(hours=72)

    # Set the checkout-completion reminder after 24 hours.
    PeriodicTask.objects.create(
        interval=interval_schedule,
        name=f'Send reminder to complete Checkout process after (24 hours), Cart Id : {cart_id}',
        task='Cart.periodic_tasks.send_email_reminder_to_complete_an_order',
        args=json.dumps([cart_id]),
        one_off=True,
        start_time=after_a_day,
    )

    # Set the checkout-completion reminder after 3 days.
    PeriodicTask.objects.create(
        interval=interval_schedule,
        name=f'Send reminder to complete Checkout process after (3 days), Cart Id : {cart_id}',
        task='Cart.periodic_tasks.send_email_reminder_to_complete_an_order',
        args=json.dumps([cart_id]),
        one_off=True,
        start_time=after_three_days,
    )


@shared_task
def send_email_reminder_to_complete_an_order(cart_id):

    cart = Cart.objects.get(id=cart_id)
    html_message = render_to_string('email/email.html', {
        "cart":cart
    })
    send_mail(
    "Complete your Order","Please complete your checkout process and place an order", settings.EMAIL_HOST_USER,
    [cart.customer.user.email], fail_silently=False, html_message=html_message
    )


def clear_inactive_cart_after_a_week(cart_id) -> bool:

    # Get the current time
    now = timezone.now()

    # Calculate the times for 48 hours, 24 hours, and 2 hours before the session
    after_a_week = now + timezone.timedelta(weeks=1)

    # Set the checkout-completion reminder after 24 hours.
    periodic_task = PeriodicTask.objects.filter(
        name=f"clear inactive cart after (a week), Cart Id : {cart_id}"
        )
    if periodic_task.exists():
       periodic_task.update(start_time=after_a_week)
       return True

    PeriodicTask.objects.create(
        interval=interval_schedule,
        name=f"clear inactive cart after (a week), Cart Id : {cart_id}",
        task='Cart.periodic_tasks.clear_inactive_cart',
        args=json.dumps([cart_id]),
        one_off=True,
        start_time=after_a_week,
    )
    return True


@shared_task
def clear_inactive_cart(cart_id):

    cart = Cart.objects.get(id=cart_id)
    cart.Total_Price = 0
    cart.save(update_fields=["Total_Price"])
    cart.cart_items.all().delete()

