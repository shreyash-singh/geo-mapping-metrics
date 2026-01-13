"""
Example usage of PolygonAnalyzer
This script demonstrates how to use the PolygonAnalyzer to analyze multiple polygons
"""

from polygon_analyzer import PolygonAnalyzer
import pandas as pd

# Your API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize the analyzer
analyzer = PolygonAnalyzer(API_KEY)

# Example 1: Define polygons as lists of (latitude, longitude) tuples
# Replace these with your actual polygon coordinates

polygon_1 = [
    (28.6139, 77.2090),  # Example coordinates (Delhi, India)
    (28.6149, 77.2100),
    (28.6159, 77.2090),
    (28.6149, 77.2080),
]

polygon_2 = [
    (28.6239, 77.2190),
    (28.6249, 77.2200),
    (28.6259, 77.2190),
    (28.6249, 77.2180),
]

# Example 2: You can also load polygons from a file (GeoJSON, CSV, etc.)
# For GeoJSON format, you would need to parse it first
# For CSV format with columns 'lat' and 'lng', you could do:
# df = pd.read_csv('polygons.csv')
# polygon_3 = list(zip(df['lat'], df['lng']))

# List all polygons to analyze
polygons = [polygon_1, polygon_2]

# Optional: Provide identifiers for each polygon
polygon_ids = ["Area_1", "Area_2"]

# Analyze all polygons
print("Starting analysis...")
print("This may take a few minutes depending on the number of polygons and API rate limits.\n")

results_df = analyzer.analyze_multiple_polygons(polygons, polygon_ids)

# Display results
print("\n" + "="*60)
print("ANALYSIS RESULTS")
print("="*60)
print(results_df)
print("\n")

# Save results to CSV
output_file = 'polygon_analysis_results.csv'
results_df.to_csv(output_file, index=False)
print(f"Results saved to '{output_file}'")

# Display summary statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)
print(f"Total Eateries: {results_df['eateries'].sum()}")
print(f"Total Offices: {results_df['offices'].sum()}")
print(f"Total Societies: {results_df['societies'].sum()}")
print(f"\nAverage Eateries per Polygon: {results_df['eateries'].mean():.2f}")
print(f"Average Offices per Polygon: {results_df['offices'].mean():.2f}")
print(f"Average Societies per Polygon: {results_df['societies'].mean():.2f}")
