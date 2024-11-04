from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


class ViewTestCase(TestCase):
    """
    Test suite for the api views.
    """

    def setUp(self):
        """
        Define the test client and other test variables.
        """
        self.client = APIClient()
        url = reverse('register')
        self.user_data = {
            'name': 'administrator',
            'email': 'admin@fttrade.com',
            'password': 'openthedoor',
        }
        self.response = self.client.post(url, self.user_data, format='json')

    def test_api_can_register_a_user(self):
        """
        Test the api has user registration capability.
        """
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
