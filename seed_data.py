"""
Seed Data Script - لملء قاعدة البيانات ببيانات تجريبية
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mystore.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from accounts.models import CustomUser, Address
from products.models import Category, Product, ProductImage, Review
from cart.models import Cart, CartItem, Wishlist
from orders.models import Order, OrderItem, Coupon, CouponUsage

def create_users():
    """إنشاء مستخدمين تجريبيين"""
    print("Creating users...")
    users = []
    
    # Admin user
    admin, created = CustomUser.objects.get_or_create(
        email='admin@mystore.com',
        defaults={
            'username': 'admin',
            'first_name': 'أحمد',
            'last_name': 'المدير',
            'phone': '+966500000000',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin.set_password('Admin@123456')
        admin.save()
        users.append(admin)
    
    # Regular users
    user_data = [
        {
            'email': 'ahmed@example.com',
            'username': 'ahmed',
            'first_name': 'أحمد',
            'last_name': 'محمد',
            'phone': '+966501234567',
        },
        {
            'email': 'sarah@example.com',
            'username': 'sarah',
            'first_name': 'سارة',
            'last_name': 'أحمد',
            'phone': '+966502345678',
        },
        {
            'email': 'khalid@example.com',
            'username': 'khalid',
            'first_name': 'خالد',
            'last_name': 'عبدالله',
            'phone': '+966503456789',
        },
        {
            'email': 'fatima@example.com',
            'username': 'fatima',
            'first_name': 'فاطمة',
            'last_name': 'علي',
            'phone': '+966504567890',
        },
        {
            'email': 'omar@example.com',
            'username': 'omar',
            'first_name': 'عمر',
            'last_name': 'حسن',
            'phone': '+966505678901',
        },
    ]
    
    for data in user_data:
        user, created = CustomUser.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        if created:
            user.set_password('User@123456')
            user.save()
            users.append(user)
    
    print(f"✓ Created {len(users)} users")
    return users

def create_categories():
    """إنشاء تصنيفات المنتجات"""
    print("\nCreating categories...")
    categories = []
    
    category_data = [
        {'name': 'الإلكترونيات', 'slug': 'electronics', 'description': 'أجهزة إلكترونية وملحقات'},
        {'name': 'الملابس', 'slug': 'clothing', 'description': 'ملابس رجالية ونسائية'},
        {'name': 'الأثاث', 'slug': 'furniture', 'description': 'أثاث منزلي ومكتبي'},
        {'name': 'الرياضة', 'slug': 'sports', 'description': 'معدات رياضية ولياقة بدنية'},
        {'name': 'الكتب', 'slug': 'books', 'description': 'كتب ومراجع تعليمية'},
        {'name': 'المستحضرات', 'slug': 'beauty', 'description': 'مستحضرات تجميل وعناية'},
    ]
    
    for data in category_data:
        # Try to get existing category or create new one
        try:
            category = Category.objects.get(name=data['name'])
            categories.append(category)
        except Category.DoesNotExist:
            category = Category.objects.create(
                name=data['name'],
                slug=data['slug'],
                description=data['description']
            )
            categories.append(category)
    
    print(f"✓ Created {len(categories)} categories")
    return categories

def create_products(categories, users):
    """إنشاء منتجات تجريبية"""
    print("\nCreating products...")
    products = []
    
    # Get all users (including existing ones)
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    products_data = [
        # Electronics
        {
            'name': 'آيفون 15 برو ماكس',
            'description': 'هاتف آيفون 15 برو ماكس بشاشة 6.7 بوصة، ذاكرة 256 جيجابايت، كاميرا احترافية 48 ميجابكسل',
            'price': Decimal('4999.00'),
            'discount_price': Decimal('4599.00'),
            'category': 'الإلكترونيات',
            'stock': 50,
            'is_featured': True,
        },
        {
            'name': 'سامسونج جالاكسي S24 الترا',
            'description': 'هاتف سامسونج جالاكسي S24 الترا بشاشة AMOLED 6.8 بوصة، ذاكرة 512 جيجابايت',
            'price': Decimal('4299.00'),
            'discount_price': Decimal('3999.00'),
            'category': 'الإلكترونيات',
            'stock': 35,
            'is_featured': True,
        },
        {
            'name': 'ماك بوك برو M3',
            'description': 'لابتوب آبل ماك بوك برو بشريحة M3، ذاكرة 18 جيجابايت، SSD 512 جيجابايت',
            'price': Decimal('12999.00'),
            'category': 'الإلكترونيات',
            'stock': 20,
            'is_featured': True,
        },
        {
            'name': 'سماعات AirPods Pro 2',
            'description': 'سماعات آبل AirPods Pro 2 مع إلغاء الضوضاء النشط',
            'price': Decimal('899.00'),
            'discount_price': Decimal('799.00'),
            'category': 'الإلكترونيات',
            'stock': 100,
            'is_featured': False,
        },
        {
            'name': 'آيباد إير 5',
            'description': 'آيباد إير الجيل الخامس بشاشة 10.9 بوصة، شريحة M1',
            'price': Decimal('2999.00'),
            'category': 'الإلكترونيات',
            'stock': 40,
            'is_featured': False,
        },
        # Clothing
        {
            'name': 'قميص قطني رجالي',
            'description': 'قميص قطني عالي الجودة، مريح ومناسب للاستخدام اليومي',
            'price': Decimal('149.00'),
            'discount_price': Decimal('119.00'),
            'category': 'الملابس',
            'stock': 200,
            'is_featured': True,
        },
        {
            'name': 'فستان صيفي نسائي',
            'description': 'فستان صيفي أنيق بقصة عصرية وألوان زاهية',
            'price': Decimal('299.00'),
            'category': 'الملابس',
            'stock': 80,
            'is_featured': True,
        },
        {
            'name': 'جاكيت جلد',
            'description': 'جاكيت جلد طبيعي بتصميم كلاسيكي',
            'price': Decimal('899.00'),
            'discount_price': Decimal('749.00'),
            'category': 'الملابس',
            'stock': 30,
            'is_featured': False,
        },
        # Furniture
        {
            'name': 'أريكة مودرن 3 مقاعد',
            'description': 'أريكة مودرن مريحة لثلاثة أشخاص بقماش فاخر',
            'price': Decimal('2499.00'),
            'discount_price': Decimal('2199.00'),
            'category': 'الأثاث',
            'stock': 15,
            'is_featured': True,
        },
        {
            'name': 'طاولة طعام خشبية',
            'description': 'طاولة طعام خشب زان طبيعي تتسع لـ 6 أشخاص',
            'price': Decimal('1899.00'),
            'category': 'الأثاث',
            'stock': 10,
            'is_featured': False,
        },
        {
            'name': 'خزانة ملابس',
            'description': 'خزانة ملابس واسعة مع أدراج ومرآة',
            'price': Decimal('1599.00'),
            'discount_price': Decimal('1399.00'),
            'category': 'الأثاث',
            'stock': 12,
            'is_featured': True,
        },
        # Sports
        {
            'name': 'حذاء رياضي نايكي',
            'description': 'حذاء رياضي نايكي للجري بتقنية Air Max',
            'price': Decimal('599.00'),
            'discount_price': Decimal('499.00'),
            'category': 'الرياضة',
            'stock': 60,
            'is_featured': True,
        },
        {
            'name': 'دمبلز adjustable 20kg',
            'description': 'طقم دمبلز قابل للتعديل من 2 إلى 20 كجم',
            'price': Decimal('349.00'),
            'category': 'الرياضة',
            'stock': 25,
            'is_featured': False,
        },
        {
            'name': 'يوجا مات برو',
            'description': 'سجادة يوجا احترافية سمك 8 ملم مضادة للانزلاق',
            'price': Decimal('129.00'),
            'category': 'الرياضة',
            'stock': 150,
            'is_featured': False,
        },
        # Books
        {
            'name': 'كتاب تعلم البرمجة بايثون',
            'description': 'دليل شامل لتعلم لغة بايثون من الصفر حتى الاحتراف',
            'price': Decimal('89.00'),
            'category': 'الكتب',
            'stock': 100,
            'is_featured': True,
        },
        {
            'name': 'رواية الخيميائي',
            'description': 'الرواية العالمية الشهيرة لباولو كويلو',
            'price': Decimal('45.00'),
            'category': 'الكتب',
            'stock': 200,
            'is_featured': False,
        },
        # Beauty
        {
            'name': 'عطر فرنسي فاخر',
            'description': 'عطر فرنسي فاخر برائحة خشبية شرقية',
            'price': Decimal('399.00'),
            'discount_price': Decimal('349.00'),
            'category': 'المستحضرات',
            'stock': 45,
            'is_featured': True,
        },
        {
            'name': 'كريم مرطب للبشرة',
            'description': 'كريم مرطب طبيعي للبشرة الجافة والحساسة',
            'price': Decimal('79.00'),
            'category': 'المستحضرات',
            'stock': 120,
            'is_featured': False,
        },
    ]
    
    for data in products_data:
        category = Category.objects.get(name=data['category'])
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={
                'description': data['description'],
                'price': data['price'],
                'discount_price': data.get('discount_price'),
                'category': category,
                'stock': data['stock'],
                'is_featured': data['is_featured'],
                'is_active': True,
            'created_by': random.choice(all_users),
            }
        )
        if created:
            products.append(product)
    
    print(f"✓ Created {len(products)} products")
    return products

def create_reviews(products, users):
    """إنشاء تقييمات للمنتجات"""
    print("\nCreating reviews...")
    reviews = []
    
    # Get all users from database
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    review_titles = [
        'منتج ممتاز!',
        'جودة عالية',
        'استحق السعر',
        'موصى به',
        'رائع جداً',
        'جيد لكن يحتاج تحسين',
        'ممتاز',
    ]
    
    review_comments = [
        'منتج رائع بجودة عالية وتوصيل سريع. أنصح به بشدة!',
        'استخدمته لعدة أسابيع وهو يعمل بشكل ممتاز. قيمة ممتازة مقابل السعر.',
        'التغليف كان ممتاز والمنتج مطابق للوصف. شكراً لكم!',
        'جودة جيدة جداً ولكن السعر مرتفع قليلاً.',
        'منتج رائع وخدمة عملاء ممتازة. سأشتري مرة أخرى.',
    ]
    
    for product in products[:15]:  # Reviews for first 15 products
        num_reviews = random.randint(1, 5)
        for _ in range(num_reviews):
            user = random.choice(all_users)
            review, created = Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={
                    'rating': random.randint(3, 5),
                    'title': random.choice(review_titles),
                    'comment': random.choice(review_comments),
                    'is_approved': True,
                }
            )
            if created:
                reviews.append(review)
    
    print(f"✓ Created {len(reviews)} reviews")
    return reviews

def create_carts(users, products):
    """إنشاء سلات تسوق"""
    print("\nCreating carts...")
    carts = []
    
    # Get all users from database
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    for user in all_users:
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            # Add random products to cart
            num_items = random.randint(1, 5)
            selected_products = random.sample(list(products), min(num_items, len(products)))
            
            for product in selected_products:
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': random.randint(1, 3)}
                )
            carts.append(cart)
    
    print(f"✓ Created {len(carts)} carts with items")
    return carts

def create_wishlists(users, products):
    """إنشاء قوائم أمنيات"""
    print("\nCreating wishlists...")
    wishlists = []
    
    # Get all users from database
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    for user in all_users:
        num_wishlists = random.randint(2, 8)
        selected_products = random.sample(list(products), min(num_wishlists, len(products)))
        
        for product in selected_products:
            wishlist, created = Wishlist.objects.get_or_create(
                user=user,
                product=product
            )
            if created:
                wishlists.append(wishlist)
    
    print(f"✓ Created {len(wishlists)} wishlist items")
    return wishlists

def create_orders(users, products):
    """إنشاء طلبات تجريبية"""
    print("\nCreating orders...")
    orders = []
    
    # Get all users from database
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    order_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
    
    for user in all_users:
        num_orders = random.randint(1, 4)
        
        for _ in range(num_orders):
            # Create order
            order = Order.objects.create(
                user=user,
                status=random.choice(order_statuses),
                payment_status=random.choice(['pending', 'paid']),
                payment_method=random.choice(['cod', 'credit_card', 'paypal']),
                subtotal=Decimal('0.00'),
                tax=Decimal('0.00'),
                shipping_cost=Decimal(random.choice([0, 25, 50])),
                discount=Decimal('0.00'),
                total=Decimal('0.00'),
                shipping_address={
                    'full_name': f'{user.first_name} {user.last_name}',
                    'address_line1': f'شارع {random.randint(1, 100)}',
                    'city': 'الرياض',
                    'state': 'الرياض',
                    'postal_code': '12345',
                    'country': 'المملكة العربية السعودية',
                    'phone': user.phone,
                },
                billing_address={
                    'full_name': f'{user.first_name} {user.last_name}',
                    'address_line1': f'شارع {random.randint(1, 100)}',
                    'city': 'الرياض',
                    'state': 'الرياض',
                    'postal_code': '12345',
                    'country': 'المملكة العربية السعودية',
                    'phone': user.phone,
                },
                ip_address='192.168.1.1',
                user_agent='Mozilla/5.0',
            )
            
            # Add order items
            num_items = random.randint(1, 4)
            selected_products = random.sample(list(products), min(num_items, len(products)))
            
            subtotal = Decimal('0.00')
            for product in selected_products:
                quantity = random.randint(1, 3)
                unit_price = product.final_price
                total_price = unit_price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=f'SKU-{product.id.hex[:8].upper()}',
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price,
                )
                subtotal += total_price
            
            # Calculate totals
            tax = subtotal * Decimal('0.15')  # 15% tax
            total = subtotal + tax + order.shipping_cost - order.discount
            
            order.subtotal = subtotal
            order.tax = tax
            order.total = total
            order.save()
            
            orders.append(order)
    
    print(f"✓ Created {len(orders)} orders with items")
    return orders

def create_coupons():
    """إنشاء كوبونات خصم"""
    print("\nCreating coupons...")
    coupons = []
    
    coupons_data = [
        {
            'code': 'WELCOME10',
            'description': 'خصم 10% للعملاء الجدد',
            'discount_type': 'percentage',
            'discount_value': Decimal('10.00'),
            'minimum_order': Decimal('100.00'),
            'usage_limit': 100,
            'usage_limit_per_user': 1,
            'times_used': 45,
        },
        {
            'code': 'SUMMER50',
            'description': 'خصم 50 ريال على الطلبات فوق 200 ريال',
            'discount_type': 'fixed',
            'discount_value': Decimal('50.00'),
            'minimum_order': Decimal('200.00'),
            'usage_limit': 50,
            'usage_limit_per_user': 2,
            'times_used': 23,
        },
        {
            'code': 'FREESHIP',
            'description': 'شحن مجاني',
            'discount_type': 'fixed',
            'discount_value': Decimal('25.00'),
            'minimum_order': Decimal('150.00'),
            'usage_limit': None,
            'usage_limit_per_user': 3,
            'times_used': 89,
        },
    ]
    
    now = timezone.now()
    for data in coupons_data:
        coupon, created = Coupon.objects.get_or_create(
            code=data['code'],
            defaults={
                'description': data['description'],
                'discount_type': data['discount_type'],
                'discount_value': data['discount_value'],
                'minimum_order': data['minimum_order'],
                'usage_limit': data['usage_limit'],
                'usage_limit_per_user': data['usage_limit_per_user'],
                'times_used': data['times_used'],
                'valid_from': now - timedelta(days=30),
                'valid_until': now + timedelta(days=60),
                'is_active': True,
            }
        )
        if created:
            coupons.append(coupon)
    
    print(f"✓ Created {len(coupons)} coupons")
    return coupons

def create_addresses(users):
    """إنشاء عناوين للمستخدمين"""
    print("\nCreating addresses...")
    addresses = []
    
    # Get all users from database
    all_users = list(CustomUser.objects.all())
    if not all_users:
        all_users = users
    
    cities = [
        {'city': 'الرياض', 'state': 'الرياض'},
        {'city': 'جدة', 'state': 'مكة المكرمة'},
        {'city': 'الدمام', 'state': 'الشرقية'},
        {'city': 'المدينة', 'state': 'المدينة المنورة'},
    ]
    
    for user in all_users:
        num_addresses = random.randint(1, 3)
        for i in range(num_addresses):
            city_data = random.choice(cities)
            address, created = Address.objects.get_or_create(
                user=user,
                address_type=random.choice(['shipping', 'billing']),
                full_name=f'{user.first_name} {user.last_name}',
                address_line1=f'شارع {random.randint(1, 100)}، حي {random.choice(["النخيل", "الورود", "الملقا", "الياسمين"])}',
                city=city_data['city'],
                state=city_data['state'],
                postal_code=f'{random.randint(10000, 99999)}',
                country='المملكة العربية السعودية',
                phone=user.phone,
                defaults={'is_default': i == 0}
            )
            if created:
                addresses.append(address)
    
    print(f"✓ Created {len(addresses)} addresses")
    return addresses

def main():
    """Main function to run all seeders"""
    print("=" * 60)
    print("Starting Database Seeding...")
    print("=" * 60)
    
    try:
        # Create data in order (respecting foreign keys)
        users = create_users()
        categories = create_categories()
        products = create_products(categories, users)
        reviews = create_reviews(products, users)
        carts = create_carts(users, products)
        wishlists = create_wishlists(users, products)
        orders = create_orders(users, products)
        coupons = create_coupons()
        addresses = create_addresses(users)
        
        print("\n" + "=" * 60)
        print("✓ Database seeding completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Users: {len(users)}")
        print(f"  - Categories: {len(categories)}")
        print(f"  - Products: {len(products)}")
        print(f"  - Reviews: {len(reviews)}")
        print(f"  - Carts: {len(carts)}")
        print(f"  - Wishlists: {len(wishlists)}")
        print(f"  - Orders: {len(orders)}")
        print(f"  - Coupons: {len(coupons)}")
        print(f"  - Addresses: {len(addresses)}")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()