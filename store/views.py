
from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
import json

# Create your views here.

def store(request):
    # Get all categories
    categories = Category.objects.all()
    
    # Get category filter from URL parameter
    category_id = request.GET.get('category')
    
    # Filter products by category if specified, otherwise show all
    if category_id:
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()
        
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(category__category_name__icontains=search_query))
    
    # Get user favorites if logged in
    user_favorites = []
    cartItems = 0
    if request.user.is_authenticated:
        user_favorites = favorites.objects.filter(user=request.user).values_list('product_id', flat=True)
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            cartItems = order.cart_items_count
        except:
            cartItems = 0
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
        cartItems = order['get_cart_items']

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'user_favorites': list(user_favorites),
        'cartItems': cartItems,
    }
    return render(request, 'store/store.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.cart_items_count
    else:
        # Create empty cart for now for non-logged in users
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, "store/Cart.html", context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.cart_items_count
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
        cartItems = order['get_cart_items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request,"store/Checkout.html",context)

@login_required(login_url='login')
def favorites_view(request):
    favs = favorites.objects.filter(user=request.user)
    # Get cart count for navbar
    try:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        cartItems = order.cart_items_count
    except:
        cartItems = 0
        
    context = {'favorites': favs, 'cartItems': cartItems}
    return render(request,"store/Favs.html",context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)

def toggle_favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required'}, status=401)
        
    data = json.loads(request.body)
    productId = data['productId']
    
    try:
        product = Product.objects.get(id=productId)
        fav, created = favorites.objects.get_or_create(user=request.user, product=product)
        
        if not created:
            # If it already existed, delete it (toggle off)
            fav.delete()
            action = 'removed'
        else:
            action = 'added'
            
        return JsonResponse({'status': 'success', 'action': action})
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)

def login(request):
    if request.user.is_authenticated:
        return redirect('store')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect('store')
        else:
            messages.error(request, 'Invalid email or password')
    
    context = {}
    return render(request, "store/login.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('store')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, "store/signup.html")
        
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, "store/signup.html")
        
        if len(password1) < 4:
            messages.error(request, 'Password must be at least 4 characters')
            return render(request, "store/signup.html")
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            Customer.objects.create(
                user=user,
                first_name=first_name,
                second_name=last_name,
                email=email,
                phone=phone
            )
            
            auth_login(request, user)
            messages.success(request, f'Welcome {first_name}! Account created successfully.')
            return redirect('store')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, "store/signup.html")
    
    context = {}
    return render(request, "store/signup.html", context)


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')
