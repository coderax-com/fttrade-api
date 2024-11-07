from django.urls import path
from . import views


urlpatterns = [
    path('new-transaction', views.NewTransactionView.as_view(), name='new_transaction'),
    path('file-upload', views.FileUploadView.as_view(), name='file_upload'),
    path('total-invested', views.TotalInvestedView.as_view(), name='total_invested'),
]
