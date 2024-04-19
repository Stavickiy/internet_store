from django.urls import path
from . import views

app_name = 'preorders'

urlpatterns = [
    path('preorder_cart_detail', views.preorder_cart_detail, name='preorder_cart_detail'),
    path("add/<int:product_id>/", views.add_to_preorder_cart, name="add_to_preorder_cart"),
    path("remove/<int:cart_item_id>/", views.remove_from_preorder_cart, name="remove_from_preorder_cart"),
    path("minus/<int:product_id>/", views.minus_from_preorder_cart, name="minus_from_preorder_cart"),
    path("preorder_checkout1/", views.checkout1, name="preorder_checkout1"),
    path("preorder_checkout2/", views.checkout2, name="preorder_checkout2"),
    path("preorder_checkout3/", views.checkout3, name="preorder_checkout3"),
    path("preorder_checkout4/", views.checkout4, name="preorder_checkout4"),
    path('create_preorder', views.create_preorder, name='create_preorder'),
    path('preorders_history/', views.preorders_history, name='preorders_history'),
    path('preorder_detail/<int:order_id>/', views.preorder_detail, name='preorder_detail'),
    path('canceling_preorder/<int:order_id>/', views.canceling_preorder, name='canceling_preorder'),
]
