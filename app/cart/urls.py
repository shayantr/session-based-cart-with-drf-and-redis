from django.urls import path

from cart import views

urlpatterns =[
    path('add-to-cart/', views.AddCartView.as_view(), name='add_to_cart'),
    path('get-cart/', views.CartView.as_view(), name='get_cart'),
    path('delete-cart/', views.RemoveFromCartView.as_view(), name='remove_cart'),
    path('update-quantity/', views.UpdateQuantityView.as_view(), name='update-quantity'),
    path('set-quantity/', views.SetQuantityView.as_view(), name='set-quantity'),
    path('set-promo_code/', views.CartPromoView.as_view(), name='prmo_code'),
    path('checkout/', views.CartCheckOutView.as_view(), name='checkout'),

]