from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import ProductForm, BuyerSignupForm, CheckoutForm, DeliveryBoyLoginForm, ReviewForm,DeliveryBoyRegisterForm,AddressForm
from .models import Product, CartItem, Wishlist, Order, OrderItem, DeliveryBoy, Review,UserProfile , Address
from django.contrib import messages
from django.db.models import Sum, Avg
from django.db import models,transaction
from django.http import HttpResponseForbidden


def home(request):

    #input from the search bar and selected sort
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    products = Product.objects.all()

    # Filter by search term
    if query:
        products = products.filter(name__icontains=query)

    # Sorting logic
    if sort_by == 'low_to_high':
        products = products.order_by('price')
    elif sort_by == 'high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'latest':
        products = products.order_by('-id')

    # Group by categories
    if not query:
        categories = {
            'Dresses': products.filter(category='dress'),
            'Skin Care': products.filter(category='skincare'),
            'Makeup': products.filter(category='makeup'),
            'Shoes': products.filter(category='shoes'),
            'Accessories': products.filter(category='accessories'),
        }
    else:
        categories = {'Search Results': products}

    # ⭐ Add avg_rating to each product
    for product_list in categories.values():
        for product in product_list:
            product.avg_rating = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0

    # Wishlist IDs
    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'home.html', {
        'categories': categories,
        'user_wishlist': wishlist_ids,
        'query': query,
        'sort_by': sort_by
    })

def cart(request):
    return render(request, 'cart.html')

def order_confirm(request):
    return render(request, 'order_confirm.html')

def store(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')
    selected_category = request.GET.get('category', '')

    products = Product.objects.all()

    if selected_category:
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(name__icontains=query)

    if sort_by == 'low_to_high':
        products = products.order_by('price')
    elif sort_by == 'high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'latest':
        products = products.order_by('-id')

    if selected_category:
        categories = {selected_category.title(): products}
    elif not query:
        categories = {
            'Dresses': products.filter(category='dress'),
            'Skin Care': products.filter(category='skincare'),
            'Makeup': products.filter(category='makeup'),
            'Shoes': products.filter(category='shoes'),
            'Accessories': products.filter(category='accessories'),
            'jewellery': products.filter(category='jewellery'),
        }
    else:
        categories = {'Search Results': products}

    for product_list in categories.values():
        for product in product_list:
            product.avg_rating = product.reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0

    wishlist_ids = []
    if request.user.is_authenticated:
        wishlist_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'store.html', {
        'categories': categories,
        'user_wishlist': wishlist_ids,
        'query': query,
        'sort_by': sort_by,
        'selected_category': selected_category,
    })

# Seller login view
def seller_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            profile = user.userprofile
            profile.is_seller = True
            profile.save()
            return redirect('seller_dashboard')
        else:
            return render(request, 'seller_login.html', {'error': 'Invalid credentials'})
    return render(request, 'seller_login.html')

@login_required
def seller_dashboard_view(request):
    # Check if user is a seller
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_seller:
        return HttpResponseForbidden("You are not authorized to access the seller dashboard.")

    products = Product.objects.filter(seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm()

    return render(request, 'seller_dashboard.html', {'form': form, 'products': products})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('seller_dashboard')
    return render(request, 'delete_product.html', {'product': product})

def seller_logout(request):
    logout(request)
    return redirect('home')

# Buyer views
def buyer_signup(request):
    if request.method == 'POST':
        form = BuyerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('buyer_login')
    else:
        form = BuyerSignupForm()
    return render(request, 'buyer_signup.html', {'form': form})

def buyer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                product_id = request.session.pop('pending_product_id', None)
                if product_id:
                    return redirect('add_to_cart', product_id=product_id)
                return redirect('cart')
        except User.DoesNotExist:
            pass
        return render(request, 'buyer_login.html', {'error': 'Invalid credentials'})
    return render(request, 'buyer_login.html')

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Get quantity from form or default to 1
    try:
        count = int(request.POST.get('count', 1))
    except (TypeError, ValueError):
        count = 1

    # Don't allow more than available quantity
    count = max(1, min(count, product.quantity))

    # Get or create cart item for this user and product
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Ensure we don't exceed available stock
        new_quantity = cart_item.quantity + count
        cart_item.quantity = min(new_quantity, product.quantity + cart_item.quantity)
    else:
        cart_item.quantity = count

    cart_item.save()

    # Reduce product quantity accordingly
    product.quantity = max(0, product.quantity - count)
    product.save()

    return redirect('cart')

def add_to_cart_or_login(request, product_id):
    if request.user.is_authenticated:
        return redirect('home')
    request.session['pending_product_id'] = product_id
    return redirect('buyer_signup')
def get_total_price(self):
    return self.quantity * self.product.get_discounted_price()

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, product_id):
    cart_item = get_object_or_404(CartItem, user=request.user, product_id=product_id)
    product = cart_item.product
    product.quantity += cart_item.quantity
    product.save()
    cart_item.delete()
    return redirect('cart')


@login_required
def checkout_view(request):
    profile = UserProfile.objects.get(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    cart_items = CartItem.objects.filter(user=request.user)
    cart_total = sum(item.quantity * item.product.get_discounted_price() for item in cart_items)

    # Coin redemption logic: 10% off if coin_balance >= 100
    eligible_for_discount = profile.coin_balance >= 100
    redeem_value = round(cart_total * 0.10) if eligible_for_discount else 0
    final_amount = cart_total - redeem_value
    coins_needed = max(0, 100 - profile.coin_balance)

    if request.method == 'POST':
        # Create the order
        order = Order.objects.create(
            user=request.user,
            address=request.POST.get('selected_address') or request.POST.get('address'),
            payment_mode=request.POST.get('payment_mode'),
        )

        # Add order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_discounted_price()
            )

        # Clear cart
        cart_items.delete()

        # Adjust coins
        if eligible_for_discount:
            profile.coin_balance -= 100
        profile.coin_balance += 20
        profile.save()

        # Render confirmation page
        return render(request, 'order_confirm.html', {
            'order': order,
            'redeem_value': redeem_value,
            'coins_used': 100 if eligible_for_discount else 0,
            'final_amount': final_amount,
            'coins_earned': 20,
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'coins': profile.coin_balance,
        'redeem_value': redeem_value,
        'final_amount': final_amount,
        'coins_used': 100 if eligible_for_discount else 0,
        'eligible_for_discount': eligible_for_discount,
        'coins_needed': coins_needed,
        'addresses': addresses,
    })


@login_required
def account_page(request):
    return render(request, 'account.html')

@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'wishlist_items': wishlist_items})

def toggle_wishlist(request, product_id):
    if not request.user.is_authenticated:
        messages.warning(request, "You need to login to use wishlist.")
        return redirect('buyer_login')

    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        wishlist_item.delete()
        messages.info(request, f"{product.name} removed from your wishlist.")
    else:
        messages.success(request, f"{product.name} added to your wishlist.")

    return redirect('home')


@login_required
def delete_order(request, order_id):
    order = Order.objects.filter(id=order_id, user=request.user).first()
    if order:
        order.delete()
        messages.success(request, "Order deleted successfully.")
    else:
        messages.error(request, "Order not found or you're not allowed to delete it.")
    return redirect('orders')

def help_center(request):
    return render(request, 'help_center.html')

def custom_logout(request):
    logout(request)
    request.session.flush()
    return redirect('home')

def delivery_login_view(request):
    form = DeliveryBoyLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username_or_email = form.cleaned_data['username']
        password = form.cleaned_data['password']

        # Try getting user by email if username fails
        try:
            user = User.objects.get(email=username_or_email)
            username = user.username
        except User.DoesNotExist:
            username = username_or_email

        user = authenticate(request, username=username, password=password)
        if user and DeliveryBoy.objects.filter(user=user).exists():
            login(request, user)
            return redirect('delivery_dashboard')
        else:
            messages.error(request, "Invalid credentials or not a delivery boy")
    return render(request, 'delivery_login.html', {'form': form})

@login_required
def delivery_dashboard(request):
    if not hasattr(request.user, 'deliveryboy'):
        messages.error(request, "You are not authorized as a delivery boy.")
        return redirect('delivery_login')

    delivery_boy = request.user.deliveryboy

    orders = Order.objects.filter(
        models.Q(delivery_status='pending', delivery_boy__isnull=True) |
        models.Q(delivery_boy=delivery_boy)
    ).order_by('-order_date')

    return render(request, 'delivery_dashboard.html', {
        'orders': orders,
        'delivery_boy': delivery_boy
    })

@login_required
def update_delivery_status(request, order_id):
    if not hasattr(request.user, 'deliveryboy'):
        messages.error(request, "You are not authorized as a delivery boy.")
        return redirect('delivery_login')

    try:
        with transaction.atomic():
            # Lock the order row so no other delivery boy can access it simultaneously
            order = Order.objects.select_for_update().get(id=order_id)

            if order.delivery_status == 'pending' and order.delivery_boy is None:
                order.delivery_boy = request.user.deliveryboy
                order.delivery_status = 'accepted'
                order.save()
                messages.success(request, f"Order #{order_id} accepted successfully.")
            elif order.delivery_status == 'accepted' and order.delivery_boy == request.user.deliveryboy:
                order.delivery_status = 'completed'
                order.save()
                messages.success(request, f"Order #{order_id} marked as completed.")
            else:
                messages.error(request, "You are not allowed to update this order.")
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")

    return redirect('delivery_dashboard')

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    has_ordered = OrderItem.objects.filter(order__user=request.user, product=product, order__delivery_status='completed').exists()

    if not has_ordered:
        messages.error(request, "You can only rate products you've received.")
        return redirect('orders')

    review, created = Review.objects.get_or_create(user=request.user, product=product)
    form = ReviewForm(request.POST or None, instance=review)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Your rating has been submitted.")
        return redirect('orders')

    return render(request, 'add_review.html', {'form': form, 'product': product})


@login_required
def seller_orders_view(request):
    if not hasattr(request.user, 'userprofile') or not request.user.userprofile.is_seller:
        return HttpResponseForbidden("You are not authorized to access this page.")

    # Get orders that contain this seller's products
    orders = Order.objects.filter(items__product__seller=request.user).distinct().order_by('-order_date')
    return render(request, 'seller_orders.html', {'orders': orders})

# @login_required
# def orders_page(request):
#     # Buyer: show only their orders
#     orders = Order.objects.filter(user=request.user).order_by('-order_date')
#     return render(request, 'orders.html', {'orders': orders})

@login_required
def orders_page(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    reviewed_product_ids = set(
        Review.objects.filter(user=request.user).values_list('product_id', flat=True)
    )
    return render(request, 'orders.html', {
        'orders': orders,
        'reviewed_product_ids': reviewed_product_ids
    })




def product_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all()
    return render(request, 'reviews.html', {'product': product, 'reviews': reviews})

@login_required
def register_delivery_boy(request):
    if request.method == 'POST':
        form = DeliveryBoyRegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            phone = form.cleaned_data['phone']
            user = User.objects.get(username=username)
            DeliveryBoy.objects.create(user=user, phone=phone)
            messages.success(request, f"{username} registered as delivery boy.")
            return redirect('delivery_dashboard')
    else:
        form = DeliveryBoyRegisterForm()
    return render(request, 'register_delivery_boy.html', {'form': form})
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import Address, Product, Order, OrderItem, Wishlist
# from .forms import AddressForm
# from django.db.models import Sum


@login_required
def profile_view(request):
    user = request.user
    address_form = AddressForm(request.POST or None)
    edit_address_id = request.POST.get('edit_address_id')

    if request.method == 'POST':
        # Save a new address
        if 'save_address' in request.POST and address_form.is_valid():
            new_address = address_form.save(commit=False)
            new_address.user = user
            new_address.save()
            messages.success(request, "Address added successfully.")
            return redirect('profile')

        # Edit an existing address
        if 'update_address' in request.POST and edit_address_id:
            addr_to_edit = Address.objects.get(id=edit_address_id, user=user)
            form = AddressForm(request.POST, instance=addr_to_edit)
            if form.is_valid():
                form.save()
                messages.success(request, "Address updated successfully.")
                return redirect('profile')

        # Update user info
        new_name = request.POST.get('name')
        new_email = request.POST.get('email')
        user.username = new_name
        user.email = new_email
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    context = {
        'name': user.username,
        'email': user.email,
        'address_form': address_form,
        'addresses': Address.objects.filter(user=user),
    }

    # 🚚 Check if user is a delivery boy FIRST
    if hasattr(user, 'deliveryboy'):
        delivery_boy = user.deliveryboy
        completed_orders = Order.objects.filter(delivery_boy=delivery_boy, delivery_status='completed')
        accepted_orders = Order.objects.filter(delivery_boy=delivery_boy, delivery_status='accepted')
        pending_orders = Order.objects.filter(delivery_status='pending', delivery_boy__isnull=True)

        context.update({
            'role': 'delivery',
            'phone': delivery_boy.phone,
            'completed_orders': completed_orders,
            'accepted_orders': accepted_orders,
            'pending_orders': pending_orders,
        })

    # 👤 Then check if user is buyer or seller
    elif hasattr(user, 'userprofile'):
        profile = user.userprofile
        if profile.is_seller:
            seller_products = Product.objects.filter(seller=user)
            total_sales = []
            for product in seller_products:
                sold_qty = OrderItem.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0
                total_sales.append((product.name, sold_qty))
            context.update({
                'role': 'seller',
                'sales_data': total_sales,
                'orders': Order.objects.filter(items__product__seller=user).distinct()
            })
        else:
            coins_needed = max(0, 100 - profile.coin_balance)
            context.update({
                'role': 'buyer',
                'orders': Order.objects.filter(user=user),
                'wishlist': Wishlist.objects.filter(user=user),
                'coin_balance': profile.coin_balance,
                'coins_needed': coins_needed,
            })

    return render(request, 'profile.html', context)

def complete_order_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.delivery_status == 'completed':  # Or your own order completion condition
        profile = UserProfile.objects.get(user=request.user)

        coins_earned = int(order.get_total()) 
        profile.coin_balance += coins_earned
        profile.save()