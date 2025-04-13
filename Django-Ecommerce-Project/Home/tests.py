from django.test import TestCase, Client
from Products.models import Product, SubCategory, Category
# Create your tests here.

class HomePageTest(TestCase):

    def setUp(self):

        self.client = Client()
        cat = Category.objects.create(name = "test_cat")
        sub_cat = SubCategory.objects.create(name="test_subcat", category=cat)
        Product.objects.create(Name="Bottle1", subcategory=sub_cat, Price=10)
        Product.objects.create(Name="Bottle2", subcategory=sub_cat, Price=10)
        Product.objects.create(Name="Bottle3", subcategory=sub_cat, Price=10)

    def test_homepage_view(self):

        response = self.client.get("/home")
        self.assertEqual(response.status_code, 200)
        # print(Product.objects.all())
        # print(response.context['products'])
        self.assertQuerysetEqual(
            response.context['products'], Product.objects.all(), ordered=False
        )

    def test_product_model(self):

        cat = Category.objects.create(name = "test_cat")
        sub_cat = SubCategory.objects.create(name="test_subcat", category=cat)
        p = Product.objects.create(Name="Bottle1", subcategory=sub_cat, Price=10)
        response = self.client.get("/home")

        self.assertEqual(str(p), "Bottle1")

    def test_contact_page(self):

        response = self.client.get("/contact")
        self.assertEqual(response.status_code, 200)
