from django.contrib import admin
from .models import Complain, Order, OrderItem, Subscription

# Register your models here.
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Complain)
admin.site.register(Subscription)

