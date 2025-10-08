#!/usr/bin/env bash
# SampleMind AI - Fast Optimized Docker Build Script
# This script uses BuildKit with optimal caching for maximum speed

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}SampleMind AI - Fast Build${NC}"
echo -e "${BLUE}=====================================${NC}"

# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

echo -e "\n${GREEN}✓${NC} BuildKit enabled"
echo -e "${GREEN}✓${NC} Using optimized Dockerfile"

# Check if we should clean build
if [ "$1" == "--clean" ] || [ "$1" == "-c" ]; then
    echo -e "\n${YELLOW}⚠${NC}  Clean build requested - removing old images..."
    docker rmi samplemind-api:latest 2>/dev/null || true
    docker builder prune -f
fi

# Build with optimal settings
echo -e "\n${BLUE}Building samplemind-api (optimized)...${NC}"
time docker-compose build \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --progress=plain \
    samplemind-api

# Show image size
echo -e "\n${GREEN}✓${NC} Build complete!"
echo -e "\n${BLUE}Image Size:${NC}"
docker images samplemind-api:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo -e "\n${GREEN}=====================================${NC}"
echo -e "${GREEN}Build Summary:${NC}"
echo -e "${GREEN}=====================================${NC}"
echo -e "Target size: <3GB (was 12.6GB)"
echo -e "To start: ${YELLOW}docker-compose up -d${NC}"
echo -e "To check: ${YELLOW}docker-compose ps${NC}"
