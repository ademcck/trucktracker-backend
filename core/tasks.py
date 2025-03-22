from celery import shared_task
from django.core.cache import cache
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.utils.getroute import  get_route,plan_route
from core.utils.getCoordinates import get_cordinates
from core.utils.svgcustomizer import create_svg_main
from core.utils.convert_to_pdf import convert_svg_to_pdf
import logging

logger = logging.getLogger(__name__)
headers = { 'User-Agent' : 'trucktrack/1.0 (adem.c1c3k@gmail.com)', }

def send_info_to_frontend(task_id, message, url=None):
    "Send info message to frontend"
    channel_layer = get_channel_layer()
    if url:
        async_to_sync(channel_layer.group_send)(
            str(task_id),  
            {
                "type": "info_message",
                "message": message,
                "task_id": task_id,
                "url": url,
            }
        )

    else:  
        async_to_sync(channel_layer.group_send)(
            str(task_id),  
            {
                "type": "info_message",
                "message": message,
                "task_id": task_id,
            }
        )
@shared_task
def generate_route_task(task_id, start_lat, start_lon, end_lat, end_lon, ccu):
    """
    Calculates routes with OSRM API and saves the result in cache.
    """
    ccu = float(int(ccu))
    cache.set(f'task_{task_id}', 'processing')
    START_COORDS = f"{start_lon},{start_lat}"  # lon,lat
    END_COORDS = f"{end_lon},{end_lat}"  # lon,lat

    # Send start message to frontend
    send_info_to_frontend(task_id, "Route calculation started.")

    route_data = get_route(START_COORDS, END_COORDS)
    if not route_data:
        send_info_to_frontend(task_id, "Route data could not be obtained.")
        return {"trip_id": task_id, "driver_log": "Route data could not be obtained."}

    # Send route data created message to frontend
    send_info_to_frontend(task_id, "Route data is created.")

    driver_log = plan_route(route_data, ccu)
    # Send driver log created message to frontend
    send_info_to_frontend(task_id, "Driver log is created.")
    logger.info(f"Toplam Kullanılan: {driver_log}h")

    draw_cordinate = get_cordinates(driver_log)
    # Send coordinates created message to frontend
    send_info_to_frontend(task_id, "Coordinates are created.")

    create_svg_main(draw_cordinate, task_id)
    # Send SVG data generated message to frontend
    send_info_to_frontend(task_id, "SVG data is created.")

    convert_svg_to_pdf(f"{task_id}_merged_pages.pdf", task_id)
    # Send PDF conversion complete message to Frontend
    send_info_to_frontend(task_id, "SVG data is converted to PDF.", f"/pdf/{task_id}_merged_pages.pdf")

    cache.set(f'route_data_{task_id}', route_data, timeout=1800)
    cache.set(f'driver_log_{task_id}', driver_log, timeout=1800)
    cache.set(f'task_{task_id}', 'completed')

    # Send task completed message to frontend
    send_info_to_frontend(task_id, "Task completed.")

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(task_id),  
        {
            "type": "task_status_update",
            "task_id": task_id,
            "status": "completed",
            "driver_log": driver_log,
            "route_data": route_data
        }
    )

    return {"trip_id": task_id, "driver_log": driver_log}
@shared_task
def searchlocation( task_id, location):
    """
    search location with openstreetmap
    """
    cache.set(f'task_{task_id}', 'processing')
    
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "addressdetails": 1, "limit": 20}
    response = requests.get(base_url, params=params, headers=headers)
    route_data = response.json()

    cache.set(f'route_{task_id}', route_data, timeout=1800)
    cache.set(f'task_{task_id}', 'completed')

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        str(task_id),  
        {
            "type": "task_status_update",
            "task_id": task_id,
            "status": "completed",
            "route_data": route_data
        }
    )

    return {"trip_id": task_id, "route_data": route_data}