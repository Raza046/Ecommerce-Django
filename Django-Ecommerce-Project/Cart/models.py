from django.db import models
from Products.models import *
from django.core.validators import MinValueValidator, MaxValueValidator
from UserAccount.models import Users
from django.dispatch import receiver
from django.db.models.signals import post_save


class CartItem(models.Model):

    product_variant = models.ForeignKey(ProductVariant, verbose_name=("prod_variant"), on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.PositiveIntegerField()
    cart = models.ForeignKey("Cart", related_name="cart_items", on_delete=models.CASCADE)



class Cart(models.Model):

    customer = models.ForeignKey(Users, related_name="customer_cart", on_delete=models.CASCADE, null=True)
    total_price = models.IntegerField(default=0)
    coupon = models.ForeignKey("Coupon", verbose_name=("cart_coupon"), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = ("Cart")


class Coupon(models.Model):

    code = models.CharField(max_length = 250, unique=True)
    user = models.ManyToManyField(Users, related_name="coupons", verbose_name=("customer_coupon"), blank = True)
    valid_from = models.DateField(auto_now_add=True)
    valid_to = models.DateField(auto_now=False, auto_now_add=False)
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    usage = models.PositiveIntegerField(default=1)
    all_users = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)

    def __str__(self):
        return self.code


@receiver(post_save, sender=Coupon)
def set_coupon_to_expire(sender, instance, created, **kwargs):
    if instance.usage == 0 and not instance.is_expired:
        instance.is_expired = True
        instance.save(update_fields=['is_expired'])
