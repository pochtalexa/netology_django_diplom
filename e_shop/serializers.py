from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.validators import UniqueTogetherValidator

from e_shop.models import Product, ProductReview, Order, ProductCollection, OrderPositions


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        exclude = ['author']
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=ProductReview.objects.all(),
        #         fields=['author', 'product']
        #     )
        # ]

    def validate_product(self, value):
        author = self.context['request'].user
        product_reviews = ProductReview.objects.filter(author=author, product=value).count()
        if product_reviews:
            raise serializers.ValidationError("You can save only one review for the same product")

        return value

    def create(self, validated_data):
        author = self.context['request'].user
        self.validated_data['author'] = author
        product_review = ProductReview.objects.create(**self.validated_data)

        return product_review

    def update(self, instance, validated_data):
        instance.mark = validated_data.get('mark', instance.mark)
        instance.review = validated_data.get('review', instance.review)
        instance.product = validated_data.get('product', instance.product)
        instance.save()

        return instance


class OrderPositionsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = OrderPositions
        fields = ['id', 'product', 'quantity']
        # fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    positions = OrderPositionsSerializer(many=True, source='orderpositions_set')
    sum = serializers.IntegerField(required=False)
    user = serializers.CharField(required=False)

    class Meta:
        model = Order
        fields = ['id', 'sum', 'user', 'status', 'positions']
        # exclude = ['user']

    def create(self, validated_data):
        positions_data = validated_data.pop('orderpositions_set')
        if not positions_data:
            raise serializers.ValidationError("You cann't create Order without positions")
        user = self.context['request'].user
        validated_data['user'] = user
        validated_data['sum'] = 0
        validated_data['status'] = 'NEW'
        total = 0
        order = Order.objects.create(**validated_data)
        for el in positions_data:
            OrderPositions.objects.create(order=order, **el)
            total += el['quantity']*el['product'].price
        order.sum = total
        order.save()

        return order

    def update(self, instance, validated_data):
        positions_data = validated_data.pop('orderpositions_set', [])
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if not positions_data:
            return instance

        total = 0
        keep_positions = []
        # existing_ids = [p.id for p in instance.positions]
        for el in positions_data:
            if 'id' in el.keys():
                if OrderPositions.objects.filter(id=el['id']).exists():
                    p = OrderPositions.objects.get(id=el['id'])
                    p.product = el.get('product', p.product)
                    p.quantity = el.get('quantity', p.quantity)
                    p.save()
                    keep_positions.append(p.id)
                else:
                    continue
            else:
                p = OrderPositions.objects.create(order=instance, **el)
                keep_positions.append(p.id)

        orderpositions = (instance.orderpositions_set).all()
        orderpositions = list(orderpositions)
        for el in orderpositions:
            if el.id not in keep_positions:
                el.delete()

        orderpositions = (instance.orderpositions_set).all()
        orderpositions = list(orderpositions)
        for el in orderpositions:
            total += el.quantity * el.product.price

        instance.sum = total
        instance.save()

        return instance


class ProductCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCollection
        fields = '__all__'
