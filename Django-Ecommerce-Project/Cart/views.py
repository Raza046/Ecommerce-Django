import json
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, redirect, render
from Cart.forms import AddItemToCartForm, CartUpdateForm
from Cart.periodic_tasks import clear_inactive_cart_after_a_week
from Products.models import ProductVariant, Category, SubCategory
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from UserAccount.models import Users
from .models import CartItem,Cart
from django.db.models import F
from django.views.generic import ListView, CreateView
from django.views import View
from django.contrib.auth.decorators import login_required

# # Here we will define some of our common code.

class CartMixin(View):

    def dispatch(self, request, *args, **kwargs):
        self.user = Users.objects.get(user=request.user)
        self.cart = self.user.customer_cart.first()
        self.cart_items = self.cart.cart_items.all()
        return super().dispatch(request, *args, **kwargs)


class CartView(CreateView, CartMixin):

    def get(self, request, *args, **kwargs):

        category = Category.objects.all()
        sub_category = SubCategory.objects.select_related("category").filter(
            category__id__in=category
            ).all()
        context = {
            "cart_items":self.cart_items,"subcat":sub_category, "cat":category, "cart":self.cart
            }
        return render(request, "view_cart.html", context)

    def post(self, request, *args, **kwargs):

        form = AddItemToCartForm(request.POST)

        if form.is_valid():
            product_variant_id = form.cleaned_data['product_variant_id']
            quantity = form.cleaned_data['quantity']

            prod_variant = ProductVariant.objects.filter(id=product_variant_id).first()
            cart_item_price = quantity * prod_variant.price
            cart_item = CartItem.objects.filter(product_variant=prod_variant, cart=self.cart).first()

            if cart_item:
                cart_item.quantity += quantity
                cart_item.price += cart_item_price
                cart_item.save()
            else:
                CartItem.objects.create(
                    product_variant=prod_variant, quantity=quantity, cart=self.cart, price=cart_item_price
                )

            self.cart.Total_Price = self.cart.Total_Price + cart_item_price
            self.cart.save()

            clear_inactive_cart_after_a_week(self.cart.id)

            return redirect('cart-view')

        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    def delete(self, request, *args, **kwargs):

        item_id = self.request.GET.get('item_id')
        cart_item = get_object_or_404(CartItem, id=item_id)
        Cart.objects.filter(customer=self.user).update(
            Total_Price = F('Total_Price') - cart_item.price
            )
        cart_item.delete()
        return HttpResponse('Removed From Cart Successfully..!')


class CartUpdateView(CartMixin):

    def post(self, request, *args, **kwargs):

        form = CartUpdateForm(request.POST)
        if form.is_valid():
            item_id = form.cleaned_data['item_id']
            quantity = form.cleaned_data['quantity']
            action = form.cleaned_data['action']

            cart_item = CartItem.objects.filter(id=item_id)
            product_price = cart_item.first().product_variant.price

            if action == form.ActionTypes.INCREMENT:
                cart_item.update(
                    price = product_price * (F('quantity') + 1),
                    quantity = F('quantity') + 1
                )
                self.cart.Total_Price = self.cart.Total_Price + product_price

            elif action == form.ActionTypes.DECREMENT and quantity >= 1:
                cart_item.update(
                    price = product_price * (cart_item.first().quantity - 1),
                    quantity = F('quantity') - 1)
                self.cart.Total_Price = self.cart.Total_Price - product_price

            self.cart.save()
            return HttpResponse('Updated Successfully')
        
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

