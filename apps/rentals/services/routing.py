"""
Delivery time estimation using OSRM (OpenStreetMap Routing).
Free, no API key needed.
"""
import requests
import logging

logger = logging.getLogger('locamaq.integrations')

# Endereço fixo da loja (Construara, Araguari/MG)
STORE_LAT = -18.6486
STORE_LNG = -48.1867


def estimate_delivery_time(dest_lat, dest_lng):
    """
    Estimate driving time from store to delivery address.
    Uses OSRM (free OpenStreetMap routing service).
    Returns dict: {'distance_km': float, 'duration_min': int} or None on error.
    """
    if not dest_lat or not dest_lng:
        return None

    try:
        url = (
            f'http://router.project-osrm.org/route/v1/driving/'
            f'{STORE_LNG},{STORE_LAT};{float(dest_lng)},{float(dest_lat)}'
            f'?overview=false'
        )

        response = requests.get(url, timeout=10, headers={'User-Agent': 'LocaMaq/1.0'})
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 'Ok' and data.get('routes'):
            route = data['routes'][0]
            distance_km = round(route['distance'] / 1000, 1)
            duration_min = round(route['duration'] / 60)
            logger.info(f'Delivery estimate: {distance_km}km, {duration_min}min')
            return {
                'distance_km': distance_km,
                'duration_min': duration_min,
            }
    except Exception as e:
        logger.error(f'OSRM routing error: {e}')

    return None
