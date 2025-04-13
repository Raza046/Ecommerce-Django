from django.test import Client, TestCase
from django.contrib.auth.models import User, AnonymousUser

# Create your tests here.

class OrderTest(TestCase):

    def setUp(self):

        self.client = Client()
        # self.user = User.objects.create(username = "test", password = "test")
        # self.client.login(self.user)

        return super().setUp()


    def test_order_view(self):
        
        response = self.client.get("/Vieworder")
        print(response)
        print(response.status_code)
        self.assertEqual(response.status_code, 200)


