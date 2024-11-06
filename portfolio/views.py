import logging
import uuid
from pathlib import Path

from click import ClickException
from django.conf import settings
from rest_framework import status, views
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView

from .exceptions import ClientException
from .serializers import JournalSerializer
from .models import Stock
from .utils.csv_loader import CsvLoader
from .utils.df_manipulator import TransactType


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

        transact_type = TransactType(type, qty)

        if not transact_type.type:
            raise ValidationError("Choose 'buy' or 'sell' for type")

        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            raise NotFound("Stock does not exist")

        data = {
            'user': self.request.user.id,
            'stock': stock.id,
            'price': stock.price,
            'debit_qty': transact_type.debit_qty,
            'credit_qty': transact_type.credit_qty,
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

        try:

            if Path(file_obj.name).suffix != '.csv':
                raise ClientException("File must be .csv")

            filepath = self._save_uploaded_file(file_obj)
            csv_loader = CsvLoader()
            df, errors = csv_loader.load_csv_to_db(filepath)
        except ClientException as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        msg = f"File {file_obj.name} was successfully uploaded"
        return Response({'message': msg}, status=status.HTTP_201_CREATED)

    def _save_uploaded_file(self, file_obj):
        unique_filename = str(uuid.uuid4())
        filepath = settings.DATA_SOURCE_DIR / f"{unique_filename}.csv"

        with open(filepath, 'wb') as destination:

            for chunk in file_obj.chunks():
                destination.write(chunk)

        return filepath
