# Tags and Criteria Used for Classification

This document explains exactly what tags, place types, and keywords are used to identify eateries, offices, and apartments.

---

## 🍽️ EATERIES

### Google Places API Types Searched:
1. `restaurant` - Restaurants
2. `food` - Food establishments
3. `cafe` - Cafes and coffee shops
4. `meal_takeaway` - Takeaway food places

### Keywords Searched:
1. `juice` - Juice shops
2. `food shop` - Food shops
3. `food court` - Food courts
4. `dining` - Dining establishments

### Filtering Criteria (Must Match):
A place is counted as an eatery if:
- **Location**: Point is inside the polygon ✓
- **AND** one of the following:
  - Has place type: `restaurant`, `food`, `cafe`, `meal_takeaway`, `bakery`, `bar`
  - **OR** name contains: `restaurant`, `cafe`, `juice`, `food`, `dining`, `bistro`

### Examples Found:
- Restaurants (A2B, Khan Saheb, etc.)
- Cafes (Café Coffee Day, The Ants Store and cafe)
- Juice shops (Ganesh Fresh Juice Corner, Juice Adda)
- Food courts (Mann Food Court, Little India Food Court)
- Bakeries (Sangam Sweets, Jadaun SAMOSA KACHORI)

---

## 🏢 OFFICES

### Google Places API Types Searched:
1. `establishment` - General establishments
2. `point_of_interest` - Points of interest

### Keywords Searched:
1. `corporate office` - Corporate offices
2. `company` - Companies
3. `technical company` - Technical companies
4. `insurance company` - Insurance companies
5. `co-working space` / `coworking space` - Co-working spaces
6. `software company` - Software companies
7. `co-working` / `coworking` - Alternative spellings

### Filtering Criteria (Must Match):
A place is counted as an office if:
- **Location**: Point is inside the polygon ✓
- **AND** name contains one of the following:

#### Specific Office Types:
- `corporate office`
- `company`
- `technical company`
- `insurance company`
- `co-working space` / `coworking space`
- `software company`
- `co-working` / `coworking`
- `corporate`
- `ltd` / `inc` / `corporation` / `pvt` / `limited` / `pvt ltd` / `private limited`
- Name ends with `company`
- Name contains `software`

### Excluded (NOT counted as offices):
- Restaurants, cafes, food places
- Hotels, resorts
- Stores, shopping malls
- Hospitals, schools, universities
- Banks, ATMs
- Parks, religious places
- Any place with `lodging` type

### Examples:
- Corporate offices
- Companies (tech, software, etc.)
- Co-working spaces
- Insurance companies
- Technical companies

---

## 🏠 APARTMENTS

### Google Places API Types Searched:
1. `lodging` - Lodging places (hotels, PGs, service apartments, etc.)

### Keywords Searched:
1. `apartment building` / `apartment buildings` - Apartment buildings
2. `building` / `buildings` - Buildings
3. `PG` / `PGs` / `pg` / `pgs` - Paying Guest accommodations
4. `hostel` / `hostels` - Hostels
5. `apartment complex` - Apartment complexes
6. `residency` - Residencies
7. `residential building` / `residential buildings` - Residential buildings

### Filtering Criteria (Must Match):
A place is counted as an apartment if:
- **Location**: Point is inside the polygon ✓
- **AND** name contains one of the following:

#### Specific Apartment Types:
- `apartment building` / `apartment buildings`
- `building` / `buildings`
- `PG` / `PGs` / `pg` / `pgs`
- `hostel` / `hostels`
- `apartment complex`
- `residency`
- `residential building` / `residential buildings`
- `apartment` / `apartments`
- `residential`
- `complex`
- `residence`
- `co-living` / `coliving`
- `paying guest`

#### By Type:
- Has type `lodging` AND:
  - Name contains apartment keywords, OR
  - Name contains `pg`, `hostel`, or `paying guest`, OR
  - Name does NOT contain `hotel` or `resort` (to include PGs and service apartments)

### Excluded (NOT counted):
- Hotels (unless they have apartment keywords in name)
- Resorts (unless they have apartment keywords in name)

### Examples:
- Apartment buildings
- Residential buildings
- PGs (Paying Guest accommodations)
- Hostels
- Apartment complexes
- Residencies
- Co-living spaces

---

## 📋 Summary Table

| Category | API Types | Keywords | Name Filters | Type Filters |
|----------|----------|----------|--------------|--------------|
| **Eateries** | restaurant, food, cafe, meal_takeaway | juice, food shop, food court, dining | restaurant, cafe, juice, food, dining, bistro | restaurant, food, cafe, meal_takeaway, bakery, bar |
| **Offices** | establishment, point_of_interest | corporate office, company, technical company, insurance company, co-working space, software company | corporate office, company, technical company, insurance company, co-working space, software company, ltd, inc, pvt, limited | establishment, point_of_interest (excluding restaurants, stores, hotels, etc.) |
| **Apartments** | lodging | apartment building, building, PG, hostel, apartment complex, residency, residential building | apartment building, building, PG, hostel, apartment complex, residency, residential building, apartment, residential, complex | lodging (excluding hotels/resorts without apartment keywords) |

---

## 🔍 How It Works

1. **Search Phase**: Uses Google Places API to search within polygon's bounding box
   - Searches by place types
   - Searches by keywords
   
2. **Filter Phase**: 
   - Checks if point is inside polygon (point-in-polygon algorithm)
   - Checks if place matches category criteria (name + type)
   
3. **Deduplication**: Removes duplicate places based on place_id

---

## ⚙️ Customization

If you want to modify these criteria, edit the following functions in `polygon_analyzer.py`:
- `count_eateries()` - Lines ~227-280
- `count_offices()` - Lines ~282-355
- `count_societies()` - Lines ~357-430
