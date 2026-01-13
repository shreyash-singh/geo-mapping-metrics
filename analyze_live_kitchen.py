"""
Analyze the Live Kitchen Geos CSV file
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import sys

# API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize analyzer
print("Initializing Polygon Analyzer...")
analyzer = PolygonAnalyzer(API_KEY)

# Process the CSV file
csv_file = "Untitled spreadsheet - Swish - Live Kitchen - Geos (Latest)- Live_Kitchen_Geos.xlsx.csv"
output_file = "live_kitchen_analysis_results.csv"

print(f"\nProcessing CSV file: {csv_file}")
print("=" * 60)

# First, check how many polygons we have
df_preview = pd.read_csv(csv_file)
print(f"Found {len(df_preview)} polygons to analyze")
print(f"Polygon names: {df_preview['name'].tolist()}")
print("\nStarting analysis... This will take some time...")
print("=" * 60)

try:
    # Process the CSV file
    results_df = analyzer.process_csv_file(csv_file, output_file)
    
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    # Display results in a more readable format
    display_cols = ['name', 'no. of eateries', 'no. of offices', 'no. of apartments']
    print("\n", results_df[display_cols].to_string(index=False))
    
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
    
    # Show top polygons by each metric
    print("\n" + "=" * 60)
    print("TOP POLYGONS BY METRIC")
    print("=" * 60)
    print("\nTop 5 by Eateries:")
    top_eateries = results_df.nlargest(5, 'no. of eateries')[['name', 'no. of eateries']]
    print(top_eateries.to_string(index=False))
    
    print("\nTop 5 by Offices:")
    top_offices = results_df.nlargest(5, 'no. of offices')[['name', 'no. of offices']]
    print(top_offices.to_string(index=False))
    
    print("\nTop 5 by Apartments:")
    top_apartments = results_df.nlargest(5, 'no. of apartments')[['name', 'no. of apartments']]
    print(top_apartments.to_string(index=False))
    
    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
