from django.core.management.base import BaseCommand
from django.utils.text import slugify
from catalog.models import (
    Brand,
    Category,
    Order,
    OrderItem,
    Product,
    ProductDetail,
    Tag,
)


class Command(BaseCommand):
    help = "Заполнение базы данных тестовыми данными"

    def handle(self, *args, **kwargs):
        self.stdout.write("Начало заполнения базы данных...")

        # Создание категорий
        categories_data = [
            {"name": "Смартфоны", "description": "Мобильные телефоны и смартфоны"},
            {"name": "Ноутбуки", "description": "Портативные компьютеры"},
            {"name": "Планшеты", "description": "Планшетные компьютеры"},
            {"name": "Наушники", "description": "Беспроводные и проводные наушники"},
        ]

        for cat_data in categories_data:
            name = cat_data["name"]
            slug = slugify(name)
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slug,
                    "description": cat_data["description"],
                }
            )
            if created:
                self.stdout.write(f"Создана категория: {name}")

        # Создание брендов
        brands_data = [
            {"name": "Apple", "description": "Американская корпорация"},
            {"name": "Samsung", "description": "Южнокорейская компания"},
            {"name": "Xiaomi", "description": "Китайская компания"},
            {"name": "Asus", "description": "Тайваньская компания"},
        ]

        for brand_data in brands_data:
            name = brand_data["name"]
            slug = slugify(name)
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={
                    "slug": slug,
                    "description": brand_data["description"],
                }
            )
            if created:
                self.stdout.write(f"Создан бренд: {name}")

        # Создание товаров
        products_data = [
            {
                "name": "iPhone 15 Pro",
                "description": "Флагманский смартфон Apple с процессором A17 Pro",
                "price": 99990,
                "old_price": 109990,
                "quantity": 15,
                "category_slug": "smartphones",
                "brand_slug": "apple",
            },
            {
                "name": "Samsung Galaxy S24",
                "description": "Мощный Android-смартфон с камерой 200 МП",
                "price": 79990,
                "quantity": 20,
                "category_slug": "smartphones",
                "brand_slug": "samsung",
            },
            {
                "name": "MacBook Air M2",
                "description": "Легкий и мощный ноутбук от Apple",
                "price": 129990,
                "old_price": 139990,
                "quantity": 8,
                "category_slug": "laptops",
                "brand_slug": "apple",
            },
            {
                "name": "Xiaomi Pad 6",
                "description": "Планшет с высоким разрешением экрана",
                "price": 34990,
                "quantity": 12,
                "category_slug": "tablets",
                "brand_slug": "xiaomi",
            },
            {
                "name": "Asus ROG Zephyrus",
                "description": "Игровой ноутбук для требовательных пользователей",
                "price": 189990,
                "quantity": 5,
                "category_slug": "laptops",
                "brand_slug": "asus",
            }
        ]

        for product_data in products_data:
            name = product_data["name"]
            slug = slugify(name)

            try:
                category = Category.objects.get(slug=product_data["category_slug"])\
                
                brand = Brand.objects.get(slug=product_data["brand_slug"])

                product, created = Product.objects.get_or_create(
                    name=name,
                    defaults={
                        "slug": slug,
                        "description": product_data["description"],
                        "price": product_data["price"],
                        "old_price": product_data.get("old_price"),
                        "quantity": product_data["quantity"],
                        "category": category,
                        "brand": brand,
                        "is_available": product_data["quantity"] > 0,
                    }
                )

                if created:
                    self.stdout.write(f"Создан товар: {name}")
                else:
                    self.stdout.write(f"Товар уже существует: {name}")

            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Категория не найдена: {product_data['category_slug']}"
                    )
                )
            except Brand.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"Бренд не найден: {product_data['brand_slug']}"
                    )
                )

        # Теги
        tags_data = ["Хит", "Новинка", "Распродажа", "Игровой", "Премиум"]
        for t in tags_data:
            slug = slugify(t)
            Tag.objects.get_or_create(slug=slug, defaults={"name": t})

        # Присвоение тегов и характеристик
        for product in Product.objects.all():
            ProductDetail.objects.get_or_create(
                product=product,
                defaults={
                    "sku": f"SKU-{product.id:05d}",
                    "warranty_months": 12,
                    "specs": "Стандартные характеристики",
                }
            )
            for tag in Tag.objects.order_by('?')[:2]:
                product.tags.add(tag)
        # Гарантированно назначаем тег "Хит" всем товарам для демонстрации
        try:
            hit_tag = Tag.objects.get(slug=slugify("Хит"))
            for product in Product.objects.all():
                product.tags.add(hit_tag)
        except Tag.DoesNotExist:
            pass

        # Пример заказов
        order = Order.objects.get_or_create(
            code="ORD-0001", defaults={"status": Order.Status.NEW}
        )[0]
        for product in Product.objects.all()[:3]:
            OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={"quantity": 1, "price": product.price},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "База данных успешно заполнена: категории, бренды, товары, теги, характеристики, заказы"
            )
        )
