from django.shortcuts import redirect, render
from django.views import View
from Products.models import Category, Product, SubCategory
from django.views.decorators.cache import cache_page

# Create your views here.

class HomePageView(View):

    model = Product

    def __init__(self):
        self.query = self.model.objects.select_related("subcategory")

    def get(self, *args):
        # tasks.CheckFun.delay()
        cat = Category.objects.all()
        subcat = SubCategory.objects.select_related("category").all()
        products = self.query.all()
        men_products = self.query.filter(subcategory__name="Men")[:3]
        women_products = self.query.filter(subcategory__name="Women")[:3]

        context =  {
            "cat": cat, "products":products, "men_products":men_products,
            "women_products":women_products, "subcat":subcat
            }
        return render(self.request,"index/index.html",context)

def ContactPage(request):
    return render(request,"contact_us/contact_us.html")
