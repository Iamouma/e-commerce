# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Product, Cart

def homepage(request):
    return render(request, 'shop/homepage.html')

def product_list(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'shop/product_list.html', {'products': products, 'category': category})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        return JsonResponse({'message': 'Product added to cart!', 'quantity': cart_item.quantity})

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total_price': total_price})
