from django.urls import path
from . import views


urlpatterns = [
    path('new-transaction', views.NewTransactionView.as_view(), name='new_transaction'),
]
