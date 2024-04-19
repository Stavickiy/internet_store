from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create_order', views.create_order, name='create_order'),
    path('orders_history/', views.orders_history, name='orders_history'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('canceling_order/<int:order_id>/', views.canceling_order, name='canceling_order'),
]
