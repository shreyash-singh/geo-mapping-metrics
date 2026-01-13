"""
Streamlit Web App for Polygon Analyzer
Two pages: Geo Metrics and Geo Mapping
"""
import streamlit as st
import pandas as pd
from polygon_analyzer import PolygonAnalyzer
import io
import time
import datetime

# Page configuration
st.set_page_config(
    page_title="Polygon Analyzer",
    page_icon="📍",
    layout="wide"
)

# Sidebar for navigation
st.sidebar.title("📍 Polygon Analyzer")
page = st.sidebar.radio("Navigate to", ["Geo Metrics", "Geo Mapping"])

# Sidebar for API key
st.sidebar.header("Settings")

# Try to get API keys from secrets (for Streamlit Cloud), otherwise use empty default
try:
    default_google_key = st.secrets.get("GOOGLE_MAPS_API_KEY", "")
    default_mapbox_key = st.secrets.get("MAPBOX_API_TOKEN", "")
except (AttributeError, FileNotFoundError, KeyError):
    # Secrets not available (local development)
    default_google_key = ""
    default_mapbox_key = ""

# Google Maps API Key input
api_key = st.sidebar.text_input(
    "Google Maps API Key",
    value=default_google_key,
    type="password",
    help="⚠️ REQUIRED: Enter your own Google Maps API key. Get one at: https://console.cloud.google.com/apis/credentials",
    placeholder="Enter your Google Maps API key"
)

if not api_key:
    st.sidebar.warning("⚠️ Please enter your Google Maps API key to use Geo Metrics")

# Initialize analyzer
def get_analyzer(api_key):
    return PolygonAnalyzer(api_key)

analyzer = get_analyzer(api_key)

# ============================================================================
# PAGE 1: GEO METRICS
# ============================================================================
if page == "Geo Metrics":
    st.title("📍 Geo Metrics")
    st.markdown("""
    Analyze the number of **eateries**, **offices**, **apartments**, **PGs**, **gyms**, and **salons** within polygons using Google Places API.

    ### Instructions:
    1. Upload a CSV file with columns: `WKT` (polygon coordinates) and `name` (polygon name)
    2. Click "Analyze Polygons" to process
    3. Download the results CSV with additional analysis columns
    """)
    
    # File upload
    st.header("📤 Upload CSV File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="CSV file must contain 'WKT' and 'name' columns"
    )
    
    if uploaded_file is not None:
        # Read and display preview
        try:
            df_preview = pd.read_csv(uploaded_file)
            st.success(f"✅ File uploaded successfully! Found {len(df_preview)} polygons.")
            
            # Validate columns
            if 'WKT' not in df_preview.columns:
                st.error("❌ Error: CSV file must contain a 'WKT' column")
                st.stop()
            if 'name' not in df_preview.columns:
                st.error("❌ Error: CSV file must contain a 'name' column")
                st.stop()
            
            # Show preview
            with st.expander("📋 Preview uploaded file"):
                st.dataframe(df_preview.head(10))
                st.caption(f"Total rows: {len(df_preview)}")
            
            # Analysis button
            st.header("🔍 Analysis")
            
            if st.button("🚀 Analyze Polygons", type="primary", use_container_width=True):
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Save uploaded file temporarily
                input_file_path = "temp_input.csv"
                df_preview.to_csv(input_file_path, index=False)
                
                # Process polygons
                try:
                    status_text.text("Processing polygons... This may take a few minutes.")
                    
                    # Process CSV file
                    results_df = analyzer.process_csv_file(input_file_path, output_csv_path=None)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Analysis complete!")
                    
                    # Display results
                    st.header("📊 Results")
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download button
                    csv_buffer = io.StringIO()
                    results_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=csv_data,
                        file_name=f"polygon_analysis_results_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                    
                    # Summary statistics
                    st.header("📈 Summary Statistics")
                    col1, col2, col3, col4, col5, col6 = st.columns(6)
                    
                    with col1:
                        st.metric("Total Eateries", results_df['no. of eateries'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of eateries'].mean():.1f}")
                    
                    with col2:
                        st.metric("Total Offices", results_df['no. of offices'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of offices'].mean():.1f}")
                    
                    with col3:
                        st.metric("Total Apartments", results_df['no. of apartments'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of apartments'].mean():.1f}")
                    
                    with col4:
                        st.metric("Total PGs", results_df['no. of PGs'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of PGs'].mean():.1f}")
                    
                    with col5:
                        st.metric("Total Gyms", results_df['no. of gyms'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of gyms'].mean():.1f}")
                    
                    with col6:
                        st.metric("Total Salons", results_df['no. of salons'].sum())
                        st.metric("Avg per Polygon", f"{results_df['no. of salons'].mean():.1f}")
                
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)
                
                finally:
                    # Clean up temp file
                    import os
                    if os.path.exists(input_file_path):
                        os.remove(input_file_path)
        
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.exception(e)
    
    else:
        # Show example format
        st.info("👆 Please upload a CSV file to begin")
        
        # Example CSV format
        with st.expander("📝 Example CSV Format"):
            example_data = {
                'WKT': [
                    'POLYGON((77.2090 28.6139, 77.2100 28.6149, 77.2090 28.6159, 77.2080 28.6149, 77.2090 28.6139))',
                    'POLYGON((77.2190 28.6239, 77.2200 28.6249, 77.2190 28.6259, 77.2180 28.6249, 77.2190 28.6239))'
                ],
                'name': ['Area_1', 'Area_2']
            }
            example_df = pd.DataFrame(example_data)
            st.dataframe(example_df)
            st.caption("Note: WKT format uses (longitude latitude) order")
    
    # Footer
    st.markdown("---")
    st.caption("💡 Tip: Processing time depends on the number of polygons and API rate limits. Large files may take several minutes.")

# ============================================================================
# PAGE 2: GEO MAPPING
# ============================================================================
elif page == "Geo Mapping":
    st.title("🗺️ Geo Mapping")
    st.markdown("""
    Generate isochrone polygons using Mapbox Isochrone API and export to CSV for Google My Maps.
    
    ### How it works:
    1. Enter origin coordinates (latitude, longitude)
    2. Specify the polygon name and time limit (minutes)
    3. Mapbox calculates the reachable area within the time limit
    4. Download the CSV file with WKT polygons ready for Google My Maps
    """)
    
    # Mapbox API Key in sidebar
    st.sidebar.header("Mapbox Settings")
    
    # Try to get from secrets, otherwise use empty
    try:
        default_mapbox = st.secrets.get("MAPBOX_API_TOKEN", "")
    except (AttributeError, FileNotFoundError, KeyError):
        default_mapbox = ""
    
    mapbox_token = st.sidebar.text_input(
        "Mapbox API Token",
        value=default_mapbox,
        type="password",
        help="⚠️ REQUIRED: Enter your own Mapbox API token. Get one at: https://account.mapbox.com/access-tokens/",
        placeholder="Enter your Mapbox API token"
    )
    
    if not mapbox_token:
        st.sidebar.warning("⚠️ Please enter your Mapbox API token to use Geo Mapping")
    
    # Input form
    st.header("📍 Input Parameters")
    
    center_coords = st.text_input(
        "Origin Coordinates (Latitude, Longitude)",
        value="12.93526, 77.62262",
        help="Enter coordinates as 'latitude, longitude' (e.g., '12.93526, 77.62262')",
        placeholder="12.93526, 77.62262"
    )
    
    # Parse coordinates
    center_lat = None
    center_lng = None
    
    if center_coords:
        try:
            # Split by comma and strip whitespace
            parts = [part.strip() for part in center_coords.split(',')]
            if len(parts) == 2:
                center_lat = float(parts[0])
                center_lng = float(parts[1])
                
                # Validate ranges
                if center_lat < -90 or center_lat > 90:
                    st.error("❌ Latitude must be between -90 and 90")
                    center_lat = None
                if center_lng < -180 or center_lng > 180:
                    st.error("❌ Longitude must be between -180 and 180")
                    center_lng = None
            else:
                st.error("❌ Please enter coordinates in format: 'latitude, longitude'")
        except ValueError:
            st.error("❌ Invalid format. Please enter numbers as 'latitude, longitude' (e.g., '12.93526, 77.62262')")
    
    # Display parsed coordinates if valid
    if center_lat is not None and center_lng is not None:
        st.success(f"✅ Coordinates: Latitude = {center_lat:.6f}, Longitude = {center_lng:.6f}")
    
    polygon_name = st.text_input(
        "Polygon Name",
        value="Kitchen 10-min Isochrone",
        help="Name for this polygon (will appear in CSV)"
    )

    time_limit = st.number_input(
        "Time Limit (minutes)",
        min_value=1,
        value=10,
        help="Maximum travel time in minutes"
    )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        # Routing profile
        routing_profile = st.selectbox(
            "Routing Profile",
            options=["driving", "driving-traffic", "walking", "cycling"],
            index=0,
            help="'driving-traffic' considers real-time and typical traffic conditions"
        )
        
        # Tolerance/Generalization
        generalize_meters = st.number_input(
            "Generalization Tolerance (meters)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            help="Douglas-Peucker simplification tolerance. 0 = no simplification (highest detail), higher values = more simplified polygons"
        )
        
        # Traffic time options
        use_traffic_time = st.checkbox(
            "Use specific departure time for traffic",
            value=False,
            help="Enable to account for traffic conditions at a specific time (e.g., 6 PM rush hour)"
        )
        
        depart_at_datetime = None
        if use_traffic_time:
            col1, col2 = st.columns(2)
            with col1:
                depart_date = st.date_input(
                    "Departure Date",
                    value=datetime.date.today(),
                    help="Date for traffic calculation"
                )
            with col2:
                depart_time = st.time_input(
                    "Departure Time",
                    value=datetime.time(18, 0),  # Default 6 PM
                    help="Time for traffic calculation (e.g., 6 PM for rush hour)"
                )
            
            # Combine date and time into ISO 8601 format
            depart_at_datetime = datetime.datetime.combine(depart_date, depart_time)
            depart_at_iso = depart_at_datetime.strftime("%Y-%m-%dT%H:%M")
            
            st.info(f"📅 Traffic will be calculated for: {depart_at_datetime.strftime('%Y-%m-%d %I:%M %p')}")
            
            # Note about driving-traffic profile
            if routing_profile != "driving-traffic":
                st.warning("⚠️ For traffic-aware routing, consider using 'driving-traffic' profile above")
        else:
            depart_at_iso = None
    
    # Generate button
    if st.button("🚀 Generate Isochrone Polygon", type="primary", use_container_width=True):
        if not polygon_name:
            st.error("❌ Please enter a polygon name")
        elif center_lat is None or center_lng is None:
            st.error("❌ Please enter valid coordinates in format: 'latitude, longitude'")
        elif not mapbox_token:
            st.error("❌ Please enter Mapbox API token in the sidebar")
        else:
            try:
                status_text = st.empty()
                status_text.text("🔄 Generating isochrone polygon using Mapbox API...")
                
                # Generate isochrone using Mapbox
                wkt_string = analyzer.generate_mapbox_isochrone(
                    center_lat=center_lat,
                    center_lng=center_lng,
                    time_limit_minutes=time_limit,
                    mapbox_token=mapbox_token,
                    profile=routing_profile,
                    generalize_meters=generalize_meters,
                    depart_at=depart_at_iso if use_traffic_time else None
                )
                
                if wkt_string:
                    status_text.text("✅ Polygon generated successfully!")
                    st.success(f"✅ Generated isochrone polygon!")
                    
                    # Show preview
                    with st.expander("📋 Preview Generated Polygon"):
                        st.code(wkt_string[:300] + "..." if len(wkt_string) > 300 else wkt_string)
                    
                    # Create DataFrame and download button
                    df_output = pd.DataFrame([{
                        "WKT": wkt_string,
                        "name": polygon_name
                    }])
                    
                    # Display result
                    st.header("📊 Generated Polygon")
                    st.dataframe(df_output, use_container_width=True)
                    
                    # Download button
                    csv_buffer = io.StringIO()
                    df_output.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"isochrone_polygon_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Failed to generate polygon. Please check your Mapbox API token and try again.")
            
            except Exception as e:
                st.error(f"❌ Error generating polygon: {str(e)}")
                st.exception(e)
    
    # Info section
    st.markdown("---")
    st.info("""
    **Note:** 
    - Uses Mapbox Isochrone API for fast and accurate polygon generation
    - Processing time: ~1-2 seconds (single API call)
    - The CSV file contains WKT and name columns, ready for Google My Maps import
    - Profile: driving (car routing)
    """)
