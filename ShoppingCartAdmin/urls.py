from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='homepage'),
    path('product_details/', views.DetailsPage.as_view(), name='detailspage'),
    path('login/', views.LoginPage.as_view(), name='loginpage'),
    path('RegisterPage/', views.RegisterPage.as_view(), name='registerpage'),
    path('cart/', views.CartPage.as_view(), name='cartpage'),
]