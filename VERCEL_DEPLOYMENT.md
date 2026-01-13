# Vercel Deployment Guide

## How Vercel Serves Your Flask App

### 1. **Automatic Detection**
Vercel automatically detects Flask applications when it finds:
- A file named `app.py`, `index.py`, or `server.py` in the root directory
- A Flask app instance named `app` in that file
- A `requirements.txt` file with Flask dependencies

### 2. **Configuration File (`vercel.json`)**
The `vercel.json` file tells Vercel:
- **What to build**: Points to `app.py` as the entry point
- **How to build it**: Uses `@vercel/python` builder (automatically handles Python dependencies)
- **How to route requests**: Routes all requests (`/(.*)`) to `app.py`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app.py",        // Entry point file
      "use": "@vercel/python" // Python builder
    }
  ],
  "routes": [
    {
      "src": "/(.*)",         // All requests
      "dest": "app.py"         // Go to app.py
    }
  ]
}
```

### 3. **How It Works**

1. **Build Phase**:
   - Vercel reads `requirements.txt` and installs all dependencies
   - Vercel uses `@vercel/python` to package your Flask app
   - Your `app.py` file is processed and the Flask `app` instance is exported

2. **Runtime**:
   - Vercel converts your Flask app into serverless functions
   - Each request is handled by a serverless function
   - The Flask app instance (`app`) is automatically available to Vercel

3. **Request Flow**:
   ```
   User Request → Vercel Edge Network → Serverless Function → Flask App → Response
   ```

### 4. **What Gets Deployed**

**Included** (automatically):
- All Python files (`.py`)
- `requirements.txt` (dependencies)
- `vercel.json` (configuration)
- `templates/` folder (HTML templates)
- Any other files in your project root

**Excluded** (via `.gitignore`):
- `__pycache__/` (Python cache)
- `.venv/` or `venv/` (virtual environments)
- `.env` (environment variables - set in Vercel dashboard instead)
- `*.pyc` (compiled Python files)

### 5. **Environment Variables**

**Important**: Environment variables are NOT set in `vercel.json`. They must be set in:
- Vercel Dashboard → Project Settings → Environment Variables
- Or via Vercel CLI: `vercel env add VARIABLE_NAME`

Your app reads them using:
```python
os.environ.get('GOOGLE_MAPS_API_KEY', '')
```

### 6. **File Structure for Vercel**

```
geo-mapping-metrics/
├── app.py                 # Flask app (entry point)
├── polygon_analyzer.py   # Your business logic
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── templates/           # HTML templates
│   └── index.html
├── .gitignore          # Files to exclude
└── README.md
```

### 7. **Deployment Steps**

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login**:
   ```bash
   vercel login
   ```

3. **Deploy** (first time):
   ```bash
   vercel
   ```
   This creates a preview deployment.

4. **Set Environment Variables**:
   ```bash
   vercel env add GOOGLE_MAPS_API_KEY
   vercel env add MAPBOX_API_TOKEN
   ```
   Or set them in the Vercel dashboard.

5. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

### 8. **How Vercel Handles Flask Routes**

When a request comes in:
1. Vercel receives the request at the edge
2. Routes it to your Flask app based on `vercel.json`
3. Flask's routing system handles it:
   - `GET /` → `index()` function → Returns HTML
   - `POST /api/analyze` → `analyze_polygons()` function
   - `POST /api/isochrone` → `generate_isochrone()` function

### 9. **Static Files & Templates**

- **Templates**: Flask automatically finds templates in the `templates/` folder
- **Static Files**: If you have CSS/JS/images, put them in a `static/` folder and reference them in your HTML

### 10. **Serverless Function Limits**

Vercel serverless functions have:
- **Timeout**: 10 seconds (Hobby), 60 seconds (Pro), 300 seconds (Enterprise)
- **Memory**: 1024 MB default
- **Cold Starts**: First request may be slower (~1-2 seconds)

For long-running operations (like polygon analysis), consider:
- Using background jobs
- Breaking work into smaller chunks
- Using Vercel Pro plan for longer timeouts

### 11. **Testing Locally**

Before deploying, test with Vercel CLI:
```bash
vercel dev
```
This simulates the Vercel environment locally.

### 12. **Troubleshooting**

**Issue**: "Module not found"
- **Solution**: Ensure all dependencies are in `requirements.txt`

**Issue**: "Environment variable not set"
- **Solution**: Set it in Vercel dashboard, not in code

**Issue**: "Template not found"
- **Solution**: Ensure `templates/` folder is in the root directory

**Issue**: "Function timeout"
- **Solution**: Optimize your code or upgrade to Pro plan for longer timeouts
