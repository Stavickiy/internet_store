from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path("add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("remove/<int:cart_item_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("minus/<int:product_id>/", views.minus_from_cart, name="minus_from_cart"),
    path("add_promo_cod/", views.add_promo_cod, name="add_promo_cod"),
    path("checkout1/", views.checkout1, name="checkout1"),
    path("checkout2/", views.checkout2, name="checkout2"),
    path("checkout3/", views.checkout3, name="checkout3"),
    path("checkout4/", views.checkout4, name="checkout4"),
]
