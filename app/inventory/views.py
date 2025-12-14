import json
from itertools import product

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework import generics, status

from rest_framework.response import Response
from .models import Product
from .redis_services.inventory import get_all_items, cache_product
from .serializers import ProductSerializer
# Create your views here.


class ProductListAPIView(APIView):
    def get(self, request):
        cached_products = get_all_items()
        serializer = ProductSerializer(cached_products , many=True)
        return Response(serializer.data)
class AddProductAPIView(APIView):
    @extend_schema(
        request=ProductSerializer,
        responses={201: ProductSerializer},
    )
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            cache_product(product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
class EditProductView(APIView):
    @extend_schema(
        request=ProductSerializer,
        responses={202: ProductSerializer},
    )
    def put(self, request, id):
        product = Product.objects.get(id=id)
        serializer = ProductSerializer(instance=product, data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            cache_product(product)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

