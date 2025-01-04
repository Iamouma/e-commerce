from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('products/<str:category>/', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
]