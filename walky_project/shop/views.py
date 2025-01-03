# Create your views here.
from django.shortcuts import render
from .models import Product

def homepage(request):
    return render(request, 'shop/homepage.html')

def product_list(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'shop/product_list.html', {'products': products, 'category': category})

