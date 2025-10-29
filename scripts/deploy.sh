#!/bin/bash
# Deployment script for AI Bug Detection Tool

set -e

echo "🚀 Starting deployment..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q numpy scikit-learn

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd backend/api
npm install --silent
cd ../..

# Train ML model
echo "🧠 Training ML model..."
python backend/ml_engine/train.py

# Run tests
echo "🧪 Running tests..."
pytest tests/ -q || echo "⚠️  Some tests failed"

# Start API server
echo "🌐 Starting API server..."
cd backend/api
npm start &
API_PID=$!
cd ../..

echo "✅ Deployment complete!"
echo "API running on http://localhost:3001"
echo "Health check: http://localhost:3001/health"
echo ""
echo "To stop the server: kill $API_PID"
