from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from rest_framework import serializers

from restaurants.models import MenuItem, MenuItemIngredientOption, Restaurant
from users.models import UserAddress
from users.profile_utils import get_or_create_profile
from users.serializers import UserAddressSerializer

from .models import Order, OrderItem, PaymentAttempt


TAX_RATE = Decimal('0.05')


def _q(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class OrderItemReadSerializer(serializers.ModelSerializer):
    dish_name            = serializers.SerializerMethodField()
    price                = serializers.DecimalField(max_digits=8, decimal_places=2)
    selected_ingredients = serializers.JSONField()
    special_instructions = serializers.CharField()

    class Meta:
        model  = OrderItem
        fields = [
            'id', 'menu_item', 'dish_name', 'quantity', 'price',
            'selected_ingredients', 'special_instructions',
        ]

    def get_dish_name(self, obj):
        return obj.menu_item.name if obj.menu_item else 'Deleted item'


class OrderItemWriteSerializer(serializers.Serializer):
    menu_item            = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity             = serializers.IntegerField(default=1)
    ingredient_option_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list,
    )
    special_instructions = serializers.CharField(required=False, allow_blank=True, default='', max_length=255)


class PaymentAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PaymentAttempt
        fields = [
            'id', 'method', 'status', 'transaction_id', 'amount',
            'card_last4', 'card_brand', 'upi_id', 'error_message', 'created_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items       = OrderItemReadSerializer(source='order_items', many=True, read_only=True)
    address_detail = UserAddressSerializer(source='address', read_only=True)
    payments    = PaymentAttemptSerializer(source='payment_attempts', many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status      = serializers.CharField(read_only=True)
    created_at  = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'user', 'restaurant', 'address',
            'subtotal', 'tax', 'delivery_fee', 'total_price',
            'status', 'payment_method', 'payment_status', 'transaction_id',
            'paid_at', 'items', 'payments', 'address_detail', 'created_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Creates orders from item IDs and calculates totals on the server."""
    restaurant = serializers.PrimaryKeyRelatedField(
        queryset=Restaurant.objects.all(), required=False, allow_null=True,
    )
    address = serializers.PrimaryKeyRelatedField(
        queryset=UserAddress.objects.all(), required=False, allow_null=True,
    )
    items = OrderItemWriteSerializer(many=True)

    def to_internal_value(self, data):
        forbidden = {}
        if 'user' in data:
            forbidden['user'] = 'Authenticated user is used; do not include user in request body'
        if 'total_price' in data:
            forbidden['total_price'] = 'Total price is calculated on the server'
        if forbidden:
            raise serializers.ValidationError(forbidden)
        return super().to_internal_value(data)

    def validate(self, attrs):
        items = attrs.get('items') or []
        if not items:
            raise serializers.ValidationError({'items': 'Order must contain at least one item'})
        if any(item['quantity'] <= 0 for item in items):
            raise serializers.ValidationError({'items': 'Quantity must be greater than 0'})

        restaurant = attrs.get('restaurant') or items[0]['menu_item'].restaurant
        attrs['restaurant'] = restaurant

        item_restaurant_ids = {item['menu_item'].restaurant_id for item in items}
        if len(item_restaurant_ids) > 1 or restaurant.id not in item_restaurant_ids:
            raise serializers.ValidationError({'items': 'All items must belong to the same restaurant'})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request      = self.context['request']
        user_profile = get_or_create_profile(request.user)
        restaurant   = validated_data.get('restaurant')
        address      = validated_data.get('address')
        items_data   = validated_data['items']

        order = Order.objects.create(
            user=user_profile,
            restaurant=restaurant,
            address=address if address and address.user_id == user_profile.id else None,
        )

        subtotal = Decimal('0.00')
        order_items = []

        for item_data in items_data:
            menu_item = item_data['menu_item']
            qty       = item_data['quantity']
            opt_ids   = item_data.get('ingredient_option_ids') or []
            notes     = (item_data.get('special_instructions') or '')[:255]

            options = list(MenuItemIngredientOption.objects.filter(
                id__in=opt_ids, menu_item=menu_item, is_active=True,
            ))
            selected = [
                {'id': opt.id, 'name': opt.name, 'extra_price': float(opt.extra_price)}
                for opt in options
            ]
            extras_total = sum((opt.extra_price for opt in options), Decimal('0.00'))
            line_unit    = menu_item.price + extras_total
            line_total   = line_unit * qty
            subtotal    += line_total

            order_items.append(OrderItem(
                order=order,
                menu_item=menu_item,
                quantity=qty,
                price=menu_item.price,
                selected_ingredients=selected,
                special_instructions=notes,
            ))

        OrderItem.objects.bulk_create(order_items)

        subtotal     = _q(subtotal)
        tax          = _q(subtotal * TAX_RATE)
        delivery_fee = Decimal('0.00')
        total        = _q(subtotal + tax + delivery_fee)

        order.subtotal     = subtotal
        order.tax          = tax
        order.delivery_fee = delivery_fee
        order.total_price  = total
        order.save(update_fields=['subtotal', 'tax', 'delivery_fee', 'total_price'])

        return order
