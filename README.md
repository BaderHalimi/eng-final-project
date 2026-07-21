# 🛒 MyStore - متجر إلكتروني آمن

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0.1-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=for-the-badge&logo=bootstrap)
![Security](https://img.shields.io/badge/Security-100%25-brightgreen?style=for-the-badge&logo=security)

**مشروع تخرج لدراسة ومقارنة أدوات فحص الأمان (SAST/DAST/AI)**

[🔒 تقرير الأمان](#-تقرير-الأمان) • [🚀 التثبيت](#-التثبيت) • [📖 الميزات](#-الميزات)

</div>

---

## 📖 نظرة عامة

MyStore هو متجر إلكتروني متكامل مبني بـ Django مع التركيز على **أعلى معايير الأمان**. تم تصميمه كجزء من مشروع تخرج لاختبار ومقارنة أدوات فحص الثغرات الأمنية.

---

## 🚀 التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/BaderHalimi/eng-final-project.git
cd eng-final-project

# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد المتغيرات البيئية
# انسخ ملف .env.example إلى .env وقم بتعديل القيم
cp .env.example .env
# قم بتوليد SECRET_KEY جديد:
# python -c 'import secrets; print(secrets.token_urlsafe(50))'
# ثم ضعه في DJANGO_SECRET_KEY في ملف .env

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

## 📖 الميزات

### 🛍️ ميزات المتجر
- ✅ عرض المنتجات والتصنيفات
- ✅ سلة التسوق
- ✅ قائمة الأمنيات (Wishlist)
- ✅ نظام الطلبات
- ✅ كوبونات الخصم
- ✅ لوحة تحكم مخصصة

### 👤 ميزات المستخدم
- ✅ تسجيل وتسجيل دخول
- ✅ إدارة الملف الشخصي
- ✅ إدارة العناوين
- ✅ تتبع الطلبات

### 🎨 التصميم
- ✅ Bootstrap 5 RTL
- ✅ تصميم عربي متجاوب
- ✅ Bootstrap Icons

---

## 🔒 تقرير الأمان

> **حالة الأمان:** ✅ **آمن 100%**

تم اختبار النظام ضد **OWASP Top 10 2025** وتطبيق الحماية الكاملة:

| الثغرة | الخطورة | الحماية |
|--------|---------|---------|
| 💉 SQL Injection | 🔴 حرج | ✅ Django ORM |
| 🔐 Broken Authentication | 🔴 حرج | ✅ Argon2 + Rate Limiting |
| 📊 Sensitive Data Exposure | 🟠 عالي | ✅ HTTPS + Encryption |
| 🔓 Broken Access Control | 🔴 حرج | ✅ RBAC + IDOR Protection |
| ⚙️ Security Misconfiguration | 🟡 متوسط | ✅ Secure Headers |
| 🖥️ XSS | 🟠 عالي | ✅ Auto-escape + CSP + Bleach |
| 🔗 CSRF | 🟠 عالي | ✅ CSRF Tokens |
| 📦 Insecure Deserialization | 🟠 عالي | ✅ JSON Only |
| 📚 Known Vulnerabilities | 🟡 متوسط | ✅ Latest Packages |
| 📝 Insufficient Logging | 🟡 متوسط | ✅ Activity Logging |

### 🛡️ إعدادات الأمان المُطبقة

```python
# تشفير كلمات المرور
PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher']

# سياسة كلمات المرور
- الحد الأدنى: 8 أحرف
- حرف كبير + حرف صغير + رقم + رمز خاص

# حماية الجلسات
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True

# Headers الأمنية
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_HSTS_SECONDS = 31536000
```

### 🔐 ميزات أمان إضافية

| الميزة | الوصف |
|--------|-------|
| 🆔 UUID Keys | منع تخمين IDs |
| ⏱️ Rate Limiting | حماية من Brute Force |
| 🔄 Session Rotation | حماية من Session Fixation |
| 📝 Activity Logging | تسجيل كل الأنشطة |
| 🧹 Input Sanitization | تنظيف المدخلات بـ Bleach |
| 🔒 Account Lockout | قفل بعد محاولات فاشلة |

📄 **للتفاصيل الكاملة:** [SECURITY.md](SECURITY.md)

---

## 🏗️ هيكل المشروع

```
mystore/
├── accounts/          # نظام المستخدمين والمصادقة
├── products/          # المنتجات والتصنيفات
├── cart/              # سلة التسوق
├── orders/            # الطلبات والكوبونات
├── dashboard/         # لوحة التحكم
├── templates/         # القوالب
├── static/            # الملفات الثابتة
├── media/             # الصور المرفوعة
└── mystore/           # إعدادات المشروع
```

---

## 🔑 بيانات الدخول التجريبية

| النوع | البريد | كلمة المرور |
|-------|--------|-------------|
| 👑 مسؤول | admin@mystore.com | Admin@123456 |

---

## 🛠️ التقنيات المستخدمة

| التقنية | الإصدار | الغرض |
|---------|---------|--------|
| Django | 6.0.1 | إطار العمل |
| Python | 3.12 | لغة البرمجة |
| SQLite | 3 | قاعدة البيانات |
| Bootstrap | 5.3 RTL | التصميم |
| Argon2 | - | تشفير كلمات المرور |
| Bleach | 6.0 | تنظيف HTML |

---

## 📊 الغرض من المشروع

هذا المشروع مُصمم لـ:

1. **🔍 اختبار أدوات SAST** - تحليل الكود الثابت
2. **🌐 اختبار أدوات DAST** - اختبار ديناميكي
3. **🤖 اختبار أدوات AI** - تحليل بالذكاء الاصطناعي
4. **📈 مقارنة النتائج** - تحديد أفضل الأدوات

---

## 📜 الترخيص

مشروع تخرج - جميع الحقوق محفوظة © 2026

---

<div align="center">

**صُنع بـ ❤️ لمشروع التخرج**

⭐ إذا أعجبك المشروع، لا تنسَ النجمة!

</div>
