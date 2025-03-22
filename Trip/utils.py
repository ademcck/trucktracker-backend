import requests
import os

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def search_place(query):
    """Google Places API kullanarak yer araması yapar."""
    url = f"https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "key": GOOGLE_PLACES_API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()
