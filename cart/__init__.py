
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages
from django.core.cache import cache
from django.db import transaction

from .models import Cart, CartItem, Wishlist
from products.models import Product

import json
import logging

logger = logging.getLogger(__name__)


def get_or_create_cart(request):
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        session_key = request.session.session_key
        if session_key:
            try:
                guest_cart = Cart.objects.get(session_key=session_key, user=None)
                guest_cart.merge_with_user_cart(request.user)
            except Cart.DoesNotExist:
                pass
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    
    return cart


@csrf_protect
def cart_view(request):
    
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    
    unavailable_items = []
    for item in items:
        if not item.is_available:
            unavailable_items.append(item)
    
    return render(request, 'cart/cart.html', {
        'cart': cart,
        'items': items,
        'unavailable_items': unavailable_items
    })


@require_POST
@csrf_protect
def add_to_cart(request):
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    if quantity < 1 or quantity > 99:
        return JsonResponse({'success': False, 'error': 'الكمية غير صالحة'}, status=400)
    
    ip = request.META.get('REMOTE_ADDR')
    cache_key = f"cart_add_{ip}"
    attempts = cache.get(cache_key, 0)
    if attempts > 30:
        return JsonResponse({'success': False, 'error': 'محاولات كثيرة'}, status=429)
    cache.set(cache_key, attempts + 1, 60)
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المنتج غير موجود'}, status=404)
    
    if not product.is_in_stock:
        return JsonResponse({'success': False, 'error': 'المنتج غير متوفر'}, status=400)
    
    cart = get_or_create_cart(request)
    
    with transaction.atomic():
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 0}
        )
        
        new_quantity = cart_item.quantity + quantity
        
        if new_quantity > product.stock:
            new_quantity = product.stock
            message = f'تم إضافة الكمية المتوفرة فقط ({product.stock})'
        else:
            message = 'تم إضافة المنتج للسلة'
        
        cart_item.quantity = new_quantity
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': message,
        'cart_count': cart.total_items
    })


@require_POST
@csrf_protect
def update_cart_item(request):
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    if quantity < 1 or quantity > 99:
        return JsonResponse({'success': False, 'error': 'الكمية غير صالحة'}, status=400)
    
    cart = get_or_create_cart(request)
    
    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'العنصر غير موجود'}, status=404)
    
    if quantity > item.product.stock:
        quantity = item.product.stock
    
    item.quantity = quantity
    item.save()
    
    return JsonResponse({
        'success': True,
        'item_total': float(item.total_price),
        'cart_subtotal': float(cart.subtotal),
        'cart_count': cart.total_items
    })


@require_POST
@csrf_protect
def remove_from_cart(request):
    
    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    cart = get_or_create_cart(request)
    
    try:
        item = CartItem.objects.get(id=item_id, cart=cart)
        item.delete()
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'العنصر غير موجود'}, status=404)
    
    return JsonResponse({
        'success': True,
        'cart_subtotal': float(cart.subtotal),
        'cart_count': cart.total_items
    })


@require_POST
@csrf_protect
def clear_cart(request):
    
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    
    return JsonResponse({
        'success': True,
        'message': 'تم تفريغ السلة'
    })


@login_required
@csrf_protect
def wishlist_view(request):
    
    wishlists = Wishlist.objects.filter(user=request.user).select_related('product')
    
    return render(request, 'cart/wishlist.html', {
        'wishlists': wishlists
    })


@login_required
@require_POST
@csrf_protect
def add_to_wishlist(request):
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'المنتج غير موجود'}, status=404)
    
    wishlist, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        return JsonResponse({'success': True, 'message': 'تم إضافة المنتج للأمنيات'})
    else:
        return JsonResponse({'success': True, 'message': 'المنتج موجود مسبقاً'})


@login_required
@require_POST
@csrf_protect
def remove_from_wishlist(request):
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'success': False, 'error': 'بيانات غير صالحة'}, status=400)
    
    try:
        wishlist = Wishlist.objects.get(user=request.user, product_id=product_id)
        wishlist.delete()
    except Wishlist.DoesNotExist:
        pass
    
    return JsonResponse({'success': True, 'message': 'تم إزالة المنتج'})

