import datetime
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from Cart.models import Cart, CartItem, Coupon
from Products.models import *
from UserAccount.models import Users

# Create your models here.

class OrderItem(models.Model):

    product_variant = models.ForeignKey(ProductVariant, related_name="product_variant", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey("Order", related_name="items", null=True,on_delete=models.CASCADE)

    def __str__(self):
        return f"Order #{self.order.order_id} - {self.product_variant.product.Name} (Qty: {self.quantity})"


class Order(models.Model):

    class Status(models.TextChoices):
        CREATED = 'Created', 'Created'
        PREPARING = 'Preparing', 'Preparing'
        SHIPPING = 'Shipping', 'Shipping'
        OUT_FOR_DELIVERY = 'Out for Delivery', 'Out for Delivery'
        DELIVERED = 'Delivered', 'Delivered'
        CANCELLED = 'Canceled', 'Canceled'

    class DeliveryOptions(models.TextChoices):
        CASH_ON_DELIVERY = "COD", "Cash On Delivery"
        ONLINE_PAYMENT = "OP", "Online Payment"

    order_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer =  models.ForeignKey(Users, related_name="orders", on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey(Cart, related_name="order_cart", on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(blank=True, max_length=20)
    address = models.CharField(blank=True, max_length=150)
    city = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    total = models.IntegerField(default=0)
    delivery_option = models.CharField(
        max_length=3, choices=DeliveryOptions.choices, default=DeliveryOptions.CASH_ON_DELIVERY
        )
    status = models.CharField(max_length=100, choices=Status.choices, default=Status.CREATED)
    admin_note = models.CharField(blank=True, max_length=100)
    create_at = models.DateField(auto_now_add=True)
    placed = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    # Add options field in above (placed and Cancelled ) Fields.

    def __str__(self):
        return f'{self.order_id}'
        # return f'{self.user.username} --- {self.order_id}'


    @classmethod
    def Order_Updation(self, email_opt, order_id, order_status):

        order = Order.objects.filter(id=order_id).first()
        order.status=order_status
        order.save()

        if email_opt == "true":
            print("Sending an email")
            html_message = render_to_string('admin/email/order_update_mail.html', {'order':order,'order_status':order_status})
            # plain_message = strip_tags(html_message)
            send_mail("Order from Smart Shops","Order update notification", settings.EMAIL_HOST_USER, [order.email], fail_silently=False, html_message=html_message)


@receiver(post_save, sender=Order)
def Send_Mail(sender, instance, created=True, **kwargs):
    pass
#    cart = Cart.objects.filter(id = cart_id).first()
#    cart_items = Cart.UserCartItems(cart, request=None)
#    instance.customer
    # if instance.customer:
    #     coupon = Coupon.objects.filter(
    #         user=instance.customer, active=True, valid_from__lte=datetime.date.today(),
    #         valid_to__gte=datetime.date.today()
    #         ).first()
    #     Cart.Discount(coupon,cart)
    # else:
    #     coupon = None

    # if coupon:
    # html_message = render_to_string('email.html', {
    #     "cart":cart_items,"dis":coupon,"Order":instance, "total_price":cart.Total_Price
    #     })
    #     # plain_message = strip_tags(html_message)
    # # else:
    # #     html_message = render_to_string('email.html', {"cart":cart_items, "Order":instance, "total_price":cart.Total_Price})
    #     # plain_message = strip_tags(html_message)

    # send_mail(
    #     "Order from Smart Shops","Thankyou for your order...", settings.EMAIL_HOST_USER,
    #     [instance.email], fail_silently=False, html_message=html_message
    #     )

@receiver(post_save, sender=Order)
def clear_cart(sender, instance, created=True, **kwargs):

    instance.cart.Total_Price = 0
    instance.cart.save()

    for item in instance.cart.cart_items.all():
        OrderItem.objects.create(
            product_variant=item.product_variant, quantity=item.quantity, order_id=instance.id
        )
    instance.cart.cart_items.all().delete()


class Complain(models.Model):

    class ReturnOptions(models.TextChoices):
        REFUND = 'Refund', 'Refund'
        EXCHANGE = 'Exchange the Product', 'Exchange the Product'

    class Status(models.TextChoices):
        RESOLVED = 'Resolved', 'Resolved'
        PENDING = 'Pending', 'Pending'


    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    order = models.ForeignKey("Order", verbose_name=("complain"), null=True,on_delete=models.CASCADE)
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, related_name="product_variant_complain")
    description = models.TextField()
    request = models.CharField(choices=ReturnOptions.choices, max_length=50)
    status = models.CharField(choices=Status.choices, max_length=100, default=Status.PENDING)
    # date = models.DateField(auto_now_add=True,null=True,blank=True)


class Subscription(models.Model):

    status_choices = (('Active', 'Active'),
                      ('Canceled', 'Canceled')
                      )

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    subscription_id = models.CharField(max_length=200)
    subscription_name = models.CharField(max_length=150)
    status = models.CharField(choices = status_choices, max_length=100, default = "Active")
    date_time = models.DateTimeField(auto_now = True)

