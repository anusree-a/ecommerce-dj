from django import forms
from .models import Product, Review, DeliveryBoy, Address
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity', 'image', 'description', 'category', 'discount']

class BuyerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CheckoutForm(forms.Form):
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Shipping Address"
    )
    PAYMENT_CHOICES = [
        ('gpay', 'Google Pay'),
        ('cod', 'Cash on Delivery'),
        ('paytm', 'Paytm'),
    ]
    payment_mode = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Payment Mode"
    )

class DeliveryBoyLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, f"{i} ★") for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Your Rating'
    )

    class Meta:
        model = Review
        fields = ['rating', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
# ✅ New form for registering delivery boys
class DeliveryBoyRegisterForm(forms.Form):
    username = forms.CharField(label="Username")
    phone = forms.CharField(label="Phone Number")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist.")
        if DeliveryBoy.objects.filter(user=user).exists():
            raise forms.ValidationError("User is already registered as a delivery boy.")
        return username

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter new address'}),
        }
