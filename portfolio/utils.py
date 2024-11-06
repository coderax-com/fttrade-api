import logging
from enum import Enum

import pandas as pd
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from fttrade.asgi import application
# from sqlalchemy import create_engine, TextClause, RowMapping
# from sqlalchemy.exc import ResourceClosedError
from users.models import User
from portfolio.models import Stock

log = logging.getLogger(__name__)


class CsvLoader:
    """
    Class for ingesting .csv files and saving it directly into the database.

    The .csv file should have the following schema:

        email:str   => user's email address
        type:str    => either "buy" or "sell"
        stock:str   => the stock ID
        qty:int     => the quantity to buy or sell
    """

    def __init__(self):
        self.user_cache = {}
        self.stock_cache = {}
        self.errors = []

    def load_csv_to_db(self, csv_path:Path):
        df = self._read_csv(csv_path)
        self._fill_df(df)
        self._clean_df(df)
        self._transform_df(df)
        # self._save_df(df)
        return df

    def _read_csv(self, path:Path) -> pd.DataFrame:
        df = pd.read_csv(str(path))
        return df

    def _fill_df(self, df:pd.DataFrame):
        self._fill_user_id(df)
        self._fill_type(df)
        self._fill_stock_id(df)
        self._fill_price(df)
        self._fill_qty(df)

    def _fill_user_id(self, df:pd.DataFrame):

        def _fetch_user_id(email):
            user = self._fetch_user(email)
            return user.id if user else None

        df['user_id'] = df['email'].apply(lambda email: _fetch_user_id(email))

    def _fill_type(self, df:pd.DataFrame):
        df['type'] = df.apply(lambda r: TransactionType(r['type'], r['qty']).type, axis=1)

    def _fill_stock_id(self, df:pd.DataFrame):

        def _fetch_stock_id(stock_id):
            stock = self._fetch_stock(stock_id)
            return stock.id if stock else None

        df['stock_id'] = df['stock'].apply(lambda stock_id: _fetch_stock_id(stock_id))

    def _fill_price(self, df:pd.DataFrame):

        def _fetch_price(stock_id:str):
            stock = self._fetch_stock(stock_id)
            return stock.price if stock else None

        df['price'] = df['stock'].apply(lambda stock_id: _fetch_price(stock_id))

    def _fill_qty(self, df:pd.DataFrame):
        df['debit_qty'] = df.apply(lambda r: TransactionType(r['type'], r['qty']).debit_qty, axis=1)
        df['credit_qty'] = df.apply(lambda r: TransactionType(r['type'], r['qty']).credit_qty, axis=1)

    def _clean_df(self, df:pd.DataFrame):
        df.dropna(subset=['user_id', 'type', 'stock_id', 'price'], inplace=True)

    def _transform_df(self, df:pd.DataFrame):
        df.drop(['email', 'type', 'stock', 'qty'], axis=1, inplace=True)

    def _fetch_user(self, email:str):

        try:
            return self.user_cache[email]
        except KeyError:
            pass

        UserClass = get_user_model()

        try:
            user = UserClass.objects.get(email=email)
        except ObjectDoesNotExist:
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
        except ObjectDoesNotExist:
            self.errors.append(f"Stock {stock_id} does not exist")
            return None
        else:
            self.stock_cache.setdefault(stock_id, stock)
            return stock

    def _connect_to_db(self):
        database = settings.DATABASES['default']
        conn_str = "postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}".format(**database)
        engine = create_engine(conn_str)
        return engine

    def _save_df(self, df:pd.DataFrame):
        table_name = 'portfolio_journal'
        engine = self._connect_to_db()
        if_exists = 'append'
        df.to_sql(name=table_name, con=engine, index=False, if_exists=if_exists)


class TransactionType:
    """
    A utility class to get type, debit_qty and credit_qty based on the type of transaction.
    """

    def __init__(self, type:str, qty:int=None):
        self.type = 'buy' if type in ['buy', 'b'] else 'sell' if type in ['sell', 's'] else None
        self._qty = qty

    @property
    def debit_qty(self):
        return self._qty if self.type == 'buy' else 0

    @property
    def credit_qty(self):
        return self._qty if self.type == 'sell' else 0
