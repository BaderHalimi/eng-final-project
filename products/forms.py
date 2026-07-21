
from django import forms
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from .models import Product, Review, Category
import bleach


class SecureCharField(forms.CharField):
    
    def clean(self, value):
        value = super().clean(value)
        if value:
            value = bleach.clean(
                value, 
                tags=[], 
                attributes={},
                strip=True
            )
        return value


class SecureTextarea(forms.CharField):
    
    widget = forms.Textarea
    
    def clean(self, value):
        value = super().clean(value)
        if value:
            allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
            value = bleach.clean(
                value, 
                tags=allowed_tags, 
                attributes={},
                strip=True
            )
        return value


class ProductSearchForm(forms.Form):
    
    q = SecureCharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'ابحث عن منتج...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        empty_label='جميع التصنيفات'
    )
    min_price = forms.DecimalField(
        min_value=0,
        max_value=999999,
        required=False
    )
    max_price = forms.DecimalField(
        min_value=0,
        max_value=999999,
        required=False
    )
    sort = forms.ChoiceField(
        choices=[
            ('newest', 'الأحدث'),
            ('price_low', 'السعر: من الأقل'),
            ('price_high', 'السعر: من الأعلى'),
            ('name', 'الاسم'),
        ],
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')
        
        if min_price and max_price and min_price > max_price:
            raise ValidationError('الحد الأدنى للسعر يجب أن يكون أقل من الحد الأقصى')
        
        return cleaned_data


class ReviewForm(forms.ModelForm):
    
    title = SecureCharField(max_length=100)
    comment = SecureTextarea(max_length=1000)
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise ValidationError('التقييم يجب أن يكون بين 1 و 5')
        return rating


class ProductImageForm(forms.Form):
    
    image = forms.ImageField(
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp'])
        ]
    )
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('حجم الصورة يجب أن لا يتجاوز 5MB')
            
            import imghdr
            image_type = imghdr.what(image)
            if image_type not in ['jpeg', 'png', 'gif', 'webp']:
                raise ValidationError('نوع الملف غير مدعوم')
        
        return image

