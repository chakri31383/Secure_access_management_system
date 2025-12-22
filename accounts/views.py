from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from dashboard.models import ActivityLog, Organization, Role
from .forms import SignupForm, LoginForm
from .models import User
import random, smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from .forms import ForgotPasswordForm, VerifyOTPForm, ResetPasswordForm
from django.contrib.auth.hashers import make_password
from django.conf import settings
import random
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.urls import reverse
from .forms import UserProfileForm
def send_otp(email, otp):
    msg = MIMEText(f"Your OTP is {otp}")
    msg['Subject'] = 'Secure Access Verification'
    msg['From'] = settings.EMAIL_HOST_USER
    msg['To'] = email
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(settings.EMAIL_HOST_USER, email, msg.as_string())
    s.quit()

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            otp = str(random.randint(100000, 999999))
            user.otp_code = otp
            user.save()
            send_otp(user.email, otp)
            messages.success(request, "OTP sent to Gmail.")
            return redirect('verify_otp')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST['email']
        otp = request.POST['otp']
        user = User.objects.filter(email=email, otp_code=otp).first()
        if user:
            user.is_verified = True
            user.save()
            messages.success(request, "Email verified. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP.")
    return render(request, 'accounts/verify_otp.html')

def login_view(request):
    if request.user.is_authenticated:  # Check if the user is already logged in
        return redirect('dashboard_home')  # Redirect to dashboard if logged in

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user and user.is_verified:
                otp = str(random.randint(100000, 999999))
                user.otp_code = otp
                user.save()
                send_otp(user.email, otp)  # Send OTP for MFA
                request.session['temp_email'] = user.email  # Store email temporarily for MFA
                return redirect('mfa_verify')  # Redirect to MFA OTP verification
            else:
                messages.error(request, "Invalid credentials or not verified.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})
def mfa_verify(request):
    if request.method == 'POST':
        otp = request.POST['otp']
        email = request.session.get('temp_email')  # Temporary email stored during login
        user = User.objects.filter(email=email, otp_code=otp).first()
        if user:
            login(request, user)  # Log the user in
            messages.success(request, "Successfully logged in.")
            return redirect('dashboard_home')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid OTP.")
    return render(request, 'accounts/mfa.html')
def logout_view(request):
    logout(request)
    return redirect('login')
from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                otp = str(random.randint(100000, 999999))
                user.otp_code = otp
                user.otp_created_at = timezone.now()
                user.save()

                send_mail(
                    subject="Password Reset OTP - Secure Portal",
                    message=f"Your OTP for password reset is {otp}. It expires in 5 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                )
                request.session['reset_email'] = email
                messages.success(request, "OTP sent to your registered email.")
                return redirect('verify_reset_otp')
            else:
                messages.error(request, "No account found with that email.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})


def verify_reset_otp(request):
    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            email = request.session.get('reset_email')
            user = User.objects.filter(email=email, otp_code=otp).first()
            if user:
                messages.success(request, "OTP verified. You can now reset your password.")
                return redirect('reset_password')
            else:
                messages.error(request, "Invalid OTP.")
    else:
        form = VerifyOTPForm()
    return render(request, 'accounts/verify_reset_otp.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required  # Ensures that only logged-in users can access this view
@login_required
def accounts_dashboard(request):
    # Display user information
    user_email = request.user.email  # Get user's email
    user_full_name = request.user.full_name  # You can add a full name field to User model if not present

    return render(request, 'dashboard/admin_dashboard.html', {
        'email': user_email,
        'full_name': user_full_name
    })

def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            email = request.session.get('reset_email')

            if new_password != confirm_password:
                messages.error(request, "Passwords do not match.")
            else:
                user = User.objects.filter(email=email).first()
                if user:
                    user.password = make_password(new_password)
                    user.otp_code = None
                    user.save()

                    # Send confirmation email with date & time
                    send_mail(
                        subject="Password Reset Confirmation - Secure Portal",
                        message=f"Your password was reset successfully on {timezone.now().strftime('%d-%m-%Y %I:%M %p')}. If this wasn’t you, contact support immediately.",
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[email],
                    )

                    messages.success(request, "Password reset successful. Please login.")
                    return redirect('login')
                else:
                    messages.error(request, "Something went wrong.")
    else:
        form = ResetPasswordForm()
    return render(request, 'accounts/reset_password.html', {'form': form})
def request_password_reset(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('reset_password_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                subject = "Password Reset Link - Secure Portal"
                message = render_to_string('accounts/reset_link_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
                messages.success(request, "Password reset link has been sent to your email.")
            else:
                messages.error(request, "No account found with that email.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/request_password_reset.html', {'form': form})


def reset_password_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = ResetPasswordForm(request.POST)
            if form.is_valid():
                new_password = form.cleaned_data['new_password']
                user.set_password(new_password)
                user.save()
                send_mail(
                    subject="Password Reset Successful - Secure Portal",
                    message=f"Your password was reset successfully on {timezone.now().strftime('%d-%m-%Y %I:%M %p')}. If this wasn't you, please contact support immediately.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                )
                messages.success(request, "Your password has been reset. Please log in.")
                return redirect('login')
        else:
            form = ResetPasswordForm()
        return render(request, 'accounts/reset_password_confirm.html', {'form': form})
    else:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')


from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from .forms import UserProfileForm, UserPasswordChangeForm
from django.contrib import messages


@login_required
def profile(request):
    user = request.user

    if request.method == 'POST':
        # Handle profile form
        profile_form = UserProfileForm(request.POST, instance=user)
        password_form = UserPasswordChangeForm(request.user, request.POST)

        if profile_form.is_valid() and password_form.is_valid():
            # Save profile changes
            profile_form.save()

            # Handle password change if necessary
            if 'password' in request.POST:
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Your profile and password were successfully updated!')
            else:
                messages.success(request, 'Your profile was successfully updated!')

            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = UserProfileForm(instance=user)
        password_form = UserPasswordChangeForm(user)

    return render(request, 'accounts/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form
    })
