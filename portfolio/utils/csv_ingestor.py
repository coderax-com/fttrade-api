import logging
import pandas as pd

from pathlib import Path
from django.conf import settings
from django.db import connection
from sqlalchemy import create_engine

from .df_transformer import DataFrameTransformer


log = logging.getLogger(__name__)


class CsvIngestor:
    """
    Class for ingesting .csv files and saving it directly into the database.

    The .csv file should have the following schema:

        email:str   => user's email address
        type:str    => either "buy" or "sell"
        stock:str   => the stock ID
        qty:int     => the quantity to buy or sell
    """

    def load_csv_to_db(self, csv_path:Path) -> list:
        """
        Load the input .csv file and save it to the database.

        :param csv_path:
        :return:
            [
                pd.DataFrame => the manipulated DataFrame
                errors => list of error messages
            ]
        """
        df = self._read_csv(csv_path)
        dfm = DataFrameTransformer(df)
        self._save_df(df)
        return [dfm.df, dfm.errors]

    @staticmethod
    def _read_csv(path:Path) -> pd.DataFrame:
        df = pd.read_csv(str(path))
        return df

    @staticmethod
    def _connect_to_db(conn_str=None):
        database = connection.settings_dict
        conn_str = conn_str or "postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}".format(**database)
        engine = create_engine(conn_str)
        return engine

    def _save_df(self, df:pd.DataFrame):
        table_name = 'portfolio_journal'
        engine = self._connect_to_db()
        df.to_sql(name=table_name, con=engine, index=False, if_exists='append')
        engine.dispose()
