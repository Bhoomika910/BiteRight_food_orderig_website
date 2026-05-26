from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.response import error_response, success_response

from .models import UserAddress, UserProfile
from .profile_utils import get_or_create_profile, unique_username_for_email
from .serializers import UserAddressSerializer, UserProfileSerializer


class UserListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = UserProfile.objects.all().order_by('-created_at')
        serializer = UserProfileSerializer(users, many=True)
        return Response(success_response(serializer.data))

    def post(self, request):
        name = (request.data.get('name') or '').strip()
        email = (request.data.get('email') or '').strip().lower()
        phone = (request.data.get('phone') or '').strip()
        allergies = (request.data.get('allergies') or '').strip()
        diet_preferences = (request.data.get('diet_preferences') or '').strip()

        if not email:
            return Response(
                error_response({'email': ['This field is required.']}),
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()
        existing = User.objects.filter(email__iexact=email).first()
        created = False

        if existing:
            profile = get_or_create_profile(existing)
            profile.name = name or profile.name
            profile.email = email
            profile.phone = phone or profile.phone
            profile.allergies = allergies
            profile.diet_preferences = diet_preferences
            profile.save()
        else:
            username = unique_username_for_email(email)
            django_user = User(username=username, email=email)
            django_user.set_unusable_password()
            django_user.save()
            profile = UserProfile.objects.create(
                user=django_user,
                name=name or email.split('@')[0][:100],
                email=email,
                phone=phone,
                allergies=allergies,
                diet_preferences=diet_preferences,
            )
            created = True

        token, _ = Token.objects.get_or_create(user=profile.user)
        payload = {**UserProfileSerializer(profile).data, 'token': token.key}
        return Response(
            success_response(
                payload,
                message='Profile created!' if created else 'Welcome back!',
            ),
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        profile = get_or_create_profile(request.user)
        if profile.pk != int(pk):
            return Response(
                error_response({'message': 'You may only access your own profile.'}),
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(success_response(UserProfileSerializer(profile).data))

    def patch(self, request, pk):
        profile = get_or_create_profile(request.user)
        if profile.pk != int(pk):
            return Response(error_response({'message': 'Forbidden.'}),
                            status=status.HTTP_403_FORBIDDEN)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(success_response(serializer.data, message='Profile updated.'))


class ProfileMeView(APIView):
    """GET/PATCH /api/users/profile/me/ — current authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        return Response(success_response(UserProfileSerializer(profile).data))

    def patch(self, request):
        profile = get_or_create_profile(request.user)
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(success_response(serializer.data, message='Profile updated.'))


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_or_create_profile(request.user)
        addresses = UserAddress.objects.filter(user=profile).order_by('-is_default', 'id')
        return Response(success_response(UserAddressSerializer(addresses, many=True).data))

    def post(self, request):
        profile = get_or_create_profile(request.user)
        serializer = UserAddressSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data.get('is_default'):
            UserAddress.objects.filter(user=profile, is_default=True).update(is_default=False)
        # First-ever address auto-becomes default.
        if not UserAddress.objects.filter(user=profile).exists():
            serializer.validated_data['is_default'] = True
        address = serializer.save(user=profile)
        return Response(
            success_response(UserAddressSerializer(address).data, message='Address saved.'),
            status=status.HTTP_201_CREATED,
        )


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def _get(self, request, pk):
        profile = get_or_create_profile(request.user)
        try:
            return profile, UserAddress.objects.get(pk=pk, user=profile)
        except UserAddress.DoesNotExist:
            return profile, None

    def get(self, request, pk):
        _, address = self._get(request, pk)
        if not address:
            return Response(error_response({'detail': 'Address not found.'}), status=status.HTTP_404_NOT_FOUND)
        return Response(success_response(UserAddressSerializer(address).data))

    def put(self, request, pk):
        return self.patch(request, pk)

    def patch(self, request, pk):
        profile, address = self._get(request, pk)
        if not address:
            return Response(error_response({'detail': 'Address not found.'}), status=status.HTTP_404_NOT_FOUND)
        serializer = UserAddressSerializer(address, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        if serializer.validated_data.get('is_default'):
            UserAddress.objects.filter(user=profile, is_default=True).exclude(pk=address.pk).update(is_default=False)
        serializer.save()
        return Response(success_response(UserAddressSerializer(address).data, message='Address updated.'))

    def delete(self, request, pk):
        profile, address = self._get(request, pk)
        if not address:
            return Response(error_response({'detail': 'Address not found.'}), status=status.HTTP_404_NOT_FOUND)
        was_default = address.is_default
        address.delete()
        if was_default:
            nxt = UserAddress.objects.filter(user=profile).order_by('id').first()
            if nxt:
                nxt.is_default = True
                nxt.save(update_fields=['is_default'])
        return Response(success_response(None, message='Address removed.'))


CreateUserProfileView = UserListCreateView
