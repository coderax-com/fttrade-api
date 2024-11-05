from django.urls import reverse
from rest_framework import status
from users.tests import BaseLoginViewTestCase
from .models import Journal


class BuyStockViewTestCase(BaseLoginViewTestCase):

    def setUp(self):
        self.buy_stock_url = reverse('new_transaction')
        print('>>>>', self.buy_stock_url)

        self.buy_stock_data = {
            'user': 1,
            'type': 'buy',
            'stock': 'ALI',
            'qty': 3,
        }

        self.response =  self.client.post(self.buy_stock_url, data=self.buy_stock_data, format='json')

    def test_buy_stock(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        self.assertGreater(Journal.objects.count(), 0)
        journal = Journal.objects.all().first()
        self.assertEqual(journal.user, self.buy_stock_data['user'])
        self.assertEqual(journal.stock, self.buy_stock_data['stock'])
        self.assertEqual(journal.debit_qty, self.buy_stock_data['qty'])
