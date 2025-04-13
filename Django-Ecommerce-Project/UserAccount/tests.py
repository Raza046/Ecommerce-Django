from django.test import Client, TestCase
from django.contrib.auth.models import AnonymousUser, User

# Create your tests here.

class UserTest(TestCase):

    def setUp(self):

        self.client = Client()
        self.user = User.objects.create_user(
        username='testuser', email='testuser@example.com', password='testpass')

    def test_user_valid_login_view(self):

        get_response = self.client.get("/login")
        post_response = self.client.post("/login", data={"username":"testuser", "password":"testpass"})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(post_response.wsgi_request.user.is_authenticated)

    def test_user_invalid_login_view(self):

        get_response = self.client.get("/login")
        post_response = self.client.post("/login", data={"username":"testuser", "password":"testpass1"})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(post_response.wsgi_request.user.is_authenticated)

    def test_invalid_login_url(self):

        get_response = self.client.get("/logins")
        get_response1 = self.client.get("login")
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(get_response1.status_code, 404)
