"""Furniture_Ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path
from Orders import views as order_views
from Admin import views as admin_views


urlpatterns = [
    path('view', order_views.OrderDetailView.as_view(), name="order_detail"),
    path('checkout/confirm-payment', order_views.CheckoutPaymentView.as_view(), name="confirm-payment"),
    path('checkout/place-order', order_views.PlaceOrderView.as_view(), name="place_order"),
    path('thankyou/<str:id>', order_views.ThankyouView.as_view(), name="thankyou"),
    path('coupon/apply', order_views.ApplyCoupon.as_view(), name="apply-coupon"),
    path('coupon/remove', order_views.RemoveCoupon.as_view(), name="remove-coupon"),
    path('onlinepayment', order_views.OnlinePayment.as_view(), name="onlinepayment"),
    path('orderpage', admin_views.OrderListView.as_view(), name="orderpage"),
    path('<str:id>', admin_views.OrderDetailView.as_view(), name="admin_view_order"),
    path('<str:id>/update', admin_views.UpdateOrderView.as_view(), name="update_orderdetail"),

    # Stripe webhook URL
    path('webhook_stripe', order_views.WebhookStripeView.as_view(), name="webhook_stripe"),

    # Stripe Subscription URL
    re_path(r'^subscription(.*)/$', order_views.ProductSubscription.as_view(), name="subscription"),
]