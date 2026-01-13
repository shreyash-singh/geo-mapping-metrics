# Quick Start Guide

## 🚀 Fastest Way to Get Started

### Option 1: API Server

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GOOGLE_MAPS_API_KEY="your-api-key"
   export MAPBOX_API_TOKEN="your-mapbox-token"  # Optional
   ```

3. **Start the API server:**
   ```bash
   python app.py
   ```

4. **Use the API endpoints:**
   - `GET /` - Health check
   - `POST /api/analyze` - Upload CSV file for analysis
   - `POST /api/isochrone` - Generate isochrone polygon

### Option 2: Python Script

```python
from polygon_analyzer import PolygonAnalyzer

# Initialize
analyzer = PolygonAnalyzer("AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI")

# Process CSV file
results = analyzer.process_csv_file('input.csv', 'output.csv')
```

## 📝 CSV File Format

Your input CSV should have these columns:

| WKT | name |
|-----|------|
| POLYGON((77.2090 28.6139, 77.2100 28.6149, ...)) | Area_1 |
| POLYGON((77.2190 28.6239, 77.2200 28.6249, ...)) | Area_2 |

**Important:** WKT format uses `(longitude latitude)` order, not `(latitude longitude)`!

## 📊 Output Format

The output CSV will have:
- All your original columns (WKT, name, etc.)
- **New columns:**
  - `no. of eateries`
  - `no. of offices`
  - `no. of apartments`

## ⚡ Performance Tips

- **Small files (< 10 polygons)**: Use the web app - it's fastest
- **Large files (> 50 polygons)**: Consider running the Python script directly for better progress tracking
- Processing time: ~1-2 minutes per polygon (depends on API rate limits)

## 🐛 Troubleshooting

**Error: "CSV must contain 'WKT' column"**
- Make sure your CSV has a column named exactly `WKT` (case-sensitive)

**Error: "CSV must contain 'name' column"**
- Make sure your CSV has a column named exactly `name` (case-sensitive)

**Slow processing:**
- This is normal - the Google Places API has rate limits
- Each polygon takes ~1-2 minutes to process
- Be patient for large files!
