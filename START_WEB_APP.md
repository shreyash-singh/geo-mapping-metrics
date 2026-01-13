# How to Run the Web App

## Quick Start

1. **Open Terminal** and navigate to the project directory:
   ```bash
   cd /Users/shreyashsingh
   ```

2. **Start the Streamlit web app**:
   ```bash
   streamlit run app.py
   ```

3. **The app will automatically open in your browser** at:
   ```
   http://localhost:8501
   ```

4. **If it doesn't open automatically**, copy the URL from the terminal and paste it into your browser.

## What You'll See

- **Upload Section**: Upload your CSV file with WKT polygons
- **Preview**: See a preview of your uploaded file
- **Analyze Button**: Click to start processing
- **Results**: View the analysis results in a table
- **Download Button**: Download the results CSV file
- **Summary Statistics**: See totals and averages

## Using the Web App

1. Click "Browse files" or drag and drop your CSV file
2. Make sure your CSV has `WKT` and `name` columns
3. Click "🚀 Analyze Polygons" button
4. Wait for processing (shows progress)
5. View results and click "📥 Download Results CSV"

## Stopping the Web App

Press `Ctrl + C` in the terminal to stop the server.

## Troubleshooting

- **Port already in use?** Streamlit will automatically use the next available port (8502, 8503, etc.)
- **Module not found?** Run: `pip3 install -r requirements.txt`
- **Browser doesn't open?** Manually go to `http://localhost:8501`
