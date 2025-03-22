import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Create WebSocket connection and add task_id to group"""
        # ws/api/check/proccess/(?P<task_id>[0-9a-fA-F-]{36})/$
        self.task_id = self.scope["url_route"]["kwargs"]["task_id"]

        await self.channel_layer.group_add(str(self.task_id), self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        """When a message is received from frontend, return the status of the related taskr"""

        status = cache.get(f"task_{self.task_id}", "pending")
        await self.send(text_data=json.dumps({"task_id": self.task_id, "status": status}))

    async def task_status_update(self, event):
        """Send data via WebSocket when Celery completes"""
        try:
            await self.send(text_data=json.dumps({
                "task_id": event["task_id"],
                "status": event["status"],
                "route_data": event["route_data"],
                "driver_log": event["driver_log"]
            }))
        except:
            await self.send(text_data=json.dumps({
                "task_id": event["task_id"],
                "status": event["status"],
                "route_data": event["route_data"]
            }))
    
    async def info_message(self, event):
        """Send info message via WebSocket"""
        print( event)
        try:
            # Send URL if available
            if "url" in event:
                await self.send(text_data=json.dumps({
                    "task_id": event["task_id"],
                    "message": event["message"],
                    "url": event["url"],
                    "type": "info"
                }))
            # If no URL, just send a message
            else:
                await self.send(text_data=json.dumps({
                    "task_id": event["task_id"],
                    "message": event["message"],
                    "type": "info"
                }))
        except Exception as e:
            # Send a simple message in case of error
            print(e)
            await self.send(text_data=json.dumps({
                "task_id": event["task_id"],
                "message": f"Error sending info: {str(e)}",
                "type": "error"
            }))

    async def disconnect(self, close_code):
        """When the WebSocket connection is closed, leave the group"""
        await self.channel_layer.group_discard(str(self.task_id), self.channel_name)
