import ast
import datetime
import json

import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, ListView, TemplateView, View

from Cart.models import Cart, Coupon
from Orders.models import Order, OrderItem, Subscription
from UserAccount.models import Users

from .forms import OrderForm


class OrderMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.user = Users.objects.get(user=request.user)
        self.cart = self.user.customer_cart.first()
        self.cart_items = self.cart.cart_items.all()
        return super().dispatch(request, *args, **kwargs)

    def PlaceOrder(self, form, cart, order_total, payment_id = 0):
        if form.is_valid():
            order = form.save(commit=False)
            order.total = order_total
            order.cart = cart
            order.customer=self.user
            order.payment_id = payment_id
            order.save()
            print(order.__dict__)
            return order
        else:
            print(form.errors)

class OrderDetailView(OrderMixin, TemplateView):

    template_name = "order/view_order.html"

    def get_context_data(self, **kwargs):
        context = {
            "cart":self.cart_items,"total_price":self.cart.Total_Price,
            "coupon_used":self.cart.coupon, "form":OrderForm()
            }
        return context


class CheckoutPaymentView(OrderDetailView, FormView):

    form_class = OrderForm
    template_name = "payment/payment_page.html"

    def form_valid(self, form):
        # Access the validated form data
        form = form.cleaned_data
        self.request.session['form_data'] = form
        context = super().get_context_data()
        context['form'] = form
        return render(self.request, self.template_name, context)


class ThankyouView(OrderMixin, TemplateView):
    template_name = "checkout/thankyou.html"

    def get_context_data(self, id, **kwargs):
        order = Order.objects.get(id=id)
        context = {"order":order, "order_item":order.items, "Found":True}
        if order is None:
            context['Found'] = False
        return context


class PlaceOrderView(OrderMixin, View):

    def post(self, request, *args, **kwargs):
        order_form = OrderForm(self.request.session['form_data'])
        order = self.PlaceOrder(order_form, self.cart, self.cart.Total_Price)
        html_message = render_to_string('email/email.html', {
        "cart":self.cart_items, "discount":getattr(self.cart.coupon, 'discount', 0),
        "order":order, "total_amount":order.total
        })

        # checking if the coupon is applied in order. Then decrement the usage.
        if self.cart.coupon:
            self.cart.coupon.usage -= 1
            self.cart.coupon.save(update_fields=['usage'])
            self.cart.coupon = None
            self.cart.save(update_fields=['coupon'])

        send_mail(
        "Order from Smart Shops","Thankyou for your order...", settings.EMAIL_HOST_USER,
        [self.user.user.email], fail_silently=False, html_message=html_message
        )

        return redirect("thankyou", order.id)


class ApplyCoupon(OrderMixin, View):

    def get(self, request, *args, **kwargs):
        coupon_code = str(request.GET.get('coupon_code'))
        date_time = datetime.date.today()
        coupon = Coupon.objects.filter(
            user__in=[self.user], code=coupon_code, valid_from__lte = date_time,
            valid_to__gte = date_time, is_expired=False
            )

        if not coupon.exists():
            return HttpResponse(f'Coupon Invalid or Expired!', status=404)

        self.cart.coupon = coupon.first()
        self.cart.save(update_fields=['coupon'])
        return JsonResponse({'status': 'Successfull!', 'discount': self.cart.coupon.discount}, status=200)


class RemoveCoupon(OrderMixin, View):

    def get(self, request, *args, **kwargs):
        """ Removing the discount coupons from the cart """

        coupon_code = str(request.GET.get('coupon_code'))
        if Cart.objects.filter(customer=self.user, coupon__code=coupon_code).exists():
            self.cart.coupon = None
            self.cart.save(update_fields=['coupon'])
        return HttpResponse('Coupon Removed!')


class OnlinePayment(OrderMixin, View):

    def post(self, form):

        order_items = []
        for item in self.cart_items:
            order_items.append(
                {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.product_variant.product.Name,
                        "images":["https://img.freepik.com/free-psd/isolated-black-t-shirt-front_125540-1167.jpg?size=626&ext=jpg"]
                        },
                    "unit_amount": item.product_variant.price * 100,
                },
                "quantity": item.quantity,
                }
            )

        stripe.api_key = settings.STRIPE_API_KEY

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items = order_items,
                mode='payment',
                metadata = {
                    "order": str(self.request.session['form_data']),
                    "order_total": self.cart.Total_Price,
                    "request_session":self.request,
                    "cart_id":self.cart.id
                },
                success_url= 'http://127.0.0.1:8000' + '/home',
                cancel_url='http://127.0.0.1:8000' + '/cart/view',
            )

        except Exception as e:
            print(str(e))
            return str(e)
        return redirect(checkout_session.url, code=303)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookStripeView(OrderMixin, View):

    current_user = None

    def post(self, *args, **kwargs):
        stripe.api_key = settings.STRIPE_API_KEY
        endpoint_secret = settings.STRIPE_SECRET_KEY
        payload = self.request.body
        sig_header = self.request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            # Invalid payload
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
            stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
            )
            try:
                payment_id = event['data']['object']['payment_intent']
                order_data = json.dumps(event['data']['object']['metadata'])
                cart_id = event['data']['object']['metadata'].get("cart_id")
                # order_info = json.loads(order_data).get("order")
                order_total = json.loads(order_data).get("order_total")
                order_info = ast.literal_eval(json.loads(order_data).get("order"))

                order_form = OrderForm(order_info)
                OrderMixin.PlaceOrder(self, order_form, cart_id, order_total, payment_id)
                print('🔔 Payment succeeded!')
            except Exception as e:
                print(e)
                pass

        if event['type'] == 'customer.subscription.created':
            subscription = event.data.object
            metadata = subscription.metadata
            subscription_id = event['data']['object']['id']
            # customer_id = event['data']['object']['customer']
            # print(customer_id)
            product_id = event['data']['object']['items'].data[0]['plan']['product']

            product = stripe.Product.retrieve(product_id)
            Subscription.objects.create(
                user = self.current_user, subscription_id = subscription_id,
                subscription_name = product.name
            )
            print("SUBSCRIPTION CREATED..!!!")

        # Passed signature verification
        return HttpResponse(status=200)


class ProductSubscription(OrderMixin, ListView):

    model = Order
    template_name = "subscription.html"
    object_list = None
    stripe.api_key = settings.STRIPE_API_KEY

    def get_context_data(self, **kwargs):
        subscription = Subscription.objects.filter(user=self.request.user).first()
        context = {"subscription":subscription}
        return context

    def get(self, request, *args, **kwargs):
        print(args[0])
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print(args)
        if args[0] == "/cancel":
            # Cancel current subscription
            user_subscription = Subscription.objects.filter(user = request.user, status = 'Active').first()
            stripe.Subscription.delete(
                user_subscription.subscription_id
            )
            user_subscription.status = 'Canceled'
            user_subscription.save()
            print("******PLAN CANCELED**********")
            return redirect(self.request.META.get('HTTP_REFERER', '/'))

        product = stripe.Product.search(
            query="active:'true' AND name~'Free'",
        )
        price = stripe.Price.search(
            query=f"active:'true' AND product:'{product['data'][0].id}'",
        )
        price_id = price['data'][0].id
        order_items = [
            {
                'price': price_id,  # Replace with your actual price ID
                'quantity': 1,  # Adjust as needed
            }
        ]
        print("*******WORKING*********")
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items = order_items,
                mode = 'subscription',
                metadata = {
                    "request_user":str(self.request.user.id),
                },
                success_url= 'http://127.0.0.1:8000' + '/home',
                cancel_url='http://127.0.0.1:8000' + '/cart/view',
            )
        except Exception as e:
            print(str(e))
            return str(e)
        return redirect(checkout_session.url, code=303)

