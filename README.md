# Polygon Analyzer

This project analyzes the number of eateries, offices, and apartments within given polygons using the Google Places API.

## Features

- **Eateries Analysis**: Counts restaurants, cafes, juice shops, food shops, and dining establishments
- **Offices Analysis**: Counts co-working spaces, offices, workplaces, companies, organizations, and corporate offices
- **Apartments Analysis**: Counts apartments, societies, residential buildings, apartment complexes, and housing
- **PGs Analysis**: Counts paying guest accommodations, hostels, and co-living spaces
- **Gyms Analysis**: Counts gyms, fitness centers, and sports complexes
- **Salons Analysis**: Counts beauty salons, hair salons, and barber shops
- **Isochrone Generation**: Generates isochrone polygons using Mapbox API

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### API Server (Flask)

1. Set environment variables:
```bash
export GOOGLE_MAPS_API_KEY="your-api-key"
export MAPBOX_API_TOKEN="your-mapbox-token"  # Optional, for isochrone generation
```

2. Start the Flask API server:
```bash
python app.py
```

3. The API will be available at `http://localhost:5000`

4. API Endpoints:
   - `GET /` - Web interface (HTML page)
   - `GET /api/health` - Health check
   - `POST /api/analyze` - Analyze polygons from CSV file
   - `POST /api/isochrone` - Generate isochrone polygon

#### API Usage Examples

**Analyze Polygons:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@input.csv" \
  -F "google_maps_api_key=your-api-key"
```

**Generate Isochrone:**
```bash
curl -X POST http://localhost:5000/api/isochrone \
  -H "Content-Type: application/json" \
  -d '{
    "center_lat": 12.93526,
    "center_lng": 77.62262,
    "time_limit_minutes": 10,
    "polygon_name": "Kitchen 10-min Isochrone",
    "mapbox_token": "your-mapbox-token",
    "routing_profile": "driving",
    "generalize_meters": 0.0
  }'
```

### Vercel Deployment

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Set Environment Variables in Vercel Dashboard:**
   - Go to your project settings in Vercel
   - Navigate to "Environment Variables"
   - Add the following:
     - `GOOGLE_MAPS_API_KEY` - Your Google Maps API key
     - `MAPBOX_API_TOKEN` - Your Mapbox API token (optional)

   Or use Vercel CLI:
   ```bash
   vercel env add GOOGLE_MAPS_API_KEY
   vercel env add MAPBOX_API_TOKEN
   ```

5. **Production Deployment:**
   ```bash
   vercel --prod
   ```

**How Vercel Works:**
- Vercel automatically detects `app.py` as the Flask entry point
- The `vercel.json` configuration tells Vercel to:
  - Build the Python app using `@vercel/python`
  - Route all requests (`/(.*)`) to `app.py`
- Vercel runs your Flask app as a serverless function
- The Flask app instance (`app`) is automatically exported and served

### Python Script Usage

#### Process CSV File with WKT Polygons

```python
from polygon_analyzer import PolygonAnalyzer

# Initialize with your API key
API_KEY = "your-google-maps-api-key"
analyzer = PolygonAnalyzer(API_KEY)

# Process CSV file
results_df = analyzer.process_csv_file('input.csv', 'output.csv')
```

#### Direct Polygon Analysis

```python
from polygon_analyzer import PolygonAnalyzer

# Initialize with your API key
API_KEY = "your-google-maps-api-key"
analyzer = PolygonAnalyzer(API_KEY)

# Define polygons as lists of (latitude, longitude) tuples
polygon_1 = [
    (28.6139, 77.2090),
    (28.6149, 77.2100),
    (28.6159, 77.2090),
    (28.6149, 77.2080),
]

# Analyze multiple polygons
polygons = [polygon_1]
polygon_ids = ["Area_1"]

results_df = analyzer.analyze_multiple_polygons(polygons, polygon_ids)
```

### Input Format

#### CSV File Format
- **WKT column**: Polygon coordinates in WKT format
  - Format: `POLYGON((lng1 lat1, lng2 lat2, lng3 lat3, ...))`
  - Note: WKT uses (longitude, latitude) order
- **name column**: Identifier/name for each polygon

Example:
```csv
WKT,name
POLYGON((77.2090 28.6139, 77.2100 28.6149, 77.2090 28.6159, 77.2080 28.6149, 77.2090 28.6139)),Area_1
POLYGON((77.2190 28.6239, 77.2200 28.6249, 77.2190 28.6259, 77.2180 28.6249, 77.2190 28.6239)),Area_2
```

#### Direct Polygon Format
- List of `(latitude, longitude)` tuples
- Coordinates in decimal degrees (WGS84)

### Output Format

The analysis returns a pandas DataFrame with:
- All original columns from input CSV
- **Additional columns**:
  - `no. of eateries`: Count of eateries in the polygon
  - `no. of offices`: Count of offices in the polygon
  - `no. of apartments`: Count of apartments in the polygon
  - `no. of PGs`: Count of PGs in the polygon
  - `no. of gyms`: Count of gyms in the polygon
  - `no. of salons`: Count of salons in the polygon

## API Key

The Google Maps API key is required for polygon analysis. Make sure you have the following APIs enabled in your Google Cloud Console:
- Places API
- Places API (New)

For isochrone generation, you need a Mapbox API token (get one at https://account.mapbox.com/access-tokens/).

## Notes

- The script uses point-in-polygon checking to ensure accurate counts
- Rate limiting is implemented to respect API quotas
- Duplicate places are automatically filtered out
- The search uses bounding boxes for initial search, then filters results to the exact polygon
- Processing time depends on the number of polygons and API rate limits

## Example Output

```
name    WKT                                    no. of eateries  no. of offices  no. of apartments  no. of PGs  no. of gyms  no. of salons
Area_1  POLYGON((77.2090 28.6139, ...))       15              8               12                 3           2            5
Area_2  POLYGON((77.2190 28.6239, ...))       22              5               8                  2           1            3
```
