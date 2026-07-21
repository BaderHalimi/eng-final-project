"""
Dashboard Views - لوحة التحكم المخصصة
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta

from products.models import Product, Category
from orders.models import Order, OrderItem
from accounts.models import CustomUser


def is_staff(user):
    """التحقق من صلاحيات الموظف"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def staff_required(view_func):
    """ديكوريتر للتحقق من صلاحيات الموظف"""
    decorated_view = user_passes_test(is_staff, login_url='accounts:login')(view_func)
    return login_required(decorated_view)


@staff_required
def dashboard_home(request):
    """الصفحة الرئيسية للوحة التحكم"""
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    

    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_users = CustomUser.objects.count()
    

    today_orders = Order.objects.filter(created_at__date=today)
    today_orders_count = today_orders.count()
    today_revenue = today_orders.aggregate(total=Sum('total'))['total'] or 0
    

    monthly_orders = Order.objects.filter(created_at__date__gte=last_30_days)
    monthly_revenue = monthly_orders.aggregate(total=Sum('total'))['total'] or 0
    monthly_orders_count = monthly_orders.count()
    

    pending_orders = Order.objects.filter(status='pending').count()
    processing_orders = Order.objects.filter(status='processing').count()
    

    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    

    top_products = OrderItem.objects.values(
        'product__name', 'product__id'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('unit_price'))
    ).order_by('-total_sold')[:5]
    

    chart_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=day)
        chart_data.append({
            'date': day.strftime('%m/%d'),
            'orders': day_orders.count(),
            'revenue': float(day_orders.aggregate(total=Sum('total'))['total'] or 0)
        })
    

    low_stock_products = Product.objects.filter(stock__lt=10, is_active=True).order_by('stock')[:5]
    
    context = {
        'total_products': total_products,
        'active_products': active_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'today_orders_count': today_orders_count,
        'today_revenue': today_revenue,
        'monthly_revenue': monthly_revenue,
        'monthly_orders_count': monthly_orders_count,
        'pending_orders': pending_orders,
        'processing_orders': processing_orders,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'chart_data': chart_data,
        'low_stock_products': low_stock_products,
    }
    
    return render(request, 'dashboard/home.html', context)




@staff_required
def product_list(request):
    """قائمة المنتجات"""
    products = Product.objects.select_related('category').order_by('-created_at')
    

    q = request.GET.get('q', '')
    if q:
        products = products.filter(name__icontains=q)
    

    category_id = request.GET.get('category', '')
    if category_id:
        products = products.filter(category_id=category_id)
    

    status = request.GET.get('status', '')
    if status == 'active':
        products = products.filter(is_active=True)
    elif status == 'inactive':
        products = products.filter(is_active=False)
    elif status == 'low_stock':
        products = products.filter(stock__lt=10)
    
    paginator = Paginator(products, 20)
    page = request.GET.get('page', 1)
    products = paginator.get_page(page)
    
    categories = Category.objects.filter(is_active=True)
    
    return render(request, 'dashboard/products/list.html', {
        'products': products,
        'categories': categories,
    })


@staff_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def product_add(request):
    """إضافة منتج جديد"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', 0)
        discount_price = request.POST.get('discount_price') or None
        category_id = request.POST.get('category') or None
        stock = request.POST.get('stock', 0)
        is_active = request.POST.get('is_active') == 'on'
        is_featured = request.POST.get('is_featured') == 'on'
        image = request.FILES.get('image')
        
        if not name or not price:
            messages.error(request, 'الاسم والسعر مطلوبان')
            return redirect('dashboard:product_add')
        
        try:
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                discount_price=discount_price if discount_price else None,
                category_id=category_id if category_id else None,
                stock=stock,
                is_active=is_active,
                is_featured=is_featured,
                image=image,
                created_by=request.user
            )
            messages.success(request, f'تم إضافة المنتج "{product.name}" بنجاح')
            return redirect('dashboard:products')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/products/form.html', {
        'categories': categories,
        'action': 'add'
    })


@staff_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def product_edit(request, pk):
    """تعديل منتج"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.name = request.POST.get('name', '').strip()
        product.description = request.POST.get('description', '').strip()
        product.price = request.POST.get('price', 0)
        discount_price = request.POST.get('discount_price')
        product.discount_price = discount_price if discount_price else None
        category_id = request.POST.get('category')
        product.category_id = category_id if category_id else None
        product.stock = request.POST.get('stock', 0)
        product.is_active = request.POST.get('is_active') == 'on'
        product.is_featured = request.POST.get('is_featured') == 'on'
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        try:
            product.save()
            messages.success(request, f'تم تحديث المنتج "{product.name}" بنجاح')
            return redirect('dashboard:products')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    categories = Category.objects.filter(is_active=True)
    return render(request, 'dashboard/products/form.html', {
        'product': product,
        'categories': categories,
        'action': 'edit'
    })


@staff_required
@csrf_protect
@require_http_methods(["POST"])
def product_delete(request, pk):
    """حذف منتج"""
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.success(request, f'تم حذف المنتج "{name}"')
    return redirect('dashboard:products')




@staff_required
def category_list(request):
    """قائمة التصنيفات"""
    categories = Category.objects.annotate(
        products_count=Count('products')
    ).order_by('name')
    
    return render(request, 'dashboard/categories/list.html', {
        'categories': categories,
    })


@staff_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def category_add(request):
    """إضافة تصنيف جديد"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        image = request.FILES.get('image')
        
        if not name:
            messages.error(request, 'اسم التصنيف مطلوب')
            return redirect('dashboard:category_add')
        
        try:
            category = Category.objects.create(
                name=name,
                description=description,
                is_active=is_active,
                image=image
            )
            messages.success(request, f'تم إضافة التصنيف "{category.name}" بنجاح')
            return redirect('dashboard:categories')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'dashboard/categories/form.html', {'action': 'add'})


@staff_required
@csrf_protect
@require_http_methods(["GET", "POST"])
def category_edit(request, pk):
    """تعديل تصنيف"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.name = request.POST.get('name', '').strip()
        category.description = request.POST.get('description', '').strip()
        category.is_active = request.POST.get('is_active') == 'on'
        
        if request.FILES.get('image'):
            category.image = request.FILES.get('image')
        
        try:
            category.save()
            messages.success(request, f'تم تحديث التصنيف "{category.name}" بنجاح')
            return redirect('dashboard:categories')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    return render(request, 'dashboard/categories/form.html', {
        'category': category,
        'action': 'edit'
    })


@staff_required
@csrf_protect
@require_http_methods(["POST"])
def category_delete(request, pk):
    """حذف تصنيف"""
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.success(request, f'تم حذف التصنيف "{name}"')
    return redirect('dashboard:categories')




@staff_required
def order_list(request):
    """قائمة الطلبات"""
    orders = Order.objects.select_related('user').order_by('-created_at')
    

    status = request.GET.get('status', '')
    if status:
        orders = orders.filter(status=status)
    

    payment = request.GET.get('payment', '')
    if payment:
        orders = orders.filter(payment_status=payment)
    

    q = request.GET.get('q', '')
    if q:
        orders = orders.filter(order_number__icontains=q)
    
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders = paginator.get_page(page)
    
    return render(request, 'dashboard/orders/list.html', {
        'orders': orders,
    })


@staff_required
def order_detail(request, pk):
    """تفاصيل الطلب"""
    order = get_object_or_404(Order.objects.select_related('user'), pk=pk)
    items = order.items.select_related('product').all()
    
    return render(request, 'dashboard/orders/detail.html', {
        'order': order,
        'items': items,
    })


@staff_required
@csrf_protect
@require_http_methods(["POST"])
def order_update_status(request, pk):
    """تحديث حالة الطلب"""
    order = get_object_or_404(Order, pk=pk)
    
    new_status = request.POST.get('status', '')
    if new_status in ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled']:
        old_status = order.status
        order.status = new_status
        
        if new_status == 'shipped':
            order.shipped_at = timezone.now()
            order.tracking_number = request.POST.get('tracking_number', '')
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
        
        order.save()
        messages.success(request, f'تم تحديث حالة الطلب من "{old_status}" إلى "{new_status}"')
    
    return redirect('dashboard:order_detail', pk=pk)




@staff_required
def user_list(request):
    """قائمة المستخدمين"""
    users = CustomUser.objects.annotate(
        orders_count=Count('orders')
    ).order_by('-date_joined')
    

    q = request.GET.get('q', '')
    if q:
        users = users.filter(email__icontains=q) | users.filter(username__icontains=q)
    

    role = request.GET.get('role', '')
    if role == 'staff':
        users = users.filter(is_staff=True)
    elif role == 'customer':
        users = users.filter(is_staff=False)
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users = paginator.get_page(page)
    
    return render(request, 'dashboard/users/list.html', {
        'users': users,
    })


@staff_required
def user_detail(request, pk):
    """تفاصيل المستخدم"""
    user = get_object_or_404(CustomUser, pk=pk)
    orders = Order.objects.filter(user=user).order_by('-created_at')[:10]
    
    return render(request, 'dashboard/users/detail.html', {
        'user_obj': user,
        'orders': orders,
    })


@staff_required
@csrf_protect
@require_http_methods(["POST"])
def user_toggle_status(request, pk):
    """تفعيل/تعطيل المستخدم"""
    user = get_object_or_404(CustomUser, pk=pk)
    

    if user == request.user:
        messages.error(request, 'لا يمكنك تعطيل حسابك الخاص')
        return redirect('dashboard:users')
    
    if user.is_superuser:
        messages.error(request, 'لا يمكن تعطيل حساب مدير النظام')
        return redirect('dashboard:users')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'تفعيل' if user.is_active else 'تعطيل'
    messages.success(request, f'تم {status} حساب المستخدم "{user.email}"')
    return redirect('dashboard:users')




@staff_required
def reports(request):
    """صفحة التقارير"""
    return render(request, 'dashboard/reports/index.html')


@staff_required
def sales_report(request):
    """تقرير المبيعات"""

    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    
    daily_sales = Order.objects.filter(
        created_at__date__gte=last_30_days
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        orders_count=Count('id'),
        total_sales=Sum('total')
    ).order_by('date')
    
    return render(request, 'dashboard/reports/sales.html', {
        'daily_sales': list(daily_sales),
    })







import os
import subprocess
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings



def dashboard_search(request):
    """
    VULNERABLE: SQL Injection
    ثغرة حقن SQL في لوحة التحكم
    """
    table = request.GET.get('table', 'products_product')
    column = request.GET.get('column', 'name')
    query = request.GET.get('q', '')
    

    with connection.cursor() as cursor:
        sql = f"SELECT * FROM {table} WHERE {column} LIKE '%{query}%' LIMIT 100"
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        results = cursor.fetchall()
    
    data = []
    for row in results:
        data.append(dict(zip(columns, row)))
    
    return JsonResponse({'results': data, 'count': len(data)})



def run_backup(request):
    """
    VULNERABLE: Command Injection
    ثغرة حقن أوامر في النسخ الاحتياطي
    """
    backup_name = request.GET.get('name', 'backup')
    destination = request.GET.get('dest', '/tmp')
    

    command = f"tar -czf {destination}/{backup_name}.tar.gz /var/www/mystore"
    
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=10)
        return HttpResponse(f"<pre>Backup successful:\n{result.decode()}</pre>")
    except subprocess.TimeoutExpired:
        return HttpResponse("<pre>Backup timeout</pre>", status=500)
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"<pre>Error: {e.output.decode()}</pre>", status=500)



def read_log_file(request):
    """
    VULNERABLE: Path Traversal
    ثغرة اختراق المسار في قراءة السجلات
    """
    filename = request.GET.get('file', 'app.log')
    

    log_path = os.path.join('/var/log/mystore', filename)
    
    try:
        with open(log_path, 'r') as f:
            content = f.read()
        return HttpResponse(f"<pre>{content}</pre>")
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)



@csrf_exempt
def bulk_delete_users(request):
    """
    VULNERABLE: Missing Authentication + CSRF
    ثغرة عدم وجود مصادقة + CSRF
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return JsonResponse({'error': 'user_ids required'}, status=400)
    

    deleted_count = CustomUser.objects.filter(id__in=user_ids).delete()[0]
    
    return JsonResponse({
        'status': 'success',
        'deleted': deleted_count,
        'message': f'{deleted_count} users deleted'
    })



def system_info(request):
    """
    VULNERABLE: Sensitive Information Disclosure
    ثغرة كشف معلومات حساسة
    """

    info = {
        'secret_key': settings.SECRET_KEY,
        'debug': settings.DEBUG,
        'database': settings.DATABASES['default'],
        'allowed_hosts': settings.ALLOWED_HOSTS,
        'installed_apps': settings.INSTALLED_APPS,
        'environment': dict(os.environ),
    }
    
    return JsonResponse(info)



def eval_expression(request):
    """
    VULNERABLE: Code Injection
    ثغرة حقن كود عبر eval
    """
    expr = request.GET.get('expr', '1+1')
    

    try:
        result = eval(expr)
        return JsonResponse({
            'expression': expr,
            'result': str(result)
        })
    except Exception as e:
        return JsonResponse({
            'expression': expr,
            'error': str(e)
        }, status=400)
