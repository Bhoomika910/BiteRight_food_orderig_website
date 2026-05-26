from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # FIX Bug 5: was ('id','user','total_amount','order_time') — old field names
    list_display = ('id', 'user', 'total_price', 'status', 'created_at')
