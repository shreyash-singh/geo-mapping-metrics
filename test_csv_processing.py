"""
Test script to verify CSV processing works with the example file
This will test WKT parsing without making API calls
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd

# Test with the example CSV file
print("Testing CSV processing with example file...")
print("=" * 60)

# Read the example CSV
csv_file = "Example of polygon file.csv"
df = pd.read_csv(csv_file)

print(f"\nLoaded CSV with {len(df)} rows")
print(f"Columns: {list(df.columns)}")
print("\nFirst few rows:")
print(df.head())

# Test WKT parsing
print("\n" + "=" * 60)
print("Testing WKT Parsing:")
print("=" * 60)

analyzer = PolygonAnalyzer("test_key")  # Dummy key for testing

for idx, row in df.head(2).iterrows():  # Test first 2 polygons
    wkt = str(row['WKT'])
    name = str(row['name'])
    
    print(f"\nPolygon: {name}")
    print(f"WKT (first 100 chars): {wkt[:100]}...")
    
    try:
        polygon = PolygonAnalyzer.parse_wkt_polygon(wkt)
        print(f"✅ Successfully parsed {len(polygon)} points")
        print(f"   First point: {polygon[0]}")
        print(f"   Last point: {polygon[-1]}")
        
        # Test point-in-polygon with a point that should be inside
        # Using approximate center of the polygon
        center_lat = sum(p[0] for p in polygon) / len(polygon)
        center_lng = sum(p[1] for p in polygon) / len(polygon)
        center_point = (center_lat, center_lng)
        
        is_inside = analyzer.point_in_polygon(center_point, polygon)
        print(f"   Center point {center_point} is inside: {is_inside}")
        
    except Exception as e:
        print(f"❌ Error parsing WKT: {e}")

print("\n" + "=" * 60)
print("✅ WKT parsing test complete!")
print("=" * 60)
print("\nNote: This test only verifies WKT parsing.")
print("To run full analysis with API calls, use: streamlit run app.py")
