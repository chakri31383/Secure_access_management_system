from django.urls import path
from . import views
from django.shortcuts import redirect
from dashboard.views import dashboard_home  # ✅ explicit import

def home_redirect(request):
    return redirect('login')

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', dashboard_home, name='dashboard_home'),  # User dashboard
    path('login/', views.login_view, name='login'),
    path('mfa_verify/', views.mfa_verify, name='mfa_verify'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_reset_otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset_password/', views.reset_password, name='reset_password'),
path('request_password_reset/', views.request_password_reset, name='request_password_reset'),
path('reset_password_confirm/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),

]
