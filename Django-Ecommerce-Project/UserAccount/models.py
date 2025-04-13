from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from Products.models import Product
import Orders.models
import Cart.models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


class Users(models.Model):

    USER_TYPE = (
        ('Customer', 'Customer'),
        ('Employee', 'Employee'),
        ('Rider', 'Rider'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    user_type = models.CharField(max_length = 100, choices=USER_TYPE, null=True, blank=True)
    full_name = models.CharField(max_length = 300)
    picture = models.FileField(upload_to="static")
    zip_code = models.IntegerField(default=0)
    phone = models.IntegerField(default=0)
    city = models.CharField(max_length = 300)
    country = models.CharField(max_length = 300)
    favourite = models.ForeignKey(Product, verbose_name=("fav_prod"), on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name = ("User")
        verbose_name_plural = ("Users")

    def __str__(self):
        return self.full_name

    @property
    def total_orders(self):
        return Orders.models.Order.objects.filter(customer=self).count()


@receiver(post_save, sender=Users)
def RegistrationEmail(sender, instance, created=True, **kwargs):
    if instance.user:
        html_message = render_to_string('reg_email.html', {"user":instance.user})
        # plain_message = strip_tags(html_message)
        send_mail(
            "Welcome to Smart Shops","Thankyou for registration...",
            settings.EMAIL_HOST_USER, [instance.user.email], fail_silently=False,
            html_message=html_message
            )

@receiver(post_save, sender=Users)
def CreateCart(sender, instance, created=True, **kwargs):
    Cart.models.Cart.objects.get_or_create(customer=instance)
