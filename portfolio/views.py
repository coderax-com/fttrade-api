from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import JournalSerializer
from .models import Journal, Stock


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

        try:
            stock = Stock.objects.get(id=stock_id)
        except Stock.DoesNotExist:
            raise NotFound("Stock does not exist")

        qty = request.data.get('qty')

        if type.lower() in ['b', 'buy']:
            debit_qty = qty
            credit_qty = 0
        elif type.lower() in ['s', 'sell']:
            debit_qty = 0
            credit_qty = qty

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
