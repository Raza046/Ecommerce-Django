from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from Orders.models import Order
from UserAccount.models import Users
from celery import shared_task


@shared_task
def send_order_confirmation_email(user_id, order_id):

    user = Users.objects.get(id=user_id)
    order = Order.objects.get(id=order_id)

    html_message = render_to_string('email/email.html', {
        "cart":user.customer_cart.first().cart_items.all(),
        "discount":getattr(user.customer_cart.first().coupon, 'discount', 0),
        "order":order, "total_amount":order.total
    })

    send_mail(
    "Order from Smart Shops","Thankyou for your order...", settings.EMAIL_HOST_USER,
    [user.user.email], fail_silently=False, html_message=html_message
    )

    return True



