# Polygon Analyzer

This project analyzes the number of eateries, offices, and apartments within given polygons using the Google Places API.

## Features

- **Eateries Analysis**: Counts restaurants, cafes, juice shops, food shops, and dining establishments
- **Offices Analysis**: Counts co-working spaces, offices, workplaces, companies, organizations, and corporate offices
- **Apartments Analysis**: Counts apartments, societies, residential buildings, apartment complexes, and housing

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Web App (Recommended - Fastest & Easiest)

1. Start the Streamlit web app:
```bash
streamlit run app.py
```

2. Open your browser to the URL shown (usually `http://localhost:8501`)

3. Upload a CSV file with columns:
   - `WKT`: Polygon coordinates in WKT format (e.g., `POLYGON((lng1 lat1, lng2 lat2, ...))`)
   - `name`: Name/identifier for the polygon

4. Click "Analyze Polygons" and wait for processing

5. Download the results CSV with additional columns:
   - `no. of eateries`
   - `no. of offices`
   - `no. of apartments`

### Python Script Usage

#### Process CSV File with WKT Polygons

```python
from polygon_analyzer import PolygonAnalyzer

# Initialize with your API key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"
analyzer = PolygonAnalyzer(API_KEY)

# Process CSV file
results_df = analyzer.process_csv_file('input.csv', 'output.csv')
```

#### Direct Polygon Analysis

```python
from polygon_analyzer import PolygonAnalyzer

# Initialize with your API key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"
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

## API Key

The Google Maps API key is already configured in the code. Make sure you have the following APIs enabled in your Google Cloud Console:
- Places API
- Places API (New)

## Notes

- The script uses point-in-polygon checking to ensure accurate counts
- Rate limiting is implemented to respect API quotas
- Duplicate places are automatically filtered out
- The search uses bounding boxes for initial search, then filters results to the exact polygon
- Processing time depends on the number of polygons and API rate limits

## Example Output

```
name    WKT                                    no. of eateries  no. of offices  no. of apartments
Area_1  POLYGON((77.2090 28.6139, ...))       15              8               12
Area_2  POLYGON((77.2190 28.6239, ...))       22              5               8
```
