import json
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings
from django.utils import timezone

from Orders.models import Order
from celery import shared_task
from django_celery_beat.models import IntervalSchedule, PeriodicTask



# Create a dummy interval schedule to run the tasks once.
interval_schedule, created = IntervalSchedule.objects.get_or_create(every=1, period=IntervalSchedule.MINUTES)


def product_review_submission_reminder(order_id) -> bool:

    order = Order.objects.get(id=order_id)

    # Calculate the times for 48 hours, 24 hours, and 2 hours before the session
    after_3_days = order.delivery_date + timezone.timedelta(days=3)

    # Set the checkout-completion reminder after 24 hours.
    PeriodicTask.objects.create(
        interval=interval_schedule,
        name=f'Product review submission reminder email, Order Id : {order_id}',
        task='Orders.periodic_tasks.product_review_submission',
        args=json.dumps([order_id]),
        one_off=True,
        start_time=after_3_days,
    )


@shared_task
def product_review_submission(order_id):

    order = Order.objects.get(id=order_id)
    html_message = render_to_string('email/email.html', {
        "order":order.items.all()
    })
    send_mail(
    "Product Review Reminder", "Please submit review of your product", settings.EMAIL_HOST_USER,
    [order.customer.user.email], fail_silently=False, html_message=html_message
    )

