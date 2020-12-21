from django.contrib.auth.models import User
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate, APIClient

from users.api.serializers import UserSerializer


# Test for users viewset
class UserViewSetTests(APITestCase):

    def setUp(self):

        self.user_data = {
            "username": "testuser",
            "password": "testpass",
        }

    # Test user registration
    def test_registration(self):

        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "bad_pass",
            "password2": "bad_pass",
        }

        response = self.client.post("/api/auth/registration/", data=data)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

    # Test that a user can login properly
    def test_login(self):

        # Create a test user, and token
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        response = self.client.post('/api/auth/login/', data=self.user_data)
        self.assertEqual(response.status_code, HTTP_200_OK)

    # Test GET requests for all users 
    def test_users(self):

        factory = APIRequestFactory()

        # Create a test user, and token
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.token = Token.objects.create(user=self.user)

        response = factory.get("/api/users/")
        force_authenticate(request=response, user=self.user)

    # GET a single, specific user
    def test_specific_user(self):

        factory = APIRequestFactory()

        # Create a test user, and token
        self.user = User.objects.create_user(id=1, username="testuser", password="testpass")
        self.token = Token.objects.create(user=self.user)

        response = factory.get("/api/users/1")
        force_authenticate(request=response, user=self.user)

    # Test updating a User's account info (email address)
    def test_updating_user(self):

        data = {
            "username": "testuser",
            "password": "testpass",
            "email": "testuser@example.com",
        }

        # Create a test user, and token
        self.user = User.objects.create_user(id=1, username="testuser", password="testpass", email="testuser@example.com")
        self.token = Token.objects.create(user=self.user)
        # Log the test user in
        self.client.post("/api/auth/login/", data=data)

        # Update the test user's email address, and verify that it has been saved to db
        user_instance = User.objects.get(id=1)
        user_instance.email = "test_user@example.com"
        user_instance.username = "test_user"
        user_instance.password = "test_password"
        user_instance.save()

        self.assertEqual(user_instance.email, "test_user@example.com")
        self.assertEqual(user_instance.username, "test_user")
        self.assertEqual(user_instance.password, "test_password")


    def test_change_password(self):

        client = APIClient()
        user_1 = User.objects.create_user(id=1, username="testuser1", password="testpass", email="testuser1@example.com")
        user_2 = User.objects.create_user(id=2, username="testuser2", password="testpass", email="testuser2@example.com")

        pw_change_data = {
            'old_password': 'testpass',
            'new_password': 'userspword'
        }

        no_cred_response = client.put('/api/users/me/change_password/', data=pw_change_data)
        self.assertNotEqual(no_cred_response.status_code, 200)

        token = Token.objects.create(user=user_1)
        client.credentials(HTTP_AUTHORIZATION='Token '+ token.key)

        correct_cred_response = client.put('/api/users/1/change_password/', data=pw_change_data)
        self.assertEqual(correct_cred_response.status_code, 200)
        
        wrong_cred_response = client.put('/api/users/2/change_password/', data=pw_change_data)
        self.assertNotEqual(wrong_cred_response.status_code, 200)