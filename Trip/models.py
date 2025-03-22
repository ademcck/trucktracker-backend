from django.db import models
from django.contrib.auth.models import User
import uuid

class Trip(models.Model):
    task_id = models.CharField(max_length=36, unique=True, default=uuid.uuid4, editable=False)  # task_id field for Celery task
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start_location = models.CharField(max_length=255)
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    hours_available = models.FloatField(null=True, blank=True)
    distance = models.FloatField(null=True, blank=True)
    estimate_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trip from {self.start_location} to {self.dropoff_location}"