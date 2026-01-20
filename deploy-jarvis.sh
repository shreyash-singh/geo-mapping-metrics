#!/bin/bash
# Quick deployment script for Jarvis to Vercel

echo "🚀 Deploying Jarvis to Vercel..."
echo ""

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Install it with: npm i -g vercel"
    exit 1
fi

# Backup existing vercel.json if it exists
if [ -f "vercel.json" ]; then
    echo "📦 Backing up existing vercel.json..."
    cp vercel.json vercel.json.backup
    echo "   Backup saved as vercel.json.backup"
fi

# Use Jarvis config
echo "📝 Using Jarvis Vercel configuration..."
cp vercel-jarvis.json vercel.json
echo "   ✅ vercel.json now points to jarvis_app.py"

# Verify the config
echo ""
echo "📋 Current vercel.json configuration:"
cat vercel.json | grep -A 2 '"src"'
echo ""

# Deploy
echo "🌐 Deploying to Vercel..."
echo "   (This may take a minute...)"
vercel --prod

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "⚠️  IMPORTANT: Restoring original vercel.json..."
    if [ -f "vercel.json.backup" ]; then
        mv vercel.json.backup vercel.json
        echo "   ✅ Original vercel.json restored"
    fi
    echo ""
    echo "🎉 Your Jarvis app should be live!"
else
    echo ""
    echo "❌ Deployment failed. Check the error above."
    echo "   Restoring original vercel.json..."
    if [ -f "vercel.json.backup" ]; then
        mv vercel.json.backup vercel.json
    fi
    exit 1
fi
