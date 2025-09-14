from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Category(models.Model):
    """Модель категорії товарів"""
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Зображення")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товару"""
    name = models.CharField(max_length=200, verbose_name="Назва товару")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Опис")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категорія")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Ціна зі знижкою")
    stock = models.PositiveIntegerField(default=0, verbose_name="Кількість на складі")
    image = models.ImageField(upload_to='products/', verbose_name="Основне зображення")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендований")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        """Повертає фінальну ціну (з урахуванням знижки)"""
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percentage(self):
        """Повертає відсоток знижки"""
        if self.discount_price and self.discount_price < self.price:
            return int((self.price - self.discount_price) / self.price * 100)
        return 0


class ProductImage(models.Model):
    """Модель додаткових зображень товару"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Товар")
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Зображення")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="Альтернативний текст")
    is_main = models.BooleanField(default=False, verbose_name="Основне зображення")

    class Meta:
        verbose_name = "Зображення товару"
        verbose_name_plural = "Зображення товарів"

    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Зображення'}"


class Cart(models.Model):
    """Модель кошика"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Користувач")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Кошик"
        verbose_name_plural = "Кошики"

    def __str__(self):
        return f"Кошик користувача {self.user.username}"

    @property
    def total_items(self):
        """Повертає загальну кількість товарів в кошику"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Повертає загальну вартість кошика"""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Модель елемента кошика"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Кошик")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Кількість")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата додавання")

    class Meta:
        verbose_name = "Елемент кошика"
        verbose_name_plural = "Елементи кошика"
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        """Повертає загальну вартість елемента"""
        return self.product.final_price * self.quantity


class Order(models.Model):
    """Модель замовлення"""
    STATUS_CHOICES = [
        ('pending', 'Очікує підтвердження'),
        ('confirmed', 'Підтверджено'),
        ('processing', 'В обробці'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    order_number = models.CharField(max_length=20, unique=True, verbose_name="Номер замовлення")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальна сума")
    
    # Інформація про доставку
    shipping_address = models.TextField(verbose_name="Адреса доставки")
    shipping_city = models.CharField(max_length=100, verbose_name="Місто")
    shipping_zip_code = models.CharField(max_length=10, verbose_name="Поштовий індекс")
    shipping_phone = models.CharField(max_length=20, verbose_name="Телефон")
    
    # Додаткова інформація
    notes = models.TextField(blank=True, verbose_name="Примітки")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"
        ordering = ['-created_at']

    def __str__(self):
        return f"Замовлення #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Модель елемента замовлення"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Замовлення")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Кількість")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за одиницю")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Загальна ціна")

    class Meta:
        verbose_name = "Елемент замовлення"
        verbose_name_plural = "Елементи замовлення"

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.price * self.quantity
        super().save(*args, **kwargs)


class Review(models.Model):
    """Модель відгуків про товари"""
    RATING_CHOICES = [
        (1, '1 зірка'),
        (2, '2 зірки'),
        (3, '3 зірки'),
        (4, '4 зірки'),
        (5, '5 зірок'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    rating = models.PositiveIntegerField(choices=RATING_CHOICES, verbose_name="Рейтинг")
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    comment = models.TextField(verbose_name="Коментар")
    is_approved = models.BooleanField(default=False, verbose_name="Схвалено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']
        unique_together = ['product', 'user']

    def __str__(self):
        return f"{self.product.name} - {self.user.username} ({self.rating} зірок)"