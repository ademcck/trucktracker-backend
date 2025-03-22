
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from Trip.models import Trip
from Trip.api.serializers import TripSerializer
from core.tasks import generate_route_task, searchlocation
from uuid import uuid4

class TripCreateView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # random uuid4
        task_id = str(uuid4())  
        # Serialize the request data
        if 'serializer' in request.data:
            serializer_data = request.data['serializer']
        else:
            serializer_data = request.data

        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        
        # Diğer veriler
        start_lat = request.data.get('start_lat')
        start_lon = request.data.get('start_lon')
        end_lat = request.data.get('end_lat')
        end_lon = request.data.get('end_lon')
        ccu = request.data.get('ccu')
        # If user is authenticated, set user, otherwise user=None
        serializer.save(user=request.user if request.user.is_authenticated else None, task_id=task_id)

        # Start the Celery task // generate_route_task function creates new route from map
        route_task = generate_route_task.delay(
            task_id=task_id,
            start_lat=start_lat,
            start_lon=start_lon,
            end_lat=end_lat,
            end_lon=end_lon,
            ccu=ccu
            )

        return Response({
            "message": "Trip created successfully!",
            "task_id": task_id,  
            "driver_log": "Calculating route...",
            "route_task_id": route_task.id
        })

class PlaceSearchView(views.APIView):
    """
    get location with Google Places API 
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # get query param
        query = request.GET.get('q', None)
        taskIdFromFrontend = request.GET.get('task_id', None)
        status = None
        # if query is empty return error
        if not query:
            return Response({"error": "Query parameter 'q' is required."}, status=400)
        
        print(taskIdFromFrontend)
        if taskIdFromFrontend == "null":
            task_id = str(uuid4()) 
            status = True
        else:
            task_id = taskIdFromFrontend
            status = False

        search_result = searchlocation.delay( task_id, query)
        
        return Response(
            {
                "task_id": task_id,
                "search_id": search_result.id
            }
        )