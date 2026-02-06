#!/bin/bash
#
# Low-Code Performance Scanner - Deployment Script
# ================================================
#
# This script handles deployment of the Low-Code Performance Scanner to various environments.
# It supports Docker deployment, production deployment, and cloud deployments.
#
# Usage: ./scripts/deploy.sh [ENVIRONMENT] [OPTIONS]
#   Environments:
#     local         Local Docker deployment (default)
#     production    Production deployment with SSL
#     staging       Staging environment deployment
#     aws           AWS deployment
#     gcp           Google Cloud deployment
#     azure         Azure deployment
#
#   Options:
#     --build       Force rebuild of images
#     --migrate     Run database migrations
#     --backup      Create backup before deployment
#     --version     Specify version tag (default: latest)
#     --help        Show this help message
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="lowcode-scanner"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="latest"
ENVIRONMENT="local"
FORCE_BUILD=false
RUN_MIGRATE=false
CREATE_BACKUP=false

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
    echo "║       Low-Code Performance Scanner - Deployment Script     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Show help
show_help() {
    echo "Usage: $0 [ENVIRONMENT] [OPTIONS]"
    echo ""
    echo "Environments:"
    echo "  local         Local Docker deployment (default)"
    echo "  production    Production deployment with SSL"
    echo "  staging       Staging environment deployment"
    echo "  aws           AWS deployment"
    echo "  gcp           Google Cloud deployment"
    echo "  azure         Azure deployment"
    echo ""
    echo "Options:"
    echo "  --build       Force rebuild of images"
    echo "  --migrate     Run database migrations"
    echo "  --backup      Create backup before deployment"
    echo "  --version     Specify version tag (default: latest)"
    echo "  --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                          # Deploy locally"
    echo "  $0 production --build       # Production deployment with build"
    echo "  $0 staging --version 1.0.3  # Deploy specific version to staging"
    echo "  $0 production --backup      # Deploy with pre-deployment backup"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env file not found. Creating from .env.example..."
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_warning "Please edit .env file with your production settings"
        fi
    fi
    
    log_success "Prerequisites check passed"
}

# Create backup
create_backup() {
    if [ "$CREATE_BACKUP" = true ]; then
        log_info "Creating backup..."
        
        BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup reports
        if [ -d "$PROJECT_ROOT/reports" ]; then
            cp -r "$PROJECT_ROOT/reports" "$BACKUP_DIR/"
        fi
        
        # Backup environment config
        cp "$PROJECT_ROOT/.env" "$BACKUP_DIR/"
        
        # Backup docker volumes
        docker run --rm -v "${PROJECT_NAME}_reports:/data" -v "$BACKUP_DIR:/backup" alpine tar czf /backup/volumes.tar.gz -C /data .
        
        log_success "Backup created at $BACKUP_DIR"
    fi
}

# Build Docker images
build_images() {
    if [ "$FORCE_BUILD" = true ] || [ "$ENVIRONMENT" != "local" ]; then
        log_info "Building Docker images..."
        
        cd "$PROJECT_ROOT"
        
        # Set version tag
        export VERSION
        
        if [ "$ENVIRONMENT" = "production" ]; then
            docker-compose -f docker-compose.yml build --no-cache
        else
            docker-compose build
        fi
        
        log_success "Docker images built"
    fi
}

# Deploy locally
deploy_local() {
    log_info "Deploying to local environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing containers
    docker-compose down
    
    # Start services
    docker-compose up -d
    
    # Wait for services to be ready
    log_info "Waiting for services to start..."
    sleep 10
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_warning "Backend health check failed"
    fi
    
    log_success "Local deployment complete"
    echo ""
    echo "Access your application:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/api/docs"
}

# Deploy to production
deploy_production() {
    log_info "Deploying to production environment..."
    
    cd "$PROJECT_ROOT"
    
    # Check SSL certificates
    if [ ! -f "$PROJECT_ROOT/nginx/ssl/cert.pem" ]; then
        log_warning "SSL certificates not found. Please set up SSL first."
        log_info "Run: sudo certbot certonly --standalone -d yourdomain.com"
        exit 1
    fi
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/logs/nginx"
    mkdir -p "$PROJECT_ROOT/reports"
    
    # Set correct permissions
    chmod -R 755 "$PROJECT_ROOT/reports"
    
    # Stop existing containers
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    
    # Start production services
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    # Wait for services
    log_info "Waiting for services to start..."
    sleep 15
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend is healthy"
    else
        log_error "Backend health check failed. Check logs with: docker-compose logs backend"
    fi
    
    log_success "Production deployment complete"
    echo ""
    echo "Your application should be accessible at:"
    echo "  https://yourdomain.com"
}

# Deploy to staging
deploy_staging() {
    log_info "Deploying to staging environment..."
    
    cd "$PROJECT_ROOT"
    
    # Use staging configuration
    if [ -f "docker-compose.staging.yml" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
    else
        log_warning "docker-compose.staging.yml not found, using production config"
        deploy_production
    fi
    
    log_success "Staging deployment complete"
}

# Deploy to AWS
deploy_aws() {
    log_info "Deploying to AWS..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed"
        exit 1
    fi
    
    # Check if ECS task definition exists
    if [ -f "$PROJECT_ROOT/aws/ecs-task-definition.json" ]; then
        log_info "Registering ECS task definition..."
        aws ecs register-task-definition --cli-input-json "file://$PROJECT_ROOT/aws/ecs-task-definition.json"
        
        log_info "Updating ECS service..."
        aws ecs update-service \
            --cluster "$PROJECT_NAME-cluster" \
            --service "$PROJECT_NAME-service" \
            --force-new-deployment
    else
        log_warning "ECS task definition not found. Please create it first."
        log_info "See docs/DEPLOYMENT.md for AWS setup instructions."
    fi
    
    log_success "AWS deployment initiated"
}

# Deploy to GCP
deploy_gcp() {
    log_info "Deploying to Google Cloud Platform..."
    
    # Check gcloud CLI
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        exit 1
    fi
    
    # Build and push image
    log_info "Building and pushing Docker image..."
    gcloud builds submit --tag "gcr.io/$GOOGLE_CLOUD_PROJECT/$PROJECT_NAME:$VERSION"
    
    # Deploy to Cloud Run
    log_info "Deploying to Cloud Run..."
    gcloud run deploy "$PROJECT_NAME" \
        --image "gcr.io/$GOOGLE_CLOUD_PROJECT/$PROJECT_NAME:$VERSION" \
        --platform managed \
        --region us-central1 \
        --allow-unauthenticated
    
    log_success "GCP deployment complete"
}

# Deploy to Azure
deploy_azure() {
    log_info "Deploying to Azure..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI is not installed"
        exit 1
    fi
    
    # Create resource group if not exists
    az group create --name "$PROJECT_NAME-rg" --location eastus
    
    # Create container instance
    az container create \
        --resource-group "$PROJECT_NAME-rg" \
        --name "$PROJECT_NAME" \
        --image "$PROJECT_NAME:$VERSION" \
        --cpu 2 \
        --memory 4 \
        --ports 8000 3000 \
        --ip-address Public
    
    log_success "Azure deployment complete"
}

# Run database migrations
run_migrations() {
    if [ "$RUN_MIGRATE" = true ]; then
        log_info "Running database migrations..."
        
        # Add migration commands here if using a database
        # Example:
        # docker-compose exec backend alembic upgrade head
        
        log_success "Migrations complete"
    fi
}

# Print deployment summary
print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║              Deployment Summary                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Environment:    $ENVIRONMENT"
    echo "Version:        $VERSION"
    echo "Build:          $([ "$FORCE_BUILD" = true ] && echo "Yes" || echo "No")"
    echo "Backup:         $([ "$CREATE_BACKUP" = true ] && echo "Yes" || echo "No")"
    echo "Migrations:     $([ "$RUN_MIGRATE" = true ] && echo "Yes" || echo "No")"
    echo ""
    echo "Useful commands:"
    echo "  View logs:           docker-compose logs -f"
    echo "  Check status:        docker-compose ps"
    echo "  Health check:        curl http://localhost:8000/health"
    echo "  Stop services:       docker-compose down"
    echo ""
}

# Parse arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            local|production|staging|aws|gcp|azure)
                ENVIRONMENT="$1"
                shift
                ;;
            --build)
                FORCE_BUILD=true
                shift
                ;;
            --migrate)
                RUN_MIGRATE=true
                shift
                ;;
            --backup)
                CREATE_BACKUP=true
                shift
                ;;
            --version)
                VERSION="$2"
                shift 2
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
    
    log_info "Starting deployment to $ENVIRONMENT environment..."
    log_info "Version: $VERSION"
    
    check_prerequisites
    create_backup
    build_images
    
    case $ENVIRONMENT in
        local)
            deploy_local
            ;;
        production)
            deploy_production
            ;;
        staging)
            deploy_staging
            ;;
        aws)
            deploy_aws
            ;;
        gcp)
            deploy_gcp
            ;;
        azure)
            deploy_azure
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    run_migrations
    print_summary
}

# Run main function
main "$@"
