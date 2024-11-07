from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Journal, Stock
from .utils.csv_ingestor import CsvIngestor


USER_CLASS = get_user_model()
ADMIN_EMAIL = 'admin@fttrade.com'


class BaseAuthenticatedTestCase(TestCase):

    def setUp(self):
        self.create_stock()
        self.create_user()
        self.authenticate_user()

    def create_stock(self):

        stock_data = [
            {
                'id': 'ALI',
                'name': 'Ayala Land Inc.',
                'price': 1.01,
            },
            {
                'id': 'BPI',
                'name': 'Bank of Philippine Islands',
                'price': 2.02,
            },
        ]

        for stock in stock_data:
            Stock.objects.create(**stock)

    def create_user(self):

        user_data = {
            'name': 'Administrator',
            'email': ADMIN_EMAIL,
            'password': 'plsletmein',
        }

        self.user = USER_CLASS.objects.create(**user_data)

    def authenticate_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")


class BuyStockViewTestCase(BaseAuthenticatedTestCase):
    """
    Test suite for /api/portfolio/new-transaction endpoint
    """

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


class SellStockViewTestCase(BaseAuthenticatedTestCase):
    """
    Test suite for /api/portfolio/new-transaction endpoint
    """

    def setUp(self):
        super().setUp()
        self.sell_stock_url = reverse('new_transaction')

        self.sell_stock_data = {
            'type': 'sell',
            'stock': 'BPI',
            'qty': 4,
        }

        self.response = self.client.post(self.sell_stock_url, self.sell_stock_data, format='json')

    def test_sell_stock(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Journal.objects.count(), 0)
        journal = Journal.objects.all().first()
        self.assertEqual(journal.user, self.user)
        self.assertEqual(journal.stock.id, self.sell_stock_data['stock'])
        self.assertEqual(journal.credit_qty, self.sell_stock_data['qty'])


# class CsvIngestorTestCase(BaseAuthenticatedTestCase):
#
#     def setUp(self):
#         super().setUp()
#         self.filepath = settings.DATA_SOURCE_DIR / 'admin-transactions.csv'
#         self.ingestor = CsvIngestor()
#
#     def test_csv_loader(self):
#         df, errors = self.ingestor.load_csv_to_db(self.filepath)
#         print('>>>>', df.head())
#         print('>>>>', errors)


class TotalInvestedViewTestCase(BaseAuthenticatedTestCase):
    """
    Test suite for /api/portfolio/total-invested endpoint
    """

    def setUp(self):
        super().setUp()
        self.buy_stock_url = reverse('new_transaction')
        self.total_invested_url = reverse('total_invested')

        self.buy_stock_data = [
            {
                'type': 'buy',
                'stock': 'ALI',
                'qty': 3,
            },
            {
                'type': 'buy',
                'stock': 'ALI',
                'qty': 5,
            },
            {
                'type': 'sell',
                'stock': 'ALI',
                'qty': 2,
            },
            {
                'type': 'buy',
                'stock': 'BPI',
                'qty': 4,
            },
            {
                'type': 'sell',
                'stock': 'BPI',
                'qty': 1,
            },
        ]

        # ALI  6.06
        for payload in self.buy_stock_data:
            self.client.post(self.buy_stock_url, payload, format='json')

        params = {'stock': 'ALI'}
        self.response = self.client.get(self.total_invested_url, params)

    def test_total_invested(self):
        self.assertEqual(self.response.status_code, status.HTTP_200_OK)
        expected_data = {'stock': 'ALI', 'transactions': 3, 'total': Decimal('6.0600')}
        self.assertEqual(self.response.data, expected_data)
