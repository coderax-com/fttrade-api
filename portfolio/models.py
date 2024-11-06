from django.contrib.auth import get_user_model
from django.db import models


USER_CLASS = get_user_model()


class Stock(models.Model):
    """
    Class that represents a Stock in the Stock Market.
    """
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=80, unique=True, null=True, blank=True)
    price = models.DecimalField(max_digits=18, decimal_places=4)


class Journal(models.Model):
    """
    Class for keeping track of transactions.
    """
    user = models.ForeignKey(USER_CLASS, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=18, decimal_places=4)
    debit_qty = models.IntegerField(default=0)
    credit_qty = models.IntegerField(default=0)
