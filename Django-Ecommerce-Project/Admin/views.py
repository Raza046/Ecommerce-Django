import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from Admin.forms import CategoryForm, AddProductForm, CouponCreateForm, CouponUpdateForm, FilterGraphValidation, OrderUpdateForm, ProductVariantCreateForm, SubCategoryForm
from Admin.services import set_product_variaiton, top_products, GraphFilteration
from Cart.models import Coupon
from Orders.models import Complain, Order, OrderItem
from Products.models import Category, Product, ProductImage, Reviews, SubCategory, Variation, VariationValue, ProductVariant
from UserAccount.models import Users
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.views.generic import TemplateView, View, FormView, ListView, DeleteView, CreateView, DetailView
from django.views.generic.edit import UpdateView

# Create your views here.


class AdminDashboardView(TemplateView):

    template_name = "dashboard/dashboard.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        sales = Order.objects.filter(status="Delivered")
        total_earnings = sales.aggregate(Sum("total"))
        products = Product.objects.count()
        prods_var = OrderItem.objects.values("product_variant").annotate(product_quantity=Sum('quantity')).order_by("-product_quantity")
        reviews = Reviews.objects.all()
        top_prod = top_products(prods_var)
        month_data = GraphFilteration(sales)

        context.update({
            "total_earnings":total_earnings, "sales":sales, "p_count":products,
            "prod_sold":top_prod[1], "month_data":month_data, "top_poducts":top_prod[0],
            "reviews":reviews
        })
        return context


class FilterGraphView(FormView):

    form_class = FilterGraphValidation

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']

            sales_graph = Order.objects.filter(
                status="Delivered", create_at__gte=from_date, create_at__lte=to_date
                ).all()
            month_data = GraphFilteration(sales_graph)
 
            return HttpResponse(json.dumps(month_data))

        return HttpResponse(form.errors)


# CRUD of Category.
class CategoryMixin:

    model = Category
    template_name = "store/category_list.html"
    success_url = "store"


class CategoryView(CategoryMixin, FormView, ListView):

    form_class = CategoryForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return redirect(self.success_url)


class DeleteCategory(CategoryMixin, DeleteView):

    def get(self, request, *args, **kwargs):
        self.get_object().delete()
        return redirect(self.success_url)

# SubCategory
class SubCategoryMixin:

    model = SubCategory
    template_name = "store/subcategory_list.html"

class SubCategoryView(SubCategoryMixin, CreateView, ListView):

    form_class = SubCategoryForm
    object_list = None

    def get_success_url(self):
        return reverse_lazy('show_subcats', args=[self.kwargs['pk']])

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs.update({"instance": self.kwargs.get('pk')})
        return kwargs

    def get_context_data(self, **kwargs):
        category_id = self.kwargs.get('pk')
        subcat = SubCategory.objects.filter(category_id=category_id).all()
        context = {
            "object_list":subcat, 'category_id':category_id, "form":SubCategoryForm()
            }
        return context

    def form_valid(self, form):
        subcat_form = form.save(commit=False)
        subcat_form.category = Category.objects.get(id = self.kwargs.get('pk'))
        return super().form_valid(form)

class DeleteSubCategoryView(SubCategoryView, DeleteView):

    def get(self, request, *args, **kwargs):
        self.get_object().delete()
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class ProductView(ListView, CreateView):

    model = Product
    form_class = AddProductForm
    template_name = "store/product_list.html"
    object_list = None
    
    def get_success_url(self):
        return reverse_lazy('products', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get('pk')
        subcat = SubCategory.objects.get(id=pk)
        prod = Product.objects.filter(subcategory_id=pk).all()
        context = {"sub_categories":subcat, "prod":prod, "form":AddProductForm()}
        return context

    def form_valid(self, form):
        forms = form.save(commit=False)
        forms.subcategory = self.get_context_data().get('sub_categories')
        forms.save()
        return super().form_valid(form)


def Addvariation(request):

    variation_id = request.POST.get('p_var_id')
    product_id = request.POST.get('product')

    variation = Variation.objects.get(id=variation_id)
    prod = Product.objects.get(id=product_id)
    prod.variations.add(variation)

    return HttpResponse("Product Variation Added!")


class ProductVariationView(DetailView):

    model = Product
    template_name = "product/product_variation_list.html"
    pk_url_kwarg = 'id'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        variations = Variation.objects.all()
        context.update({
            "variations":variations,
        })
        return context


class AddProductVariationView(DetailView):

    model = Product
    template_name = "product/product_variant_list.html"
    pk_url_kwarg = 'id'
    context_object_name = 'product'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        product_variants = self.get_object().variants.all()
        product_img = ProductImage.objects.filter(product_variant__in=product_variants).all()

        variation_values = VariationValue.objects.filter(variations__in=product_variants).all()
        variation_ids = variation_values.values_list("variation__id", flat=True)
        variation = Variation.objects.filter(id__in=variation_ids).all()

        context.update({
            "variation_value":variation_values,"product_img":product_img,
            "product_variants":product_variants,"variation":variation
        })
        return context


class CreateProductVariantView(CreateView):
    form_class = ProductVariantCreateForm
    model = Product
    pk_url_kwarg = 'id'

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        variation_values = []  # store VariationValue instances here

        for item in request.POST:
            if item.startswith("variation_"):
                variation_id = item.split("variation_")[1]
                variation = Variation.objects.get(id=variation_id)
                variation_value = request.POST.get(item)
                var_get, var_create = VariationValue.objects.get_or_create(
                    variation=variation,
                    value=variation_value
                )
                variation_values.append(var_get)

        if form.is_valid():
            product_variant = form.save()
            product_variant.variation.add(*variation_values)
            product_variant.save()

        return redirect(self.request.META.get('HTTP_REFERER', '/'))
        #return JsonResponse({"errors": form.errors}, status=400)



def AddProductImages(request): #DONE

    product_id = str(request.POST.get('product_id'))
    product_imgs = request.FILES.get('images')
    ProductImage.objects.create(Image=product_imgs, product_variant_id=product_id)

    return HttpResponse('Updated Successfully')


class DeleteProductVariantView(DeleteView):

    model = ProductVariant
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse_lazy(f"products/{self.get_object().id}/add-variation")


def EditProductVariation(request):

    print("---------EDIT VARIATION----------")
    prod_id = str(request.GET.get('p_id'))
    prod_color = str(request.GET.get('p_color'))
    prod_val = str(request.GET.get('p_values'))
    prod_price = str(request.GET.get('p_price'))

    p_var = ProductVariant.objects.filter(id=prod_id).update(color=prod_color, price=prod_price)
    prod_var = ProductVariant.objects.filter(id=prod_id).first()
    prod_var.variation.clear()

    Product.SetProductVariaiton(prod_val, prod_var)

    return HttpResponse('Updated Successfully')


class OrderListView(ListView):

    queryset = Order.objects.all()
    template_name = "order/order_list.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        monthly_graph_data = GraphFilteration(self.queryset)
        context.update({
            "monthly_graph_data":monthly_graph_data,
        })
        return context


class OrderDetailView(DetailView):

    model = Order
    pk_url_kwarg = 'id'
    template_name = "order/order_detail.html"


class UpdateOrderView(UpdateView):

    model = Order
    form_class = OrderUpdateForm
    pk_url_kwarg = 'id'

    def form_valid(self, form):
        form.save()
        return JsonResponse({'message': 'Order updated successfully'}, status=200)



def UpdateOrder(request):

    order_id = int(request.GET.get('order_id'))
    email_opt = request.GET.get('email_option')
    order_status = request.GET.get('order_status')

    order = Order.objects.filter(id=order_id).first()
    order.status=order_status
    order.save(update_fields=["status"])

#    Order.order_updation(email_opt, order_id, order_status)

    return HttpResponse('Updated Successfully')


# DISOCUNT COUPON PAGE

class CouponViewMixin:
    model = Coupon
    template_name = "coupon/coupon_list.html"


class CouponView(CouponViewMixin, ListView):

    def post(self, request):
        id = self.request.POST.get("id")
        coupon = Coupon.objects.filter(id=id).first()
        form = CouponUpdateForm(self.request.POST, instance=coupon)
        if form.is_valid():
            form.save()
            return HttpResponse("Successfull", 201)

        return HttpResponse("Coupon not found!", 404)


class CouponCreateView(CouponViewMixin, CreateView):
    form_class = CouponCreateForm

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Created successfully"}, status=201)
        return JsonResponse({"errors": form.errors}, status=400)


class CustomerView(ListView):

    queryset = Users.objects.filter(user_type="Customer").all()
    template_name = "customer/customer_list.html"


class CustomerOrdersListView(DetailView):

    model = Users
    pk_url_kwarg = 'id'
    template_name = "order/customer_order_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "coupons":Coupon.objects.all(),
            "month_data":GraphFilteration(self.get_object().orders.all())
            })
        return context


class ComplainListView(ListView):

    model = Complain
    template_name = "complain/complain_list.html"


class AdminSettingView(TemplateView):

    template_name = "setting/settings_page.html"


def EditProfile(request):

    username = request.POST.get('editusername')
    password = request.POST.get('editpassword')
    user = User.objects.filter(id=request.user.id).first()
    user.username=username
    user.set_password(password)
    user.save(update_fields=["username", "password"])

    return render(request,"setting/settings_page.html")


# ADMIN CREATE VARIATION

class CreateVariationView(ListView):

    model = Variation
    template_name = "product/variations_list.html"


def CreateVariation(request):

    variantion_name = request.POST.get('varname')
    if not Variation.objects.filter(name=variantion_name).exists():
        Variation.objects.create(name=variantion_name)

    return redirect('admin_panel_variations_list')

def EditVariation(request, id):

    variantion_name = request.POST.get('edit_varname')
    variantion_value = request.POST.get('add_varname')

    variation = Variation.objects.filter(id=id).first()
    variation.name=variantion_name
    variation.save(update_fields=["name"])

    VariationValue.objects.get_or_create(
        value=variantion_value, variation = variation
        )
    return redirect('admin_panel_variations_list')

def RemoveVariationValue(request, id):
    variation = VariationValue.objects.filter(id=id).first()
    variation.delete()
    return redirect('admin_panel_variations_list')

def RemoveVariation(request, id):
    Variation.objects.get(id=id).delete()
    return redirect('admin_panel_variations_list')


# ADMIN TEAM VIEWS

class TeamListView(ListView):

    queryset = Users.objects.filter(user_type="Employee").all()
    template_name = "team/team_list.html"

