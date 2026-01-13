"""
Run analysis on the example CSV file
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import sys

# API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize analyzer
print("Initializing Polygon Analyzer...")
analyzer = PolygonAnalyzer(API_KEY)

# Process the example CSV file
csv_file = "Example of polygon file.csv"
output_file = "analysis_results.csv"

print(f"\nProcessing CSV file: {csv_file}")
print("=" * 60)

try:
    # Process the CSV file
    results_df = analyzer.process_csv_file(csv_file, output_file)
    
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print("\n", results_df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Total Polygons Analyzed: {len(results_df)}")
    print(f"Total Eateries: {results_df['no. of eateries'].sum()}")
    print(f"Total Offices: {results_df['no. of offices'].sum()}")
    print(f"Total Apartments: {results_df['no. of apartments'].sum()}")
    print(f"\nAverage Eateries per Polygon: {results_df['no. of eateries'].mean():.2f}")
    print(f"Average Offices per Polygon: {results_df['no. of offices'].mean():.2f}")
    print(f"Average Apartments per Polygon: {results_df['no. of apartments'].mean():.2f}")
    
    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
