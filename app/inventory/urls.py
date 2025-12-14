from django.urls import path, include
from .views import ProductListAPIView, AddProductAPIView, EditProductView

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product-list'),
    path('add-product/', AddProductAPIView.as_view(), name='add-product'),
    path('edit-product/<int:id>', EditProductView.as_view(), name='edit-product'),

]