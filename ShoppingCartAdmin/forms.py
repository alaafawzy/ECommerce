from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms.widgets import PasswordInput

from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=250)
    password = forms.CharField(max_length=250, widget=PasswordInput)


class AddressForm(forms.Form):
    street = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.CharField(max_length=100)
    address_type = forms.ChoiceField(choices = ADDRESS_CHOICES)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254)
    phone_number = forms.CharField(max_length=100)
    shipping_address = forms.ModelChoiceField(queryset=Address.objects.filter(address_type='S'))
    billing_address = forms.ModelChoiceField(queryset=Address.objects.filter(address_type='B'))

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'shipping_address', 'billing_address', 'password1', 'password2', )


class CartUpdate(forms.Form):
    update_quantity = forms.IntegerField()
    
