# Deploying Jarvis to Vercel

Yes! You can absolutely host Jarvis on Vercel. Here are two approaches:

## Option 1: Deploy as Separate Vercel Project (Recommended)

This keeps Jarvis separate from your geo-mapping app, which is cleaner.

### Steps:

1. **Rename the Vercel config** (or use a separate directory):
   ```bash
   # Copy vercel-jarvis.json to vercel.json in a separate folder, or:
   cp vercel-jarvis.json vercel.json
   ```

2. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

3. **Login to Vercel**:
   ```bash
   vercel login
   ```

4. **Deploy Jarvis**:
   ```bash
   # From your project root
   vercel --prod
   ```
   
   When prompted:
   - **Set up and deploy?** → Yes
   - **Which scope?** → Your account
   - **Link to existing project?** → No (create new)
   - **Project name?** → `jarvis` (or your preferred name)
   - **Directory?** → `.` (current directory)
   - **Override settings?** → Yes, and point to `jarvis_app.py`

5. **Set Environment Variables** (optional):
   ```bash
   vercel env add JARVIS_MEALS_SHEET_URL
   ```
   Or set it in Vercel Dashboard → Project Settings → Environment Variables

6. **Update vercel.json**:
   Make sure `vercel.json` points to `jarvis_app.py`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "jarvis_app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "jarvis_app.py"
       }
     ]
   }
   ```

## Option 2: Deploy Both Apps in Same Project (Advanced)

If you want both apps in one Vercel project, you'll need to modify routing:

### Create a router app (`vercel_app.py`):

```python
from flask import Flask, request
import os

app = Flask(__name__)

# Import both apps
from app import app as geo_app
from jarvis_app import app as jarvis_app

@app.route('/jarvis/<path:path>')
def jarvis_route(path):
    """Route /jarvis/* to Jarvis app"""
    with jarvis_app.test_request_context(path=f'/{path}', method=request.method):
        return jarvis_app.full_dispatch_request()

@app.route('/<path:path>')
def geo_route(path):
    """Route everything else to geo-mapping app"""
    with geo_app.test_request_context(path=f'/{path}', method=request.method):
        return geo_app.full_dispatch_request()
```

This is more complex, so **Option 1 is recommended**.

## Quick Deploy Checklist

- [ ] `jarvis_app.py` exists and has Flask `app` instance (lowercase `app`)
- [ ] `templates/jarvis.html` exists
- [ ] `requirements.txt` includes all dependencies (pandas, requests, flask, flask-cors)
- [ ] `vercel.json` points to `jarvis_app.py` correctly
- [ ] Environment variables set in Vercel dashboard (if needed)

## Important: Fixing 404 Errors

If you get a `404 NOT_FOUND` error on Vercel:

1. **Make sure `vercel.json` is correct:**
   ```json
   {
     "version": 2,
     "builds": [
       { "src": "jarvis_app.py", "use": "@vercel/python" }
     ],
     "routes": [
       { "src": "/(.*)", "dest": "jarvis_app.py" }
     ]
   }
   ```

2. **Ensure Flask app instance is named `app` (lowercase)** - ✅ Already correct

3. **Test locally first:**
   ```bash
   ./test-jarvis-local.sh
   # Or: python3 jarvis_app.py
   # Then visit http://localhost:5001
   ```

4. **Test with Vercel CLI locally:**
   ```bash
   # Make sure vercel.json is active (backup the other one)
   cp vercel-jarvis.json vercel.json
   vercel dev
   ```

5. **Check Vercel build logs** in the dashboard for any errors during build

## Testing Locally with Vercel

Before deploying, test locally:
```bash
vercel dev
```

This simulates the Vercel environment and helps catch issues early.

## Important Notes

1. **Port**: The app uses port 5001 locally, but Vercel handles routing automatically
2. **Dependencies**: Make sure `requirements.txt` includes:
   - flask
   - flask-cors
   - pandas
   - requests
3. **Templates**: Vercel automatically includes the `templates/` folder
4. **Timeout**: Vercel serverless functions have a 10-second timeout on Hobby plan. Meal fetching should be fast enough, but if you hit issues, consider the Pro plan.

## Troubleshooting

**"Module not found"**
- Ensure all dependencies are in `requirements.txt`

**"Template not found"**
- Verify `templates/jarvis.html` exists
- Check that `template_folder='templates'` is set in Flask app

**"Function timeout"**
- Meal fetching should be quick, but if your Google Sheet is very large, consider pagination
- Upgrade to Pro plan for 60-second timeout if needed

## After Deployment

Your Jarvis app will be available at:
- Preview: `https://jarvis-xxx.vercel.app`
- Production: `https://jarvis.vercel.app` (or your custom domain)

You can then:
1. Share the URL
2. Use it on any device
3. Update your Google Sheets and refresh to see new meals instantly!
