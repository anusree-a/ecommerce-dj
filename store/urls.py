from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('seller_login/', views.seller_login_view, name='login'),
    path('seller_dashboard/', views.seller_dashboard_view, name='seller_dashboard'),
    path('cart/', views.cart, name='cart'),
    path('order_confirm/', views.order_confirm, name='order_confirm'),
    path('store/', views.store, name='store'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('buyer_signup/', views.buyer_signup, name='buyer_signup'),
    path('buyer_login/', views.buyer_login, name='buyer_login'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('add_to_cart_or_login/<int:product_id>/', views.add_to_cart_or_login, name='add_to_cart_or_login'),
    path('seller_logout/', views.seller_logout, name='seller_logout'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('account/', views.account_page, name='account'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('toggle_wishlist/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('orders/', views.orders_page, name='orders'),
    path('seller/orders/', views.seller_orders_view, name='seller_orders'),
    path('help/', views.help_center, name='help_center'),
    path('orders/delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/deliveryboy/', views.register_delivery_boy, name='register_delivery_boy'),
    path('delivery/login/', views.delivery_login_view, name='delivery_login'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/update/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    path('review/product/<int:product_id>/', views.product_reviews, name='product_reviews'),
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('profile/', views.profile_view, name='profile'),


]