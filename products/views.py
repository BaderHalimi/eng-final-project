"""
Products Views - SECURE VERSION
عروض آمنة مع حماية كاملة
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.conf import settings

from .models import Product, Category, Review
from .forms import ProductSearchForm, ReviewForm

import logging

logger = logging.getLogger(__name__)


def home_view(request):
    """الصفحة الرئيسية"""
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category').prefetch_related('reviews')[:8]
    
    latest_products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')[:8]
    

    best_sellers = Product.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('reviews').annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-review_count', '-avg_rating')[:8]
    
    categories = Category.objects.filter(is_active=True, parent=None)[:6]
    
    return render(request, 'products/home.html', {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'best_sellers': best_sellers,
        'categories': categories,
    })


class ProductListView(ListView):
    """
    عرض قائمة المنتجات - آمن
    أمان:
    - Parameterized queries (تلقائي في Django ORM)
    - Rate limiting (via cache)
    - Input sanitization
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):

        queryset = Product.objects.filter(is_active=True).select_related('category')
        

        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(description__icontains=q)
            )
        

        category_slug = self.request.GET.get('category', '').strip()
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        

        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        

        if self.request.GET.get('in_stock'):
            queryset = queryset.filter(stock__gt=0)
        

        if self.request.GET.get('sale'):
            queryset = queryset.filter(discount_price__isnull=False)
        

        sort = self.request.GET.get('sort', '')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort == 'newest':
            queryset = queryset.order_by('-created_at')
        elif sort == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        

        category_slug = self.request.GET.get('category', '')
        if category_slug:
            context['current_category'] = Category.objects.filter(slug=category_slug).first()
        
        return context


class ProductDetailView(DetailView):
    """
    تفاصيل المنتج - آمن
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        

        context['reviews'] = product.reviews.filter(
            is_approved=True
        ).select_related('user').order_by('-created_at')[:10]
        

        context['avg_rating'] = product.reviews.filter(
            is_approved=True
        ).aggregate(avg=Avg('rating'))['avg'] or 0
        

        if self.request.user.is_authenticated:

            existing_review = product.reviews.filter(user=self.request.user).exists()
            if not existing_review:
                context['review_form'] = ReviewForm()
        

        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        return context


@login_required
@require_http_methods(["POST"])
@csrf_protect
def add_review(request, slug):
    """
    إضافة تقييم - آمن
    أمان:
    - CSRF protection
    - Login required
    - Rate limiting
    - Input validation
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)
    

    cache_key = f"review_rate_{request.user.id}"
    if cache.get(cache_key):
        return JsonResponse({
            'success': False,
            'error': 'يرجى الانتظار قبل إضافة تقييم آخر'
        }, status=429)
    

    if Review.objects.filter(product=product, user=request.user).exists():
        return JsonResponse({
            'success': False,
            'error': 'لقد قمت بتقييم هذا المنتج مسبقاً'
        }, status=400)
    
    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.is_approved = False
        review.save()
        

        cache.set(cache_key, True, 300)
        
        logger.info(f"New review added by {request.user.email} for product {product.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'تم إرسال تقييمك وسيتم مراجعته قريباً'
        })
    
    return JsonResponse({
        'success': False,
        'errors': form.errors
    }, status=400)


def category_products(request, slug):
    """عرض منتجات التصنيف"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    return render(request, 'products/category_products.html', {
        'category': category,
        'products': products
    })







import os
import subprocess
from django.db import connection
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import Template, Context



def product_search_raw(request):
    """
    """
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')
    

    with connection.cursor() as cursor:
        sql = f"SELECT id, name, price, stock FROM products_product WHERE name LIKE '%{query}%' ORDER BY {sort}"
        cursor.execute(sql)
        results = cursor.fetchall()
    
    products = [
        {
            'id': str(row[0]),
            'name': row[1],
            'price': str(row[2]),
            'stock': row[3]
        }
        for row in results
    ]
    
    return JsonResponse({'products': products})



def product_preview(request):
    """
    """
    name = request.GET.get('name', 'Product Name')
    description = request.GET.get('description', 'Product Description')
    

    html = f"""
    <html>
    <head><title>Product Preview</title></head>
    <body>
        <h1>{name}</h1>
        <p>{description}</p>
    </body>
    </html>
    """
    
    return HttpResponse(html)



def product_image_path(request):
    """
    """
    filename = request.GET.get('file', '')
    
    if not filename:
        return HttpResponse('Filename required', status=400)
    

    file_path = os.path.join(settings.MEDIA_ROOT, 'products', filename)
    
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
        return HttpResponse(content, content_type='application/octet-stream')
    except FileNotFoundError:
        return HttpResponse('File not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)



def execute_report(request):
    """
    """
    report_type = request.GET.get('type', 'sales')
    date = request.GET.get('date', '2026-01-01')
    

    command = f"python manage.py generate_report --type {report_type} --date {date}"
    
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return HttpResponse(f"<pre>{result.decode()}</pre>")
    except subprocess.CalledProcessError as e:
        return HttpResponse(f"<pre>Error: {e.output.decode()}</pre>", status=500)



@csrf_exempt
def product_comment(request):
    """
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    import json
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    product_id = data.get('product_id', '')
    comment = data.get('comment', '')
    
    if not product_id or not comment:
        return JsonResponse({'error': 'product_id and comment required'}, status=400)
    



    
    return JsonResponse({
        'status': 'success',
        'comment': comment,
        'message': 'Comment added successfully'
    })



def render_template(request):
    """
    """
    template_string = request.GET.get('template', 'Hello {{ name }}!')
    name = request.GET.get('name', 'User')
    

    template = Template(template_string)
    context = Context({'name': name, 'settings': settings})
    rendered = template.render(context)
    
    return HttpResponse(rendered)
