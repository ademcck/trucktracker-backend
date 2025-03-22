from django.urls import path
import Trip.api.views as api_views

urlpatterns = [
    path('search/', api_views.PlaceSearchView.as_view(), name='place_search'),
    path('create/', api_views.TripCreateView.as_view(), name='trip_create'),
]
