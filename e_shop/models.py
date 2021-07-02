from django.conf import settings
from django.core import validators
from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    title = models.CharField(max_length=256, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.title


class ProductReview(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='ID автора отзыва')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='ID товара')
    review = models.TextField(verbose_name='Текст отзыва')

    mark = models.IntegerField(
        verbose_name='Оценка',
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(5),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отзыв к товару'
        verbose_name_plural = 'Отзывы к товарам'

    def __str__(self):
        return f'{self.author} - {self.product}'


class OrderStatusChoices(models.TextChoices):
    NEW = "NEW", "Новый"
    IN_PROGRESS = "IN_PROGRESS", "В работе"
    DONE = "DONE", "Закрыт"


class OrderPositions(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='ID товара')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='ID заказа')
    quantity = models.IntegerField(verbose_name='количество единиц товара')

    class Meta:
        verbose_name = 'Детализация заказа'
        verbose_name_plural = 'Детализации заказов'

    def __str__(self):
        return f'{self.order}'


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='ID пользователя')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='ID пользователя')
    positions = models.ManyToManyField(Product, through=OrderPositions)
    status = models.TextField(
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.NEW
    )
    sum = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма заказа')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.id} - {self.status}'


class ProductCollection(models.Model):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    selection = models.ManyToManyField(Product, verbose_name='элементы подборки')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подборка'
        verbose_name_plural = 'Подборки'

    def __str__(self):
        return self.title
