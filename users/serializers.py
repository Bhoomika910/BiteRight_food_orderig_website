from rest_framework import serializers

from .models import UserAddress, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'id', 'name', 'email', 'phone',
            'allergies', 'diet_preferences', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = [
            'id', 'full_name', 'phone',
            'house', 'street', 'city', 'state', 'pincode',
            'address_line', 'is_default', 'address_type',
        ]
        read_only_fields = ['id', 'address_line']

    def validate(self, attrs):
        # On create we require the structured fields. On partial update (PATCH)
        # we let individual fields be omitted.
        partial = self.partial
        errors = {}
        def req(field, label, minlen=1, maxlen=None):
            val = (attrs.get(field) if field in attrs else getattr(self.instance, field, '') or '')
            val = (val or '').strip()
            if not partial and len(val) < minlen:
                errors[field] = f'{label} is required.'
            if maxlen and len(val) > maxlen:
                errors[field] = f'{label} is too long.'
            return val
        req('full_name', 'Full name', 2, 120)
        phone = req('phone', 'Phone number', 7, 20)
        if phone and not phone.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            errors['phone'] = 'Phone number is invalid.'
        req('house', 'House / Flat', 1, 120)
        req('street', 'Street', 2, 200)
        req('city', 'City', 2, 100)
        req('state', 'State', 2, 100)
        pin = req('pincode', 'Pincode', 4, 10)
        if pin and not pin.isdigit():
            errors['pincode'] = 'Pincode must be digits only.'
        if errors:
            raise serializers.ValidationError(errors)
        return attrs
