# Run Locally - Quick Start Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Run the App
```bash
python3 app.py
```

### 3. Open in Browser
Visit: **http://localhost:5000**

---

## 📋 Detailed Steps

### Prerequisites
- Python 3.7+ installed
- pip installed

### Step-by-Step

1. **Navigate to project directory:**
   ```bash
   cd /Users/shreyashsingh/Desktop/geo-mapping-metrics
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```
   
   Or if using virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set environment variables (optional):**
   ```bash
   export GOOGLE_MAPS_API_KEY="your-api-key-here"
   export MAPBOX_API_TOKEN="your-mapbox-token-here"
   ```
   
   Or create a `.env` file (make sure it's in `.gitignore`)

4. **Run the Flask app:**
   ```bash
   python3 app.py
   ```
   
   You should see:
   ```
   * Running on http://0.0.0.0:5000
   * Debug mode: on
   ```

5. **Open your browser:**
   - **Main App:** http://localhost:5000
   - **Health Check:** http://localhost:5000/api/health

---

## 🧪 Test the API

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Test CSV Upload (using curl)
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "file=@your_file.csv" \
  -F "google_maps_api_key=your-api-key"
```

---

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is busy:
```bash
# Find process using port 5000
lsof -ti:5000

# Kill it
kill -9 $(lsof -ti:5000)

# Or use a different port
PORT=5001 python3 app.py
```

### Module Not Found
```bash
# Reinstall dependencies
pip3 install -r requirements.txt --upgrade
```

### API Key Issues
- Make sure your Google Maps API key is valid
- Check API is enabled in Google Cloud Console
- Verify billing is set up (if required)

---

## 📁 Project Structure

```
geo-mapping-metrics/
├── app.py                 # Main Flask app
├── polygon_analyzer.py   # Core analysis logic
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web UI
└── README.md
```

---

## 🔗 Quick Links

- **Local URL:** http://localhost:5000
- **Health Check:** http://localhost:5000/api/health
- **API Docs:** See README.md

---

## ✅ Verify It's Working

1. Open http://localhost:5000
2. You should see the "Conquest - Geo Analytics Platform" homepage
3. Try uploading a CSV file with WKT and name columns
4. Enter your Google Maps API key
5. Click "Analyze Polygons"

---

**That's it! Your app is running locally.** 🎉
