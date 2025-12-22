import razorpay
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Payment

client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

@login_required
def create_payment(request):
    amount = 50000  # INR ₹500
    DATA = {"amount": amount, "currency": "INR", "receipt": "org_create"}
    payment = client.order.create(data=DATA)
    Payment.objects.create(user=request.user, order_id=payment['id'], amount=amount)
    return render(request, 'payments/pay.html', {'payment': payment})
