#!/bin/bash
#
# Low-Code Performance Scanner - Setup Script
# ===========================================
#
# This script sets up the development environment for the Low-Code Performance Scanner.
# It handles Python environment setup, dependency installation, and Playwright browser installation.
#
# Usage: ./scripts/setup.sh [OPTIONS]
#   Options:
#     --dev          Install development dependencies
#     --production   Set up for production deployment
#     --docker       Set up Docker environment
#     --help         Show this help message
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.8"
NODE_VERSION="18"
VENV_DIR="venv"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Flags
INSTALL_DEV=false
PRODUCTION_MODE=false
DOCKER_MODE=false

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print banner
print_banner() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║        Low-Code Performance Scanner - Setup Script         ║"
    echo "║                                                            ║"
    echo "║   This script will set up your development environment    ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --dev          Install development dependencies (testing, linting)"
    echo "  --production   Set up for production deployment"
    echo "  --docker       Set up Docker environment"
    echo "  --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Basic setup"
    echo "  $0 --dev                    # Setup with dev dependencies"
    echo "  $0 --production             # Production setup"
    echo "  $0 --docker                 # Docker setup"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python version
check_python() {
    log_info "Checking Python installation..."
    
    if ! command_exists python3; then
        log_error "Python 3 is not installed. Please install Python $PYTHON_VERSION or higher."
        exit 1
    fi
    
    PYTHON_VERSION_INSTALLED=$(python3 --version | cut -d' ' -f2)
    log_info "Found Python $PYTHON_VERSION_INSTALLED"
    
    # Check if version is sufficient
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_error "Python $PYTHON_VERSION or higher is required. Found: $PYTHON_VERSION_INSTALLED"
        exit 1
    fi
    
    log_success "Python version check passed"
}

# Check Node.js installation
check_node() {
    log_info "Checking Node.js installation..."
    
    if ! command_exists node; then
        log_warning "Node.js is not installed. Frontend development will not be available."
        log_info "To install Node.js, visit: https://nodejs.org/"
        return 1
    fi
    
    NODE_VERSION_INSTALLED=$(node --version | cut -d'v' -f2)
    log_info "Found Node.js $NODE_VERSION_INSTALLED"
    
    log_success "Node.js check passed"
    return 0
}

# Create virtual environment
create_venv() {
    log_info "Creating Python virtual environment..."
    
    cd "$PROJECT_ROOT"
    
    if [ -d "$VENV_DIR" ]; then
        log_warning "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    python3 -m venv "$VENV_DIR"
    log_success "Virtual environment created"
}

# Activate virtual environment
activate_venv() {
    log_info "Activating virtual environment..."
    
    source "$PROJECT_ROOT/$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Virtual environment activated"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Install base requirements
    pip install -r requirements.txt
    
    # Install the package in editable mode
    if [ "$INSTALL_DEV" = true ]; then
        log_info "Installing with development dependencies..."
        pip install -e ".[dev]"
    else
        pip install -e .
    fi
    
    log_success "Python dependencies installed"
}

# Install Playwright browsers
install_playwright() {
    log_info "Installing Playwright browsers..."
    
    # Install only Chromium for faster setup
    python -m playwright install chromium
    
    # Install system dependencies for Playwright
    if command_exists apt-get; then
        log_info "Installing Playwright system dependencies (Ubuntu/Debian)..."
        python -m playwright install-deps chromium || log_warning "Could not install system dependencies. You may need to install them manually."
    elif command_exists yum; then
        log_info "Installing Playwright system dependencies (RHEL/CentOS)..."
        log_warning "Please install Playwright system dependencies manually."
    elif command_exists brew; then
        log_info "Playwright system dependencies should be handled by Homebrew on macOS"
    fi
    
    log_success "Playwright browsers installed"
}

# Install Node.js dependencies
install_node_deps() {
    log_info "Installing Node.js dependencies..."
    
    cd "$PROJECT_ROOT/frontend"
    
    if [ -d "node_modules" ]; then
        log_warning "node_modules already exists. Skipping npm install."
    else
        npm install
    fi
    
    log_success "Node.js dependencies installed"
}

# Set up environment file
setup_env() {
    log_info "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info "Created .env file from .env.example"
            log_warning "Please edit .env file with your configuration"
        else
            log_warning ".env.example not found. You may need to create .env manually."
        fi
    else
        log_info ".env file already exists"
    fi
}

# Run tests
run_tests() {
    log_info "Running tests..."
    
    cd "$PROJECT_ROOT"
    
    if python -c "import pytest" 2>/dev/null; then
        pytest tests/ -v --tb=short || log_warning "Some tests failed. Please review the output."
    else
        log_warning "pytest not installed. Skipping tests."
    fi
}

# Set up pre-commit hooks
setup_precommit() {
    if [ "$INSTALL_DEV" = true ]; then
        log_info "Setting up pre-commit hooks..."
        
        if command_exists pre-commit; then
            pre-commit install
            log_success "Pre-commit hooks installed"
        else
            log_warning "pre-commit not installed. Skipping."
        fi
    fi
}

# Docker setup
setup_docker() {
    log_info "Setting up Docker environment..."
    
    if ! command_exists docker; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        log_error "docker-compose is not installed. Please install docker-compose first."
        exit 1
    fi
    
    cd "$PROJECT_ROOT"
    
    # Build images
    docker-compose build
    
    log_success "Docker environment set up"
    log_info "Run 'docker-compose up -d' to start services"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    cd "$PROJECT_ROOT"
    
    # Check Python imports
    if python -c "from lowcode_scanner import LowCodePerformanceScanner; print('OK')" 2>/dev/null; then
        log_success "Package import successful"
    else
        log_error "Package import failed. There may be an issue with the installation."
        return 1
    fi
    
    # Check CLI
    if command_exists lowcode-scanner; then
        log_success "CLI command available"
    else
        log_warning "CLI command not found in PATH. You may need to reactivate your virtual environment."
    fi
    
    # Check Playwright
    if python -c "from playwright.sync_api import sync_playwright; print('OK')" 2>/dev/null; then
        log_success "Playwright installation verified"
    else
        log_warning "Playwright installation issue detected"
    fi
    
    log_success "Installation verification complete"
}

# Print completion message
print_completion() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              Setup Complete! 🎉                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Edit the environment configuration:"
    echo "   nano .env"
    echo ""
    
    if [ "$DOCKER_MODE" = true ]; then
        echo "3. Start Docker services:"
        echo "   docker-compose up -d"
        echo ""
        echo "4. Access the application:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
    else
        echo "3. Start the backend server:"
        echo "   cd backend && python main.py"
        echo ""
        echo "4. In another terminal, start the frontend:"
        echo "   cd frontend && npm run dev"
        echo ""
        echo "5. Access the application:"
        echo "   Frontend: http://localhost:3000"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/api/docs"
    fi
    
    echo ""
    echo "Run a quick test scan:"
    echo "   lowcode-scanner scan-url https://example.com --formats json"
    echo ""
    echo "For more information, see:"
    echo "   - README.md"
    echo "   - docs/USER_GUIDE.md"
    echo "   - docs/API.md"
    echo ""
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dev)
                INSTALL_DEV=true
                shift
                ;;
            --production)
                PRODUCTION_MODE=true
                shift
                ;;
            --docker)
                DOCKER_MODE=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Main function
main() {
    print_banner
    parse_args "$@"
    
    log_info "Starting setup process..."
    log_info "Project root: $PROJECT_ROOT"
    
    if [ "$DOCKER_MODE" = true ]; then
        setup_docker
        print_completion
        exit 0
    fi
    
    # Run setup steps
    check_python
    create_venv
    activate_venv
    install_python_deps
    install_playwright
    
    if check_node; then
        install_node_deps
    fi
    
    setup_env
    
    if [ "$INSTALL_DEV" = true ]; then
        setup_precommit
        run_tests
    fi
    
    verify_installation
    print_completion
}

# Run main function
main "$@"
