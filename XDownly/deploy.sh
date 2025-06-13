#!/bin/bash

# Downly Deployment Script
echo "🚀 Deploying Downly..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment
print_status "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Create downloads directory
print_status "Creating downloads directory..."
mkdir -p downloads

# Copy environment file
if [ ! -f .env ]; then
    print_status "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your configuration!"
fi

# Set permissions
print_status "Setting permissions..."
chmod +x deploy.sh
chmod 755 downloads

print_status "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python app.py (for development)"
echo "4. Or run: gunicorn app:app (for production)"
echo ""
echo "🌐 Your Downly app will be available at http://localhost:5000"
