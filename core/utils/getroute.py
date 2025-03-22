import requests
from datetime import datetime, timedelta

# OSRM API endpoint
OSRM_URL = "https://router.project-osrm.org/route/v1/driving-hgv"

# Driving and rest times according to European standards
MAX_DRIVING_WITHOUT_BREAK = 4.5 # 45 minutes rest every 4.5 hours
MAX_DAILY_DRIVING = 9 # Maximum daily driving time
MIN_BREAK_AFTER_DRIVING = 0.75 # 45 minutes rest
DAILY_REST = 11 # Daily rest time (hours)
NIGHT_REST_START = 22 # Night rest start time (22:00)
FUEL_STOP_INTERVAL = 800 # Refueling interval (km)

# Average speed (km/h)
AVERAGE_SPEED = 80

def get_route(start_coords, end_coords):
    """Get route information using the OSRM API"""
    params = {
        'overview': 'full',
        'geometries': 'geojson',
        'steps': 'true',
        'annotations': 'true',
        'continue_straight': 'true',
        'alternatives': 'false',
    }
    headers = {
        'User-Agent': 'trucktrack/1.0 (abc@gmail.com)',
    }
    url = f"{OSRM_URL}/{start_coords};{end_coords}"
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def plan_route(route_data, current_cycle_used):
    """Plan routes and identify resting places"""
    total_distance = route_data['routes'][0]['distance'] / 1000  # Meter -> Kilometer
    total_duration = route_data['routes'][0]['duration'] / 3600  # Second -> Hour
    route_plan = []

    # Start time (used 2025-03-15 06:30:00 as an example)
    current_time = datetime(2025, 3, 15, 6, 30, 0)

    # Current working hours of the driver
    driving_time = current_cycle_used
    daily_driving_time = driving_time
    cumulative_distance = 0

    # Refueling control
    last_fuel_stop_distance = 0

    # Process route steps
    steps = route_data['routes'][0]['legs'][0]['steps']
    driving_segment = None  # Unified driving segment

    for step in steps:
        step_distance = step['distance'] / 1000  # Meter -> Kilometer
        step_duration = step['duration'] / 3600  # Second -> Hour
        
        # Night rest control
        if current_time.hour >= NIGHT_REST_START:
            # Save previous driving segment
            if driving_segment:
                route_plan.append(driving_segment)
                driving_segment = None

            # Add night rest
            night_rest_duration = DAILY_REST  # 11 hours
            end_time = current_time + timedelta(hours=night_rest_duration)
            route_plan.append({
                "mode": "Sleeper Berth",
                "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": night_rest_duration * 60,
                "location": step['maneuver']['location'],
                "cumulative_distance": cumulative_distance
            })
            current_time = end_time
            daily_driving_time = 0


        # Refueling control
        if cumulative_distance + step_distance - last_fuel_stop_distance >= FUEL_STOP_INTERVAL:
            # Save previous driving segment
            if driving_segment:
                route_plan.append(driving_segment)
                driving_segment = None

            # Add refueling break
            fuel_stop_duration = 0.5  # 30 minutes
            end_time = current_time + timedelta(hours=fuel_stop_duration)
            route_plan.append({
                "mode": "On Duty (Fueling)",
                "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": fuel_stop_duration * 60,
                "location": step['maneuver']['location'],
                "cumulative_distance": cumulative_distance
            })
            current_time = end_time
            last_fuel_stop_distance = cumulative_distance

        # Rest check every 4.5 hours
        if driving_time >= MAX_DRIVING_WITHOUT_BREAK:
            # Save previous driving segment
            if driving_segment:
                route_plan.append(driving_segment)
                driving_segment = None

            # Add rest break
            break_duration = MIN_BREAK_AFTER_DRIVING  # 45 minutes
            end_time = current_time + timedelta(hours=break_duration)
            if cumulative_distance == 0:
                    route_plan.append({
                        "mode": "On Duty (Fueling) start",
                        "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": datetime(2025, 3, 15, 7, 00, 0).strftime("%Y-%m-%d %H:%M:%S"),
                        "duration": 0.5 * 60,
                        "location": steps[0]['maneuver']['location'],
                        "cumulative_distance": cumulative_distance
                    })
                    current_time = current_time + timedelta(hours=0.5)
                    driving_time = 0
                    daily_driving_time += break_duration
            else:
                route_plan.append({
                    "mode": "Off Duty (Break)",
                    "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration": break_duration * 60,
                    "location": step['maneuver']['location'],
                    "cumulative_distance": cumulative_distance
                })
                current_time = end_time
                driving_time = 0
                daily_driving_time += break_duration

        # Unify the driving segment
        if not driving_segment:
            driving_segment = {
                "mode": "Driving",
                "start_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": None,
                "duration": 0,
                "location": step['maneuver']['location'],
                "cumulative_distance": cumulative_distance
            }

        # Update driving segment
        driving_segment["end_time"] = (current_time + timedelta(hours=step_duration)).strftime("%Y-%m-%d %H:%M:%S")
        driving_segment["duration"] += step_duration * 60
        driving_segment["location"] = step['maneuver']['location']
        driving_segment["cumulative_distance"] += step_distance

        # Updates
        current_time += timedelta(hours=step_duration)
        cumulative_distance += step_distance
        driving_time += step_duration
        daily_driving_time += step_duration

    # Add the last driving segment
    if driving_segment:
        route_plan.append(driving_segment)

    return {
    'total_distance': total_distance,
    'total_duration': total_duration,
    'schedule': route_plan
    }
    