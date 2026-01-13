"""
Flask API for Polygon Analyzer
Provides REST API endpoints for geo metrics and geo mapping functionality
"""
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from polygon_analyzer import PolygonAnalyzer
import pandas as pd
import io
import os
import tempfile

app = Flask(__name__, template_folder='templates')
CORS(app)  # Enable CORS for all routes

# Initialize analyzer (API key from environment variable)
def get_analyzer():
    api_key = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    if not api_key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is required")
    return PolygonAnalyzer(api_key)

@app.route('/')
def index():
    """Serve the main webpage"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Polygon Analyzer API is running",
        "endpoints": {
            "/api/analyze": "POST - Analyze polygons from CSV file",
            "/api/isochrone": "POST - Generate isochrone polygon"
        }
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_polygons():
    """
    Analyze polygons from uploaded CSV file
    
    Request:
        - file: CSV file with 'WKT' and 'name' columns
        - google_maps_api_key: (optional) Google Maps API key (if not in env)
    
    Response:
        - CSV file with analysis results
    """
    try:
        # Get API key from request or environment
        api_key = request.form.get('google_maps_api_key') or os.environ.get('GOOGLE_MAPS_API_KEY', '')
        if not api_key:
            return jsonify({"error": "Google Maps API key is required"}), 400
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file extension
        if not file.filename.endswith('.csv'):
            return jsonify({"error": "File must be a CSV file"}), 400
        
        # Read CSV file
        try:
            df = pd.read_csv(file)
        except Exception as e:
            return jsonify({"error": f"Error reading CSV file: {str(e)}"}), 400
        
        # Validate required columns
        if 'WKT' not in df.columns:
            return jsonify({"error": "CSV file must contain a 'WKT' column"}), 400
        if 'name' not in df.columns:
            return jsonify({"error": "CSV file must contain a 'name' column"}), 400
        
        # Initialize analyzer and process
        analyzer = PolygonAnalyzer(api_key)
        
        # Save to temporary file for processing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_input:
            df.to_csv(tmp_input.name, index=False)
            tmp_input_path = tmp_input.name
        
        try:
            # Process CSV file
            results_df = analyzer.process_csv_file(tmp_input_path, output_csv_path=None)
            
            # Convert to CSV string
            csv_buffer = io.StringIO()
            results_df.to_csv(csv_buffer, index=False)
            csv_data = csv_buffer.getvalue()
            
            # Create response
            output = io.BytesIO()
            output.write(csv_data.encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name='polygon_analysis_results.csv'
            )
        finally:
            # Clean up temp file
            if os.path.exists(tmp_input_path):
                os.remove(tmp_input_path)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/isochrone', methods=['POST'])
def generate_isochrone():
    """
    Generate isochrone polygon using Mapbox API
    
    Request JSON:
        {
            "center_lat": float,
            "center_lng": float,
            "time_limit_minutes": int,
            "polygon_name": str,
            "mapbox_token": str (optional if in env),
            "routing_profile": str (optional, default: "driving"),
            "generalize_meters": float (optional, default: 0.0),
            "depart_at": str (optional, ISO 8601 format)
        }
    
    Response:
        {
            "wkt": str,
            "polygon_name": str,
            "csv": str (CSV content as string)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON body is required"}), 400
        
        # Validate required fields
        required_fields = ['center_lat', 'center_lng', 'time_limit_minutes', 'polygon_name']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        center_lat = float(data['center_lat'])
        center_lng = float(data['center_lng'])
        time_limit = int(data['time_limit_minutes'])
        polygon_name = str(data['polygon_name'])
        
        # Validate coordinates
        if not (-90 <= center_lat <= 90):
            return jsonify({"error": "Latitude must be between -90 and 90"}), 400
        if not (-180 <= center_lng <= 180):
            return jsonify({"error": "Longitude must be between -180 and 180"}), 400
        
        # Get Mapbox token
        mapbox_token = data.get('mapbox_token') or os.environ.get('MAPBOX_API_TOKEN', '')
        if not mapbox_token:
            return jsonify({"error": "Mapbox API token is required"}), 400
        
        # Get optional parameters
        routing_profile = data.get('routing_profile', 'driving')
        generalize_meters = float(data.get('generalize_meters', 0.0))
        depart_at = data.get('depart_at')  # ISO 8601 format string
        
        # Initialize analyzer without API key (not needed for isochrone generation)
        # Isochrone generation only uses Mapbox API, not Google Maps
        analyzer = PolygonAnalyzer()
        
        # Generate isochrone
        wkt_string = analyzer.generate_mapbox_isochrone(
            center_lat=center_lat,
            center_lng=center_lng,
            time_limit_minutes=time_limit,
            mapbox_token=mapbox_token,
            profile=routing_profile,
            generalize_meters=generalize_meters,
            depart_at=depart_at
        )
        
        if not wkt_string:
            return jsonify({"error": "Failed to generate isochrone polygon"}), 500
        
        # Create CSV DataFrame
        df_output = pd.DataFrame([{
            "WKT": wkt_string,
            "name": polygon_name
        }])
        
        # Convert to CSV string
        csv_buffer = io.StringIO()
        df_output.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
                    
        return jsonify({
            "wkt": wkt_string,
            "polygon_name": polygon_name,
            "csv": csv_data
        })
    
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
