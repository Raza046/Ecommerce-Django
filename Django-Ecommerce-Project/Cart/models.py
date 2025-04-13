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

# @receiver(post_save, sender=CartItem)
# def update_price(sender, instance, created, **kwargs):
#     instance.price = instance.quantity * instance.price
#     instance.save()


class Cart(models.Model):

    customer = models.ForeignKey(Users, related_name="customer_cart", on_delete=models.CASCADE, null=True)
    Total_Price = models.IntegerField(default=0)
    coupon = models.ForeignKey("Coupon", verbose_name=("cart_coupon"), on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = ("Cart")
        verbose_name_plural = ("Carts")

    # def __str__(self):
    #     if self.customer.full_name:
    #         return self.customer.full_name
    #     else:
    #         return self.customer.device

    # @classmethod
    # def Discount(self, coupon, cart):
    #     if coupon:
    #         discount = coupon.discount/100
    #         discounted_price = cart.Total_Price * discount
    #         cart.Total_Price = cart.Total_Price - discounted_price
    #         cart.save(update_fields=['Total_Price'])

    # @classmethod
    # def UserCart(self, request, customer = None, cart_id=None):
    #     if cart_id:
    #         cart = Cart.objects.filter(id=cart_id).first()
    #     elif customer:
    #         cart = Cart.objects.select_related("customer").filter(customer=customer).first()
    #     # else:
    #     #     cart = Cart.objects.filter(id=request.session.get('cart_id')).first()
    #     return cart

    # @classmethod
    # def UserCartItems(self, cart=None, request=None):
    #     if request:
    #         user = Users.objects.get(user=request.user)
    #         cart = Cart.UserCart(request, cart_id=user.customer_cart.first().id)
    #     cart_items = CartItem.objects.select_related("cart").filter(cart=cart).all()
    #     context = { "cart":cart_items, 'user_cart':cart }
    #     return context


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
