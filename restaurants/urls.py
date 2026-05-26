from django.urls import path
from .views import (
    AllergyCheckView,
    MenuItemListView,
    RecommendationView,
    RestaurantListView,
    SafeMenuView,
    SearchMenuView,
    ReviewListView,
)

urlpatterns = [
    path('check-allergy/',                                    AllergyCheckView.as_view(),   name='check-allergy'),
    path('search-menu/',                                      SearchMenuView.as_view(),      name='search-menu'),
    path('safe-menu/<int:restaurant_id>/',                   SafeMenuView.as_view(),        name='safe-menu'),
    path('recommendations/<int:restaurant_id>/',             RecommendationView.as_view(), name='recommendations'),
    path('restaurants/',                                      RestaurantListView.as_view(),  name='restaurant-list'),
    path('restaurants/<int:restaurant_id>/menu/',             MenuItemListView.as_view(),    name='restaurant-menu-items'),
    path('restaurants/<int:restaurant_id>/reviews/',          ReviewListView.as_view(),      name='restaurant-reviews'),
    path('reviews/',                                          ReviewListView.as_view(),      name='review-create'),
]
