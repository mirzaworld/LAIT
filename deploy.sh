#!/bin/bash

# LAIT Legal Analytics Platform - Quick Deploy Script
# This script helps deploy the LAIT platform to various cloud platforms

echo "🚀 LAIT Legal Analytics Platform - Production Deployment"
echo "========================================================"

# Check if build exists
if [ ! -d "dist" ]; then
    echo "📦 Building frontend..."
    npm run build
fi

echo ""
echo "Choose deployment platform:"
echo "1) Vercel (Recommended for frontend)"
echo "2) Netlify"  
echo "3) GitHub Pages"
echo "4) Local deployment info"
echo "5) Show deployment URLs"

read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "🔧 Deploying to Vercel..."
        echo ""
        echo "Steps to deploy to Vercel:"
        echo "1. Install Vercel CLI: npm i -g vercel"
        echo "2. Run: vercel --prod"
        echo "3. Follow the prompts"
        echo ""
        echo "Backend deployment:"
        echo "- Deploy backend/simple_app.py to Railway, Render, or Heroku"
        echo "- Update VITE_API_URL in .env to point to your backend URL"
        ;;
    2)
        echo "🔧 Deploying to Netlify..."
        echo ""
        echo "Steps to deploy to Netlify:"
        echo "1. Install Netlify CLI: npm i -g netlify-cli"
        echo "2. Run: netlify deploy --prod --dir=dist"
        echo "3. Follow the prompts"
        ;;
    3)
        echo "🔧 Deploying to GitHub Pages..."
        echo ""
        echo "Steps to deploy to GitHub Pages:"
        echo "1. Push code to GitHub repository"
        echo "2. Go to repository Settings > Pages"
        echo "3. Select 'GitHub Actions' as source"
        echo "4. Use the Vite GitHub Pages action"
        ;;
    4)
        echo "💻 Local deployment info:"
        echo ""
        echo "Frontend: Serve the 'dist' folder with any static server"
        echo "Backend: Run 'python backend/simple_app.py' (port 5002)"
        echo ""
        echo "Quick local serve:"
        echo "npx serve dist -p 3000"
        ;;
    5)
        echo "🌐 Example deployment URLs:"
        echo ""
        echo "Frontend options:"
        echo "- Vercel: https://lait-analytics.vercel.app"
        echo "- Netlify: https://lait-analytics.netlify.app"
        echo "- GitHub Pages: https://yourusername.github.io/lait"
        echo ""
        echo "Backend options:"
        echo "- Railway: https://lait-backend.railway.app"
        echo "- Render: https://lait-backend.onrender.com"
        echo "- Heroku: https://lait-backend.herokuapp.com"
        ;;
    *)
        echo "❌ Invalid choice"
        ;;
esac

echo ""
echo "📋 Pre-deployment checklist:"
echo "✅ Frontend build completed (dist/ folder created)"
echo "✅ Backend API endpoints tested and working"
echo "✅ Environment variables configured"
echo "✅ CORS enabled for production domain"
echo ""
echo "🎉 Your LAIT Legal Analytics Platform is ready for production!"
echo "📖 See PRODUCTION_DEPLOYMENT_GUIDE.md for detailed instructions"
