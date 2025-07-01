from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

CATEGORY_CHOICES = [
    ('dress', 'Dresses'),
    ('skincare', 'Skin Care'),
    ('makeup', 'Makeup'),
    ('shoes', 'Shoes'),
    ('accessories', 'Accessories'),
    ('jewellery', 'Jewellery'),
]

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    quantity = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='dress')
    discount = models.PositiveIntegerField(blank=True, null=True, help_text="Enter discount percentage (e.g., 10 for 10%)")

    def get_discounted_price(self):
        if self.discount:
            return round(self.price * (100 - self.discount) / 100, 2)
        return self.price

    def __str__(self):
        return self.name

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_total_price(self):
     return self.quantity * self.product.get_discounted_price()

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    payment_mode = models.CharField(max_length=20)
    order_date = models.DateTimeField(auto_now_add=True)

    # NEW FIELDS
    delivery_boy = models.ForeignKey('DeliveryBoy', null=True, blank=True, on_delete=models.SET_NULL)
    delivery_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
    ], default='pending')

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.price

class DeliveryBoy(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=1)  # ⭐ 1 to 5
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate reviews

    def __str__(self):
        return f"{self.product.name} review by {self.user.username} ({self.rating}★)"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_seller = models.BooleanField(default=False)
    coin_balance = models.PositiveIntegerField(default=0)   

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address[:50]
