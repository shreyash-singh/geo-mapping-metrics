"""
Polygon Analyzer - Analyzes eateries, offices, apartments, PGs, and gyms in given polygons
Uses Google Places API to count different types of establishments
"""

import googlemaps
import pandas as pd
from typing import List, Tuple, Dict, Optional
import time
import math
import re
import requests
import numpy as np
from shapely.geometry import MultiPoint
import datetime


class PolygonAnalyzer:
    def __init__(self, api_key: str = None):
        """
        Initialize the Polygon Analyzer with Google Maps API key
        
        Args:
            api_key: Google Maps API key (optional, required only for Google Maps operations)
        """
        self.api_key = api_key or ''
        # Only initialize googlemaps client if API key is provided and not empty
        # This allows the class to be used for Mapbox-only operations
        if self.api_key and self.api_key.strip():
            try:
                self.gmaps = googlemaps.Client(key=self.api_key)
            except Exception:
                # If initialization fails, set to None - will fail later if Google Maps is used
                self.gmaps = None
        else:
            self.gmaps = None
    
    @staticmethod
    def parse_wkt_polygon(wkt_string: str) -> List[Tuple[float, float]]:
        """
        Parse WKT (Well-Known Text) polygon string to list of (lat, lng) tuples
        
        Args:
            wkt_string: WKT format string like "POLYGON((lng1 lat1, lng2 lat2, ...))"
                       or "POLYGON ((lng1 lat1, lng2 lat2, ...))" (with space)
                       or just the coordinate string "(lng1 lat1, lng2 lat2, ...)"
        
        Returns:
            List of (latitude, longitude) tuples
        """
        # Remove quotes if present
        wkt_string = wkt_string.strip().strip('"').strip("'")
        
        # Remove POLYGON keyword if present (case insensitive)
        wkt_upper = wkt_string.upper()
        if wkt_upper.startswith('POLYGON'):
            # Extract coordinates part: POLYGON((...)) or POLYGON ((...)) -> (...)
            # Try with double parentheses first (most common format)
            match = re.search(r'POLYGON\s*\(\((.*?)\)\)', wkt_string, re.IGNORECASE)
            if match:
                coords_str = match.group(1)
            else:
                # Try with single parentheses
                match = re.search(r'POLYGON\s*\((.*?)\)', wkt_string, re.IGNORECASE)
                if match:
                    coords_str = match.group(1)
                else:
                    # Fallback: try to extract anything in parentheses
                    match = re.search(r'\((.*?)\)', wkt_string)
                    coords_str = match.group(1) if match else wkt_string
        else:
            # Assume it's just the coordinate string, remove outer parentheses
            coords_str = wkt_string.strip('()')
        
        # Parse coordinates
        # WKT format: "lng1 lat1, lng2 lat2, ..." (note: lng comes first in WKT)
        polygon = []
        for coord_pair in coords_str.split(','):
            coord_pair = coord_pair.strip()
            if not coord_pair:
                continue
            # Split by whitespace (handles multiple spaces)
            parts = coord_pair.split()
            if len(parts) >= 2:
                try:
                    lng = float(parts[0])
                    lat = float(parts[1])
                    # Convert to (lat, lng) format for our internal use
                    polygon.append((lat, lng))
                except ValueError:
                    continue
        
        # Remove duplicate consecutive points (common in WKT where first and last point are the same)
        if len(polygon) > 1 and polygon[0] == polygon[-1]:
            polygon = polygon[:-1]
        
        return polygon
        
    def get_polygon_bounds(self, polygon: List[Tuple[float, float]]) -> Dict[str, float]:
        """
        Calculate bounding box for a polygon
        
        Args:
            polygon: List of (lat, lng) tuples representing polygon vertices
            
        Returns:
            Dictionary with 'northeast' and 'southwest' bounds
        """
        lats = [point[0] for point in polygon]
        lngs = [point[1] for point in polygon]
        
        return {
            'northeast': {'lat': max(lats), 'lng': max(lngs)},
            'southwest': {'lat': min(lats), 'lng': min(lngs)}
        }
    
    def point_in_polygon(self, point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        """
        Check if a point is inside a polygon using ray casting algorithm
        
        Args:
            point: (lat, lng) tuple
            polygon: List of (lat, lng) tuples representing polygon vertices
            
        Returns:
            True if point is inside polygon, False otherwise
        """
        if len(polygon) < 3:
            return False
        
        lat, lng = point
        n = len(polygon)
        inside = False
        
        # Ray casting algorithm: count intersections of horizontal ray from point
        p1_lat, p1_lng = polygon[0]
        for i in range(1, n + 1):
            p2_lat, p2_lng = polygon[i % n]
            
            # Check if ray crosses this edge
            if ((p1_lng > lng) != (p2_lng > lng)):  # Ray crosses edge in longitude
                # Calculate intersection point
                if p1_lng != p2_lng:
                    # Linear interpolation to find lat at intersection
                    intersect_lat = (lng - p1_lng) * (p2_lat - p1_lat) / (p2_lng - p1_lng) + p1_lat
                    if lat <= intersect_lat:
                        inside = not inside
                elif lat <= max(p1_lat, p2_lat):
                    # Edge is vertical, check if point is on the correct side
                    inside = not inside
            
            p1_lat, p1_lng = p2_lat, p2_lng
        
        return inside
    
    def search_places_in_bounds(self, bounds: Dict, place_types: List[str] = None, 
                                keyword: str = None, max_results: int = 60) -> List[Dict]:
        """
        Search for places within bounding box using Google Places API
        
        Args:
            bounds: Bounding box dictionary with 'northeast' and 'southwest'
            place_types: List of place types to search for
            keyword: Optional keyword to filter results
            max_results: Maximum number of results to return
            
        Returns:
            List of place dictionaries
        """
        all_places = []
        center_lat = (bounds['northeast']['lat'] + bounds['southwest']['lat']) / 2
        center_lng = (bounds['northeast']['lng'] + bounds['southwest']['lng']) / 2
        
        # Calculate approximate radius in meters
        lat_diff = bounds['northeast']['lat'] - bounds['southwest']['lat']
        lng_diff = bounds['northeast']['lng'] - bounds['southwest']['lng']
        # Rough approximation: 1 degree lat ≈ 111km, 1 degree lng ≈ 111km * cos(lat)
        radius = int(max(lat_diff * 111000, lng_diff * 111000 * math.cos(math.radians(center_lat))))
        # Ensure radius is within API limits (max 50000 meters)
        radius = min(radius, 50000)
        
        # Use nearby search with bounds
        try:
            # Search with each place type if multiple types provided
            types_to_search = place_types if place_types else [None]
            
            for place_type in types_to_search:
                if len(all_places) >= max_results:
                    break
                    
                # First search
                results = self.gmaps.places_nearby(
                    location=(center_lat, center_lng),
                    radius=radius,
                    type=place_type,
                    keyword=keyword
                )
                
                all_places.extend(results.get('results', []))
                
                # Handle pagination
                while 'next_page_token' in results and len(all_places) < max_results:
                    time.sleep(2)  # Required delay for next_page_token
                    results = self.gmaps.places_nearby(
                        location=(center_lat, center_lng),
                        radius=radius,
                        type=place_type,
                        keyword=keyword,
                        page_token=results['next_page_token']
                    )
                    all_places.extend(results.get('results', []))
                    
        except Exception as e:
            print(f"Error searching places: {e}")
        
        # Also try text search if keyword is provided (as fallback)
        if keyword and len(all_places) < max_results:
            try:
                # Format bounds for text search
                bounds_str = f"{bounds['southwest']['lat']},{bounds['southwest']['lng']}|{bounds['northeast']['lat']},{bounds['northeast']['lng']}"
                text_results = self.gmaps.places(
                    query=keyword,
                    location=(center_lat, center_lng),
                    radius=radius
                )
                all_places.extend(text_results.get('results', []))
            except Exception as e:
                print(f"Error in text search: {e}")
        
        # Remove duplicates based on place_id
        seen_ids = set()
        unique_places = []
        for place in all_places:
            if place.get('place_id') not in seen_ids:
                seen_ids.add(place.get('place_id'))
                unique_places.append(place)
        
        return unique_places[:max_results]
    
    def count_eateries(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count eateries (restaurants, juice shops, food shops) in polygon
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of eateries
        """
        bounds = self.get_polygon_bounds(polygon)
        eateries = []
        
        # Search for restaurants
        restaurant_places = self.search_places_in_bounds(
            bounds, 
            place_types=['restaurant', 'food', 'cafe', 'meal_takeaway'],
            max_results=60
        )
        
        # Also search with keywords for juice shops and food shops
        keyword_searches = ['juice', 'food shop', 'food court', 'dining']
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            restaurant_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        for place in restaurant_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    # Additional filtering by name/type
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    if any(t in ['restaurant', 'food', 'cafe', 'meal_takeaway', 'bakery', 'bar'] 
                           for t in place_types) or \
                       any(kw in place_name for kw in ['restaurant', 'cafe', 'juice', 'food', 'dining', 'bistro']):
                        eateries.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_eateries = []
        for eatery in eateries:
            if eatery.get('place_id') not in seen_ids:
                seen_ids.add(eatery.get('place_id'))
                unique_eateries.append(eatery)
        
        return len(unique_eateries)
    
    def count_offices(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count offices: corporate office, company, technical company, insurance company, 
        co-working space, software company
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of offices
        """
        bounds = self.get_polygon_bounds(polygon)
        offices = []
        
        # Search for establishments and points of interest
        office_places = self.search_places_in_bounds(
            bounds,
            place_types=['establishment', 'point_of_interest'],
            max_results=60
        )
        
        # Search with specific keywords for offices
        keyword_searches = [
            'corporate office',
            'company',
            'technical company',
            'insurance company',
            'co-working space',
            'coworking space',
            'software company',
            'co-working',
            'coworking'
        ]
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            office_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        # and match office criteria
        for place in office_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    
                    # Check if it's an office-related place based on specific criteria
                    is_office = False
                    
                    # Specific office keywords to match
                    office_keywords = [
                        'corporate office',
                        'company',
                        'technical company',
                        'insurance company',
                        'co-working space',
                        'coworking space',
                        'software company',
                        'co-working',
                        'coworking',
                        'corporate',
                        'ltd',
                        'inc',
                        'corporation',
                        'pvt',
                        'limited',
                        'pvt ltd',
                        'private limited'
                    ]
                    
                    # Check if name contains any office keywords
                    if any(kw in place_name for kw in office_keywords):
                        is_office = True
                    
                    # Also check if name ends with 'company' or contains 'software'
                    if place_name.endswith('company') or 'software' in place_name:
                        is_office = True
                    
                    # Exclude non-office establishments
                    excluded_types = ['restaurant', 'cafe', 'food', 'store', 'shopping_mall', 
                                     'hospital', 'school', 'university', 'park', 'church', 'mosque',
                                     'temple', 'gas_station', 'atm', 'bank', 'lodging']
                    excluded_keywords = ['restaurant', 'cafe', 'hotel', 'resort', 'mall', 'store']
                    
                    # If it has excluded types or keywords, don't count as office
                    if any(t in place_types for t in excluded_types):
                        is_office = False
                    if any(kw in place_name for kw in excluded_keywords):
                        is_office = False
                    
                    if is_office:
                        offices.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_offices = []
        for office in offices:
            if office.get('place_id') not in seen_ids:
                seen_ids.add(office.get('place_id'))
                unique_offices.append(office)
        
        return len(unique_offices)
    
    def count_apartments(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count apartments: apartment buildings, apartment complex, residency, 
        residential building, apartment, residential, complex, residence
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of apartments
        """
        bounds = self.get_polygon_bounds(polygon)
        apartments = []
        
        # Search for lodging and residential places
        apartment_places = self.search_places_in_bounds(
            bounds,
            place_types=['lodging'],
            max_results=60
        )
        
        # Search with specific keywords for apartments only
        keyword_searches = [
            'apartment building',
            'apartment buildings',
            'apartment complex',
            'residency',
            'residential building',
            'residential buildings',
            'apartment',
            'apartments',
            'residential',
            'complex',
            'residence'
        ]
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            apartment_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        for place in apartment_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    
                    # Check if it's an apartment/residential place
                    is_apartment = False
                    
                    # Specific apartment keywords to match
                    apartment_keywords = [
                        'apartment building',
                        'apartment buildings',
                        'apartment complex',
                        'residency',
                        'residential building',
                        'residential buildings',
                        'apartment',
                        'apartments',
                        'residential',
                        'complex',
                        'residence'
                    ]
                    
                    # Check if name contains any apartment keywords
                    if any(kw in place_name for kw in apartment_keywords):
                        is_apartment = True
                    
                    # Check by type - lodging places that match apartment criteria
                    if 'lodging' in place_types:
                        # Include if it has apartment keywords
                        if any(kw in place_name for kw in apartment_keywords):
                            is_apartment = True
                        # Exclude hotels, resorts, PGs, hostels unless they have apartment keywords
                        elif 'hotel' not in place_name and 'resort' not in place_name and \
                             'pg' not in place_name and 'hostel' not in place_name and \
                             'paying guest' not in place_name and 'co-living' not in place_name:
                            # Could be residential apartment, include it
                            is_apartment = True
                    
                    # Exclude if it's clearly a hotel/resort/PG without apartment keywords
                    if ('hotel' in place_name or 'resort' in place_name or 
                        'pg' in place_name or 'hostel' in place_name or 
                        'paying guest' in place_name or 'co-living' in place_name) and \
                       not any(kw in place_name for kw in ['apartment', 'residential']):
                        is_apartment = False
                    
                    if is_apartment:
                        apartments.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_apartments = []
        for apartment in apartments:
            if apartment.get('place_id') not in seen_ids:
                seen_ids.add(apartment.get('place_id'))
                unique_apartments.append(apartment)
        
        return len(unique_apartments)
    
    def count_pgs(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count PGs: PG, PGs, pg, pgs, hostel, hostels, co-living, coliving, 
        paying guest, service apartments
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of PGs
        """
        bounds = self.get_polygon_bounds(polygon)
        pgs = []
        
        # Search for lodging places
        pg_places = self.search_places_in_bounds(
            bounds,
            place_types=['lodging'],
            max_results=60
        )
        
        # Search with specific keywords for PGs
        keyword_searches = [
            'PG',
            'PGs',
            'pg',
            'pgs',
            'hostel',
            'hostels',
            'co-living',
            'coliving',
            'paying guest',
            'service apartment',
            'service apartments'
        ]
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            pg_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        for place in pg_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    
                    # Check if it's a PG/hostel/co-living place
                    is_pg = False
                    
                    # Specific PG keywords to match
                    pg_keywords = [
                        'pg',
                        'pgs',
                        'hostel',
                        'hostels',
                        'co-living',
                        'coliving',
                        'paying guest',
                        'service apartment',
                        'service apartments'
                    ]
                    
                    # Check if name contains any PG keywords
                    if any(kw in place_name for kw in pg_keywords):
                        is_pg = True
                    
                    # Check by type - lodging places that match PG criteria
                    if 'lodging' in place_types:
                        # Include if it has PG keywords
                        if any(kw in place_name for kw in pg_keywords):
                            is_pg = True
                        # Include PGs and hostels (even if they don't have explicit keywords in some cases)
                        elif 'pg' in place_name or 'hostel' in place_name or 'paying guest' in place_name:
                            is_pg = True
                        # Exclude hotels and resorts unless they have PG/service apartment keywords
                        elif 'hotel' not in place_name and 'resort' not in place_name:
                            # Could be PG or service apartment, check more carefully
                            if 'service' in place_name and 'apartment' in place_name:
                                is_pg = True
                    
                    # Exclude if it's clearly a hotel/resort without PG keywords
                    if ('hotel' in place_name or 'resort' in place_name) and \
                       not any(kw in place_name for kw in ['pg', 'hostel', 'service apartment', 'paying guest']):
                        is_pg = False
                    
                    # Exclude regular apartments (not service apartments)
                    if 'apartment' in place_name and 'service' not in place_name and \
                       not any(kw in place_name for kw in ['pg', 'hostel', 'paying guest']):
                        is_pg = False
                    
                    if is_pg:
                        pgs.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_pgs = []
        for pg in pgs:
            if pg.get('place_id') not in seen_ids:
                seen_ids.add(pg.get('place_id'))
                unique_pgs.append(pg)
        
        return len(unique_pgs)
    
    def count_gyms(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count gyms: gym, fitness centres, sports complex
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of gyms
        """
        bounds = self.get_polygon_bounds(polygon)
        gyms = []
        
        # Search for gym and fitness related places
        gym_places = self.search_places_in_bounds(
            bounds,
            place_types=['gym'],
            max_results=60
        )
        
        # Search with specific keywords for gyms
        keyword_searches = [
            'gym',
            'fitness centre',
            'fitness center',
            'fitness centres',
            'fitness centers',
            'sports complex',
            'fitness',
            'workout'
        ]
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            gym_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        for place in gym_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    
                    # Check if it's a gym/fitness place
                    is_gym = False
                    
                    # Check by type
                    if 'gym' in place_types:
                        is_gym = True
                    
                    # Check by name keywords
                    gym_keywords = [
                        'gym',
                        'fitness centre',
                        'fitness center',
                        'fitness centres',
                        'fitness centers',
                        'sports complex',
                        'fitness',
                        'workout',
                        'health club',
                        'athletic club',
                        'training center',
                        'training centre'
                    ]
                    if any(kw in place_name for kw in gym_keywords):
                        is_gym = True
                    
                    if is_gym:
                        gyms.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_gyms = []
        for gym in gyms:
            if gym.get('place_id') not in seen_ids:
                seen_ids.add(gym.get('place_id'))
                unique_gyms.append(gym)
        
        return len(unique_gyms)
    
    def count_salons(self, polygon: List[Tuple[float, float]]) -> int:
        """
        Count salons: beauty salon, hair salon, barber shop, spa
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            Count of salons
        """
        bounds = self.get_polygon_bounds(polygon)
        salons = []
        
        # Search for salon related places
        salon_places = self.search_places_in_bounds(
            bounds,
            place_types=['beauty_salon', 'hair_care'],
            max_results=60
        )
        
        # Search with specific keywords for salons
        keyword_searches = [
            'salon',
            'beauty salon',
            'hair salon',
            'barber',
            'barber shop',
            'haircut',
            'spa',
            'beauty parlor',
            'beauty parlour',
            'hair care',
            'haircutting',
            'hair styling',
            'unisex salon'
        ]
        for keyword in keyword_searches:
            keyword_places = self.search_places_in_bounds(
                bounds,
                keyword=keyword,
                max_results=60
            )
            salon_places.extend(keyword_places)
        
        # Filter places that are actually inside the polygon (ONLY points inside polygon are counted)
        for place in salon_places:
            location = place.get('geometry', {}).get('location', {})
            if location:
                point = (location.get('lat'), location.get('lng'))
                # Only count if point is inside the polygon
                if self.point_in_polygon(point, polygon):
                    place_name = place.get('name', '').lower()
                    place_types = [t.lower() for t in place.get('types', [])]
                    
                    # Check if it's a salon/beauty place
                    is_salon = False
                    
                    # Check by type
                    salon_types = [
                        'beauty_salon',
                        'hair_care',
                        'spa',
                        'hair_salon',
                        'barber'
                    ]
                    if any(st in place_types for st in salon_types):
                        is_salon = True
                    
                    # Check by name keywords
                    salon_keywords = [
                        'salon',
                        'beauty salon',
                        'hair salon',
                        'barber',
                        'barber shop',
                        'haircut',
                        'spa',
                        'beauty parlor',
                        'beauty parlour',
                        'hair care',
                        'haircutting',
                        'hair styling',
                        'unisex salon',
                        'hair dresser',
                        'hair dresser',
                        'haircut salon',
                        'beauty center',
                        'beauty centre'
                    ]
                    if any(kw in place_name for kw in salon_keywords):
                        is_salon = True
                    
                    # Exclude places that are clearly not salons
                    exclude_keywords = [
                        'nail',
                        'nail art',
                        'nail salon'  # Only exclude if it's ONLY nail-related
                    ]
                    # Only exclude if it's ONLY nail-related and nothing else
                    if any(ekw in place_name for ekw in exclude_keywords) and \
                       not any(skw in place_name for skw in ['salon', 'hair', 'barber', 'beauty']):
                        is_salon = False
                    
                    if is_salon:
                        salons.append(place)
        
        # Remove duplicates
        seen_ids = set()
        unique_salons = []
        for salon in salons:
            if salon.get('place_id') not in seen_ids:
                seen_ids.add(salon.get('place_id'))
                unique_salons.append(salon)
        
        return len(unique_salons)
    
    def generate_mapbox_isochrone(self,
                                  center_lat: float,
                                  center_lng: float,
                                  time_limit_minutes: int,
                                  mapbox_token: str,
                                  profile: str = "driving",
                                  denoise: float = 0.0,
                                  generalize_meters: float = 0,
                                  depart_at: Optional[str] = None) -> Optional[str]:
        """
        Generate isochrone polygon using Mapbox Isochrone API.
        Returns WKT string of the polygon.
        
        Args:
            center_lat: Origin latitude
            center_lng: Origin longitude
            time_limit_minutes: Time limit in minutes
            mapbox_token: Mapbox API token
            profile: Routing profile (driving, driving-traffic, walking, cycling)
            denoise: Denoise parameter (0.0 = highest fidelity)
            generalize_meters: Generalize parameter (0 = no generalization, higher = more simplified)
            depart_at: Departure time in ISO 8601 format (e.g., "2026-01-13T18:00") for traffic-aware routing
            
        Returns:
            WKT string of the polygon, or None if failed
        """
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        # Create session with retries
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=0.7,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset(["GET"])
        )
        session.mount("https://", HTTPAdapter(max_retries=retries))
        session.mount("http://", HTTPAdapter(max_retries=retries))
        
        # Mapbox API endpoint
        url = f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/{center_lng},{center_lat}"
        params = {
            "contours_minutes": str(time_limit_minutes),
            "polygons": "true",
            "denoise": str(denoise),
            "generalize": str(generalize_meters),
            "access_token": mapbox_token,
        }
        
        # Add depart_at parameter if provided (for traffic-aware routing)
        if depart_at:
            params["depart_at"] = depart_at
        
        try:
            response = session.get(url, params=params, timeout=30)
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(
                "ConnectionError: Could not reach api.mapbox.com. This is usually DNS/proxy/VPN.\n"
                "Try: nslookup api.mapbox.com, curl -I https://api.mapbox.com, or set HTTPS_PROXY.\n"
                f"Raw error: {e}"
            ) from e
        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"Timeout calling Mapbox: {e}") from e
        
        if response.status_code != 200:
            raise RuntimeError(f"Mapbox HTTP {response.status_code}: {response.text[:800]}")
        
        data = response.json()
        if not data.get("features"):
            raise RuntimeError(f"Unexpected response: {str(data)[:800]}")
        
        # Extract polygon ring
        feature = data["features"][0]
        geom = feature.get("geometry") or {}
        gtype = geom.get("type")
        coords = geom.get("coordinates") or []
        
        ring = None
        if gtype == "Polygon":
            ring = coords[0] if coords and coords[0] else None
        elif gtype == "MultiPolygon":
            best, best_len = None, -1
            for poly in coords:
                if poly and poly[0]:
                    ring_candidate = poly[0]
                    if len(ring_candidate) > best_len:
                        best, best_len = ring_candidate, len(ring_candidate)
            ring = best
        
        if not ring:
            raise RuntimeError("Could not extract polygon ring from Mapbox response.")
        
        # Ensure closed ring
        if ring[0] != ring[-1]:
            ring = ring + [ring[0]]
        
        # Convert to WKT (lon lat format)
        coord_str = ", ".join([f"{lon} {lat}" for lon, lat in ring])
        wkt = f"POLYGON (({coord_str}))"
        
        return wkt
    
    def generate_isochrone(self,
                          center_lat: float,
                          center_lng: float,
                          time_limit_minutes: int,
                          grid_resolution: int = 50,
                          travel_mode: str = "TWO_WHEELER") -> List[Tuple[float, float]]:
        """
        Generate an isochrone polygon (area reachable within the time limit).
        Uses a fixed 50x50 grid, evaluates from perimeter (outside) to center,
        and stops early when boundary is found.
        
        Note: Uses DRIVE mode primarily, with automatic fallback to TWO_WHEELER
        mode if DRIVE is not available.
        """
        if time_limit_minutes < 1 or time_limit_minutes > 20:
            raise ValueError("Time limit must be between 1 and 20 minutes")

        time_limit_seconds = time_limit_minutes * 60

        # Estimate a generous search radius (m) so we don't miss reachable points.
        # Use a slightly optimistic average speed (~30 km/h = 8.3 m/s) with buffer.
        avg_speed_ms = 8.3
        search_radius_m = time_limit_seconds * avg_speed_ms * 1.3

        # Generate fixed 50x50 grid
        candidate_points = self._generate_candidate_points(
            center_lat, center_lng, search_radius_m, grid_resolution=50
        )

        if not candidate_points:
            raise ValueError("Unable to generate candidate points for isochrone calculation.")

        # Sort points by distance from center (furthest first - perimeter to center)
        candidate_points_with_distance = [
            (point, self._haversine_distance(center_lat, center_lng, point[0], point[1]))
            for point in candidate_points
        ]
        candidate_points_with_distance.sort(key=lambda x: x[1], reverse=True)  # Furthest first
        
        # Extract sorted points (outside to inside)
        sorted_candidate_points = [point for point, _ in candidate_points_with_distance]

        reachable_points: List[Tuple[float, float]] = []
        total_candidates = len(sorted_candidate_points)
        api_failures = 0
        api_successes = 0
        points_over_limit = 0
        two_wheeler_failures = 0
        drive_failures = 0
        last_error_message = None

        # Evaluate points from outside to inside (perimeter to center)
        for idx, point in enumerate(sorted_candidate_points, start=1):
            duration_seconds, mode_used, error_msg = self._get_travel_time_seconds_with_fallback(
                origin=(center_lat, center_lng),
                destination=point,
                travel_mode=travel_mode
            )

            if duration_seconds is None:
                api_failures += 1
                if error_msg:
                    last_error_message = error_msg
                if mode_used == "TWO_WHEELER":
                    two_wheeler_failures += 1
                elif mode_used == "DRIVE":
                    drive_failures += 1
            else:
                api_successes += 1
                if duration_seconds <= time_limit_seconds:
                    reachable_points.append(point)
                else:
                    points_over_limit += 1

            time.sleep(0.05)  # Gentle rate limiting

        # Diagnostic information
        print(f"Diagnostics: {api_successes} successful API calls, {api_failures} failures, "
              f"{len(reachable_points)} reachable points, {points_over_limit} points over time limit")
        print(f"Mode failures: TWO_WHEELER={two_wheeler_failures}, DRIVE={drive_failures}")

        # If we have very few reachable points, provide more helpful error message
        if len(reachable_points) < 3:
            error_msg = (
                f"Not enough reachable points found ({len(reachable_points)}/3 minimum).\n"
                f"Diagnostics: {api_successes} successful API calls, {api_failures} failures.\n"
            )
            
            if api_failures > api_successes:
                error_msg += (
                    f"⚠️ All API calls failed (TWO_WHEELER: {two_wheeler_failures}, DRIVE: {drive_failures}).\n\n"
                    "Possible issues:\n"
                    "1. API key may not have Routes API enabled\n"
                    "2. API key may be invalid or expired\n"
                    "3. Network connectivity issues\n"
                    "4. API quota exceeded\n\n"
                )
                if last_error_message:
                    error_msg += f"Last error: {last_error_message}\n\n"
                error_msg += (
                    "💡 Solutions:\n"
                    "- Verify your API key has Routes API enabled in Google Cloud Console\n"
                    "- Check API key billing/quota status\n"
                    "- Verify network connectivity\n"
                    "- Try with a different API key\n"
                )
            elif points_over_limit > len(reachable_points):
                error_msg += (
                    f"⚠️ Most points ({points_over_limit}) exceed the time limit ({time_limit_minutes} min).\n"
                    "💡 Try increasing the time limit or using a smaller search area.\n"
                )
            else:
                error_msg += (
                    "💡 Suggestions:\n"
                    "- Increase the time limit (try 15-20 minutes)\n"
                    "- Increase grid resolution (try 20-25)\n"
                )
            
            raise ValueError(error_msg)

        multipoint = MultiPoint([(lng, lat) for lat, lng in reachable_points])
        polygon = multipoint.convex_hull

        if polygon.is_empty:
            raise ValueError("Generated polygon is empty. Unable to construct geofence.")

        coords = list(polygon.exterior.coords)
        lat_lng_coords = [(lat, lng) for (lng, lat) in coords]

        return lat_lng_coords

    def _generate_candidate_points(self,
                                   center_lat: float,
                                   center_lng: float,
                                   radius_m: float,
                                   grid_resolution: int) -> List[Tuple[float, float]]:
        """
        Generate a grid of candidate latitude/longitude pairs around the center.
        Points outside the circular search radius are discarded.
        """
        lat_span = radius_m / 111000  # Rough conversion meters -> degrees latitude
        lng_span = radius_m / (111000 * max(math.cos(math.radians(center_lat)), 0.0001))

        lat_values = np.linspace(center_lat - lat_span, center_lat + lat_span, grid_resolution)
        lng_values = np.linspace(center_lng - lng_span, center_lng + lng_span, grid_resolution)

        points = []
        for lat in lat_values:
            for lng in lng_values:
                if self._haversine_distance(center_lat, center_lng, lat, lng) <= radius_m:
                    points.append((float(lat), float(lng)))

        return points

    def _get_travel_time_seconds_with_fallback(self,
                                                origin: Tuple[float, float],
                                                destination: Tuple[float, float],
                                                travel_mode: str = "TWO_WHEELER") -> Tuple[Optional[float], str, Optional[str]]:
        """
        Get travel time with fallback. Returns (duration_seconds, mode_used, error_message).
        Prioritizes DRIVE mode first, falls back to TWO_WHEELER if DRIVE fails.
        """
        # Try DRIVE first (prioritized)
        result = self._get_travel_time_seconds(origin, destination, "DRIVE")
        if result is not None:
            return (result, "DRIVE", None)
        # Try TWO_WHEELER as fallback
        result = self._get_travel_time_seconds(origin, destination, "TWO_WHEELER")
        if result is not None:
            return (result, "TWO_WHEELER", None)
        # Both modes failed - try to get a sample error message
        error_msg = self._test_api_connection(origin, destination)
        return (None, "TWO_WHEELER", error_msg or "Both DRIVE and TWO_WHEELER modes failed")
    
    def _test_api_connection(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Optional[str]:
        """Test API connection and return error message if any."""
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration"
        }
        
        payload = {
            "origin": {"location": {"latLng": {"latitude": float(origin[0]), "longitude": float(origin[1])}}},
            "destination": {"location": {"latLng": {"latitude": float(destination[0]), "longitude": float(destination[1])}}},
            "travelMode": "DRIVE"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and "error" in error_data:
                        err = error_data["error"]
                        return f"API Error ({err.get('code', '?')}): {err.get('message', 'Unknown')}"
                except:
                    return f"HTTP {response.status_code}: {response.text[:200]}"
        except requests.RequestException as exc:
            return f"Network error: {str(exc)}"
        
        return None
    
    def _get_travel_time_seconds(self,
                                 origin: Tuple[float, float],
                                 destination: Tuple[float, float],
                                 travel_mode: str = "TWO_WHEELER") -> Optional[float]:
        """
        Call Google Routes API (computeRoutes) and return travel time in seconds.
        Returns None on failure. Fallback is handled by _get_travel_time_seconds_with_fallback.
        """
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "routes.duration,"
                "routes.distanceMeters,"
                "routes.legs.duration,"
                "routes.legs.distanceMeters"
            )
        }

        # Try the specified mode (fallback is handled by _get_travel_time_seconds_with_fallback)
        mode = travel_mode
        # Build payload with enhanced traffic-aware routing
        # Use 6 PM (18:00) for traffic-aware routing to consider evening rush hour conditions
        now = datetime.datetime.now(datetime.timezone.utc)
        # Set time to 6 PM (18:00) while keeping today's date
        traffic_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        payload = {
            "origin": {"location": {"latLng": {"latitude": float(origin[0]), "longitude": float(origin[1])}}},
            "destination": {"location": {"latLng": {"latitude": float(destination[0]), "longitude": float(destination[1])}}},
            "travelMode": mode,
            "routingPreference": "TRAFFIC_AWARE",
            "trafficModel": "BEST_GUESS",  # Uses traffic conditions at 6 PM
            "departureTime": traffic_time.strftime("%Y-%m-%dT%H:%M:%SZ")  # 6 PM for traffic consideration
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
        except requests.RequestException as exc:
            return None

        if response.status_code != 200:
            return None

        try:
            data = response.json()
        except ValueError:
            return None

        if isinstance(data, dict) and "error" in data:
            return None

        routes = data.get("routes", [])
        if not routes:
            return None

        route = routes[0]
        duration_seconds = self._parse_duration_seconds(route.get("duration"))

        if duration_seconds is None:
            leg_total = 0.0
            for leg in route.get("legs", []):
                leg_dur = self._parse_duration_seconds(leg.get("duration"))
                if leg_dur is not None:
                    leg_total += leg_dur
            duration_seconds = leg_total if leg_total > 0 else None

        return duration_seconds

    @staticmethod
    def _parse_duration_seconds(duration_value) -> Optional[float]:
        """
        Parse the duration field returned by the Routes API. Supports multiple formats.
        """
        if duration_value is None:
            return None

        if isinstance(duration_value, (int, float)):
            return float(duration_value)

        if isinstance(duration_value, str):
            duration_value = duration_value.strip()
            if duration_value.endswith("s"):
                try:
                    return float(duration_value[:-1])
                except ValueError:
                    return None
            try:
                return float(duration_value)
            except ValueError:
                return None

        if isinstance(duration_value, dict):
            if "seconds" in duration_value:
                return float(duration_value["seconds"])
            if "value" in duration_value:
                return float(duration_value["value"])

        return None

    @staticmethod
    def _haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Great-circle distance between two points (meters).
        """
        R = 6371000  # meters
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        d_lat = lat2_rad - lat1_rad
        d_lng = math.radians(lng2 - lng1)

        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(d_lng / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
    
    def polygon_to_wkt(self, polygon: List[Tuple[float, float]]) -> str:
        """
        Convert polygon coordinates to WKT format
        
        Args:
            polygon: List of (lat, lng) tuples
            
        Returns:
            WKT string: POLYGON((lng1 lat1, lng2 lat2, ...))
        """
        if len(polygon) < 3:
            raise ValueError("Polygon must have at least 3 points")
        
        # WKT format: POLYGON((lng lat, lng lat, ...))
        coords_str = ", ".join([f"{lng} {lat}" for lat, lng in polygon])
        return f"POLYGON(({coords_str}))"
    
    def analyze_polygon(self, polygon: List[Tuple[float, float]], polygon_id: str = None) -> Dict:
        """
        Analyze a single polygon and return counts
        
        Args:
            polygon: List of (lat, lng) tuples
            polygon_id: Optional identifier for the polygon
            
        Returns:
            Dictionary with counts for each category
        """
        print(f"Analyzing polygon {polygon_id or 'Unknown'}...")
        
        eateries_count = self.count_eateries(polygon)
        print(f"  Found {eateries_count} eateries")
        
        offices_count = self.count_offices(polygon)
        print(f"  Found {offices_count} offices")
        
        apartments_count = self.count_apartments(polygon)
        print(f"  Found {apartments_count} apartments")
        
        pgs_count = self.count_pgs(polygon)
        print(f"  Found {pgs_count} PGs")
        
        gyms_count = self.count_gyms(polygon)
        print(f"  Found {gyms_count} gyms")
        
        salons_count = self.count_salons(polygon)
        print(f"  Found {salons_count} salons")
        
        return {
            'polygon_id': polygon_id or 'Unknown',
            'eateries': eateries_count,
            'offices': offices_count,
            'apartments': apartments_count,
            'pgs': pgs_count,
            'gyms': gyms_count,
            'salons': salons_count
        }
    
    def analyze_multiple_polygons(self, polygons: List[List[Tuple[float, float]]], 
                                  polygon_ids: List[str] = None) -> pd.DataFrame:
        """
        Analyze multiple polygons and return results as DataFrame
        
        Args:
            polygons: List of polygons, where each polygon is a list of (lat, lng) tuples
            polygon_ids: Optional list of identifiers for each polygon
            
        Returns:
            DataFrame with columns: polygon_id, eateries, offices, apartments, pgs, gyms
        """
        if polygon_ids is None:
            polygon_ids = [f"Polygon_{i+1}" for i in range(len(polygons))]
        
        results = []
        total = len(polygons)
        for i, polygon in enumerate(polygons):
            print(f"\n[{i+1}/{total}] Processing {polygon_ids[i]}...")
            result = self.analyze_polygon(polygon, polygon_ids[i])
            results.append(result)
            print(f"  ✅ Completed: {result['eateries']} eateries, {result['offices']} offices, {result['apartments']} apartments, {result['pgs']} PGs")
            if i < total - 1:  # Don't sleep after last polygon
                time.sleep(1)  # Rate limiting
        
        df = pd.DataFrame(results)
        return df
    
    def process_csv_file(self, input_csv_path: str, output_csv_path: str = None) -> pd.DataFrame:
        """
        Process a CSV file with WKT polygons and return results DataFrame
        
        Args:
            input_csv_path: Path to input CSV file with 'WKT' and 'name' columns
            output_csv_path: Optional path to save output CSV
            
        Returns:
            DataFrame with original columns plus 'no. of eateries', 'no. of offices', 'no. of apartments', 'no. of PGs', 'no. of gyms', 'no. of salons'
        """
        # Read input CSV
        df = pd.read_csv(input_csv_path)
        
        # Validate required columns
        if 'WKT' not in df.columns:
            raise ValueError("CSV must contain 'WKT' column")
        if 'name' not in df.columns:
            raise ValueError("CSV must contain 'name' column")
        
        # Parse WKT polygons and analyze
        results = []
        for idx, row in df.iterrows():
            wkt_string = str(row['WKT'])
            polygon_name = str(row['name'])
            
            try:
                # Parse WKT to polygon coordinates
                polygon = self.parse_wkt_polygon(wkt_string)
                
                if len(polygon) < 3:
                    print(f"Warning: Polygon '{polygon_name}' has less than 3 points, skipping...")
                    results.append({
                        'name': polygon_name,
                        'no. of eateries': 0,
                        'no. of offices': 0,
                        'no. of apartments': 0,
                        'no. of PGs': 0,
                        'no. of gyms': 0,
                        'no. of salons': 0
                    })
                    continue
                
                # Analyze polygon
                analysis = self.analyze_polygon(polygon, polygon_name)
                
                results.append({
                    'name': polygon_name,
                    'no. of eateries': analysis['eateries'],
                    'no. of offices': analysis['offices'],
                    'no. of apartments': analysis['apartments'],
                    'no. of PGs': analysis['pgs'],
                    'no. of gyms': analysis['gyms'],
                    'no. of salons': analysis['salons']
                })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing polygon '{polygon_name}': {e}")
                results.append({
                    'name': polygon_name,
                    'no. of eateries': 0,
                    'no. of offices': 0,
                    'no. of apartments': 0,
                    'no. of PGs': 0,
                    'no. of gyms': 0,
                    'no. of salons': 0
                })
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Merge with original DataFrame (preserve all original columns)
        # Use 'name' as the key for merging
        output_df = df.merge(results_df, on='name', how='left')
        
        # Reorder columns: original columns first, then new analysis columns
        original_cols = [col for col in df.columns]
        new_cols = ['no. of eateries', 'no. of offices', 'no. of apartments', 'no. of PGs', 'no. of gyms', 'no. of salons']
        column_order = original_cols + new_cols
        output_df = output_df[column_order]
        
        # Save to CSV if output path provided
        if output_csv_path:
            output_df.to_csv(output_csv_path, index=False)
            print(f"Results saved to '{output_csv_path}'")
        
        return output_df


def main():
    """
    Example usage of PolygonAnalyzer
    """
    API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"
    
    analyzer = PolygonAnalyzer(API_KEY)
    
    # Example: Define polygons as lists of (lat, lng) coordinates
    # Replace these with your actual polygon coordinates
    example_polygon_1 = [
        (28.6139, 77.2090),  # Example coordinates (Delhi)
        (28.6149, 77.2100),
        (28.6159, 77.2090),
        (28.6149, 77.2080),
    ]
    
    example_polygon_2 = [
        (28.6239, 77.2190),
        (28.6249, 77.2200),
        (28.6259, 77.2190),
        (28.6249, 77.2180),
    ]
    
    polygons = [example_polygon_1, example_polygon_2]
    polygon_ids = ["Area_1", "Area_2"]
    
    # Analyze polygons
    results_df = analyzer.analyze_multiple_polygons(polygons, polygon_ids)
    
    # Save to CSV
    results_df.to_csv('polygon_analysis_results.csv', index=False)
    print("\nResults saved to 'polygon_analysis_results.csv'")
    print("\nResults:")
    print(results_df)


if __name__ == "__main__":
    main()
