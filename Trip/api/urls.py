from django.urls import path
import Trip.api.views as api_views

urlpatterns = [
    path('search/', api_views.PlaceSearchView.as_view(), name='place_search'),
    path('create/', api_views.TripCreateView.as_view(), name='trip_create'),
    path('generate_task/', api_views.GenerateTaskView.as_view(), name='generate_route_task'),
    path('download_pdf/<str:task_id>/', api_views.DownloadPdfView.as_view(), name='download_pdf'),
]
