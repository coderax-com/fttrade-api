from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserSerializer
from .models import Journal, Stock


class BaseAuthenticatedTestCase(TestCase):

    def setUp(self):
        self.UserClass = get_user_model()
        self.create_stock()
        self.create_user()
        self.authenticate_user()

    def create_stock(self):

        stock_data = {
            'id': 'ALI',
            'name': 'Ayala Land Inc.',
            'price': 1.01,
        }

        Stock.objects.create(**stock_data)

    def create_user(self):

        user_data = {
            'name': 'Administrator',
            'email': 'admin@fttrade.com',
            'password': 'plsletmein',
        }

        self.user = self.UserClass.objects.create(**user_data)

    def authenticate_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")


class BuyStockViewTestCase(BaseAuthenticatedTestCase):

    def setUp(self):
        super().setUp()
        self.buy_stock_url = reverse('new_transaction')

        self.buy_stock_data = {
            'type': 'buy',
            'stock': 'ALI',
            'qty': 3,
        }

        self.response = self.client.post(self.buy_stock_url, self.buy_stock_data, format='json')

    def test_buy_stock(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Journal.objects.count(), 0)
        journal = Journal.objects.all().first()
        self.assertEqual(journal.user, self.user)
        self.assertEqual(journal.stock.id, self.buy_stock_data['stock'])
        self.assertEqual(journal.debit_qty, self.buy_stock_data['qty'])