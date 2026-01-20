"""
Jarvis - Personal Agent Web App for Shreyash
A Flask-based personal assistant with meal planning and other utilities
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import requests
import random
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Default Google Sheets CSV URL (user can update this)
DEFAULT_SHEETS_URL = os.environ.get('JARVIS_MEALS_SHEET_URL', '')

@app.route('/')
def index():
    """Serve the Jarvis homepage"""
    return render_template('jarvis.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Jarvis is running",
        "endpoints": {
            "/api/meals/fetch": "GET - Fetch meals from Google Sheets",
            "/api/meals/generate": "POST - Generate meal combinations"
        }
    })

@app.route('/api/meals/fetch', methods=['GET'])
def fetch_meals():
    """
    Fetch meals from Google Sheets CSV
    
    Query params:
        - sheet_url: (optional) Google Sheets CSV URL. If not provided, uses default from env.
    
    Response:
        {
            "meals": [
                {"name": str, "category": str, "ingredients": str, ...}
            ],
            "categories": [str],
            "count": int
        }
    """
    try:
        # Get sheet URL from query param or use default
        sheet_url = request.args.get('sheet_url', DEFAULT_SHEETS_URL)
        
        if not sheet_url:
            return jsonify({
                "error": "No Google Sheets URL provided. Please provide sheet_url parameter or set JARVIS_MEALS_SHEET_URL environment variable."
            }), 400
        
        # Fetch CSV from Google Sheets
        response = requests.get(sheet_url, timeout=10)
        response.raise_for_status()
        
        # Parse CSV
        from io import StringIO
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        
        # Convert to list of dictionaries
        meals = df.to_dict('records')
        
        # Extract unique categories (assuming there's a 'category' or 'type' column)
        # Try common column names
        category_col = None
        for col in ['category', 'type', 'meal_type', 'Category', 'Type', 'Meal Type']:
            if col in df.columns:
                category_col = col
                break
        
        categories = []
        if category_col:
            categories = df[category_col].dropna().unique().tolist()
        else:
            # If no category column, infer from other columns or use 'All'
            categories = ['All']
        
        return jsonify({
            "meals": meals,
            "categories": categories,
            "count": len(meals),
            "columns": df.columns.tolist()
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({
            "error": f"Failed to fetch from Google Sheets: {str(e)}"
        }), 500
    except Exception as e:
        return jsonify({
            "error": f"Error processing meals data: {str(e)}"
        }), 500

@app.route('/api/meals/generate', methods=['POST'])
def generate_meal_plan():
    """
    Generate meal combinations for breakfast, lunch, and dinner
    
    Request JSON:
        {
            "meals": [{"name": str, "category": str, ...}],  # List of all meals
            "days": int (optional, default: 7),  # Number of days to plan
            "preferences": {
                "breakfast_categories": [str] (optional),
                "lunch_categories": [str] (optional),
                "dinner_categories": [str] (optional)
            }
        }
    
    Response:
        {
            "plan": [
                {
                    "day": int,
                    "date": str,
                    "breakfast": {...},
                    "lunch": {...},
                    "dinner": {...}
                }
            ]
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'meals' not in data:
            return jsonify({"error": "Meals data is required"}), 400
        
        meals = data['meals']
        days = data.get('days', 7)
        preferences = data.get('preferences', {})
        
        if not meals:
            return jsonify({"error": "No meals provided"}), 400
        
        # Identify category column
        category_col = None
        for col in ['category', 'type', 'meal_type', 'Category', 'Type', 'Meal Type']:
            if col in meals[0].keys():
                category_col = col
                break
        
        # Filter meals by category for each meal type
        breakfast_cats = preferences.get('breakfast_categories', ['breakfast', 'Breakfast', 'morning', 'Morning'])
        lunch_cats = preferences.get('lunch_categories', ['lunch', 'Lunch', 'midday', 'Midday'])
        dinner_cats = preferences.get('dinner_categories', ['dinner', 'Dinner', 'evening', 'Evening'])
        
        def filter_meals(categories):
            if not category_col:
                return meals  # Return all if no category column
            return [m for m in meals if m.get(category_col, '').lower() in [c.lower() for c in categories]]
        
        breakfast_meals = filter_meals(breakfast_cats)
        lunch_meals = filter_meals(lunch_cats)
        dinner_meals = filter_meals(dinner_cats)
        
        # If no meals found in categories, use all meals
        if not breakfast_meals:
            breakfast_meals = meals
        if not lunch_meals:
            lunch_meals = meals
        if not dinner_meals:
            dinner_meals = meals
        
        # Generate meal plan
        plan = []
        today = datetime.now()
        
        for day in range(days):
            date = (today.replace(hour=0, minute=0, second=0, microsecond=0) + 
                   pd.Timedelta(days=day))
            
            plan.append({
                "day": day + 1,
                "date": date.strftime("%Y-%m-%d"),
                "day_name": date.strftime("%A"),
                "breakfast": random.choice(breakfast_meals) if breakfast_meals else None,
                "lunch": random.choice(lunch_meals) if lunch_meals else None,
                "dinner": random.choice(dinner_meals) if dinner_meals else None
            })
        
        return jsonify({
            "plan": plan,
            "summary": {
                "total_days": days,
                "breakfast_options": len(breakfast_meals),
                "lunch_options": len(lunch_meals),
                "dinner_options": len(dinner_meals)
            }
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Error generating meal plan: {str(e)}"
        }), 500

# Export app for Vercel
# Vercel will automatically detect and use the 'app' instance

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))  # Different port from geo-mapping app
    app.run(host='0.0.0.0', port=port, debug=True)
