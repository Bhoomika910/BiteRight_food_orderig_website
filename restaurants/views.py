from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.utils.response import error_response, success_response
from users.profile_utils import get_or_create_profile

from .models import MenuItem, Restaurant, Review
from .nlp_service import detect_allergy_risk
from .serializers import MenuItemSerializer, RestaurantSerializer, ReviewSerializer
from .services.recommendation_service import get_recommendations


def _parse_allergies(raw_allergies):
    if raw_allergies is None:
        return []
    if isinstance(raw_allergies, str):
        raw_allergies = raw_allergies.split(',')

    allergies = []
    for allergy in raw_allergies:
        allergies.extend(
            part.strip()
            for part in str(allergy).split(',')
            if part.strip()
        )
    return allergies


def _as_allergy_text(value):
    if isinstance(value, (list, tuple, set)):
        return ' '.join(str(item) for item in value)
    return str(value or '')


def _menu_item_allergy_text(item):
    return ' '.join(
        str(value)
        for value in [
            getattr(item, 'name', ''),
            getattr(item, 'description', ''),
            getattr(item, 'ingredients', ''),
        ]
        if value
    )


class RestaurantListView(APIView):
    """GET /api/restaurants/"""
    permission_classes = [AllowAny]

    def get(self, request):
        restaurants = Restaurant.objects.all().order_by('id')
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(success_response(serializer.data))


class MenuItemListView(APIView):
    """GET /api/restaurants/<restaurant_id>/menu/"""
    permission_classes = [AllowAny]

    def get(self, request, restaurant_id):
        items = MenuItem.objects.filter(restaurant_id=restaurant_id)
        serializer = MenuItemSerializer(items, many=True)
        return Response(success_response(serializer.data))


class AllergyCheckView(APIView):
    """
    POST /api/check-allergy/
    Body: { "allergies": ["peanuts"], "ingredients": ["flour", "peanut oil"] }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        allergies = _parse_allergies(request.data.get('allergies', []))
        text = request.data.get('text')
        if text is None:
            text = [
                request.data.get('name', ''),
                request.data.get('description', ''),
                request.data.get('ingredients', ''),
            ]

        result = detect_allergy_risk(allergies, _as_allergy_text(text))
        return Response(success_response(result))


class SearchMenuView(APIView):
    """GET /api/search-menu/?q=<query>"""
    permission_classes = [AllowAny]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if not q:
            return Response(success_response([]))

        items = (
            MenuItem.objects.filter(name__icontains=q) |
            MenuItem.objects.filter(ingredients__icontains=q)
        ).distinct()
        serializer = MenuItemSerializer(items, many=True)
        return Response(success_response(serializer.data))


class SafeMenuView(APIView):
    """GET /api/safe-menu/<restaurant_id>/ — uses the authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request, restaurant_id):
        profile = get_or_create_profile(request.user)

        items = MenuItem.objects.filter(restaurant_id=restaurant_id)
        allergens = _parse_allergies(profile.allergies)
        if allergens:
            safe = [
                item
                for item in items
                if detect_allergy_risk(allergens, _menu_item_allergy_text(item))['safe']
            ]
        else:
            safe = list(items)

        serializer = MenuItemSerializer(safe, many=True)
        return Response(success_response(serializer.data))


class RecommendationView(APIView):
    """
    GET /api/recommendations/<restaurant_id>/?mood=comfort&time=afternoon
    Returns up to 5 dishes ranked for the authenticated user's profile.
    AllowAny so the demo works without a token; if a token IS sent the
    user's real allergies / diet are used, otherwise defaults are used.
    """
    permission_classes = [AllowAny]

    def get(self, request, restaurant_id):
        mood = request.query_params.get('mood', '')
        time_of_day = request.query_params.get('time', '')

        # Use real profile if authenticated, otherwise use an empty stand-in
        if request.user and request.user.is_authenticated:
            profile = get_or_create_profile(request.user)
        else:
            # Anonymous user: no allergies, no diet preference
            class _AnonProfile:
                allergies = ''
                diet_preferences = ''
            profile = _AnonProfile()

        try:
            restaurant = Restaurant.objects.get(pk=restaurant_id)
        except Restaurant.DoesNotExist:
            return Response(
                error_response({'message': f'Restaurant {restaurant_id} not found.'}),
                status=status.HTTP_404_NOT_FOUND,
            )

        recommendations = get_recommendations(
            user=profile,
            restaurant=restaurant,
            mood=mood,
            time=time_of_day,
        )
        result = [
            {
                'id': recommendation['item'].id,
                'name': recommendation['item'].name,
                'price': float(recommendation['item'].price),
                'diet_tags': recommendation['item'].diet_tags,
                'mood_tags': recommendation['item'].mood_tags,
                'ingredients': recommendation['item'].ingredients,
                'score': recommendation['score'],
                'reasons': recommendation['reasons'],
            }
            for recommendation in recommendations
        ]
        return Response(success_response(result))


class ReviewListView(APIView):
    """
    GET /api/restaurants/<restaurant_id>/reviews/
    POST /api/reviews/ { "user": 1, "restaurant": 1, "rating": 5, "comment": "Great!" }
    """
    # GET is public (anyone can read reviews); POST requires a logged-in user.
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request, restaurant_id=None):
        if restaurant_id is None:
            return Response(
                error_response({'message': 'Restaurant id is required.'}),
                status=status.HTTP_404_NOT_FOUND,
            )
        reviews = Review.objects.filter(restaurant_id=restaurant_id).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(success_response(serializer.data))

    def post(self, request):
        profile = get_or_create_profile(request.user)
        payload = request.data.copy()
        payload['user'] = profile.pk
        serializer = ReviewSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(success_response(serializer.data), status=status.HTTP_201_CREATED)
        return Response(error_response(serializer.errors), status=status.HTTP_400_BAD_REQUEST)
