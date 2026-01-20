# Jarvis - Personal Agent Setup Guide

## Overview
Jarvis is a personal web app designed to help with meal planning and other personal tasks. It connects to Google Sheets to fetch meal data and generate personalized meal combinations.

## Quick Start

### 1. Run the App
```bash
python jarvis_app.py
```

The app will run on `http://localhost:5001` (different port from the geo-mapping app).

### 2. Setup Google Sheets for Meal Planner

#### Step 1: Create a Google Sheet
Create a new Google Sheet with your meals. Recommended columns:
- `name` - Name of the meal
- `category` or `type` - Category like "breakfast", "lunch", "dinner"
- `ingredients` - List of ingredients (optional)
- Any other columns you want (calories, prep time, etc.)

Example:
| name | category | ingredients |
|------|----------|-------------|
| Oatmeal | breakfast | Oats, milk, banana |
| Grilled Chicken | lunch | Chicken, vegetables |
| Pasta | dinner | Pasta, sauce, cheese |

#### Step 2: Publish to Web
1. Open your Google Sheet
2. Click **File** → **Share** → **Publish to web**
3. Select the sheet/tab you want to publish
4. Choose **CSV** as the format
5. Click **Publish**
6. Copy the generated URL

The URL will look like:
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/export?format=csv&gid=0
```

#### Step 3: Use in Jarvis
1. Open Jarvis in your browser
2. Click the hamburger menu (☰) → **Meal Planner**
3. Paste your Google Sheets CSV URL
4. Enter number of days
5. Click **Generate Meal Plan**

## Features

### Meal Planner
- **Automatic Fetching**: Connects to your Google Sheets in real-time
- **Smart Categorization**: Automatically identifies breakfast, lunch, and dinner meals
- **Random Generation**: Creates varied meal combinations for each day
- **Flexible**: Works with any column structure in your sheet

## API Endpoints

### Health Check
```
GET /api/health
```

### Fetch Meals
```
GET /api/meals/fetch?sheet_url=YOUR_CSV_URL
```

### Generate Meal Plan
```
POST /api/meals/generate
Body: {
    "meals": [...],
    "days": 7,
    "preferences": {
        "breakfast_categories": ["breakfast"],
        "lunch_categories": ["lunch"],
        "dinner_categories": ["dinner"]
    }
}
```

## Environment Variables

Optional:
- `JARVIS_MEALS_SHEET_URL` - Default Google Sheets URL (can also be provided in UI)
- `PORT` - Port to run on (default: 5001)

## Notes

- The app uses a simple CSV fetch approach - no authentication needed for public sheets
- Make sure your Google Sheet is published to the web (publicly accessible)
- The meal planner randomly selects meals, so you'll get different combinations each time
- You can add more tabs/features to the sidebar by editing `jarvis.html`

## Troubleshooting

**"Failed to fetch from Google Sheets"**
- Make sure the sheet is published to web as CSV
- Check that the URL is correct
- Verify the sheet is publicly accessible

**"No meals found"**
- Check that your sheet has data
- Verify column names (the app looks for common names like "category", "type", etc.)

**Meals not categorizing correctly**
- Make sure you have a category/type column
- Use consistent naming: "breakfast", "lunch", "dinner" (case-insensitive)
