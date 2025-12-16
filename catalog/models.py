from django.db import models
from django.db.models import Q
from django.urls import reverse
import os
import uuid


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=60, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'category_slug': self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def published(self):
        return self.filter(status=Product.Status.PUBLISHED, is_available=True)

    def available(self):
        return self.filter(is_available=True)

    def with_discount(self):
        return self.filter(old_price__isnull=False, old_price__gt=models.F('price'))

class AdvancedProductManager(models.Manager):
    def get_expensive_products(self, min_price=50000):
        return self.filter(price__gte=min_price)
    
    def get_products_by_status(self, status):
        return self.filter(status=status)
    
    def get_products_in_price_range(self, min_price, max_price):
        return self.filter(price__gte=min_price, price__lte=max_price)
    
    def search_products(self, query):
        return self.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query)
        )


class Product(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    quantity = models.IntegerField(default=0, verbose_name="Количество на складе")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name="Категория")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, verbose_name="Бренд")
    is_available = models.BooleanField(default=True, verbose_name="Доступен")
    status = models.IntegerField(choices=Status.choices, default=Status.PUBLISHED, verbose_name="Статус")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated = models.DateTimeField(auto_now=True, verbose_name="Обновлен")
    objects = ProductManager()
    advanced = AdvancedProductManager()
    tags = models.ManyToManyField('Tag', related_name='products', blank=True, verbose_name="Теги")
    def product_image_upload_to(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        return f'products/{uuid.uuid4().hex}{ext}'
    image = models.ImageField(upload_to=product_image_upload_to, blank=True, null=True, verbose_name="Изображение")

    class ProductType(models.TextChoices):
        PHYSICAL = 'physical', 'Физический товар'
        DIGITAL = 'digital', 'Цифровой товар'
        SERVICE = 'service', 'Услуга'
    
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.PHYSICAL,
        verbose_name="Тип товара"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_slug': self.slug})

    @property
    def has_discount(self):
        return self.old_price and self.old_price > self.price


class ProductDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='details', verbose_name="Товар")
    sku = models.CharField(max_length=100, verbose_name="Артикул")
    warranty_months = models.IntegerField(default=12, verbose_name="Гарантия (мес)")
    specs = models.TextField(blank=True, verbose_name="Характеристики")

    class Meta:
        verbose_name = "Характеристики товара"
        verbose_name_plural = "Характеристики товара"

    def __str__(self):
        return f"Характеристики: {self.product.name}"


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        PROCESSING = 'processing', 'В обработке'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    code = models.CharField(max_length=20, unique=True, verbose_name="Код заказа")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Статус")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders', verbose_name="Товары")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created']

    def __str__(self):
        return self.code


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items', verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.order.code}: {self.product.name} x{self.quantity}"

