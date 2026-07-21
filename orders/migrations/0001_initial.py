import django.core.validators
import django.db.models.deletion
import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('discount_type', models.CharField(choices=[('percentage', 'نسبة مئوية'), ('fixed', 'مبلغ ثابت')], max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('minimum_order', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('maximum_discount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('usage_limit', models.PositiveIntegerField(blank=True, null=True)),
                ('usage_limit_per_user', models.PositiveIntegerField(default=1)),
                ('times_used', models.PositiveIntegerField(default=0)),
                ('valid_from', models.DateTimeField()),
                ('valid_until', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('order_number', models.CharField(editable=False, max_length=20, unique=True)),
                ('status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('confirmed', 'مؤكد'), ('processing', 'قيد المعالجة'), ('shipped', 'تم الشحن'), ('delivered', 'تم التوصيل'), ('cancelled', 'ملغي'), ('refunded', 'مسترد')], default='pending', max_length=20)),
                ('payment_status', models.CharField(choices=[('pending', 'قيد الانتظار'), ('paid', 'مدفوع'), ('failed', 'فشل'), ('refunded', 'مسترد')], default='pending', max_length=20)),
                ('payment_method', models.CharField(choices=[('cod', 'الدفع عند الاستلام'), ('credit_card', 'بطاقة ائتمان'), ('paypal', 'PayPal'), ('bank_transfer', 'تحويل بنكي')], max_length=20)),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('shipping_cost', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('integrity_hash', models.CharField(editable=False, max_length=64)),
                ('shipping_address', models.JSONField()),
                ('billing_address', models.JSONField()),
                ('notes', models.TextField(blank=True, max_length=500)),
                ('tracking_number', models.CharField(blank=True, max_length=100)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CouponUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('used_at', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='orders.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_usages', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_usage', to='orders.order')),
            ],
            options={
                'ordering': ['-used_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('product_name', models.CharField(max_length=200)),
                ('product_sku', models.CharField(blank=True, max_length=50)),
                ('quantity', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(99)])),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='products.product')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['order_number'], name='orders_orde_order_n_f3ada5_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['user', 'status'], name='orders_orde_user_id_02a211_idx'),
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['created_at'], name='orders_orde_created_0e92de_idx'),
        ),
    ]
