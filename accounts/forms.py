"""
Accounts Forms - SECURE VERSION
نماذج المستخدمين الآمنة
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
import bleach

User = get_user_model()


class SecureCharField(forms.CharField):
    """حقل نصي آمن"""
    def clean(self, value):
        value = super().clean(value)
        if value:
            value = bleach.clean(value, tags=[], attributes={}, strip=True)
        return value


class SecureRegistrationForm(UserCreationForm):
    """
    نموذج التسجيل الآمن
    أمان:
    - التحقق من قوة كلمة المرور
    - تنظيف المدخلات
    - التحقق من البريد الإلكتروني
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email'
        })
    )
    username = SecureCharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='اسم المستخدم يمكن أن يحتوي فقط على حروف وأرقام و @/./+/-/_'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'autocomplete': 'username'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError('هذا البريد الإلكتروني مسجل مسبقاً')
        return email

    def clean_password1(self):
        """
        التحقق من قوة كلمة المرور
        أمان: فرض سياسة كلمات مرور قوية
        """
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على حرف كبير')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على حرف صغير')
        
        if not re.search(r'\d', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على رقم')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على رمز خاص')
        

        common_passwords = ['password123', 'qwerty123', '123456789']
        if password.lower() in common_passwords:
            raise ValidationError('كلمة المرور ضعيفة جداً')
        
        return password


class SecureLoginForm(AuthenticationForm):
    """
    نموذج تسجيل الدخول الآمن
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'autocomplete': 'email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    remember_me = forms.BooleanField(required=False)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username.lower() if username else username


class SecurePasswordChangeForm(PasswordChangeForm):
    """نموذج تغيير كلمة المرور الآمن"""
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password'
        })
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        old_password = self.cleaned_data.get('old_password')
        

        if len(password) < 8:
            raise ValidationError('كلمة المرور يجب أن تكون 8 أحرف على الأقل')
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على حرف كبير')
        
        if not re.search(r'[a-z]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على حرف صغير')
        
        if not re.search(r'\d', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على رقم')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('كلمة المرور يجب أن تحتوي على رمز خاص')
        

        if password == old_password:
            raise ValidationError('كلمة المرور الجديدة يجب أن تكون مختلفة عن القديمة')
        
        return password


class ProfileUpdateForm(forms.ModelForm):
    """نموذج تحديث الملف الشخصي"""
    first_name = SecureCharField(max_length=30, required=False)
    last_name = SecureCharField(max_length=30, required=False)
    phone = forms.CharField(
        max_length=17,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="رقم الهاتف يجب أن يكون بالصيغة: '+999999999'"
            )
        ]
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')


class AddressForm(forms.Form):
    """نموذج العنوان"""
    full_name = SecureCharField(max_length=100)
    address_line1 = SecureCharField(max_length=255)
    address_line2 = SecureCharField(max_length=255, required=False)
    city = SecureCharField(max_length=100)
    state = SecureCharField(max_length=100)
    postal_code = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^[\d-]+$',
                message='الرمز البريدي غير صالح'
            )
        ]
    )
    country = SecureCharField(max_length=100)
    phone = forms.CharField(max_length=17, required=False)
    is_default = forms.BooleanField(required=False)
