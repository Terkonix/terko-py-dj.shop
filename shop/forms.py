from django import forms
from .models import Review, Order


class ReviewForm(forms.ModelForm):
    """Форма для відгуків про товари"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(choices=Review.RATING_CHOICES, attrs={
                'class': 'form-select'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок відгуку'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ваш відгук про товар...'
            })
        }
        labels = {
            'rating': 'Рейтинг',
            'title': 'Заголовок',
            'comment': 'Коментар'
        }


class CheckoutForm(forms.ModelForm):
    """Форма оформлення замовлення"""
    
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_zip_code', 'shipping_phone', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Введіть адресу доставки'
            }),
            'shipping_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Місто'
            }),
            'shipping_zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Поштовий індекс'
            }),
            'shipping_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер телефону'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Додаткові примітки (необов\'язково)'
            })
        }
        labels = {
            'shipping_address': 'Адреса доставки',
            'shipping_city': 'Місто',
            'shipping_zip_code': 'Поштовий індекс',
            'shipping_phone': 'Телефон',
            'notes': 'Примітки'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Робимо всі поля обов'язковими, крім notes
        self.fields['shipping_address'].required = True
        self.fields['shipping_city'].required = True
        self.fields['shipping_zip_code'].required = True
        self.fields['shipping_phone'].required = True
        self.fields['notes'].required = False


class SearchForm(forms.Form):
    """Форма пошуку товарів"""
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пошук товарів...',
            'name': 'q'
        })
    )
