from typing import Any, Dict
from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from Cart.forms import CartItemsForm
from Products.forms import ReviewForm
from .models import *
from django.views.generic import ListView, CreateView, DetailView, FormView


class ProductMixin:

    model = Product

    def __init__(self):
        self.product_query = self.model.objects.select_related("subcategory")
        self.subcat_query = SubCategory.objects.select_related("category")
        self.category_query = Category.objects.all()


class ViewProducts(ProductMixin, ListView):

    template_name = "product/products_list.html"
    # paginate_by = 1
    object_list = None

    def get_context_data(self, **kwargs):

        if self.kwargs['search'] == "subcat":
            sub_cat = self.subcat_query.filter(id = self.kwargs['id'])

        elif self.kwargs['search'] == "cat":
            sub_cat = self.subcat_query.filter(category_id = self.kwargs['id']).all()

        products = self.product_query.filter(subcategory__in=sub_cat).all()
        p_variation = ProductVariant.objects.select_related("product").filter(product__in = products).all()
        p_max = p_variation.order_by('price').last().price

        context = {
            'cat':self.category_query, 'subcat':self.subcat_query, 'p_var':p_variation,
            "sub_cat":sub_cat, 'products':products, 'p_min':0, 'p_max':p_max
        }
        return context

    def post(self, *args, **kwargs):

        instock = self.request.POST.get('instock')
        p_max = self.request.POST.get('priceRange')
        context = self.get_context_data()

        if instock is None:
            instock = False

        products = self.product_query.filter(subcategory__in = context['sub_cat'], Price__lte=p_max, availability=instock).all()
        context["products"] = products
        return render(self.request, self.template_name, context)


class ProductDetailView(ProductMixin, DetailView):

    template_name = "product/product_detail.html"
    object_list = None
    pk_url_kwarg = 'id'

    def get_context_data(self, *args, **kwargs):

        product = self.get_object()
        product_variants = product.variants.all()
        #product_variant = ProductVariant.objects.select_related("product").filter(product=product).all()
        p_img = ProductImage.objects.select_related("product_variant").filter(product_variant__in=product_variants).all()
        #reviews = Reviews.objects.select_related("product").filter(product=product).all()
        reviews = product.reviews.all()
        reviews_img = ReviewImages.objects.select_related("review").filter(review__in=reviews).all()
        form = ReviewForm()

        context={
            "product":product, "prod_variants":product_variants, "product_images":p_img, "p_vars":product_variants, "reviews":reviews,
            "reviews_img":reviews_img, "cat":self.category_query, "subcat":self.subcat_query,
            "form":form
            }
        return context


class ReviewFormView(FormView):

    model = Reviews
    form_class = ReviewForm
    template_name = "product/product_detail.html"

    def form_valid(self, form, **kwargs):

        review_form = form.save(commit=False)
        review_form.product = Product.objects.get(id = self.kwargs.get('id'))
        try:
            review_form.users = self.request.user
        except:
            pass
        review_form.save()
        return redirect('product', self.kwargs.get('id'))

    def form_invalid(self, form):
        print(form.errors)
        return redirect('product', self.kwargs.get('id'))
