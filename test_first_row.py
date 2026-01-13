"""
Analyze only the first row and show detailed results
"""
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import json

# API Key
API_KEY = "AIzaSyDcuwSXSdSnL-Aqd6VFGgTD7KmTbKlUJAI"

# Initialize analyzer
print("Initializing Polygon Analyzer...")
analyzer = PolygonAnalyzer(API_KEY)

# Read CSV and get first row
csv_file = "Untitled spreadsheet - Swish - Live Kitchen - Geos (Latest)- Live_Kitchen_Geos.xlsx.csv"
df = pd.read_csv(csv_file)

print(f"\nTotal rows in CSV: {len(df)}")
print(f"Analyzing FIRST ROW ONLY: {df.iloc[0]['name']}")
print("=" * 60)

# Get first row
first_row = df.iloc[0]
wkt_string = str(first_row['WKT'])
polygon_name = str(first_row['name'])

# Parse WKT
polygon = analyzer.parse_wkt_polygon(wkt_string)
print(f"\nParsed polygon with {len(polygon)} points")
print(f"Polygon bounds: Lat {min(p[0] for p in polygon):.6f} to {max(p[0] for p in polygon):.6f}")
print(f"                Lng {min(p[1] for p in polygon):.6f} to {max(p[1] for p in polygon):.6f}")

# Get bounds for searching
bounds = analyzer.get_polygon_bounds(polygon)

print("\n" + "=" * 60)
print("SEARCHING FOR PLACES...")
print("=" * 60)

# Search for eateries
print("\n🔍 Searching for EATERIES...")
eateries_list = []
restaurant_places = analyzer.search_places_in_bounds(
    bounds, 
    place_types=['restaurant', 'food', 'cafe', 'meal_takeaway'],
    max_results=60
)

keyword_searches = ['juice', 'food shop', 'food court', 'dining']
for keyword in keyword_searches:
    keyword_places = analyzer.search_places_in_bounds(
        bounds,
        keyword=keyword,
        max_results=60
    )
    restaurant_places.extend(keyword_places)

# Filter eateries inside polygon
for place in restaurant_places:
    location = place.get('geometry', {}).get('location', {})
    if location:
        point = (location.get('lat'), location.get('lng'))
        if analyzer.point_in_polygon(point, polygon):
            place_name = place.get('name', '').lower()
            place_types = [t.lower() for t in place.get('types', [])]
            if any(t in ['restaurant', 'food', 'cafe', 'meal_takeaway', 'bakery', 'bar'] 
                   for t in place_types) or \
               any(kw in place_name for kw in ['restaurant', 'cafe', 'juice', 'food', 'dining', 'bistro']):
                eateries_list.append({
                    'name': place.get('name', 'Unknown'),
                    'types': place.get('types', []),
                    'address': place.get('vicinity', place.get('formatted_address', 'N/A')),
                    'location': f"{location.get('lat')}, {location.get('lng')}"
                })

# Remove duplicates
seen_names = set()
unique_eateries = []
for eatery in eateries_list:
    if eatery['name'] not in seen_names:
        seen_names.add(eatery['name'])
        unique_eateries.append(eatery)

# Search for offices
print("🔍 Searching for OFFICES...")
offices_list = []
office_places = analyzer.search_places_in_bounds(
    bounds,
    place_types=['establishment', 'point_of_interest'],
    max_results=60
)

keyword_searches = ['office', 'company', 'corporate', 'co-working', 'coworking', 
                  'workplace', 'organization', 'organisation', 'insurance']
for keyword in keyword_searches:
    keyword_places = analyzer.search_places_in_bounds(
        bounds,
        keyword=keyword,
        max_results=60
    )
    office_places.extend(keyword_places)

# Filter offices inside polygon
for place in office_places:
    location = place.get('geometry', {}).get('location', {})
    if location:
        point = (location.get('lat'), location.get('lng'))
        if analyzer.point_in_polygon(point, polygon):
            place_name = place.get('name', '').lower()
            place_types = [t.lower() for t in place.get('types', [])]
            
            is_office = False
            office_keywords = ['office', 'company', 'corporate', 'co-working', 'coworking',
                             'workplace', 'organization', 'organisation', 'insurance company',
                             'ltd', 'inc', 'corporation', 'pvt', 'limited']
            if any(kw in place_name for kw in office_keywords) or place_name.endswith('company'):
                is_office = True
            
            excluded_types = ['restaurant', 'cafe', 'food', 'store', 'shopping_mall', 
                             'hospital', 'school', 'university', 'park', 'church', 'mosque',
                             'temple', 'gas_station', 'atm', 'bank']
            if any(t in place_types for t in ['establishment', 'point_of_interest']) and \
               not any(t in place_types for t in excluded_types):
                if any(kw in place_name for kw in ['office', 'company', 'corp', 'ltd', 'inc']):
                    is_office = True
            
            if is_office:
                offices_list.append({
                    'name': place.get('name', 'Unknown'),
                    'types': place.get('types', []),
                    'address': place.get('vicinity', place.get('formatted_address', 'N/A')),
                    'location': f"{location.get('lat')}, {location.get('lng')}"
                })

# Remove duplicates
seen_names = set()
unique_offices = []
for office in offices_list:
    if office['name'] not in seen_names:
        seen_names.add(office['name'])
        unique_offices.append(office)

# Search for apartments
print("🔍 Searching for APARTMENTS...")
apartments_list = []
society_places = analyzer.search_places_in_bounds(
    bounds,
    place_types=['lodging'],
    max_results=60
)

keyword_searches = ['apartment', 'society', 'residential', 'building', 'complex', 
                  'home', 'housing', 'society', 'apartments']
for keyword in keyword_searches:
    keyword_places = analyzer.search_places_in_bounds(
        bounds,
        keyword=keyword,
        max_results=60
    )
    society_places.extend(keyword_places)

# Filter apartments inside polygon
for place in society_places:
    location = place.get('geometry', {}).get('location', {})
    if location:
        point = (location.get('lat'), location.get('lng'))
        if analyzer.point_in_polygon(point, polygon):
            place_name = place.get('name', '').lower()
            place_types = [t.lower() for t in place.get('types', [])]
            
            is_society = False
            society_keywords = ['apartment', 'society', 'residential', 'building', 'complex',
                              'home', 'housing', 'apartments', 'societies', 'residency',
                              'tower', 'residence', 'colony']
            if any(kw in place_name for kw in society_keywords):
                is_society = True
            
            if 'lodging' in place_types:
                if any(kw in place_name for kw in ['apartment', 'society', 'residential', 'building']):
                    is_society = True
                elif 'hotel' not in place_name and 'resort' not in place_name:
                    is_society = True
            
            if is_society:
                apartments_list.append({
                    'name': place.get('name', 'Unknown'),
                    'types': place.get('types', []),
                    'address': place.get('vicinity', place.get('formatted_address', 'N/A')),
                    'location': f"{location.get('lat')}, {location.get('lng')}"
                })

# Remove duplicates
seen_names = set()
unique_apartments = []
for apartment in apartments_list:
    if apartment['name'] not in seen_names:
        seen_names.add(apartment['name'])
        unique_apartments.append(apartment)

# Display results
print("\n" + "=" * 60)
print("RESULTS FOR:", polygon_name)
print("=" * 60)

print(f"\n📊 SUMMARY:")
print(f"  Eateries: {len(unique_eateries)}")
print(f"  Offices: {len(unique_offices)}")
print(f"  Apartments: {len(unique_apartments)}")

print("\n" + "=" * 60)
print("🍽️  EATERIES FOUND:")
print("=" * 60)
if unique_eateries:
    for i, eatery in enumerate(unique_eateries, 1):
        print(f"\n{i}. {eatery['name']}")
        print(f"   Types: {', '.join(eatery['types'][:5])}")
        print(f"   Address: {eatery['address']}")
        print(f"   Location: {eatery['location']}")
else:
    print("No eateries found inside the polygon.")

print("\n" + "=" * 60)
print("🏢 OFFICES FOUND:")
print("=" * 60)
if unique_offices:
    for i, office in enumerate(unique_offices, 1):
        print(f"\n{i}. {office['name']}")
        print(f"   Types: {', '.join(office['types'][:5])}")
        print(f"   Address: {office['address']}")
        print(f"   Location: {office['location']}")
else:
    print("No offices found inside the polygon.")

print("\n" + "=" * 60)
print("🏠 APARTMENTS FOUND:")
print("=" * 60)
if unique_apartments:
    for i, apartment in enumerate(unique_apartments, 1):
        print(f"\n{i}. {apartment['name']}")
        print(f"   Types: {', '.join(apartment['types'][:5])}")
        print(f"   Address: {apartment['address']}")
        print(f"   Location: {apartment['location']}")
else:
    print("No apartments found inside the polygon.")

# Save detailed results to JSON
output_file = "first_row_detailed_results.json"
results = {
    'polygon_name': polygon_name,
    'summary': {
        'eateries': len(unique_eateries),
        'offices': len(unique_offices),
        'apartments': len(unique_apartments)
    },
    'eateries': unique_eateries,
    'offices': unique_offices,
    'apartments': unique_apartments
}

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Detailed results saved to: {output_file}")
print("=" * 60)
