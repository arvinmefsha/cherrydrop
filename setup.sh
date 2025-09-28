#!/bin/bash

# OwlHacks Delivery Setup Script

echo "🦉 Setting up OwlHacks Delivery Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3."
    exit 1
fi

echo "✅ Python and pip found"

# Navigate to backend directory
cd backend

echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo "⚙️  Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Please edit .env file with your MongoDB Atlas connection string and other settings"
    echo "   Required settings:"
    echo "   - MONGODB_URL: Your MongoDB Atlas connection string"
    echo "   - SECRET_KEY: A secure random string for JWT tokens"
    echo ""
    echo "   Example MongoDB Atlas URL format:"
    echo "   mongodb+srv://username:password@cluster.mongodb.net/owlhacks_delivery"
    echo ""
fi

echo ""
echo "🚀 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your MongoDB Atlas connection details"
echo "2. Start the backend server:"
echo "   cd backend && uvicorn main:app --reload"
echo "3. Open frontend/index.html in your browser or serve with a local server"
echo ""
echo "📚 For development, you can also serve the frontend with Python:"
echo "   cd frontend && python3 -m http.server 3000"
echo ""
echo "Happy coding! 🦉"