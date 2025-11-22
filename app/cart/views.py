from itertools import product

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response


from cart import redis_cart
from cart.redis_cart import clear_cart, set_promo_code, get_promo_code
from cart.serializers import AddToCartSerializer, CartItemSerializer, RemoveFromCartSerializer, \
    UpdateQuantitySerializer, SetQuantitySerializer, CartPromoSerializer, CheckoutResponseItemSerializer
from inventory.models import Product


# Create your views here.
class CartView(APIView):
    @extend_schema(
        responses={200: CartItemSerializer(many=True)},
        description="all cart items",
    )
    def get(self, request):
        session_id = request.session.session_key
        cart_data = redis_cart.get_cart(session_id)
        promo_code = get_promo_code(session_id)
        return Response(
            {'items': cart_data, "promo_code": promo_code},
        )

    def delete(self, request):
        session_id = request.session.session_key
        clear_cart(session_id)
        return Response({"message": "cart removed successfully"}, status=status.HTTP_204_NO_CONTENT)

class AddCartView(APIView):
    @extend_schema(
        request=AddToCartSerializer,
        responses={200: None},
        description="Add cart to cart",
    )
    def post(self, request):
        if not request.session.session_key:
            request.session.create()
        session_id = request.session.session_key
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data= serializer.validated_data

        redis_cart.add_to_cart(
            session_id,
            product_id=data["product_id"],
            quantity=data["quantity"],
            name=data["name"],
            price=data["price"],
        )

        return Response({"message": "cart added successfully"}, status=status.HTTP_200_OK)

class RemoveFromCartView(APIView):
    @extend_schema(
        request=RemoveFromCartSerializer,
        responses={200: None, 404: {"description": "Not found"}},
        description='Removes cart item from redis.'
    )
    def post(self, request):
        session_id = request.session.session_key

        serializer = RemoveFromCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]

        redis_cart.remove_from_cart(session_id=session_id, product_id=product_id)
        return Response({"message": "cart removed successfully"}, status=status.HTTP_200_OK)

class UpdateQuantityView(APIView):
    @extend_schema(
        request= UpdateQuantitySerializer,
        responses={200: None},
        description='Updates quantity of cart.'
    )
    def post(self, request):
        session_id = request.session.session_key
        product_id = request.data["product_id"]
        action = request.data.get("action", "inc")

        if action == 'inc':
            redis_cart.increament_quantity(session_id=session_id, product_id=product_id)
        elif action == 'dec':
            redis_cart.decrement_quantity(session_id=session_id, product_id=product_id)

        return Response({"message": "cart updated successfully"}, status=status.HTTP_200_OK)

class SetQuantityView(APIView):
    @extend_schema(
        request=SetQuantitySerializer,
        responses={200: None},
        description='Sets quantity of cart.'
    )
    def post(self, request):
        session_id = request.session.session_key
        serializer = SetQuantitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data["product_id"]
        quantity = serializer.validated_data["quantity"]
        redis_cart.set_quantity(session_id, product_id, quantity)
        return Response({"message": "cart updated successfully"}, status=status.HTTP_202_ACCEPTED)

class CartPromoView(APIView):
    @extend_schema(
        request=CartPromoSerializer,
        responses={200:None},
        description='Carts promoted for cart.',
    )
    def post(self, request):
        session_id = request.session.session_key

        serializer = CartPromoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promo_code = serializer.validated_data["promo_code"]
        set_promo_code(session_id, promo_code)
        return Response({'message': 'cart promoted successfully'}, status=status.HTTP_200_OK)


class CartCheckOutView(APIView):
    @extend_schema(
        responses={200: CheckoutResponseItemSerializer},
        description='Checks out cart.',
    )
    def put(self, request):
        session_id = request.session.session_key
        cart_items = redis_cart.get_cart(session_id=session_id)

        if not cart_items:
            return Response({"message": "cart empty"}, status=status.HTTP_404_NOT_FOUND)

        product_ids = [item["product_id"] for item in cart_items]

        products = Product.objects.filter(id__in=product_ids, is_active=True)
        product_map = {product.id: product for product in products}

        cleaned_cart = []

        for item in cart_items:
            product_id = item["product_id"]
            product = product_map.get(product_id)

            if not product:
                redis_cart.remove_from_cart(session_id=session_id, product_id=product_id)
                continue
            if item["name"] != product.name or int(item["price"]) != int(product.price):
                redis_cart.update_cart_item(
                    session_id=session_id,
                    product_id=product_id,
                    price=product.price,
                    name=product.name,
                    quantity=item["quantity"],
                )
                item["name"] = product.name
                item["price"] = int(product.price)
            item["valid"] = True
            item['error'] = ""
            cleaned_cart.append(item)

        return Response(cleaned_cart)

