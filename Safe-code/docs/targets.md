# Application Targets - MyStore

## 📋 معلومات عامة

| المعلومة | القيمة |
|----------|--------|
| **اسم التطبيق** | MyStore - متجر إلكتروني آمن |
| **الإطار** | Django 6.0.1 |
| **Python** | 3.12 |
| **قاعدة البيانات** | SQLite3 |

---

## 🔐 معلومات الدخول (Demos)

### المستخدم المسؤول (Admin/Staff)
- **إنشاء حساب:** `python manage.py createsuperuser`
- **لوحة التحكم:** `/admin/` أو `/dashboard/`
- **الصلاحيات:** `is_staff=True` أو `is_superuser=True`

### المستخدم العادي (Customer)
- **التسجيل:** `/accounts/register/`
- **تسجيل الدخول:** `/accounts/login/`
- **الصلاحيات:** مستخدم عادي بدون صلاحيات إدارية

---

## 🌐 Endpoints

### 🏠 الصفحات العامة (Public)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/` | no | - | الصفحة الرئيسية |
| GET | `/products/` | no | - | قائمة المنتجات |
| GET | `/product/<slug>/` | no | - | تفاصيل منتج |
| GET | `/category/<slug>/` | no | - | منتجات التصنيف |

### 👤 الحسابات (Accounts)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET, POST | `/accounts/register/` | no | - | تسجيل مستخدم جديد |
| GET, POST | `/accounts/login/` | no | - | تسجيل الدخول |
| POST | `/accounts/logout/` | yes | user | تسجيل الخروج |
| GET, POST | `/accounts/profile/` | yes | user | عرض/تعديل الملف الشخصي |
| GET, POST | `/accounts/profile/edit/` | yes | user | تعديل الملف الشخصي |
| GET, POST | `/accounts/change-password/` | yes | user | تغيير كلمة المرور |
| GET | `/accounts/addresses/` | yes | user | عرض العناوين |
| GET, POST | `/accounts/address/add/` | yes | user | إضافة عنوان |
| POST | `/accounts/address/<uuid>/delete/` | yes | user | حذف عنوان |
| POST | `/accounts/address/<uuid>/set-default/` | yes | user | تعيين عنوان افتراضي |
| GET, POST | `/accounts/password-reset/` | no | - | طلب إعادة تعيين كلمة المرور |
| GET | `/accounts/password-reset/done/` | no | - | تأكيد إرسال البريد |
| GET, POST | `/accounts/password-reset/<uidb64>/<token>/` | no | - | تأكيد إعادة التعيين |
| GET | `/accounts/password-reset/complete/` | no | - | اكتمال إعادة التعيين |

### 🛒 السلة (Cart)               

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/cart/` | no | - | عرض السلة |
| POST | `/cart/add/` | no | - | إضافة منتج للسلة (JSON) |
| POST | `/cart/update/` | no | - | تحديث كمية (JSON) |
| POST | `/cart/remove/` | no | - | إزالة منتج (JSON) |
| POST | `/cart/clear/` | no | - | تفريغ السلة (JSON) |
| GET | `/cart/wishlist/` | yes | user | قائمة الأمنيات |
| POST | `/cart/wishlist/add/` | yes | user | إضافة للأمنيات (JSON) |
| POST | `/cart/wishlist/remove/` | yes | user | إزالة من الأمنيات (JSON) |

### 📦 الطلبات (Orders)

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET, POST | `/orders/checkout/` | yes | user | صفحة الدفع |
| POST | `/orders/place/` | yes | user | إنشاء الطلب (JSON) |
| GET | `/orders/` | yes | user | قائمة طلبات المستخدم |
| GET | `/orders/<uuid>/` | yes | user | تفاصيل الطلب |
| POST | `/orders/<uuid>/cancel/` | yes | user | إلغاء الطلب (JSON) |
| POST | `/orders/coupon/apply/` | yes | user | تطبيق كوبون (JSON) |
| POST | `/orders/coupon/remove/` | yes | user | إزالة كوبون (JSON) |

### 🖥️ المنتجات - إضافات

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| POST | `/product/<slug>/review/` | yes | user | إضافة تقييم (JSON) |

### 📊 لوحة التحكم (Dashboard) - Staff Only

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET | `/dashboard/` | yes | staff | الصفحة الرئيسية |
| GET | `/dashboard/products/` | yes | staff | قائمة المنتجات |
| GET, POST | `/dashboard/products/add/` | yes | staff | إضافة منتج |
| GET, POST | `/dashboard/products/<uuid>/edit/` | yes | staff | تعديل منتج |
| POST | `/dashboard/products/<uuid>/delete/` | yes | staff | حذف منتج |
| GET | `/dashboard/categories/` | yes | staff | قائمة التصنيفات |
| GET, POST | `/dashboard/categories/add/` | yes | staff | إضافة تصنيف |
| GET, POST | `/dashboard/categories/<int>/edit/` | yes | staff | تعديل تصنيف |
| POST | `/dashboard/categories/<int>/delete/` | yes | staff | حذف تصنيف |
| GET | `/dashboard/orders/` | yes | staff | قائمة الطلبات |
| GET | `/dashboard/orders/<uuid>/` | yes | staff | تفاصيل الطلب |
| POST | `/dashboard/orders/<uuid>/update-status/` | yes | staff | تحديث حالة الطلب |
| GET | `/dashboard/users/` | yes | staff | قائمة المستخدمين |
| GET | `/dashboard/users/<uuid>/` | yes | staff | تفاصيل المستخدم |
| POST | `/dashboard/users/<uuid>/toggle-status/` | yes | staff | تفعيل/تعطيل المستخدم |
| GET | `/dashboard/reports/` | yes | staff | صفحة التقارير |
| GET | `/dashboard/reports/sales/` | yes | staff | تقرير المبيعات |

### ⚙️ Django Admin

| Method | Path | Auth | Role | Description |
|--------|------|------|------|-------------|
| GET, POST | `/admin/` | yes | superuser | لوحة تحكم Django الافتراضية |

---

## 📝 Notes - ملاحظات للفحص الأمني

### إعدادات خاصة

1. **Rate Limiting:**
   - تسجيل الدخول: 10 محاولات / 30 دقيقة لكل IP
   - التسجيل: 5 محاولات / ساعة لكل IP
   - إضافة للسلة: 30 عملية / دقيقة لكل IP
   - إنشاء طلب: 1 طلب / دقيقة لكل مستخدم
   - إضافة تقييم: 1 تقييم / 5 دقائق لكل مستخدم

2. **Account Lockout:**
   - 5 محاولات فاشلة = قفل الحساب لمدة 30 دقيقة

3. **CSRF Protection:**
   - جميع طلبات POST محمية بـ CSRF tokens

4. **تشفير كلمات المرور:**
   - Argon2 (الخوارزمية الأقوى)

5. **متطلبات كلمة المرور:**
   - الحد الأدنى: 8 أحرف
   - لا تشابه مع بيانات المستخدم
   - ليست من كلمات المرور الشائعة
   - ليست رقمية بالكامل

### Headers الأمنية

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
```

### إعدادات الجلسة

```
SESSION_COOKIE_HTTPONLY: True
SESSION_COOKIE_SAMESITE: Lax
CSRF_COOKIE_SAMESITE: Lax
```

### بيانات JSON للاختبار

#### إضافة منتج للسلة
```json
POST /cart/add/
{
    "product_id": "uuid-here",
    "quantity": 1
}
```

#### تحديث كمية
```json
POST /cart/update/
{
    "item_id": 1,
    "quantity": 2
}
```

#### إنشاء طلب
```json
POST /orders/place/
{
    "shipping_address_id": "uuid-here",
    "billing_address_id": "uuid-here",
    "payment_method": "cod|credit_card|paypal|bank_transfer",
    "notes": "ملاحظات اختيارية"
}
```

#### تطبيق كوبون
```json
POST /orders/coupon/apply/
{
    "code": "DISCOUNT20"
}
```

### تشغيل التطبيق للفحص

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد قاعدة البيانات
python manage.py migrate

# إنشاء بيانات تجريبية
python manage.py create_sample_data

# إنشاء مستخدم مسؤول
python manage.py createsuperuser

# تشغيل الخادم
python manage.py runserver
```

---

## 🔍 ملخص للفحص السريع

| الفئة | عدد الـ Endpoints |
|-------|-------------------|
| Public (بدون تسجيل دخول) | 12 |
| User (مستخدم عادي) | 18 |
| Staff (موظف) | 16 |
| Total | 46 |
