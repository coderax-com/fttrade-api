import logging
import uuid
from pathlib import Path
from django.conf import settings
from rest_framework import status, views
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from .serializers import JournalSerializer
from .models import Stock
from .utils import CsvLoader, TransactionType


log = logging.getLogger(__name__)


class NewTransactionView(APIView):
    """
    New buy or sell transaction view
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = JournalSerializer

    def post(self, request):
        type = request.data.get('type')
        stock_id =request.data.get('stock')
        qty = request.data.get('qty')

        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            raise NotFound("Stock does not exist")

        transaction_type = TransactionType(type, qty)

        debit_qty = qty
        credit_qty = 0
        if debit_qty + credit_qty != 0:
            raise ValidationError("Choose 'buy' or 'sell' for type")

        data = {
            'user': self.request.user.id,
            'stock': stock.id,
            'price': stock.price,
            'debit_qty': debit_qty,
            'credit_qty': credit_qty,
        }

        serializer = JournalSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
        else:
            raise ValidationError(serializer.errors)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FileUploadView(views.APIView):
    """
    Upload a .csv file
    """
    parser_classes = (FormParser, MultiPartParser,)

    def put(self, request):

        try:
            file_obj = request.FILES['file']
        except KeyError as exc:
            err_msg = str(exc)
            err_msg = "Form key file is missing" if err_msg == "'file'" else err_msg
            return Response({'detail': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        if Path(file_obj.name).suffix != '.csv':
            err_msg = "File must be .csv"
            return Response({'detail': err_msg}, status=status.HTTP_400_BAD_REQUEST)

        try:
            filepath = self._save_uploaded_file(file_obj)
        except Exception as exc:
            err_msg = str(exc)
            return Response({'detail': err_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        csv_loader = CsvLoader()
        df = csv_loader.load_csv_to_db(filepath)

        if settings.DEBUG:
            print('>>>>', df.head())
            print('>>>>', csv_loader.errors)

        msg = f"File {file_obj.name} was successfully uploaded"
        return Response({'message': msg}, status=status.HTTP_201_CREATED)

    def _save_uploaded_file(self, file_obj):
        unique_filename = str(uuid.uuid4())
        filepath = settings.DATA_SOURCE_DIR / f"{unique_filename}.csv"

        with open(filepath, 'wb') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        return filepath
