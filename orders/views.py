
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from .models import Order, OrderItem, Coupon, CouponUsage
from cart.models import Cart, CartItem
from cart.views import get_or_create_cart
from accounts.models import Address

from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)

def get_client_ip(request):
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
@require_http_methods(["GET", "POST"])
def checkout_view(request):
    
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    
    if not items:
        messages.warning(request, 'السلة فارغة')
        return redirect('cart:cart')

    for item in items:
        if not item.is_available:
            messages.error(request, f'المنتج "{item.product.name}" غير متوفر بالكمية المطلوبة')
            return redirect('cart:cart')
    
    addresses = request.user.addresses.all()

    applied_coupon = None
    discount = Decimal('0.00')
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid():
                discount = coupon.calculate_discount(cart.subtotal)
                applied_coupon = coupon
        except Coupon.DoesNotExist:
            del request.session['coupon_code']
    
    subtotal = cart.subtotal
    tax = subtotal * Decimal('0.15')
    shipping = Decimal('10.00') if subtotal < 100 else Decimal('0.00')
    total = subtotal + tax + shipping - discount
    
    context = {
        'cart': cart,
        'items': items,
        'addresses': addresses,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'discount': discount,
        'total': total,
        'applied_coupon': applied_coupon
    }
    
    return render(request, 'orders/checkout.html', context)

@login_required
@require_POST
def place_order(request):

    cache_key = f"place_order_{request.user.id}"
    if cache.get(cache_key):
        return JsonResponse({
            'success': False,
            'error': 'يرجى الانتظار قبل إنشاء طلب جديد'
        }, status=429)
    
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    
    if not items:
        return JsonResponse({'success': False, 'error': 'السلة فارغة'}, status=400)
    
    try:
        data = json.loads(request.body)
        shipping_address_id = data.get('shipping_address_id')
        billing_address_id = data.get('billing_address_id')
        payment_method = data.get('payment_method')
        notes = data.get('notes', '')[:500]
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)

    valid_methods = ['cod', 'credit_card', 'paypal', 'bank_transfer']
    if payment_method not in valid_methods:
        return JsonResponse({'success': False, 'error': 'طريقة دفع غير صالحة'}, status=400)

    try:
        shipping_address = Address.objects.get(id=shipping_address_id, user=request.user)
        billing_address = Address.objects.get(id=billing_address_id, user=request.user)
    except Address.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'العنوان غير موجود'}, status=400)
    
    with transaction.atomic():

        subtotal = cart.subtotal
        tax = subtotal * Decimal('0.15')
        shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0.00')
        discount = Decimal('0.00')

        coupon = None
        coupon_code = request.session.get('coupon_code')
        if coupon_code:
            try:
                coupon = Coupon.objects.select_for_update().get(code=coupon_code)
                if coupon.is_valid():

                    user_usages = CouponUsage.objects.filter(
                        coupon=coupon, user=request.user
                    ).count()
                    if user_usages < coupon.usage_limit_per_user:
                        discount = coupon.calculate_discount(subtotal)
                    else:
                        coupon = None
            except Coupon.DoesNotExist:
                coupon = None
        
        total = subtotal + tax + shipping_cost - discount

        for item in items:
            product = item.product
            if item.quantity > product.stock:
                return JsonResponse({
                    'success': False,
                    'error': f'الكمية المتوفرة من "{product.name}" هي {product.stock} فقط'
                }, status=400)

            product.stock -= item.quantity
            product.save(update_fields=['stock'])

        order = Order.objects.create(
            user=request.user,
            status='pending',
            payment_status='pending',
            payment_method=payment_method,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            discount=discount,
            total=total,
            shipping_address={
                'full_name': shipping_address.full_name,
                'address_line1': shipping_address.address_line1,
                'address_line2': shipping_address.address_line2,
                'city': shipping_address.city,
                'state': shipping_address.state,
                'postal_code': shipping_address.postal_code,
                'country': shipping_address.country,
                'phone': shipping_address.phone,
            },
            billing_address={
                'full_name': billing_address.full_name,
                'address_line1': billing_address.address_line1,
                'address_line2': billing_address.address_line2,
                'city': billing_address.city,
                'state': billing_address.state,
                'postal_code': billing_address.postal_code,
                'country': billing_address.country,
                'phone': billing_address.phone,
            },
            notes=notes,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=item.product.final_price,
                total_price=item.total_price
            )

        if coupon and discount > 0:
            CouponUsage.objects.create(
                coupon=coupon,
                user=request.user,
                order=order,
                discount_amount=discount
            )
            coupon.times_used += 1
            coupon.save(update_fields=['times_used'])

        cart.items.all().delete()

        if 'coupon_code' in request.session:
            del request.session['coupon_code']

    cache.set(cache_key, True, 60)
    
    logger.info(f"Order {order.order_number} created by {request.user.email}")
    
    return JsonResponse({
        'success': True,
        'order_number': order.order_number,
        'redirect_url': f'/orders/{order.id}/'
    })

@login_required
def order_detail(request, order_id):
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items
    })

@login_required
def order_list(request):
    
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'orders/order_list.html', {
        'orders': orders
    })

@login_required
@require_POST
def cancel_order(request, order_id):
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not order.can_cancel:
        return JsonResponse({
            'success': False,
            'error': 'لا يمكن إلغاء هذا الطلب'
        }, status=400)
    
    with transaction.atomic():

        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save(update_fields=['stock'])
        
        order.status = 'cancelled'
        order.save(update_fields=['status', 'updated_at'])
    
    logger.info(f"Order {order.order_number} cancelled by {request.user.email}")
    
    return JsonResponse({
        'success': True,
        'message': 'تم إلغاء الطلب'
    })

@login_required
@require_POST
def apply_coupon(request):
    
    try:
        data = json.loads(request.body)
        code = data.get('code', '').strip().upper()
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    if not code:
        return JsonResponse({'success': False, 'error': 'الرجاء إدخال كود الكوبون'}, status=400)
    
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'كود الكوبون غير صالح'}, status=400)
    
    if not coupon.is_valid():
        return JsonResponse({'success': False, 'error': 'الكوبون منتهي الصلاحية'}, status=400)

    user_usages = CouponUsage.objects.filter(coupon=coupon, user=request.user).count()
    if user_usages >= coupon.usage_limit_per_user:
        return JsonResponse({
            'success': False,
            'error': 'لقد استخدمت هذا الكوبون من قبل'
        }, status=400)
    
    cart = get_or_create_cart(request)

    if cart.subtotal < coupon.minimum_order:
        return JsonResponse({
            'success': False,
            'error': f'الحد الأدنى للطلب هو {coupon.minimum_order}'
        }, status=400)

    request.session['coupon_code'] = code
    
    discount = coupon.calculate_discount(cart.subtotal)
    
    return JsonResponse({
        'success': True,
        'message': 'تم تطبيق الكوبون',
        'discount': float(discount)
    })

@login_required
@require_POST
def remove_coupon(request):
    
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    
    return JsonResponse({
        'success': True,
        'message': 'تم إزالة الكوبون'
    })

import xml.etree.ElementTree as ET
import yaml
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def order_search(request):

    order_number = request.GET.get('order_number', '')
    status = request.GET.get('status', '')

    with connection.cursor() as cursor:
        sql = f"SELECT id, order_number, total, status FROM orders_order WHERE order_number LIKE '%{order_number}%'"
        if status:
            sql += f" AND status = '{status}'"
        cursor.execute(sql)
        results = cursor.fetchall()
    
    orders = [
        {
            'id': str(row[0]),
            'order_number': row[1],
            'total': str(row[2]),
            'status': row[3]
        }
        for row in results
    ]
    
    return JsonResponse({'orders': orders})

@csrf_exempt
def import_orders_xml(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    xml_data = request.body.decode('utf-8')
    
    if not xml_data:
        return JsonResponse({'error': 'No XML data provided'}, status=400)
    
    try:

        root = ET.fromstring(xml_data)
        
        orders_imported = []
        for order_elem in root.findall('order'):
            order_data = {
                'order_number': order_elem.find('order_number').text if order_elem.find('order_number') is not None else '',
                'total': order_elem.find('total').text if order_elem.find('total') is not None else '0',
                'status': order_elem.find('status').text if order_elem.find('status') is not None else 'pending'
            }
            orders_imported.append(order_data)
        
        return JsonResponse({
            'status': 'success',
            'imported': len(orders_imported),
            'orders': orders_imported
        })
    except ET.ParseError as e:
        return JsonResponse({'error': f'XML parsing error: {str(e)}'}, status=400)

@csrf_exempt
def import_orders_yaml(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    yaml_data = request.body.decode('utf-8')
    
    if not yaml_data:
        return JsonResponse({'error': 'No YAML data provided'}, status=400)
    
    try:

        data = yaml.load(yaml_data, Loader=yaml.Loader)
        
        return JsonResponse({
            'status': 'success',
            'message': 'YAML processed',
            'data': str(data)
        })
    except yaml.YAMLError as e:
        return JsonResponse({'error': f'YAML error: {str(e)}'}, status=400)

def order_invoice(request, order_id):

    try:
        order = Order.objects.get(id=order_id)
        
        invoice_data = {
            'order_id': str(order.id),
            'order_number': order.order_number,
            'customer_email': order.user.email,
            'customer_name': order.user.get_full_name(),
            'total': str(order.total),
            'status': order.status,
            'created_at': str(order.created_at),
            'shipping_address': str(order.shipping_address) if order.shipping_address else None,
        }
        
        return JsonResponse(invoice_data)
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

@csrf_exempt
def update_order_status(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    order_id = data.get('order_id')
    
    if not order_id:
        return JsonResponse({'error': 'order_id required'}, status=400)
    
    try:
        order = Order.objects.get(id=order_id)

        for key, value in data.items():
            if hasattr(order, key) and key != 'id':
                setattr(order, key, value)
        
        order.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Order updated',
            'order': {
                'id': str(order.id),
                'status': order.status,
                'total': str(order.total)
            }
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)

def export_orders(request):

    orders = Order.objects.all().select_related('user')[:100]
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': str(order.id),
            'order_number': order.order_number,
            'customer_email': order.user.email,
            'customer_name': order.user.get_full_name(),
            'total': str(order.total),
            'status': order.status,
            'created_at': str(order.created_at),
        })
    
    return JsonResponse({'orders': orders_data})