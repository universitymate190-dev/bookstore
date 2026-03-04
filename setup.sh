#!/bin/bash
# Quick Start Script for Bookstore Website
# This script sets up and runs the Bookstore application

echo "🚀 Starting Bookstore Setup..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create necessary directories
echo "📁 Creating upload directories..."
mkdir -p uploads/books
mkdir -p uploads/notes
mkdir -p uploads/exams
echo "✅ Upload directories created"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "📖 To start the application, run:"
echo "   source venv/bin/activate"
echo "   python app.py"
echo ""
echo "🌐 Then open in your browser:"
echo "   http://localhost:5000"
echo ""
echo "📊 To add sample data (optional):"
echo "   python populate_db.py"
echo ""
echo "⚡ The app will create database.db automatically on first run"
