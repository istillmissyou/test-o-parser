from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import (HTTP_200_OK, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from .models import Product
from .serializers import ProductParsingRequestSerializer, ProductSerializer
from .tasks import parser_ozon


@swagger_auto_schema(method='get',
                     responses={200: ProductSerializer(many=True)},
                     operation_description="Получение всех товаров")
@swagger_auto_schema(method='post',
                     request_body=ProductParsingRequestSerializer,
                     responses={201: 'Created', 400: 'Bad Request'},
                     operation_description="Включить парсер. В теле запроса отправлять число товаров")
@api_view(['POST', 'GET'])
def products_view(request):
    if request.method == 'POST':
        serializer = ProductParsingRequestSerializer(data=request.data)
        if serializer.is_valid():
            products_count = serializer.validated_data.get('products_count')

            parser_ozon.delay(products_count=products_count)
            
            return Response({'error': False, 'message': f'Parsing {products_count} products started.'}, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({'error': False, 'message': 'OK', 'payload': serializer.data}, status=HTTP_200_OK)


@swagger_auto_schema(method='get',
                     responses={200: ProductSerializer()},
                     operation_description="GET - получение товара по ID")
@api_view(['GET'])
def get_product_by_id(request, product_id: int):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({'error': True, 'message': 'Product not found.', 'payload': None}, status=HTTP_200_OK)

    serializer = ProductSerializer(product)
    return Response({'error': False, 'message': 'OK', 'payload': serializer.data}, status=HTTP_200_OK)
