from rest_framework import serializers
from .models import Journal, Stock


class JournalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Journal
        fields = ['id', 'user', 'stock', 'price', 'debit_qty', 'credit_qty']
