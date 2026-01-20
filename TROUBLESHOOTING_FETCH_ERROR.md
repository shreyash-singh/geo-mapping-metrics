# Troubleshooting "Failed to fetch" Error

## Common Causes

### 1. **Server Not Running**
**Symptom**: Immediate "Failed to fetch" error
**Solution**: 
```bash
# Check if server is running
lsof -ti:5000

# Start the server
python3 app.py
# Should see: "Running on http://0.0.0.0:5000"
```

### 2. **Request Timeout**
**Symptom**: Error after waiting for a while (especially with large CSV files)
**Cause**: Processing takes too long (>5 minutes)
**Solution**: 
- Use smaller CSV files
- The app now has a 5-minute timeout
- Check server logs for processing progress

### 3. **Server Crashed During Processing**
**Symptom**: Error occurs mid-processing
**Solution**:
- Check server terminal for error messages
- Look for Python tracebacks
- Common causes:
  - Invalid API key
  - Network issues calling Google Maps API
  - Memory issues with large files

### 4. **CORS Issues**
**Symptom**: Error in browser console about CORS
**Solution**: Already handled - `CORS(app)` is enabled

### 5. **Wrong URL/Port**
**Symptom**: Immediate connection error
**Solution**: 
- Make sure you're accessing `http://localhost:5000`
- Check if port 5000 is correct
- If using Vercel, use the Vercel URL

## Debugging Steps

### Step 1: Check Server Status
```bash
# Check if server is running
curl http://localhost:5000/api/health

# Should return:
# {"status":"ok","message":"Conquest API is running",...}
```

### Step 2: Check Browser Console
1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Try the request again
4. Look for:
   - Red failed requests
   - Status codes (500, 502, 503, etc.)
   - Error messages

### Step 3: Check Server Logs
Look at the terminal where `app.py` is running:
- Any Python errors?
- Any tracebacks?
- "Connection refused" messages?

### Step 4: Test with Smaller File
Try uploading a very small CSV file (1-2 rows) to see if it's a timeout issue.

### Step 5: Check API Keys
Make sure your Google Maps API key is valid:
- Check in Google Cloud Console
- Verify API is enabled
- Check quota/limits

## Quick Fixes

### Restart Server
```bash
# Kill existing server
pkill -f "python.*app.py"

# Start fresh
python3 app.py
```

### Increase Timeout (if needed)
The frontend now has a 5-minute timeout. For longer processing:
- Edit `templates/index.html`
- Change `300000` (5 min) to a higher value
- Or process files in smaller batches

### Check File Size
Large CSV files can cause:
- Memory issues
- Timeout errors
- Server crashes

**Recommendation**: Process files with < 100 polygons at a time.

## Still Not Working?

1. **Check server logs** - Look for Python errors
2. **Test API directly**:
   ```bash
   curl -X POST http://localhost:5000/api/health
   ```
3. **Check network tab** - See exact error response
4. **Try different browser** - Rule out browser issues
5. **Check firewall** - Make sure port 5000 isn't blocked

## Error Messages Explained

- **"Failed to fetch"** = Can't connect to server
- **"Network error"** = Connection issue
- **"Request timed out"** = Processing took too long
- **"CORS error"** = Cross-origin issue (shouldn't happen with relative URLs)
