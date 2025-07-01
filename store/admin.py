from django.contrib import admin
from .models import Product,CartItem,Wishlist,Order,OrderItem,DeliveryBoy,Review,Address

# Register your models here.
admin.site.register(Product)
admin.site.register(CartItem )
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(DeliveryBoy)
admin.site.register(Address)
admin.site.register(Review)