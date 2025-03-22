from django.urls import re_path
from .consumers import TaskStatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/api/check/proccess/(?P<task_id>[0-9a-fA-F-]{36})/$", TaskStatusConsumer.as_asgi()),
]
