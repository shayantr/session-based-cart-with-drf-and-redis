from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        # read_only_fields = ('id',)
        # extra_kwargs = {
        #     'name': {'read_only': True},
        #     'description': {'read_only': True},
        #     'price': {'read_only': True},
        #     'image': {'read_only': True},
        #
        # }