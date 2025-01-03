from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('products/<str:category>/', views.product_list, name='product_list'),
]