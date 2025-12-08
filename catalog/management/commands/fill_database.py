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
            {"name": "Смартфоны", "slug": "smartphones", "description": "Мобильные телефоны и смартфоны"},
            {"name": "Ноутбуки", "slug": "laptops", "description": "Портативные компьютеры"},
            {"name": "Планшеты", "slug": "tablets", "description": "Планшетные компьютеры"},
            {"name": "Наушники", "slug": "headphones", "description": "Беспроводные и проводные наушники"},
            {"name": "Умные часы", "slug": "smartwatches", "description": "Наручные умные часы и трекеры"},
        ]

        for cat_data in categories_data:
            name = cat_data["name"]
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    "slug": cat_data["slug"],
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
            {"name": "Sony", "description": "Японская компания"},
            {"name": "Google", "description": "Американская компания"},
            {"name": "Lenovo", "description": "Китайская компания"},
            {"name": "Dell", "description": "Американская компания"},
            {"name": "HP", "description": "Американская компания"},
            {"name": "Microsoft", "description": "Американская компания"},
            {"name": "Acer", "description": "Тайваньская компания"},
            {"name": "MSI", "description": "Тайваньская компания"},
            {"name": "Huawei", "description": "Китайская компания"},
            {"name": "Amazon", "description": "Американская компания"},
            {"name": "Beats", "description": "Американский бренд аудиотехники"},
            {"name": "JBL", "description": "Американский бренд аудиотехники"},
            {"name": "Sennheiser", "description": "Немецкая компания"},
            {"name": "Razer", "description": "Американская компания"},
            {"name": "Garmin", "description": "Американская компания"},
            {"name": "Amazfit", "description": "Китайская компания"},
            {"name": "Suunto", "description": "Финская компания"},
            {"name": "Polar", "description": "Финская компания"},
            {"name": "Bose", "description": "Американская компания"},
            {"name": "OnePlus", "description": "Китайская компания"},
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
            {"name": "iPhone 15 Pro 128GB", "description": "Флагманский смартфон Apple с процессором A17 Pro", "price": 99990, "old_price": 109990, "quantity": 45, "category_slug": "smartphones", "brand_slug": "apple"},
            {"name": "iPhone 15 Pro 256GB", "description": "Флагманский смартфон Apple с процессором A17 Pro", "price": 109990, "old_price": 119990, "quantity": 35, "category_slug": "smartphones", "brand_slug": "apple"},
            {"name": "iPhone 15 128GB", "description": "Современный смартфон Apple", "price": 79990, "old_price": 84990, "quantity": 40, "category_slug": "smartphones", "brand_slug": "apple"},
            {"name": "Samsung Galaxy S24 256GB", "description": "Мощный Android-смартфон с камерой 200 МП", "price": 89990, "quantity": 38, "category_slug": "smartphones", "brand_slug": "samsung"},
            {"name": "Samsung Galaxy S24 Ultra 512GB", "description": "Флагман Samsung с продвинутой камерой", "price": 129990, "quantity": 22, "category_slug": "smartphones", "brand_slug": "samsung"},
            {"name": "Google Pixel 9 128GB", "description": "Чистый Android и топовая камера", "price": 89990, "quantity": 30, "category_slug": "smartphones", "brand_slug": "google"},
            {"name": "Xiaomi 14 256GB", "description": "Флагман Xiaomi", "price": 69990, "quantity": 50, "category_slug": "smartphones", "brand_slug": "xiaomi"},
            {"name": "Redmi Note 13 Pro 8/256", "description": "Доступный смартфон с отличной камерой", "price": 34990, "quantity": 50, "category_slug": "smartphones", "brand_slug": "xiaomi"},
            {"name": "OnePlus 12 256GB", "description": "Флагман OnePlus с быстрой зарядкой", "price": 89990, "quantity": 28, "category_slug": "smartphones", "brand_slug": "oneplus"},
            {"name": "Sony Xperia 1 VI 256GB", "description": "Премиальный смартфон с OLED-экраном", "price": 109990, "quantity": 15, "category_slug": "smartphones", "brand_slug": "sony"},

            {"name": "MacBook Air 13 M2 256GB", "description": "Легкий и мощный ноутбук от Apple", "price": 129990, "old_price": 139990, "quantity": 42, "category_slug": "laptops", "brand_slug": "apple"},
            {"name": "MacBook Pro 14 M3 Pro 512GB", "description": "Профессиональный ноутбук Apple", "price": 229990, "quantity": 18, "category_slug": "laptops", "brand_slug": "apple"},
            {"name": "Asus ROG Zephyrus G16", "description": "Игровой ноутбук для требовательных пользователей", "price": 189990, "quantity": 25, "category_slug": "laptops", "brand_slug": "asus"},
            {"name": "Dell XPS 13 9320", "description": "Компактный премиальный ультрабук", "price": 149990, "quantity": 20, "category_slug": "laptops", "brand_slug": "dell"},
            {"name": "Lenovo ThinkPad X1 Carbon Gen11", "description": "Бизнес-ноутбук с прочным корпусом", "price": 179990, "quantity": 12, "category_slug": "laptops", "brand_slug": "lenovo"},
            {"name": "HP Spectre x360 14", "description": "Трансформер с OLED-экраном", "price": 139990, "quantity": 27, "category_slug": "laptops", "brand_slug": "hp"},
            {"name": "Microsoft Surface Laptop 7", "description": "Тонкий ноутбук на платформе ARM", "price": 159990, "quantity": 16, "category_slug": "laptops", "brand_slug": "microsoft"},
            {"name": "Acer Predator Helios 16", "description": "Игровой ноутбук с мощной графикой", "price": 169990, "quantity": 9, "category_slug": "laptops", "brand_slug": "acer"},
            {"name": "MSI Stealth 15", "description": "Тонкий игровой ноутбук", "price": 159990, "quantity": 11, "category_slug": "laptops", "brand_slug": "msi"},
            {"name": "Huawei MateBook X Pro", "description": "Премиальный ноутбук Huawei", "price": 129990, "quantity": 13, "category_slug": "laptops", "brand_slug": "huawei"},

            {"name": "iPad Pro 11 M4 256GB", "description": "Профессиональный планшет Apple", "price": 119990, "quantity": 26, "category_slug": "tablets", "brand_slug": "apple"},
            {"name": "iPad Air M2 128GB", "description": "Легкий планшет Apple", "price": 94990, "quantity": 30, "category_slug": "tablets", "brand_slug": "apple"},
            {"name": "Samsung Galaxy Tab S9 256GB", "description": "Планшет Samsung с AMOLED", "price": 99990, "quantity": 22, "category_slug": "tablets", "brand_slug": "samsung"},
            {"name": "Samsung Galaxy Tab S9 FE 128GB", "description": "Доступный планшет Samsung", "price": 54990, "quantity": 35, "category_slug": "tablets", "brand_slug": "samsung"},
            {"name": "Xiaomi Pad 6 128GB", "description": "Планшет с высоким разрешением экрана", "price": 34990, "quantity": 45, "category_slug": "tablets", "brand_slug": "xiaomi"},
            {"name": "Lenovo Tab P12 256GB", "description": "Большой планшет Lenovo", "price": 44990, "quantity": 33, "category_slug": "tablets", "brand_slug": "lenovo"},
            {"name": "Huawei MatePad 11.5", "description": "Планшет Huawei для работы и учебы", "price": 39990, "quantity": 28, "category_slug": "tablets", "brand_slug": "huawei"},
            {"name": "Microsoft Surface Pro 10", "description": "Планшет 2-в-1", "price": 189990, "quantity": 10, "category_slug": "tablets", "brand_slug": "microsoft"},
            {"name": "Amazon Fire HD 10 (2023)", "description": "Доступный планшет для мультимедиа", "price": 14990, "quantity": 50, "category_slug": "tablets", "brand_slug": "amazon"},
            {"name": "Google Pixel Tablet 128GB", "description": "Планшет Google с док-станцией", "price": 69990, "quantity": 20, "category_slug": "tablets", "brand_slug": "google"},

            {"name": "AirPods Pro 2", "description": "Наушники с активным шумоподавлением", "price": 29990, "quantity": 50, "category_slug": "headphones", "brand_slug": "apple"},
            {"name": "Sony WH-1000XM5", "description": "Флагманские накладные наушники", "price": 39990, "quantity": 40, "category_slug": "headphones", "brand_slug": "sony"},
            {"name": "Bose QuietComfort Ultra", "description": "Премиальные наушники с ANC", "price": 34990, "quantity": 35, "category_slug": "headphones", "brand_slug": "bose"},
            {"name": "Beats Studio Pro", "description": "Стильные накладные наушники", "price": 32990, "quantity": 25, "category_slug": "headphones", "brand_slug": "beats"},
            {"name": "Samsung Galaxy Buds3 Pro", "description": "Компактные TWS-наушники", "price": 22990, "quantity": 45, "category_slug": "headphones", "brand_slug": "samsung"},
            {"name": "JBL Tune 760NC", "description": "Бюджетные наушники с ANC", "price": 11990, "quantity": 50, "category_slug": "headphones", "brand_slug": "jbl"},
            {"name": "Sennheiser Momentum 4", "description": "Премиальные наушники с высоким качеством звука", "price": 39990, "quantity": 18, "category_slug": "headphones", "brand_slug": "sennheiser"},
            {"name": "Xiaomi Buds 4 Pro", "description": "Флагманские TWS-наушники Xiaomi", "price": 15990, "quantity": 40, "category_slug": "headphones", "brand_slug": "xiaomi"},
            {"name": "Huawei FreeBuds Pro 3", "description": "TWS-наушники с хорошим ANC", "price": 21990, "quantity": 38, "category_slug": "headphones", "brand_slug": "huawei"},
            {"name": "Razer BlackShark V2 Pro", "description": "Игровая гарнитура", "price": 19990, "quantity": 16, "category_slug": "headphones", "brand_slug": "razer"},

            {"name": "Apple Watch Series 10 GPS 45mm", "description": "Умные часы Apple", "price": 49990, "quantity": 50, "category_slug": "smartwatches", "brand_slug": "apple"},
            {"name": "Apple Watch Ultra 2", "description": "Премиальные часы Apple для спорта", "price": 99990, "quantity": 14, "category_slug": "smartwatches", "brand_slug": "apple"},
            {"name": "Samsung Galaxy Watch7 44mm", "description": "Умные часы на Wear OS", "price": 29990, "quantity": 40, "category_slug": "smartwatches", "brand_slug": "samsung"},
            {"name": "Garmin Fenix 8 Sapphire", "description": "Профессиональные часы для спорта", "price": 89990, "quantity": 12, "category_slug": "smartwatches", "brand_slug": "garmin"},
            {"name": "Huawei Watch GT 5", "description": "Автономные смарт-часы Huawei", "price": 24990, "quantity": 33, "category_slug": "smartwatches", "brand_slug": "huawei"},
            {"name": "Google Pixel Watch 3", "description": "Часы Google на Wear OS", "price": 34990, "quantity": 28, "category_slug": "smartwatches", "brand_slug": "google"},
            {"name": "Amazfit GTR 4", "description": "Легкие фитнес-часы", "price": 19990, "quantity": 37, "category_slug": "smartwatches", "brand_slug": "amazfit"},
            {"name": "Xiaomi Watch 2 Pro", "description": "Смарт-часы Xiaomi", "price": 22990, "quantity": 34, "category_slug": "smartwatches", "brand_slug": "xiaomi"},
            {"name": "Suunto Race", "description": "Часы для бега и триатлона", "price": 54990, "quantity": 9, "category_slug": "smartwatches", "brand_slug": "suunto"},
            {"name": "Polar Vantage V3", "description": "Профессиональные спортивные часы", "price": 69990, "quantity": 7, "category_slug": "smartwatches", "brand_slug": "polar"},
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
        order1 = Order.objects.get_or_create(
            code="ORD-0001", defaults={"status": Order.Status.NEW}
        )[0]
        for product in Product.objects.all()[:5]:
            OrderItem.objects.get_or_create(
                order=order1,
                product=product,
                defaults={"quantity": 1, "price": product.price},
            )

        order2 = Order.objects.get_or_create(
            code="ORD-0002", defaults={"status": Order.Status.PROCESSING}
        )[0]
        for product in Product.objects.all()[5:10]:
            OrderItem.objects.get_or_create(
                order=order2,
                product=product,
                defaults={"quantity": 2, "price": product.price},
            )

        order3 = Order.objects.get_or_create(
            code="ORD-0003", defaults={"status": Order.Status.COMPLETED}
        )[0]
        for product in Product.objects.all()[10:15]:
            OrderItem.objects.get_or_create(
                order=order3,
                product=product,
                defaults={"quantity": 1, "price": product.price},
            )

        self.stdout.write(
            self.style.SUCCESS(
                "База данных успешно заполнена: категории, бренды, товары, теги, характеристики, заказы"
            )
        )
