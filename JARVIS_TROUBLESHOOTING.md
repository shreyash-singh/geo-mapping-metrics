# Jarvis Troubleshooting Guide

## Issue: 404 NOT_FOUND Error

### Step 1: Test Locally First

```bash
# Test if the app runs locally
python3 jarvis_app.py

# In another terminal, test the endpoint
curl http://localhost:5001/api/health
```

If this works locally but not on Vercel, continue to Step 2.

### Step 2: Check Vercel Configuration

**CRITICAL**: Make sure you're using the correct `vercel.json` for Jarvis!

```bash
# Backup your current vercel.json (if it's for geo-mapping app)
cp vercel.json vercel.json.geo-backup

# Use Jarvis config
cp vercel-jarvis.json vercel.json

# Verify the content
cat vercel.json
```

The `vercel.json` should contain:
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

### Step 3: Deploy with Correct Config

```bash
# Make sure vercel.json points to jarvis_app.py
vercel --prod
```

### Step 4: Check Vercel Build Logs

1. Go to Vercel Dashboard
2. Click on your project
3. Go to "Deployments"
4. Click on the latest deployment
5. Check "Build Logs" for any errors

Common issues:
- Missing dependencies in `requirements.txt`
- Template file not found
- Python version mismatch

### Step 5: Verify File Structure

Make sure these files exist:
```
geo-mapping-metrics/
├── jarvis_app.py          ✅ Must exist
├── vercel.json            ✅ Must point to jarvis_app.py
├── requirements.txt       ✅ Must include flask, pandas, requests
└── templates/
    └── jarvis.html        ✅ Must exist
```

### Step 6: Test with Vercel CLI Locally

```bash
# Install Vercel CLI if not installed
npm i -g vercel

# Test locally with Vercel's environment
vercel dev
```

This simulates Vercel's environment and helps catch issues.

## Common Fixes

### Fix 1: Wrong vercel.json
**Symptom**: 404 on all routes
**Solution**: Use `vercel-jarvis.json` as your `vercel.json` before deploying

### Fix 2: Missing Dependencies
**Symptom**: Build fails or runtime errors
**Solution**: Ensure `requirements.txt` has:
```
flask==3.0.0
flask-cors==4.0.0
pandas==2.0.3
requests==2.31.0
```

### Fix 3: Template Not Found
**Symptom**: 500 error on homepage
**Solution**: Ensure `templates/jarvis.html` exists and `template_folder='templates'` is set in Flask app

### Fix 4: Flask App Not Detected
**Symptom**: 404 on all routes
**Solution**: Ensure Flask instance is named `app` (lowercase) in `jarvis_app.py`

## Quick Test Commands

```bash
# 1. Test app loads
python3 -c "from jarvis_app import app; print('✅ App loaded')"

# 2. Test locally
python3 jarvis_app.py
# Visit http://localhost:5001

# 3. Test API endpoint
curl http://localhost:5001/api/health

# 4. Test with Vercel CLI
vercel dev
```

## Still Not Working?

1. **Check Vercel Dashboard** → Your Project → Settings → Build & Development Settings
   - Ensure "Build Command" is empty (Vercel auto-detects Python)
   - Ensure "Output Directory" is empty

2. **Check Environment Variables** (if using):
   - Vercel Dashboard → Settings → Environment Variables
   - `JARVIS_MEALS_SHEET_URL` (optional)

3. **Check Python Version**:
   - Vercel uses Python 3.12 by default
   - Your code should be compatible

4. **Redeploy**:
   ```bash
   vercel --prod --force
   ```

## Getting Help

If still stuck, check:
- Vercel build logs in dashboard
- Browser console for frontend errors
- Network tab for API errors
- Vercel function logs
