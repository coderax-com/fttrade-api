from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class BaseUserTestCase(TestCase):

    USER_NAME = 'Administrator'
    USER_EMAIL = 'admin@fttrade.com'
    USER_PASSWORD = 'openthedoor'
    INVALID_EMAIL = 'invalid@fttrade.com'
    INVALID_PASSWORD = 'invalidpassword'

    class Meta:
        abstract = True

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')

        self.login_data = {
            'email': self.USER_EMAIL,
            'password': self.USER_PASSWORD,
        }

        self.user_data = dict(self.login_data, name=self.USER_NAME)
        self.response = self.client.post(self.register_url, self.user_data, format='json')


class RegisterViewTestCase(BaseUserTestCase):
    """
    Test suite for the user registration api views.
    """

    def test_api_can_register_a_user(self):
        """
        Test the api has user registration capability.
        """
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)


class BaseLoginViewTestCase(BaseUserTestCase):
    """
    Test suite with an authenticated user.
    """

    def setUp(self):
        super().setUp()
        self.response = self.client.post(self.login_url, self.login_data, format='json')


class LoginViewTestCase(BaseLoginViewTestCase):
    """
    Test suite for the user login api views.
    """

    def test_api_can_login_a_user(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        self.check_jwt(self.response.data)

    def test_invalid_email(self):
        _login_data = dict(self.login_data, email=self.INVALID_EMAIL)
        response = self.client.post(self.login_url, _login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_password(self):
        _login_data = dict(self.login_data, password=self.INVALID_PASSWORD)
        response = self.client.post(self.login_url, _login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def check_jwt(self, src):
        self.assertIn('jwt', src)
        token = src['jwt']
        self.assertIs(type(token), str)
        self.assertGreater(len(token), 0)


class UserViewTestCase(BaseLoginViewTestCase):
    """
    Test suite for the user details api views.
    """

    def test_api_user_details(self):
        url = reverse('user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.USER_EMAIL)
