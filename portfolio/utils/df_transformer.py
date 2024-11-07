import logging
import pandas as pd
from django.contrib.auth import get_user_model

from portfolio.exceptions import ClientException
from portfolio.models import Stock


log = logging.getLogger(__name__)
USER_CLASS = get_user_model()


class DataFrameTransformer:
    """
    Class for transforming a DataFrame. The df is filled, cleaned and transformed.

    The df should have the following schema:

        email:str   => user's email address
        type:str    => either "buy" or "sell"
        stock:str   => the stock ID
        qty:int     => the quantity to buy or sell
    """

    REQUIRED_SCHEMA = ['email', 'type', 'stock', 'qty']

    def __init__(self, df:pd.DataFrame):
        self.user_cache = {}
        self.stock_cache = {}
        self.errors = []
        
        self.df = df

        self._validate_df()
        self._fill_df()
        self._clean_df()
        self._transform_df()

    def _validate_df(self) -> None:
        columns = list(self.df)

        if columns != self.REQUIRED_SCHEMA:
            err_msg = f"Schema must be {', '.join(self.REQUIRED_SCHEMA)}"
            raise ClientException(err_msg)

    def _fill_df(self):
        self._fill_user_id()
        self._fill_type()
        self._fill_stock_id()
        self._fill_price()
        self._fill_qty()

    def _fill_user_id(self):

        def _fetch_user_id(email):
            user = self._fetch_user(email)
            return getattr(user, 'id', None)

        self.df['user_id'] = self.df['email'].apply(lambda email: _fetch_user_id(email))

    def _fill_type(self):
        self.df['type'] = self.df.apply(lambda r: TransactType(r['type'], r['qty']).type, axis=1)

    def _fill_stock_id(self):

        def _fetch_stock_id(stock_id):
            stock = self._fetch_stock(stock_id)
            return getattr(stock, 'id', None)

        self.df['stock_id'] = self.df['stock'].apply(lambda stock_id: _fetch_stock_id(stock_id))

    def _fill_price(self):

        def _fetch_price(stock_id:str):
            stock = self._fetch_stock(stock_id)
            return getattr(stock, 'price', None)

        self.df['price'] = self.df['stock'].apply(lambda stock_id: _fetch_price(stock_id))

    def _fill_qty(self):
        self.df['debit_qty'] = self.df.apply(lambda r: TransactType(r['type'], r['qty']).debit_qty, axis=1)
        self.df['credit_qty'] = self.df.apply(lambda r: TransactType(r['type'], r['qty']).credit_qty, axis=1)

    def _clean_df(self):
        self.df.dropna(subset=['user_id', 'type', 'stock_id', 'price'], inplace=True)

    def _transform_df(self):
        self.df.drop(['email', 'type', 'stock', 'qty'], axis=1, inplace=True)

    def _fetch_user(self, email:str):

        try:
            return self.user_cache[email]
        except KeyError:
            pass

        try:
            user = USER_CLASS.objects.get(email=email)
        except USER_CLASS.DoesNotExist:
            self.errors.append(f"User {email} does not exist")
            return None
        else:
            self.user_cache.setdefault(email, user)
            return user

    def _fetch_stock(self, stock_id:str):
        try:
            return self.stock_cache[stock_id]
        except KeyError:
            pass

        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            self.errors.append(f"Stock {stock_id} does not exist")
            return None
        else:
            self.stock_cache.setdefault(stock_id, stock)
            return stock


class TransactType:
    """
    A utility class to get type, debit_qty and credit_qty based on the type of transaction.
    """

    def __init__(self, transact_type:str, qty:int=None):
        self.type = 'buy' if transact_type in ['buy', 'b'] else 'sell' if transact_type in ['sell', 's'] else None
        self._qty = qty

    @property
    def debit_qty(self):
        return self._qty if self.type == 'buy' else 0

    @property
    def credit_qty(self):
        return self._qty if self.type == 'sell' else 0
