#!/bin/bash

# Descope AI GTM Intelligence Engine Setup Script
# ===============================================

echo "🚀 Descope AI GTM Intelligence Engine Setup"
echo "=" * 45

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python $PYTHON_VERSION found"
else
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_info "Installing Python packages..."
pip install -r requirements.txt
print_status "All packages installed successfully"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating environment configuration..."
    cp .env.example .env
    print_warning "Please edit .env file with your API keys"
    print_info "Required: OPENAI_API_KEY"
    print_info "Optional: GITHUB_TOKEN, REDDIT_CLIENT_ID, etc."
else
    print_warning ".env file already exists"
fi

echo
print_status "Setup completed successfully!"
echo
print_info "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run the demo: python demo.py"
echo "3. Launch dashboard: streamlit run dashboard.py"
echo "4. Explore the code in main.py"
echo
print_info "For help, check README.md or run: python main.py"
echo
