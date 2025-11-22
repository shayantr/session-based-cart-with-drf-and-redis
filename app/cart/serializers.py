from rest_framework import serializers


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()


class CartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()


class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()


class UpdateQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['inc', 'dec'], default='inc')


class SetQuantitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()


class CartPromoSerializer(serializers.Serializer):
    promo_code = serializers.CharField(max_length=500)


class CheckoutResponseItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    name = serializers.CharField()
    price = serializers.IntegerField()
    quantity = serializers.IntegerField()
    valid = serializers.BooleanField()
    error = serializers.CharField(allow_blank=True)
