# Setting Up API Keys for Streamlit Deployment

This application requires API keys for both Google Maps and Mapbox. **Each user must provide their own API keys.**

## Option 1: Using Streamlit Cloud Secrets (Recommended for Deployment)

When deploying on Streamlit Community Cloud:

1. Go to your app's settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Add your API keys in TOML format:

```toml
GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"
MAPBOX_API_TOKEN = "your_mapbox_api_token_here"
```

4. Save the secrets
5. The app will use these secrets, but users can still override them in the sidebar

## Option 2: Local Development

For local development:

1. Copy the example secrets file:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. Edit `.streamlit/secrets.toml` and add your API keys:
   ```toml
   GOOGLE_MAPS_API_KEY = "your_google_maps_api_key_here"
   MAPBOX_API_TOKEN = "your_mapbox_api_token_here"
   ```

3. **Important**: The `secrets.toml` file is in `.gitignore` and will NOT be committed to the repository

## Option 3: Enter Keys in the App (Always Available)

Users can always enter their API keys directly in the app's sidebar:
- **Google Maps API Key**: Required for Geo Metrics tab
- **Mapbox API Token**: Required for Geo Mapping tab

The app will prioritize:
1. Keys entered in the sidebar (highest priority)
2. Keys from secrets.toml (if available)
3. Empty (will show warnings)

## Getting API Keys

### Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Places API
   - Routes API
   - Directions API
4. Create credentials → API Key
5. Restrict the API key (recommended) to only the APIs you need

### Mapbox API Token
1. Go to [Mapbox Account](https://account.mapbox.com/access-tokens/)
2. Sign up or log in
3. Create a new access token
4. Copy the token (starts with `pk.`)

## Security Notes

- ⚠️ **Never commit API keys to the repository**
- ⚠️ **Each user should use their own API keys**
- ⚠️ **Restrict API keys to specific APIs and domains when possible**
- ⚠️ **Monitor API usage to prevent unexpected charges**
