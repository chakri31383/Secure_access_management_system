from django.urls import path
from . import views

app_name = 'payments'  # Ensure the app name is set

urlpatterns = [
    path('', views.create_payment, name='payment_home'),  # Define a view for payments
    # Add any other payment-related URLs here
]