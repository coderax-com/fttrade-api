import logging
import pandas as pd


log = logging.getLogger(__name__)


class DataFrameCalculator(object):
    """
    Class to calculate summary totals in a DataFrame.
    """

    REQUIRED_SCHEMA = ['id', 'user_id', 'stock_id', 'price', 'debit_qty', 'credit_qty']

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self._validate_df()
        self._fill_subtotals()

    def _validate_df(self):
        columns = list(self.df)

        if columns != self.REQUIRED_SCHEMA:
            err_msg = f"DataFrame does not have required columns ({', '.join(self.REQUIRED_SCHEMA)})"
            raise Exception(err_msg)

    def _fill_subtotals(self):
        self.df['debit_amt'] = self.df.apply(lambda r: r['price'] * r['debit_qty'], axis=1)
        self.df['credit_amt'] = self.df.apply(lambda r: r['price'] * r['credit_qty'], axis=1)
        self.df['sub_total'] = self.df.apply(lambda r: r['debit_amt'] - r['credit_amt'], axis=1)

    def get_total(self):
        total = self.df['sub_total'].sum()
        return total