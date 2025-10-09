#!/bin/bash
# OBCMS Production Deployment Script
# This script handles the complete deployment process for OBCMS in production

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}OBCMS Production Deployment${NC}"
echo -e "${BLUE}================================${NC}\n"

# Check if .env.production exists
if [ ! -f "$PROJECT_ROOT/.env.production" ]; then
    echo -e "${RED}✗ ERROR: .env.production file not found${NC}"
    echo -e "${YELLOW}Please create .env.production from .env.production.template${NC}"
    echo -e "${YELLOW}Command: cp .env.production.template .env.production${NC}"
    exit 1
fi

# Validate critical environment variables
echo -e "${YELLOW}⚙ Validating environment configuration...${NC}"
source "$PROJECT_ROOT/.env.production"

if [ "$SECRET_KEY" == "CHANGE-THIS-TO-A-RANDOM-50-CHARACTER-STRING-FOR-PRODUCTION" ]; then
    echo -e "${RED}✗ ERROR: SECRET_KEY not changed from template${NC}"
    echo -e "${YELLOW}Generate a new key with:${NC}"
    echo -e "${YELLOW}python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"${NC}"
    exit 1
fi

if [ "$DEBUG" != "0" ]; then
    echo -e "${RED}✗ ERROR: DEBUG must be 0 in production${NC}"
    exit 1
fi

if [ "$POSTGRES_PASSWORD" == "CHANGE-THIS-TO-SECURE-PASSWORD-MINIMUM-32-CHARACTERS" ]; then
    echo -e "${RED}✗ ERROR: POSTGRES_PASSWORD not changed from template${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment configuration validated${NC}\n"

# Stop existing containers
echo -e "${YELLOW}⚙ Stopping existing containers...${NC}"
cd "$PROJECT_ROOT"
docker-compose -f docker-compose.prod.yml --env-file .env.production down || true
echo -e "${GREEN}✓ Containers stopped${NC}\n"

# Build fresh images
echo -e "${YELLOW}⚙ Building production images...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production build --no-cache
echo -e "${GREEN}✓ Images built successfully${NC}\n"

# Start database and redis first
echo -e "${YELLOW}⚙ Starting database and redis...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d db redis
sleep 10  # Wait for services to be ready
echo -e "${GREEN}✓ Database and redis started${NC}\n"

# Run migrations
echo -e "${YELLOW}⚙ Running database migrations...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production up migrate
echo -e "${GREEN}✓ Migrations complete${NC}\n"

# Start all services
echo -e "${YELLOW}⚙ Starting all services...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
echo -e "${GREEN}✓ All services started${NC}\n"

# Wait for health checks
echo -e "${YELLOW}⚙ Waiting for services to be healthy...${NC}"
sleep 15

# Check service health
echo -e "${YELLOW}⚙ Checking service health...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production ps

# Test health endpoint
echo -e "\n${YELLOW}⚙ Testing health endpoint...${NC}"
if docker-compose -f docker-compose.prod.yml --env-file .env.production exec -T web curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠ Health check pending (service may still be starting)${NC}"
fi

# Display deployment summary
echo -e "\n${BLUE}================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}================================${NC}\n"

echo -e "${YELLOW}Services:${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.production ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n${YELLOW}Useful Commands:${NC}"
echo -e "View logs:      ${BLUE}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "Restart:        ${BLUE}docker-compose -f docker-compose.prod.yml restart${NC}"
echo -e "Stop:           ${BLUE}docker-compose -f docker-compose.prod.yml down${NC}"
echo -e "Database shell: ${BLUE}docker-compose -f docker-compose.prod.yml exec db psql -U \$POSTGRES_USER -d \$POSTGRES_DB${NC}"
echo -e "Django shell:   ${BLUE}docker-compose -f docker-compose.prod.yml exec web python src/manage.py shell${NC}"
echo -e "Create backup:  ${BLUE}./scripts/backup-database.sh${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "1. Configure your reverse proxy (Nginx/Traefik/Coolify)"
echo -e "2. Set up SSL certificates"
echo -e "3. Configure automated backups"
echo -e "4. Set up monitoring and logging"
echo -e "5. Create superuser: ${BLUE}docker-compose -f docker-compose.prod.yml exec web python src/manage.py createsuperuser${NC}"

echo -e "\n${GREEN}✓ Deployment script completed successfully${NC}\n"
