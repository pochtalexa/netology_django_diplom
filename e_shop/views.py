from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Product, ProductReview, Order, ProductCollection
from .serializers import ProductSerializer, ProductReviewSerializer, OrderSerializer, ProductCollectionSerializer
from .filters import ProductFilter, ProductReviewFilter, OrderFilter
from .permissions import IsSelfReviewOrOrder, DenyAny


class ProductsViewSet(ModelViewSet):
    """
    + Создавать товары могут только админы.
    + Доступные действия: retrieve, list, create, update, destroy.
    + Смотреть могут все пользователи.
    + Должна быть возможность фильтровать товары по цене содержимому из названия / описания.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy', 'partial_update']:
            return [IsAdminUser()]
        elif self.action in ['retrieve', 'list']:
            return [AllowAny()]

        return [DenyAny()]


class ProductReviewViewSet(ModelViewSet):
    """
    + Доступные действия: retrieve, list, create, update, destroy.
    + Оставлять отзыв к товару могут только авторизованные пользователи. 1 пользователь не может оставлять более 1го отзыва.
    + Отзыв можно фильтровать по ID пользователя, дате создания и ID товара.
    + Пользователь может обновлять и удалять только свой собственный отзыв.
    """
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = ProductReviewFilter

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsSelfReviewOrOrder()]
        elif self.action in ['retrieve', 'list']:
            return [AllowAny()]

        return [DenyAny()]


class OrderViewSet(ModelViewSet):
    """
    + Доступные действия: retrieve, list, create, update, destroy.
    + Создавать заказы могут только авторизованные пользователи.
    + Админы могут получать все заказы,
    + остальное пользователи только свои.
    + Заказы можно фильтровать по статусу / общей сумме / дате создания / дате обновления
    + и продуктам из позиций.
    + Менять статус заказа могут только админы.
    """
    # queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend]
    filter_class = OrderFilter

    # def get_serializer_class(self):
    #     if self.action in ['update', 'partial_update']:
    #         return OrderUpdateSerializer
    #     else:
    #         return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(user=user.id)

    def get_permissions(self):
        if self.action in ['create']:
            return [IsAuthenticated()]
        elif self.action in ['list', 'retrieve']:
            # return [IsAdminUser()]
            return [AllowAny()]
        elif self.action in ['destroy', 'update', 'partial_update']:
            # return [IsSelfReviewOrOrder()]
            return [IsAdminUser()]

        return [DenyAny()]


class ProductCollectionViewSet(ModelViewSet):
    """
    + Доступные действия: retrieve, list, create, update, destroy
    + Создавать подборки могут только админы, остальные пользователи могут только их смотреть.
    """
    queryset = ProductCollection.objects.all()
    serializer_class = ProductCollectionSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        if self.action in ['retrieve', 'list']:
            return [AllowAny()]

        return [DenyAny()]







