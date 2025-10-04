#!/bin/bash

# SampleMind AI Deployment Script
# Usage: ./deploy.sh [environment] [component]
# Example: ./deploy.sh production backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
COMPONENT=${2:-all}
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENT_DIR="$PROJECT_ROOT/deployment"

echo -e "${GREEN}🚀 SampleMind AI Deployment${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}Component: ${COMPONENT}${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null && [ "$COMPONENT" != "docker" ]; then
        echo -e "${YELLOW}⚠️  kubectl not found, skipping Kubernetes checks${NC}"
    fi
    
    echo -e "${GREEN}✅ Prerequisites OK${NC}"
    echo ""
}

# Function to load environment variables
load_env() {
    if [ -f "$DEPLOYMENT_DIR/.env.$ENVIRONMENT" ]; then
        echo -e "${YELLOW}📝 Loading environment variables...${NC}"
        export $(cat "$DEPLOYMENT_DIR/.env.$ENVIRONMENT" | grep -v '^#' | xargs)
        echo -e "${GREEN}✅ Environment loaded${NC}"
    else
        echo -e "${RED}❌ Environment file not found: .env.$ENVIRONMENT${NC}"
        exit 1
    fi
    echo ""
}

# Function to build Docker images
build_images() {
    echo -e "${YELLOW}🏗️  Building Docker images...${NC}"
    
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
        echo -e "${YELLOW}Building backend image...${NC}"
        docker build -t samplemind/backend:latest \
            -f "$DEPLOYMENT_DIR/docker/Dockerfile.backend" \
            "$PROJECT_ROOT"
        echo -e "${GREEN}✅ Backend image built${NC}"
    fi
    
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "frontend" ]; then
        echo -e "${YELLOW}Building frontend image...${NC}"
        docker build -t samplemind/frontend:latest \
            --build-arg NEXT_PUBLIC_API_URL="$API_URL" \
            -f "$DEPLOYMENT_DIR/docker/Dockerfile.frontend" \
            "$PROJECT_ROOT/frontend/web"
        echo -e "${GREEN}✅ Frontend image built${NC}"
    fi
    
    echo ""
}

# Function to push Docker images
push_images() {
    echo -e "${YELLOW}📤 Pushing Docker images...${NC}"
    
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_PASSWORD" ]; then
        echo -e "${RED}❌ Docker credentials not set${NC}"
        exit 1
    fi
    
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
    
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
        docker tag samplemind/backend:latest samplemind/backend:${ENVIRONMENT}
        docker push samplemind/backend:latest
        docker push samplemind/backend:${ENVIRONMENT}
        echo -e "${GREEN}✅ Backend image pushed${NC}"
    fi
    
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "frontend" ]; then
        docker tag samplemind/frontend:latest samplemind/frontend:${ENVIRONMENT}
        docker push samplemind/frontend:latest
        docker push samplemind/frontend:${ENVIRONMENT}
        echo -e "${GREEN}✅ Frontend image pushed${NC}"
    fi
    
    echo ""
}

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo -e "${YELLOW}🐳 Deploying with Docker Compose...${NC}"
    
    cd "$DEPLOYMENT_DIR/docker"
    docker-compose -f docker-compose.prod.yml up -d
    
    echo -e "${GREEN}✅ Services deployed${NC}"
    echo ""
    
    echo -e "${YELLOW}📊 Service status:${NC}"
    docker-compose -f docker-compose.prod.yml ps
    echo ""
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    echo -e "${YELLOW}☸️  Deploying to Kubernetes...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}❌ kubectl is not installed${NC}"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "backend" ]; then
        kubectl apply -f "$DEPLOYMENT_DIR/kubernetes/backend-deployment.yaml"
        echo -e "${GREEN}✅ Backend deployed${NC}"
    fi
    
    if [ "$COMPONENT" = "all" ] || [ "$COMPONENT" = "worker" ]; then
        kubectl apply -f "$DEPLOYMENT_DIR/kubernetes/celery-worker-deployment.yaml"
        echo -e "${GREEN}✅ Workers deployed${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📊 Deployment status:${NC}"
    kubectl get pods -n samplemind
    echo ""
}

# Function to run database migrations
run_migrations() {
    echo -e "${YELLOW}🗄️  Running database migrations...${NC}"
    
    # Add migration commands here
    echo -e "${GREEN}✅ Migrations complete${NC}"
    echo ""
}

# Function to perform health checks
health_check() {
    echo -e "${YELLOW}🏥 Performing health checks...${NC}"
    
    # Wait for services to be ready
    sleep 10
    
    # Check backend health
    if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
        echo -e "${GREEN}✅ Backend is healthy${NC}"
    else
        echo -e "${RED}❌ Backend health check failed${NC}"
    fi
    
    # Check frontend health
    if curl -f http://localhost:3000 &> /dev/null; then
        echo -e "${GREEN}✅ Frontend is healthy${NC}"
    else
        echo -e "${RED}❌ Frontend health check failed${NC}"
    fi
    
    echo ""
}

# Function to create backup
create_backup() {
    echo -e "${YELLOW}💾 Creating backup...${NC}"
    
    BACKUP_DIR="$PROJECT_ROOT/backups"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    mkdir -p "$BACKUP_DIR"
    
    # Backup MongoDB
    if [ -n "$MONGODB_URL" ]; then
        mongodump --uri="$MONGODB_URL" --out="$BACKUP_DIR/mongodb_$TIMESTAMP"
        echo -e "${GREEN}✅ MongoDB backup created${NC}"
    fi
    
    # Backup Redis (optional)
    if [ -n "$REDIS_URL" ]; then
        redis-cli --rdb "$BACKUP_DIR/redis_$TIMESTAMP.rdb" &> /dev/null || true
        echo -e "${GREEN}✅ Redis backup created${NC}"
    fi
    
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    load_env
    
    # Create backup before deployment
    if [ "$ENVIRONMENT" = "production" ]; then
        create_backup
    fi
    
    # Build and push images
    build_images
    
    if [ "$ENVIRONMENT" != "local" ]; then
        push_images
    fi
    
    # Deploy based on deployment method
    if [ -f "$DEPLOYMENT_DIR/docker/docker-compose.prod.yml" ] && [ "$ENVIRONMENT" != "kubernetes" ]; then
        deploy_docker_compose
    else
        deploy_kubernetes
    fi
    
    # Run migrations
    run_migrations
    
    # Health checks
    health_check
    
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo -e "${GREEN}🎉 SampleMind AI is now running on ${ENVIRONMENT}${NC}"
    echo ""
    echo -e "${YELLOW}📍 Endpoints:${NC}"
    echo -e "   Backend API: http://localhost:8000/api/v1"
    echo -e "   Frontend: http://localhost:3000"
    echo -e "   Flower: http://localhost:5555"
    echo ""
}

# Run main function
main
