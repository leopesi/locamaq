"""
Geocoding service using Google Maps Geocoding API (free tier) or Nominatim (OpenStreetMap).
"""
import requests
from django.conf import settings


def geocode_address(address: str) -> tuple:
    """
    Geocode an address to (lat, lng) coordinates.
    Uses Nominatim (OpenStreetMap) — free, no API key needed.
    Returns (lat, lng) or (None, None) if not found.
    """
    if not address or not address.strip():
        return None, None

    try:
        response = requests.get(
            'https://nominatim.openstreetmap.org/search',
            params={
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'br',
            },
            headers={'User-Agent': 'LocaMaq/1.0'},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        if data:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            return lat, lng
    except Exception:
        pass

    return None, None
