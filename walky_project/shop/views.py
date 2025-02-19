# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.decorators import login_required, permission_required
from .models import Product, Cart, Order, OrderItem, Review, Wishlist
from django.core.mail import send_mail
from .forms import ReviewForm, UserForm, ProfileForm
from django.db.models import Q




def homepage(request):
    return render(request, 'shop/homepage.html')

def product_list(request, category):
    products = Product.objects.filter(category=category)
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    products = Product.objects.all()

    # Search by name or description
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Filter by category
    if category:
        products = products.filter(category=category)

    # Filter by price range
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'products': products,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    review_form = ReviewForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect('product_detail', product_id=product.id)

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
    }
    return render(request, 'shop/product_detail.html', context)

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
 
@login_required
def update_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        new_quantity = int(request.POST.get('quantity', 1))
        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
            return JsonResponse({'message': 'Cart updated!', 'quantity': cart_item.quantity, 'total_price': cart_item.total_price()})
        else:
            return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

@login_required
def remove_from_cart(request, cart_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(Cart, id=cart_id, user=request.user)
        cart_item.delete()
        return JsonResponse({'message': 'Item removed from cart!'})


@login_required
@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('cart')

        # Calculate total price
        total_price = sum(item.quantity * item.product.price for item in cart_items)

        # Create an Order
        order = Order.objects.create(user=request.user, total_price=total_price)

        # Create OrderItems and clear the cart
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price,
            )
            cart_item.delete()

        # Send Confirmation Email
        subject = f"Order Confirmation - Order #{order.id}"
        message = f"Thank you for your purchase, {request.user.username}! Your order #{order.id} has been successfully placed.\n\nOrder Details:\n"
        for item in order.items.all():
            message += f"{item.quantity} x {item.product.name} @ ${item.price}\n"
        message += f"\nTotal: ${order.total_price}\n\nThank you for shopping with us!"
        send_mail(subject, message, 'your_email@gmail.com', [request.user.email])

        messages.success(request, f"Order #{order.id} has been placed successfully!")
        return redirect('order_summary', order_id=order.id)

    return redirect('cart')

@login_required
def order_summary(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_summary.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order_history.html', {'orders': orders})

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, "Product added to your wishlist.")
    return redirect('wishlist')

@login_required
def wishlist(request):
    items = request.user.wishlist.select_related('product')
    context = {'wishlist_items': items}
    return render(request, 'shop/wishlist.html', context)

@login_required
def remove_from_wishlist(request, product_id):
    item = get_object_or_404(Wishlist, user=request.user, product_id=product_id)
    item.delete()
    messages.success(request, "Product removed from your wishlist.")
    return redirect('wishlist')

@login_required
def edit_profile(request):
    user_form = UserForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('edit_profile')

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'shop/edit_profile.html', context)

@login_required  # Ensures the user is logged in
@permission_required('shop.change_model', raise_exception=True)  # Checks permissions
def admin_view(request):
    return render(request, 'admin_view.html')  # Render a template for admin users

def no_access(request):
    return render(request, 'no_access.html')