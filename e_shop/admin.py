from django.contrib import admin
from .models import Product, ProductReview, Order, ProductCollection, OrderPositions
from django.db import models


class ProductCollectionInLine(admin.TabularInline):
    model = ProductCollection.selection.through
    extra = 1


class OrderPositionsInLine(admin.TabularInline):
    model = OrderPositions
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']

    # inlines = [
    #     ProductCollectionInLine,
    #     OrderPositionsInLine
    # ]
    #
    # readonly_fields = ('created_at', 'updated_at')
    pass


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    inlines = [
        ProductCollectionInLine
    ]

    exclude = ('selection', )


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'get_product_sum']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(product_sum=models.Sum('orderpositions__quantity'))

        return qs

    def get_product_sum(self, obj):
        return obj.product_sum

    get_product_sum.admin_order_field = 'product_sum'
    get_product_sum.short_description = 'количество товаров'





    inlines = [
        OrderPositionsInLine
    ]


# @admin.register(OrderPositions)
# class OrderPositionsAdmin(admin.ModelAdmin):
#     pass
