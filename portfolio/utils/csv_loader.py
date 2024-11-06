import logging
import pandas as pd

from pathlib import Path
from django.conf import settings
from .df_manipulator import DataFrameManipulator


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
        dfm = DataFrameManipulator(df)
        # self._save_df(df)
        return [dfm.df, dfm.errors]

    def _read_csv(self, path:Path) -> pd.DataFrame:
        df = pd.read_csv(str(path))
        return df


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
