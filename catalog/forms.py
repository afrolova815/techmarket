from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
import re
from .models import Product, Category, Brand, Tag


class ProductForm(forms.ModelForm):
    name = forms.CharField(
        min_length=2,
        max_length=200,
        label="Название",
        widget=forms.TextInput(attrs={'class': 'select'}),
    )
    slug = forms.SlugField(
        max_length=200,
        label="URL",
        validators=[MinLengthValidator(5), MaxLengthValidator(100)],
        widget=forms.TextInput(attrs={'class': 'select'}),
    )
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label="Цена",
        widget=forms.NumberInput(attrs={'class': 'select', 'step': '0.01', 'min': '0.01'}),
    )
    old_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Старая цена",
        widget=forms.NumberInput(attrs={'class': 'select', 'step': '0.01', 'min': '0'}),
    )
    quantity = forms.IntegerField(
        min_value=1,
        label="Количество на складе",
        widget=forms.NumberInput(attrs={'class': 'select', 'min': '1'}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория",
        widget=forms.Select(attrs={"class": "select"}),
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        empty_label="Бренд не выбран",
        label="Бренд",
        widget=forms.Select(attrs={"class": "select"}),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.SelectMultiple(attrs={"class": "select"}),
    )
    image = forms.ImageField(
        required=False,
        label="Изображение",
        widget=forms.ClearableFileInput(attrs={'class': 'select'}),
    )

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'price', 'old_price',
            'quantity', 'is_available', 'category', 'brand', 'tags', 'product_type'
            , 'image'
        ]
        labels = {
            'description': 'Описание',
            'is_available': 'Доступен',
            'product_type': 'Тип товара',
        }
        widgets = {
            'description': forms.Textarea(attrs={'class': 'select', 'rows': 5, 'cols': 50}),
            'is_available': forms.CheckboxInput(),
            'product_type': forms.Select(attrs={'class': 'select'}),
        }

    def clean_name(self):
        value = self.cleaned_data.get('name', '')
        if not value or not value.strip():
            raise forms.ValidationError("Поле не должно быть пустым")
        if not re.match(r'^[A-Za-zА-Яа-яЁё0-9 -]+$', value):
            raise forms.ValidationError("Недопустимые символы")
        return value
