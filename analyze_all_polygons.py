"""
Analyze all polygons incrementally and update CSV file after each polygon
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import os
import sys
from datetime import datetime

# API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize analyzer
print("=" * 60)
print("POLYGON ANALYZER - Incremental Processing")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

analyzer = PolygonAnalyzer(API_KEY)

# File paths
input_csv = "Untitled spreadsheet - Swish - Live Kitchen - Geos (Latest)- Live_Kitchen_Geos.xlsx.csv"
output_csv = "live_kitchen_analysis_results.csv"

# Read input CSV
print(f"Reading input file: {input_csv}")
df_input = pd.read_csv(input_csv)
total_polygons = len(df_input)
print(f"Found {total_polygons} polygons to analyze")
print()

# Check if output file exists (for resuming)
if os.path.exists(output_csv):
    print(f"Output file exists: {output_csv}")
    df_existing = pd.read_csv(output_csv)
    processed_names = set(df_existing['name'].tolist())
    print(f"Found {len(processed_names)} already processed polygons")
    print(f"Processed: {', '.join(sorted(processed_names))}")
    print()
    
    # Filter out already processed polygons
    df_remaining = df_input[~df_input['name'].isin(processed_names)]
    print(f"Remaining polygons to process: {len(df_remaining)}")
    
    if len(df_remaining) == 0:
        print("All polygons already processed!")
        sys.exit(0)
    
    df_input = df_remaining
    total_polygons = len(df_input)
else:
    processed_names = set()
    df_existing = None

print("=" * 60)
print("STARTING ANALYSIS")
print("=" * 60)
print()

# Process each polygon
results_list = []
start_time = datetime.now()

for idx, row in df_input.iterrows():
    polygon_num = idx + 1
    wkt_string = str(row['WKT'])
    polygon_name = str(row['name'])
    
    print(f"[{polygon_num}/{total_polygons}] Processing: {polygon_name}")
    print("-" * 60)
    
    try:
        # Parse WKT to polygon coordinates
        polygon = analyzer.parse_wkt_polygon(wkt_string)
        
        if len(polygon) < 3:
            print(f"  ⚠️  Warning: Polygon has less than 3 points, skipping...")
            result = {
                'name': polygon_name,
                'no. of eateries': 0,
                'no. of offices': 0,
                'no. of apartments': 0
            }
            results_list.append(result)
            
            # Merge with original row data
            result_row = row.to_dict()
            result_row.update(result)
            
            # Append to output CSV
            result_df = pd.DataFrame([result_row])
            if os.path.exists(output_csv):
                result_df.to_csv(output_csv, mode='a', header=False, index=False)
            else:
                # Create new file with all original columns + new columns
                all_cols = list(row.index) + ['no. of eateries', 'no. of offices', 'no. of apartments']
                result_df[all_cols].to_csv(output_csv, index=False)
            
            print(f"  ✅ Saved to CSV (0 eateries, 0 offices, 0 apartments)")
            continue
        
        # Analyze polygon
        print(f"  🔍 Analyzing polygon...")
        analysis = analyzer.analyze_polygon(polygon, polygon_name)
        
        # The analyze_polygon function returns: {'polygon_id': ..., 'eateries': ..., 'offices': ..., 'societies': ...}
        result = {
            'name': polygon_name,
            'no. of eateries': analysis['eateries'],
            'no. of offices': analysis['offices'],
            'no. of apartments': analysis['societies']
        }
        results_list.append(result)
        
        # Merge with original row data
        result_row = row.to_dict()
        result_row.update(result)
        
        # Append to output CSV immediately
        result_df = pd.DataFrame([result_row])
        if os.path.exists(output_csv):
            result_df.to_csv(output_csv, mode='a', header=False, index=False)
        else:
            # Create new file with all original columns + new columns
            all_cols = list(row.index) + ['no. of eateries', 'no. of offices', 'no. of apartments']
            result_df[all_cols].to_csv(output_csv, index=False)
        
        print(f"  ✅ Results: {analysis['eateries']} eateries, {analysis['offices']} offices, {analysis['societies']} apartments")
        print(f"  💾 Saved to CSV: {output_csv}")
        
        # Estimate remaining time
        elapsed = (datetime.now() - start_time).total_seconds()
        avg_time_per_polygon = elapsed / polygon_num
        remaining = total_polygons - polygon_num
        estimated_seconds = avg_time_per_polygon * remaining
        estimated_minutes = estimated_seconds / 60
        
        print(f"  ⏱️  Progress: {polygon_num}/{total_polygons} ({polygon_num*100//total_polygons}%)")
        print(f"  ⏱️  Estimated time remaining: ~{estimated_minutes:.1f} minutes")
        
    except Exception as e:
        print(f"  ❌ Error processing polygon '{polygon_name}': {e}")
        import traceback
        traceback.print_exc()
        
        # Save error result
        result = {
            'name': polygon_name,
            'no. of eateries': 0,
            'no. of offices': 0,
            'no. of apartments': 0
        }
        result_row = row.to_dict()
        result_row.update(result)
        result_df = pd.DataFrame([result_row])
        if os.path.exists(output_csv):
            result_df.to_csv(output_csv, mode='a', header=False, index=False)
        else:
            all_cols = list(row.index) + ['no. of eateries', 'no. of offices', 'no. of apartments']
            result_df[all_cols].to_csv(output_csv, index=False)
    
    print()

# Final summary
end_time = datetime.now()
total_time = (end_time - start_time).total_seconds() / 60

print("=" * 60)
print("ANALYSIS COMPLETE!")
print("=" * 60)
print(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Total time: {total_time:.1f} minutes")
print(f"Results saved to: {output_csv}")
print()

# Read and display final results
if os.path.exists(output_csv):
    df_final = pd.read_csv(output_csv)
    print("=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    print(f"Total Polygons Analyzed: {len(df_final)}")
    print(f"Total Eateries: {df_final['no. of eateries'].sum()}")
    print(f"Total Offices: {df_final['no. of offices'].sum()}")
    print(f"Total Apartments: {df_final['no. of apartments'].sum()}")
    print()
    print(f"Average Eateries per Polygon: {df_final['no. of eateries'].mean():.2f}")
    print(f"Average Offices per Polygon: {df_final['no. of offices'].mean():.2f}")
    print(f"Average Apartments per Polygon: {df_final['no. of apartments'].mean():.2f}")
    print()
    print("Results by Polygon:")
    print("-" * 60)
    display_cols = ['name', 'no. of eateries', 'no. of offices', 'no. of apartments']
    print(df_final[display_cols].to_string(index=False))
    print("=" * 60)
