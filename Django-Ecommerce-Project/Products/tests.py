from django.test import RequestFactory, TestCase, Client
from django.contrib.auth.models import User
from Products.forms import ReviewForm

from Products.models import Category, ProductImage, ProductVariant, ReviewImages, Reviews, Product, SubCategory
from Products.views import ProductDetailView

# Create your tests here.

class ProductTest(TestCase):

    def setUp(self):

        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create(
            username='testuser', email='testuser@example.com', password='testpass')
        self.cat = Category.objects.create(name = "test_cat")
        self.sub_cat = SubCategory.objects.create(name="test_subcat", category=self.cat)
        self.product = Product.objects.create(
            id = 1, Name="Bottle1", subcategory=self.sub_cat, Price=10
            )
        self.review = Reviews.objects.create(product_id=1, name="Test1", email="test@gmail.com",
                                        comment="Very Nice Dude")
        self.review_img = ReviewImages.objects.create(review=self.review)
        self.product_variation = ProductVariant.objects.create(product_id=1, price=40)
        self.product_image = ProductImage.objects.create(product_variation_id = 1)

    def test_product_review_form(self):

        data = { "name":"Test1", "email":"test@gmail.com", "comment":"Very Nice Dude",
                "users":self.user }

        response = self.client.post('/product/submit_review/1', data = data)
        reviews = Reviews.objects.first()

        self.assertEqual(reviews, self.review)
        self.assertEqual(response.status_code, 302)

    def test_product_detail_view(self):

        request = self.factory.get('/product/1')
        response = ProductDetailView.as_view()(request, id=1)

        self.assertEqual(self.product, response.context_data['p'])
        self.assertEqual(self.product_image, response.context_data['P_Img'].first())
        self.assertEqual(response.status_code, 200)

    def test_product_list_view(self):

        response_cat = self.client.get("/products/cat/1/1")
        response_subcat = self.client.get("/products/cat/1/1")

        products = Product.objects.all()

        # Testing Subcategory
        self.assertEqual(response_subcat.context['subcat'].first(), self.sub_cat)
        self.assertEqual(response_subcat.status_code, 200)

        # Testing Category
        self.assertEqual(response_cat.context['subcat'].first(), self.sub_cat)
        self.assertEqual(response_cat.status_code, 200)
        self.assertEqual(response_cat.context['p_var'].first(), self.product_variation)
        self.assertQuerysetEqual(response_cat.context['products'], products)
        self.assertTemplateUsed(response_cat, "product/products_list.html")
        self.assertEqual(response_cat.status_code, 200)

