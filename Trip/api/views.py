
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from Trip.models import Trip
from Trip.api.serializers import TripSerializer
from core.tasks import generate_route_task, searchlocation
from uuid import uuid4
from django.http import FileResponse, Http404
from django.conf import settings
import os

class TripCreateView(generics.CreateAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # get task_id from frontend
        task_id = request.data.get('task_id')
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
            "driver_log": "Calculating route...",
            "route_task_id": route_task.id
        })

class GenerateTaskView(views.APIView):
    permission_classes = [AllowAny]

    # generate task_id
    def get(self, request):
        task_id = str(uuid4())
        return Response({"task_id": task_id})
    

class DownloadPdfView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, task_id):
        # Construct the full path to the PDF file
        pdf_file_path = os.path.join(settings.MEDIA_ROOT, "pdf", f"{task_id}.pdf")

        # Check if the file exists
        if not os.path.exists(pdf_file_path):
            raise Http404("PDF file not found.")

        # Open the file in binary mode
        try:
            pdf_file = open(pdf_file_path, 'rb')
        except IOError:
            raise Http404("Unable to open the PDF file.")

        # Return the file as a response
        response = FileResponse(pdf_file)
        response['Content-Disposition'] = f'attachment; filename="{task_id}.pdf"'
        response['Content-Type'] = 'application/pdf'
        return response
    
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