from django.db import models
from users.models import UserProfile
from restaurants.models import MenuItem, Restaurant


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',          'Pending'),
        ('preparing',        'Preparing'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered',        'Delivered'),
        ('cancelled',        'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('paid',      'Paid'),
        ('failed',    'Failed'),
        ('cod',       'Cash on Delivery'),
        ('refunded',  'Refunded'),
    ]

    user           = models.ForeignKey(UserProfile,  on_delete=models.CASCADE,  related_name='orders')
    restaurant     = models.ForeignKey(Restaurant,   on_delete=models.SET_NULL, null=True, blank=True)
    address        = models.ForeignKey('users.UserAddress', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    subtotal       = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax            = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee   = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price    = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, default='UPI')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    paid_at        = models.DateTimeField(null=True, blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} — {self.user.name} — {self.status}'


class OrderItem(models.Model):
    order                = models.ForeignKey(Order,    on_delete=models.CASCADE,  related_name='order_items')
    menu_item            = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    quantity             = models.PositiveIntegerField(default=1)
    price                = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot at order time
    selected_ingredients = models.JSONField(default=list, blank=True)  # list of {"name": str, "extra_price": float}
    special_instructions = models.CharField(max_length=255, blank=True, default='')

    def subtotal(self):
        extras = sum((float(opt.get('extra_price', 0) or 0) for opt in (self.selected_ingredients or [])), 0.0)
        return (float(self.price) + extras) * self.quantity

    def __str__(self):
        name = self.menu_item.name if self.menu_item else 'deleted item'
        return f'{self.quantity}x {name}'


class PaymentAttempt(models.Model):
    METHOD_CHOICES = [
        ('card', 'Card'),
        ('upi',  'UPI'),
        ('cod',  'Cash on Delivery'),
    ]
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('success',   'Success'),
        ('failed',    'Failed'),
    ]

    order          = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_attempts')
    method         = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    amount         = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    card_last4     = models.CharField(max_length=4, blank=True, default='')
    card_brand     = models.CharField(max_length=20, blank=True, default='')
    upi_id         = models.CharField(max_length=100, blank=True, default='')
    error_message  = models.CharField(max_length=255, blank=True, default='')
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.transaction_id} — {self.status}'
