# Google APIs Used in This Project

This document lists all Google Maps APIs used in the codebase and their purposes.

---

## 📍 **1. Google Places API (Nearby Search)**

**Endpoint:** `places_nearby`  
**Library Method:** `gmaps.places_nearby()`  
**Purpose:** Search for places near a location within a radius

**Used For:**
- Finding eateries (restaurants, cafes, food places)
- Finding offices (companies, co-working spaces)
- Finding apartments (residential buildings, PGs, hostels)
- Finding gyms (fitness centers, sports complexes)

**Parameters Used:**
- `location`: Center point (lat, lng)
- `radius`: Search radius in meters (max 50,000m)
- `type`: Place type (e.g., 'restaurant', 'gym', 'lodging')
- `keyword`: Optional keyword filter
- `page_token`: For pagination (next page of results)

**Location in Code:**
- `polygon_analyzer.py` - `search_places_in_bounds()` method
- Lines: ~181, ~193

**API Documentation:**
- https://developers.google.com/maps/documentation/places/web-service/search-nearby

---

## 📍 **2. Google Places API (Text Search)**

**Endpoint:** `places` (Text Search)  
**Library Method:** `gmaps.places()`  
**Purpose:** Search for places by text query

**Used For:**
- Fallback search when keyword-based searches are needed
- Finding places by name or description

**Parameters Used:**
- `query`: Search query string
- `location`: Center point (lat, lng)
- `radius`: Search radius in meters

**Location in Code:**
- `polygon_analyzer.py` - `search_places_in_bounds()` method
- Line: ~210

**API Documentation:**
- https://developers.google.com/maps/documentation/places/web-service/search-text

---

## 🗺️ **3. Google Routes API (v2)**

**Endpoint:** `https://routes.googleapis.com/directions/v2:computeRoutes`  
**Method:** REST API (POST request)  
**Purpose:** Calculate routes and travel times using TWO_WHEELER mode

**Used For:**
- Generating isochrone polygons (Geo Mapping page)
- Finding travel time by two-wheeler between two points
- Primary method for isochrone generation

**Parameters Used:**
- `origin`: Starting point (latLng)
- `destination`: End point (latLng)
- `travelMode`: "TWO_WHEELER"
- `routingPreference`: "TRAFFIC_AWARE"
- `X-Goog-FieldMask`: "routes.duration,routes.distanceMeters"

**Location in Code:**
- `polygon_analyzer.py` - `_find_boundary_point()` method
- Lines: ~701-729

**API Documentation:**
- https://developers.google.com/maps/documentation/routes/route-two-wheel

**Note:** This is the newer Routes API that supports TWO_WHEELER mode specifically.

---

## 🚴 **4. Google Directions API (Legacy)**

**Endpoint:** `directions`  
**Library Method:** `gmaps.directions()`  
**Purpose:** Calculate routes and travel times (fallback method)

**Used For:**
- Fallback when Routes API fails
- Uses "bicycling" mode as approximation for two-wheelers

**Parameters Used:**
- `origin`: Starting point (lat, lng)
- `destination`: End point (lat, lng)
- `mode`: "bicycling"
- `alternatives`: False

**Location in Code:**
- `polygon_analyzer.py` - `_find_boundary_point()` method
- Line: ~749

**API Documentation:**
- https://developers.google.com/maps/documentation/directions

**Note:** Used as fallback when Routes API is unavailable or fails.

---

## 📊 Summary Table

| API | Purpose | Used In | Primary/Backup |
|-----|---------|---------|----------------|
| **Places API (Nearby Search)** | Find places by type/location | Geo Metrics page | Primary |
| **Places API (Text Search)** | Find places by keyword | Geo Metrics page | Fallback |
| **Routes API v2** | Calculate two-wheeler routes | Geo Mapping page | Primary |
| **Directions API** | Calculate routes (bicycling) | Geo Mapping page | Fallback |

---

## 🔑 API Key Requirements

Your API key needs to have the following APIs enabled in Google Cloud Console:

1. ✅ **Places API** (for Places Nearby Search and Text Search)
2. ✅ **Places API (New)** (if using new Places API)
3. ✅ **Routes API** (for TWO_WHEELER mode in isochrone generation)
4. ✅ **Directions API** (as fallback for Routes API)

---

## 💰 API Usage & Billing

### Geo Metrics Page:
- **Places API calls:** ~15-20 per polygon
  - Multiple searches per category (eateries, offices, apartments, gyms)
  - Each search may have pagination
- **Cost:** Standard Places API pricing

### Geo Mapping Page:
- **Routes API calls:** ~90 per polygon (one per bearing direction)
  - Each call may require multiple iterations (binary search)
  - Total: ~450-900 API calls per polygon
- **Cost:** Routes API pricing (TWO_WHEELER mode may have different rates)
- **Fallback:** Uses Directions API if Routes API fails

---

## 🔧 API Configuration

All APIs use the same API key:
- Configured in: `app.py` sidebar
- Default key: `AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI`
- Can be overridden in the web app sidebar

---

## 📝 Notes

1. **Routes API vs Directions API:**
   - Routes API (v2) is newer and supports TWO_WHEELER mode
   - Directions API is legacy but more widely supported
   - Code tries Routes API first, falls back to Directions API

2. **Rate Limiting:**
   - Places API: 2-second delay for pagination tokens
   - Routes/Directions API: 0.05-0.1 second delays between calls
   - Implemented to respect API quotas

3. **Error Handling:**
   - All API calls have try-except blocks
   - Fallback mechanisms in place
   - Errors are logged but don't stop processing
