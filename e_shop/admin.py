from django.contrib import admin
from .models import Product, ProductReview, Order, ProductCollection, OrderPositions


class ProductCollectionInLine(admin.TabularInline):
    model = ProductCollection.selection.through
    extra = 1


class OrderPositionsInLine(admin.TabularInline):
    model = OrderPositions
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ProductCollectionInLine,
        OrderPositionsInLine
    ]

    readonly_fields = ('created_at', 'updated_at')


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
    inlines = [
        OrderPositionsInLine
    ]


# @admin.register(OrderPositions)
# class OrderPositionsAdmin(admin.ModelAdmin):
#     pass
