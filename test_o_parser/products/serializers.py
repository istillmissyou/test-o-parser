from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductParsingRequestSerializer(serializers.Serializer):
    products_count = serializers.IntegerField(min_value=1, max_value=50, required=False, default=10)
