
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Product
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء بيانات نموذجية للمتجر (تصنيفات ومنتجات)'

    def handle(self, *args, **options):
        self.stdout.write('جاري إنشاء البيانات النموذجية...')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('لم يتم العثور على مستخدم admin. أنشئ superuser أولاً.'))
            return
        
        categories_data = [
            {
                'name': 'الإلكترونيات',
                'slug': 'electronics',
                'description': 'أحدث الأجهزة الإلكترونية والتقنية'
            },
            {
                'name': 'الهواتف الذكية',
                'slug': 'smartphones',
                'description': 'هواتف ذكية من أفضل الماركات العالمية'
            },
            {
                'name': 'أجهزة الكمبيوتر',
                'slug': 'computers',
                'description': 'لابتوبات وأجهزة مكتبية وملحقاتها'
            },
            {
                'name': 'الملابس الرجالية',
                'slug': 'mens-clothing',
                'description': 'أزياء رجالية عصرية وأنيقة'
            },
            {
                'name': 'الملابس النسائية',
                'slug': 'womens-clothing',
                'description': 'أزياء نسائية متنوعة وعصرية'
            },
            {
                'name': 'الأحذية',
                'slug': 'shoes',
                'description': 'أحذية رياضية وكلاسيكية'
            },
            {
                'name': 'الساعات',
                'slug': 'watches',
                'description': 'ساعات فاخرة ورياضية'
            },
            {
                'name': 'الإكسسوارات',
                'slug': 'accessories',
                'description': 'إكسسوارات متنوعة'
            },
        ]
        
        categories = {}
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            categories[cat_data['slug']] = category
            if created:
                self.stdout.write(f'  ✓ تم إنشاء تصنيف: {category.name}')
            else:
                self.stdout.write(f'  • تصنيف موجود: {category.name}')
        
        products_data = [
            {
                'name': 'سماعات بلوتوث لاسلكية Pro',
                'slug': 'wireless-bluetooth-headphones-pro',
                'description': 'سماعات لاسلكية عالية الجودة مع خاصية إلغاء الضوضاء النشطة. بطارية تدوم حتى 30 ساعة. صوت استريو فائق الوضوح.',
                'price': Decimal('299.99'),
                'discount_price': Decimal('249.99'),
                'stock': 50,
                'category': 'electronics',
                'is_featured': True
            },
            {
                'name': 'شاحن لاسلكي سريع 15W',
                'slug': 'fast-wireless-charger-15w',
                'description': 'شاحن لاسلكي سريع بقوة 15 واط. متوافق مع جميع الأجهزة التي تدعم الشحن اللاسلكي. تصميم أنيق ومضاد للانزلاق.',
                'price': Decimal('79.99'),
                'discount_price': Decimal('59.99'),
                'stock': 100,
                'category': 'electronics',
                'is_featured': False
            },
            {
                'name': 'مكبر صوت بلوتوث محمول',
                'slug': 'portable-bluetooth-speaker',
                'description': 'مكبر صوت بلوتوث مقاوم للماء. بطارية تدوم 12 ساعة. صوت 360 درجة.',
                'price': Decimal('149.99'),
                'stock': 75,
                'category': 'electronics',
                'is_featured': True
            },
            {
                'name': 'هاتف Galaxy Ultra 2024',
                'slug': 'galaxy-ultra-2024',
                'description': 'أحدث هاتف ذكي مع شاشة 6.8 بوصة Dynamic AMOLED. كاميرا 200 ميجابكسل. معالج فائق السرعة.',
                'price': Decimal('1299.99'),
                'discount_price': Decimal('1199.99'),
                'stock': 25,
                'category': 'smartphones',
                'is_featured': True
            },
            {
                'name': 'هاتف iPhone Pro Max',
                'slug': 'iphone-pro-max',
                'description': 'iPhone بشريحة A17 Pro. كاميرا ثلاثية احترافية. شاشة Super Retina XDR.',
                'price': Decimal('1499.99'),
                'stock': 30,
                'category': 'smartphones',
                'is_featured': True
            },
            {
                'name': 'هاتف Pixel 8 Pro',
                'slug': 'pixel-8-pro',
                'description': 'أفضل كاميرا هاتف مع ذكاء اصطناعي متقدم. نظام أندرويد نقي.',
                'price': Decimal('999.99'),
                'discount_price': Decimal('899.99'),
                'stock': 40,
                'category': 'smartphones',
                'is_featured': False
            },
            {
                'name': 'لابتوب MacBook Pro M3',
                'slug': 'macbook-pro-m3',
                'description': 'لابتوب احترافي بشريحة M3 Pro. شاشة Liquid Retina XDR. ذاكرة 18GB.',
                'price': Decimal('2499.99'),
                'discount_price': Decimal('2299.99'),
                'stock': 15,
                'category': 'computers',
                'is_featured': True
            },
            {
                'name': 'لابتوب Dell XPS 15',
                'slug': 'dell-xps-15',
                'description': 'لابتوب أنيق بشاشة OLED 4K. معالج Intel Core i9. ذاكرة 32GB.',
                'price': Decimal('1899.99'),
                'stock': 20,
                'category': 'computers',
                'is_featured': False
            },
            {
                'name': 'لوحة مفاتيح ميكانيكية RGB',
                'slug': 'mechanical-keyboard-rgb',
                'description': 'لوحة مفاتيح ميكانيكية للألعاب مع إضاءة RGB. مفاتيح Cherry MX.',
                'price': Decimal('159.99'),
                'discount_price': Decimal('129.99'),
                'stock': 80,
                'category': 'computers',
                'is_featured': False
            },
            {
                'name': 'قميص كلاسيكي أبيض',
                'slug': 'classic-white-shirt',
                'description': 'قميص رجالي كلاسيكي من القطن المصري الفاخر. مناسب للمناسبات الرسمية.',
                'price': Decimal('89.99'),
                'discount_price': Decimal('69.99'),
                'stock': 100,
                'category': 'mens-clothing',
                'is_featured': True
            },
            {
                'name': 'بدلة رسمية سوداء',
                'slug': 'black-formal-suit',
                'description': 'بدلة رسمية أنيقة من الصوف الإيطالي. تصميم عصري ومريح.',
                'price': Decimal('599.99'),
                'discount_price': Decimal('499.99'),
                'stock': 30,
                'category': 'mens-clothing',
                'is_featured': True
            },
            {
                'name': 'تيشيرت قطني مريح',
                'slug': 'comfortable-cotton-tshirt',
                'description': 'تيشيرت من القطن الناعم 100%. متوفر بعدة ألوان.',
                'price': Decimal('39.99'),
                'stock': 200,
                'category': 'mens-clothing',
                'is_featured': False
            },
            {
                'name': 'فستان سهرة أنيق',
                'slug': 'elegant-evening-dress',
                'description': 'فستان سهرة طويل بتصميم عصري. مناسب للمناسبات الخاصة.',
                'price': Decimal('399.99'),
                'discount_price': Decimal('299.99'),
                'stock': 25,
                'category': 'womens-clothing',
                'is_featured': True
            },
            {
                'name': 'عباية سوداء فاخرة',
                'slug': 'luxury-black-abaya',
                'description': 'عباية سوداء من أجود أنواع القماش. تطريز يدوي فاخر.',
                'price': Decimal('249.99'),
                'stock': 50,
                'category': 'womens-clothing',
                'is_featured': True
            },
            {
                'name': 'بلوزة حريرية',
                'slug': 'silk-blouse',
                'description': 'بلوزة من الحرير الطبيعي. تصميم كلاسيكي أنيق.',
                'price': Decimal('129.99'),
                'discount_price': Decimal('99.99'),
                'stock': 60,
                'category': 'womens-clothing',
                'is_featured': False
            },
            {
                'name': 'حذاء رياضي Nike Air Max',
                'slug': 'nike-air-max-sneakers',
                'description': 'حذاء رياضي من نايكي مع تقنية Air Max للراحة القصوى.',
                'price': Decimal('189.99'),
                'discount_price': Decimal('159.99'),
                'stock': 75,
                'category': 'shoes',
                'is_featured': True
            },
            {
                'name': 'حذاء جلدي كلاسيكي',
                'slug': 'classic-leather-shoes',
                'description': 'حذاء رجالي من الجلد الطبيعي. مناسب للمناسبات الرسمية.',
                'price': Decimal('249.99'),
                'stock': 40,
                'category': 'shoes',
                'is_featured': False
            },
            {
                'name': 'صندل صيفي مريح',
                'slug': 'comfortable-summer-sandals',
                'description': 'صندل مريح للصيف. نعل طبي وتصميم عصري.',
                'price': Decimal('79.99'),
                'discount_price': Decimal('59.99'),
                'stock': 100,
                'category': 'shoes',
                'is_featured': False
            },
            {
                'name': 'ساعة Apple Watch Ultra',
                'slug': 'apple-watch-ultra',
                'description': 'ساعة ذكية من أبل. مقاومة للماء. شاشة Always-On.',
                'price': Decimal('799.99'),
                'discount_price': Decimal('749.99'),
                'stock': 35,
                'category': 'watches',
                'is_featured': True
            },
            {
                'name': 'ساعة Rolex Submariner',
                'slug': 'rolex-submariner',
                'description': 'ساعة فاخرة من رولكس. مقاومة للماء حتى 300 متر.',
                'price': Decimal('12999.99'),
                'stock': 5,
                'category': 'watches',
                'is_featured': True
            },
            {
                'name': 'ساعة Casio G-Shock',
                'slug': 'casio-g-shock',
                'description': 'ساعة رياضية متينة. مقاومة للصدمات والماء.',
                'price': Decimal('149.99'),
                'stock': 80,
                'category': 'watches',
                'is_featured': False
            },
            {
                'name': 'حقيبة جلدية فاخرة',
                'slug': 'luxury-leather-bag',
                'description': 'حقيبة يد من الجلد الطبيعي. تصميم إيطالي أنيق.',
                'price': Decimal('349.99'),
                'discount_price': Decimal('299.99'),
                'stock': 45,
                'category': 'accessories',
                'is_featured': True
            },
            {
                'name': 'نظارة شمسية Ray-Ban',
                'slug': 'ray-ban-sunglasses',
                'description': 'نظارة شمسية أصلية من راي بان. حماية UV400.',
                'price': Decimal('199.99'),
                'stock': 60,
                'category': 'accessories',
                'is_featured': False
            },
            {
                'name': 'محفظة جلدية رجالية',
                'slug': 'mens-leather-wallet',
                'description': 'محفظة من الجلد الطبيعي. حماية RFID للبطاقات.',
                'price': Decimal('89.99'),
                'discount_price': Decimal('69.99'),
                'stock': 100,
                'category': 'accessories',
                'is_featured': False
            },
        ]
        
        for prod_data in products_data:
            category_slug = prod_data.pop('category')
            category = categories.get(category_slug)
            
            product, created = Product.objects.get_or_create(
                slug=prod_data['slug'],
                defaults={
                    **prod_data,
                    'category': category,
                    'created_by': admin_user
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ تم إنشاء منتج: {product.name}')
            else:
                self.stdout.write(f'  • منتج موجود: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ تم إنشاء البيانات النموذجية بنجاح!'))
        self.stdout.write(f'   - {Category.objects.count()} تصنيفات')
        self.stdout.write(f'   - {Product.objects.count()} منتجات')

