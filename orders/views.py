import secrets
import time
from datetime import datetime, timezone
from decimal import Decimal

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.response import error_response, success_response
from users.profile_utils import get_or_create_profile

from .models import Order, PaymentAttempt
from .serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    PaymentAttemptSerializer,
)


class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        orders = (
            Order.objects
            .filter(user=profile)
            .prefetch_related('order_items__menu_item', 'payment_attempts')
        )
        return Response(success_response(OrderSerializer(orders, many=True).data))

    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        order = serializer.save()
        return Response(
            success_response(OrderSerializer(order).data, message='Order placed successfully!'),
            status=status.HTTP_201_CREATED,
        )


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        profile = get_or_create_profile(request.user)
        try:
            order = (
                Order.objects
                .prefetch_related('order_items__menu_item', 'payment_attempts')
                .get(pk=pk, user=profile)
            )
        except Order.DoesNotExist:
            return Response(error_response({'detail': 'Order not found'}), status=status.HTTP_404_NOT_FOUND)
        return Response(success_response(OrderSerializer(order).data))


def _make_txn_id(prefix='BR'):
    return f'{prefix}-{int(time.time())}-{secrets.token_hex(4).upper()}'


def _luhn_valid(num):
    digits = [int(c) for c in str(num) if c.isdigit()]
    if len(digits) < 12:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


class PaymentProcessView(APIView):
    """
    POST /api/payments/
    Body:
      { "order_id": 1, "method": "card"|"upi"|"cod",
        "card_number": "...", "cardholder_name": "...",
        "expiry": "MM/YY", "cvv": "123",
        "upi_id": "name@bank" }

    Security:
      - CVV is never stored.
      - Raw card number is never stored — only the last 4 digits and brand.
      - Returns a transaction reference.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        profile = get_or_create_profile(request.user)
        data    = request.data or {}

        order_id = data.get('order_id')
        method   = (data.get('method') or '').lower().strip()

        if method not in {'card', 'upi', 'cod'}:
            return Response(error_response({'method': 'Choose card, upi or cod.'}),
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=order_id, user=profile)
        except Order.DoesNotExist:
            return Response(error_response({'order_id': 'Order not found.'}),
                            status=status.HTTP_404_NOT_FOUND)

        if order.payment_status == 'paid':
            return Response(error_response({'order_id': 'Order is already paid.'}),
                            status=status.HTTP_400_BAD_REQUEST)

        # Build payment attempt — never persist CVV / full PAN.
        card_last4 = ''
        card_brand = ''
        upi_id     = ''
        attempt_status = 'pending'
        error_msg = ''

        if method == 'card':
            card_number_raw = (data.get('card_number') or '').replace(' ', '').replace('-', '')
            cvv             = (data.get('cvv') or '').strip()
            expiry          = (data.get('expiry') or '').strip()
            cardholder      = (data.get('cardholder_name') or '').strip()

            if not (card_number_raw.isdigit() and 12 <= len(card_number_raw) <= 19):
                error_msg = 'Invalid card number.'
            elif not (cvv.isdigit() and 3 <= len(cvv) <= 4):
                error_msg = 'Invalid CVV.'
            elif len(expiry) < 4:
                error_msg = 'Invalid expiry.'
            elif not cardholder:
                error_msg = 'Cardholder name required.'
            else:
                card_last4 = card_number_raw[-4:]
                first = card_number_raw[0]
                card_brand = {'4': 'Visa', '5': 'Mastercard', '3': 'Amex', '6': 'Discover'}.get(first, 'Card')
                # Simulated success rule: passes Luhn check.
                attempt_status = 'success' if _luhn_valid(card_number_raw) else 'failed'
                if attempt_status == 'failed':
                    error_msg = 'Card declined by issuer (simulated).'

        elif method == 'upi':
            upi_id = (data.get('upi_id') or '').strip().lower()
            if '@' not in upi_id or len(upi_id) < 4:
                error_msg = 'Invalid UPI ID.'
            else:
                # Simulated success: UPI ids not containing the word "fail" succeed.
                attempt_status = 'failed' if 'fail' in upi_id else 'success'
                if attempt_status == 'failed':
                    error_msg = 'UPI payment failed (simulated).'

        else:  # cod
            attempt_status = 'success'

        txn_id = _make_txn_id('COD' if method == 'cod' else 'PAY')

        attempt = PaymentAttempt.objects.create(
            order=order,
            method=method,
            status=attempt_status if not error_msg or attempt_status == 'success' else 'failed',
            transaction_id=txn_id if attempt_status == 'success' else '',
            amount=order.total_price,
            card_last4=card_last4,
            card_brand=card_brand,
            upi_id=upi_id,
            error_message=error_msg,
        )

        if attempt.status == 'success':
            order.payment_method = method.upper()
            order.payment_status = 'cod' if method == 'cod' else 'paid'
            order.transaction_id = txn_id
            order.paid_at = datetime.now(tz=timezone.utc)
            order.status = 'preparing' if method != 'cod' else 'pending'
            order.save(update_fields=['payment_method', 'payment_status', 'transaction_id', 'paid_at', 'status'])
            return Response(success_response({
                'payment': PaymentAttemptSerializer(attempt).data,
                'order':   OrderSerializer(order).data,
            }, message='Payment successful!'), status=status.HTTP_200_OK)

        # Failed → mark order payment_status=failed
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
        return Response(error_response({
            'payment': PaymentAttemptSerializer(attempt).data,
            'message': error_msg or 'Payment failed.',
        }), status=status.HTTP_402_PAYMENT_REQUIRED)
