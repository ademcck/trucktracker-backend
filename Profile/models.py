from django.db import models
from django.contrib.auth.models import User
    
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    plate_number = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - {self.plate_number}"
    
        