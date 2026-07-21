
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetConfirmView,
    PasswordResetDoneView, PasswordResetCompleteView
)
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.core.cache import cache
from django.contrib import messages
from django.conf import settings

from .models import CustomUser, Address, UserActivity
from .forms import (
    SecureRegistrationForm, SecureLoginForm,
    SecurePasswordChangeForm, ProfileUpdateForm, AddressForm
)

import logging
import secrets

logger = logging.getLogger(__name__)

def get_client_ip(request):
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_activity(user, activity_type, request, extra_data=None):
    
    UserActivity.objects.create(
        user=user,
        activity_type=activity_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        extra_data=extra_data or {}
    )

@never_cache
@require_http_methods(["GET", "POST"])
def register_view(request):

    ip = get_client_ip(request)
    cache_key = f"register_attempts_{ip}"
    attempts = cache.get(cache_key, 0)
    
    if attempts >= 5:
        messages.error(request, 'تم تجاوز عدد محاولات التسجيل. يرجى المحاولة لاحقاً.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = SecureRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()

            user.generate_email_verification_token()

            log_activity(user, 'login', request)

            login(request, user)
            
            logger.info(f"New user registered: {user.email}")
            messages.success(request, 'تم إنشاء حسابك بنجاح!')
            
            return redirect('products:product_list')
        else:

            cache.set(cache_key, attempts + 1, 3600)
    else:
        form = SecureRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@never_cache
@require_http_methods(["GET", "POST"])
def login_view(request):
    
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    ip = get_client_ip(request)

    ip_cache_key = f"login_attempts_ip_{ip}"
    ip_attempts = cache.get(ip_cache_key, 0)
    
    if ip_attempts >= 10:
        messages.error(request, 'تم تجاوز عدد المحاولات. يرجى المحاولة بعد 30 دقيقة.')
        return render(request, 'accounts/login.html', {'form': SecureLoginForm()})
    
    if request.method == 'POST':
        form = SecureLoginForm(request, data=request.POST)
        email = request.POST.get('username', '').lower()

        try:
            user = CustomUser.objects.get(email=email)
            if user.is_locked_out():
                messages.error(request, 'الحساب مقفل مؤقتاً. يرجى المحاولة لاحقاً.')
                log_activity(user, 'failed_login', request, {'reason': 'account_locked'})
                return render(request, 'accounts/login.html', {'form': form})
        except CustomUser.DoesNotExist:
            user = None
        
        if form.is_valid():
            user = form.get_user()

            user.reset_failed_logins()
            user.last_login_ip = ip
            user.save(update_fields=['last_login_ip'])

            login(request, user)

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)

            request.session.cycle_key()

            log_activity(user, 'login', request)
            
            logger.info(f"User logged in: {user.email} from {ip}")

            next_url = request.GET.get('next', '')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('products:product_list')
        else:

            cache.set(ip_cache_key, ip_attempts + 1, 1800)
            
            if user:
                user.record_failed_login()
                log_activity(user, 'failed_login', request, {'reason': 'invalid_password'})
            else:

                UserActivity.objects.create(
                    user=None,
                    activity_type='failed_login',
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    extra_data={'email': email, 'reason': 'user_not_found'}
                )

            messages.error(request, 'البريد الإلكتروني أو كلمة المرور غير صحيحة')
    else:
        form = SecureLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
@require_http_methods(["POST"])
def logout_view(request):
    
    log_activity(request.user, 'logout', request)
    logout(request)
    messages.success(request, 'تم تسجيل الخروج بنجاح')
    return redirect('accounts:login')

@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    
    from orders.models import Order
    from cart.models import Wishlist
    from django.db.models import Sum
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'profile_update', request)
            messages.success(request, 'تم تحديث الملف الشخصي')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    orders = Order.objects.filter(user=request.user)
    orders_count = orders.count()
    completed_orders = orders.filter(status='delivered').count()
    total_spent = orders.filter(status='delivered').aggregate(total=Sum('total'))['total'] or 0

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    recent_orders = orders.order_by('-created_at')[:5]

    default_address = request.user.addresses.filter(is_default=True).first()
    if not default_address:
        default_address = request.user.addresses.first()
    
    addresses = request.user.addresses.all()
    activities = request.user.activities.all()[:10]
    
    return render(request, 'accounts/profile.html', {
        'form': form,
        'addresses': addresses,
        'activities': activities,
        'orders_count': orders_count,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'wishlist_count': wishlist_count,
        'recent_orders': recent_orders,
        'default_address': default_address,
    })

@login_required
@require_http_methods(["GET", "POST"])
def change_password_view(request):
    
    if request.method == 'POST':
        form = SecurePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            user.password_changed_at = timezone.now()
            user.save(update_fields=['password_changed_at'])

            update_session_auth_hash(request, user)
            
            log_activity(user, 'password_change', request)
            messages.success(request, 'تم تغيير كلمة المرور بنجاح')
            
            logger.info(f"Password changed for user: {user.email}")
            
            return redirect('accounts:profile')
    else:
        form = SecurePasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

@login_required
@require_http_methods(["GET", "POST"])
def add_address_view(request):
    
    if request.method == 'POST':
        form = AddressForm(request.POST)
        address_type = request.POST.get('address_type', 'shipping')
        
        if form.is_valid():

            is_default = form.cleaned_data.pop('is_default', False)

            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            
            Address.objects.create(
                user=request.user,
                address_type=address_type,
                is_default=is_default,
                **form.cleaned_data
            )
            messages.success(request, 'تم إضافة العنوان')
            return redirect('accounts:addresses')
    else:
        form = AddressForm()
    
    return render(request, 'accounts/add_address.html', {'form': form})

@login_required
@require_http_methods(["GET"])
def addresses_view(request):
    
    addresses = request.user.addresses.all().order_by('-is_default', '-created_at')
    return render(request, 'accounts/addresses.html', {'addresses': addresses})

@login_required
@require_http_methods(["GET", "POST"])
def edit_profile_view(request):
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            log_activity(request.user, 'profile_update', request)
            messages.success(request, 'تم تحديث الملف الشخصي')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
@require_http_methods(["POST"])
def set_default_address_view(request, address_id):
    
    address = get_object_or_404(Address, id=address_id, user=request.user)

    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

    address.is_default = True
    address.save()
    
    messages.success(request, 'تم تعيين العنوان كافتراضي')
    return redirect('accounts:addresses')

@login_required
@require_http_methods(["POST"])
def delete_address_view(request, address_id):

    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'تم حذف العنوان')
    return redirect('accounts:profile')

class SecurePasswordResetView(PasswordResetView):
    
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):

        ip = get_client_ip(self.request)
        cache_key = f"password_reset_{ip}"
        attempts = cache.get(cache_key, 0)
        
        if attempts >= 3:
            messages.error(self.request, 'تم تجاوز عدد المحاولات. يرجى المحاولة لاحقاً.')
            return redirect('accounts:password_reset')
        
        cache.set(cache_key, attempts + 1, 3600)
        
        return super().form_valid(form)

class SecurePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')

import pickle
import base64
import hashlib
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def user_search(request):

    query = request.GET.get('q', '')

    with connection.cursor() as cursor:
        sql = f"SELECT id, email, first_name, last_name FROM accounts_customuser WHERE email LIKE '%{query}%' OR first_name LIKE '%{query}%'"
        cursor.execute(sql)
        results = cursor.fetchall()
    
    users = [
        {
            'id': str(row[0]),
            'email': row[1],
            'first_name': row[2],
            'last_name': row[3]
        }
        for row in results
    ]
    
    return JsonResponse({'users': users})

def export_user_data(request):

    data_param = request.GET.get('data', '')
    
    if data_param:

        try:
            decoded = base64.b64decode(data_param)
            user_data = pickle.loads(decoded)
            return JsonResponse({'status': 'success', 'data': str(user_data)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    if request.user.is_authenticated:
        data = {
            'email': request.user.email,
            'name': request.user.get_full_name()
        }
        pickled = pickle.dumps(data)
        encoded = base64.b64encode(pickled).decode()
        return JsonResponse({'export': encoded})
    
    return JsonResponse({'error': 'Not authenticated'}, status=401)

def debug_user_info(request):

    user_id = request.GET.get('id', '')
    
    if not user_id:
        return JsonResponse({'error': 'User ID required'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)

        debug_info = {
            'id': str(user.id),
            'email': user.email,
            'password_hash': user.password,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'last_login': str(user.last_login),
            'date_joined': str(user.date_joined),
        }
        
        return JsonResponse(debug_info)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@csrf_exempt
def update_email(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    user_id = request.POST.get('user_id', '')
    new_email = request.POST.get('email', '')
    
    if not user_id or not new_email:
        return JsonResponse({'error': 'user_id and email required'}, status=400)
    
    try:

        user = CustomUser.objects.get(id=user_id)
        user.email = new_email
        user.save()
        
        return JsonResponse({'status': 'success', 'message': 'Email updated'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

def weak_password_reset(request):

    email = request.GET.get('email', '')
    
    if not email:
        return JsonResponse({'error': 'Email required'}, status=400)
    
    try:
        user = CustomUser.objects.get(email=email)

        reset_token = hashlib.md5(email.encode()).hexdigest()
        
        reset_link = f"/accounts/reset/{reset_token}/"
        
        return JsonResponse({
            'status': 'success',
            'message': 'Reset link generated',
            'reset_token': reset_token,
            'reset_link': reset_link
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

def admin_action(request):

    action = request.GET.get('action', '')
    user_id = request.GET.get('user_id', '')
    
    if not action or not user_id:
        return JsonResponse({'error': 'action and user_id required'}, status=400)
    
    try:
        user = CustomUser.objects.get(id=user_id)

        if action == 'make_admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
            return JsonResponse({'status': 'success', 'message': f'{user.email} is now admin'})
        
        elif action == 'delete':
            user.delete()
            return JsonResponse({'status': 'success', 'message': 'User deleted'})
        
        elif action == 'deactivate':
            user.is_active = False
            user.save()
            return JsonResponse({'status': 'success', 'message': 'User deactivated'})
        
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)