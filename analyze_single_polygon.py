"""
Analyze a single polygon and append results to output CSV
Usage: python3 analyze_single_polygon.py
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import os
import sys
from datetime import datetime

# API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize analyzer
analyzer = PolygonAnalyzer(API_KEY)

# Output file
output_csv = "polygon_analysis_results.csv"

# Polygon data (you can modify these)
WKT = "POLYGON ((77.7340853 12.997085, 77.7322184 12.9964787, 77.7281201 12.9957365, 77.7263083 12.9975633, 77.7250805 12.9980586, 77.7246038 12.9985538, 77.7254526 12.9989694, 77.7254754 12.9993326, 77.7225048 13.0001429, 77.7222225 12.9989537, 77.7219311 12.9983278, 77.7214037 12.9978692, 77.7199265 12.998435, 77.7189213 12.9986244, 77.7182434 12.998793, 77.7180439 12.9984957, 77.7175547 12.9987107, 77.7173998 12.9981788, 77.7174273 12.9976261, 77.7173753 12.9973209, 77.7174414 12.996974, 77.7177773 12.9963847, 77.7142583 12.9972, 77.7134661 12.9955428, 77.7133919 12.9946776, 77.7132103 12.9938124, 77.7127203 12.9934461, 77.7122123 12.992588, 77.7137106 12.9919704, 77.7158527 12.9921787, 77.7142928 12.9905967, 77.712911 12.9896153, 77.7135548 12.9890847, 77.7134126 12.9869644, 77.7134797 12.9866514, 77.7136084 12.986458, 77.7135333 12.9857654, 77.7138149 12.9852904, 77.7147027 12.9853551, 77.7159932 12.9851462, 77.7176309 12.9852665, 77.7184659 12.985311, 77.7184676 12.9861565, 77.7204864 12.9865421, 77.7214976 12.9870125, 77.7218597 12.9880841, 77.7218221 12.9888681, 77.7219241 12.9889099, 77.722034 12.9885388, 77.722262 12.988152, 77.7227663 12.9879717, 77.7233993 12.9879638, 77.7239974 12.9881206, 77.7244132 12.9885963, 77.7247981 12.9884552, 77.7247753 12.9880422, 77.7245164 12.9877234, 77.7245151 12.9867564, 77.7254377 12.9868295, 77.7266716 12.9869132, 77.7267198 12.9876057, 77.7270256 12.9876919, 77.7273207 12.9890118, 77.7279645 12.9888524, 77.7296113 12.9884944, 77.7293847 12.987875, 77.7301176 12.9880631, 77.7303714 12.9883376, 77.73283 12.9879586, 77.7346372 12.987778, 77.7364444 12.9875974, 77.7390456 12.9875108, 77.739186 12.9879706, 77.7398335 12.9878424, 77.7424323 12.9876868, 77.743355 12.9908858, 77.7443581 12.9965101, 77.7384386 12.9979893, 77.7340853 12.997085))"
NAME = "BLR-WHITE-06"

print("=" * 60)
print("ANALYZING SINGLE POLYGON")
print("=" * 60)
print(f"Polygon Name: {NAME}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

try:
    # Parse WKT to polygon coordinates
    polygon = analyzer.parse_wkt_polygon(WKT)
    print(f"Parsed polygon with {len(polygon)} points")
    
    if len(polygon) < 3:
        print("⚠️  Error: Polygon has less than 3 points")
        sys.exit(1)
    
    # Analyze polygon
    print(f"\nAnalyzing polygon...")
    analysis = analyzer.analyze_polygon(polygon, NAME)
    
    # Prepare result row
    result_row = {
        'WKT': WKT,
        'name': NAME,
        'description': '',  # Add description if needed
        'no. of eateries': analysis['eateries'],
        'no. of offices': analysis['offices'],
        'no. of apartments': analysis['apartments'],
        'no. of PGs': analysis['pgs'],
        'no. of gyms': analysis['gyms']
    }
    
    # Append to CSV
    result_df = pd.DataFrame([result_row])
    
    if os.path.exists(output_csv):
        # Append to existing file
        result_df.to_csv(output_csv, mode='a', header=False, index=False)
        print(f"\n✅ Results appended to: {output_csv}")
    else:
        # Create new file
        result_df.to_csv(output_csv, index=False)
        print(f"\n✅ Results saved to new file: {output_csv}")
    
    # Display results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Polygon Name: {NAME}")
    print(f"Eateries: {analysis['eateries']}")
    print(f"Offices: {analysis['offices']}")
    print(f"Apartments: {analysis['apartments']}")
    print(f"PGs: {analysis['pgs']}")
    print(f"Gyms: {analysis['gyms']}")
    print()
    
    # Show summary of existing results
    if os.path.exists(output_csv):
        df_all = pd.read_csv(output_csv)
        print("=" * 60)
        print("CUMULATIVE SUMMARY")
        print("=" * 60)
        print(f"Total Polygons Analyzed: {len(df_all)}")
        print(f"Total Eateries: {df_all['no. of eateries'].sum()}")
        print(f"Total Offices: {df_all['no. of offices'].sum()}")
        print(f"Total Apartments: {df_all['no. of apartments'].sum()}")
        print(f"Total PGs: {df_all['no. of PGs'].sum()}")
        print(f"Total Gyms: {df_all['no. of gyms'].sum()}")
        print()
        print("All Results:")
        print("-" * 60)
        display_cols = ['name', 'no. of eateries', 'no. of offices', 'no. of apartments', 'no. of PGs', 'no. of gyms']
        print(df_all[display_cols].to_string(index=False))
    
    print("\n" + "=" * 60)
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
