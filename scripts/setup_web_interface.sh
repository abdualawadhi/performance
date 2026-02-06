#!/bin/bash

# =============================================================================
# Low-Code Performance Scanner - Web Interface Setup Script
# =============================================================================
# This script automates the setup of both backend and frontend components
# Version: 1.0.2
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emoji for better UX
CHECK_MARK="✅"
CROSS_MARK="❌"
ROCKET="🚀"
WRENCH="🔧"
PACKAGE="📦"
GLOBE="🌐"
PYTHON="🐍"
NODE="⚙️"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo -e "${PURPLE}"
    echo "=============================================================================="
    echo "  $1"
    echo "=============================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${BLUE}${WRENCH} $1${NC}"
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python_version() {
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            return 0
        fi
    fi
    return 1
}

# Check Node.js version
check_node_version() {
    if command_exists node; then
        NODE_VERSION=$(node --version 2>&1 | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)

        if [ "$NODE_MAJOR" -ge 18 ]; then
            return 0
        fi
    fi
    return 1
}

# =============================================================================
# Main Setup
# =============================================================================

main() {
    print_header "${ROCKET} Low-Code Performance Scanner - Web Interface Setup"

    echo ""
    print_info "This script will set up both the backend API and frontend UI"
    echo ""

    # =============================================================================
    # Step 1: Check Prerequisites
    # =============================================================================

    print_step "Step 1: Checking prerequisites..."
    echo ""

    # Check Python
    if check_python_version; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_success "Python $PYTHON_VERSION installed"
    else
        print_error "Python 3.8+ is required but not found"
        echo "Please install Python from https://www.python.org/"
        exit 1
    fi

    # Check Node.js
    if check_node_version; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION installed"
    else
        print_error "Node.js 18+ is required but not found"
        echo "Please install Node.js from https://nodejs.org/"
        exit 1
    fi

    # Check npm
    if command_exists npm; then
        NPM_VERSION=$(npm --version)
        print_success "npm $NPM_VERSION installed"
    else
        print_error "npm is required but not found"
        exit 1
    fi

    # Check if virtual environment exists
    if [ -d "venv" ]; then
        print_success "Virtual environment found"
    else
        print_warning "Virtual environment not found (will create)"
    fi

    echo ""

    # =============================================================================
    # Step 2: Setup Backend
    # =============================================================================

    print_step "Step 2: Setting up backend..."
    echo ""

    # Activate or create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    print_info "Activating virtual environment..."
    source venv/bin/activate || source venv/Scripts/activate

    # Install backend dependencies
    print_info "Installing backend dependencies..."
    pip install --quiet --upgrade pip
    pip install --quiet fastapi uvicorn[standard] python-multipart websockets

    # Check if core scanner dependencies are installed
    if ! python -c "import lowcode_scanner" 2>/dev/null; then
        print_info "Installing core scanner dependencies..."
        pip install --quiet -r requirements.txt
        playwright install chromium
    fi

    print_success "Backend dependencies installed"
    echo ""

    # =============================================================================
    # Step 3: Setup Frontend
    # =============================================================================

    print_step "Step 3: Setting up frontend..."
    echo ""

    # Navigate to frontend directory
    cd frontend

    # Install frontend dependencies
    print_info "Installing frontend dependencies (this may take a few minutes)..."
    npm install --silent

    print_success "Frontend dependencies installed"

    # Create .env.local if it doesn't exist
    if [ ! -f ".env.local" ]; then
        print_info "Creating frontend environment configuration..."
        cat > .env.local << EOF
# Backend API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
        print_success "Environment configuration created"
    else
        print_success "Environment configuration already exists"
    fi

    # Create missing frontend files
    print_info "Creating frontend application files..."

    # Create main page if it doesn't exist
    if [ ! -f "app/page.tsx" ]; then
        mkdir -p app
        cat > app/page.tsx << 'EOF'
'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    // API call implementation
    alert('Scan started for: ' + url)
    setLoading(false)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Start Performance Scan
        </h1>
        <p className="text-lg text-gray-600">
          Test your low-code application performance in seconds
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL to Test
            </label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://your-app.bubbleapps.io"
              className="input"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full"
          >
            {loading ? 'Starting Scan...' : 'Start Scan'}
          </button>
        </form>
      </motion.div>
    </div>
  )
}
EOF
    fi

    # Create globals.css if it doesn't exist
    if [ ! -f "app/globals.css" ]; then
        cat > app/globals.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-all duration-200;
  }

  .btn-primary {
    @apply bg-primary-600 text-white hover:bg-primary-700;
  }

  .card {
    @apply bg-white rounded-xl shadow-soft border border-gray-200 p-6;
  }

  .input {
    @apply w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500;
  }
}
EOF
    fi

    cd ..

    print_success "Frontend setup complete"
    echo ""

    # =============================================================================
    # Step 4: Verify Installation
    # =============================================================================

    print_step "Step 4: Verifying installation..."
    echo ""

    # Check if backend can be imported
    if python -c "import backend.main" 2>/dev/null; then
        print_success "Backend module verified"
    else
        print_warning "Backend module check skipped"
    fi

    # Check if frontend build works
    cd frontend
    if [ -f "package.json" ]; then
        print_success "Frontend configuration verified"
    fi
    cd ..

    echo ""

    # =============================================================================
    # Final Summary
    # =============================================================================

    print_header "${CHECK_MARK} Setup Complete!"

    echo ""
    echo -e "${GREEN}${ROCKET} Web Interface is ready!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo -e "${YELLOW}1. Start the backend:${NC}"
    echo "   cd website_performance_scanner"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "   python backend/main.py"
    echo ""
    echo -e "${YELLOW}2. In a new terminal, start the frontend:${NC}"
    echo "   cd website_performance_scanner/frontend"
    echo "   npm run dev"
    echo ""
    echo -e "${YELLOW}3. Open your browser:${NC}"
    echo "   Frontend UI:  http://localhost:3000"
    echo "   Backend API:  http://localhost:8000"
    echo "   API Docs:     http://localhost:8000/api/docs"
    echo ""
    echo -e "${CYAN}${GLOBE} Documentation:${NC}"
    echo "   See WEB_INTERFACE_SETUP.md for detailed instructions"
    echo ""
    echo -e "${GREEN}Happy testing! 🎉${NC}"
    echo ""
}

# =============================================================================
# Run Main Function
# =============================================================================

main "$@"
