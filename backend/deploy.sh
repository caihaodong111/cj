#!/bin/bash
# MediaCrawler Backend - Production Deployment Script
# Server: 39.105.122.26

set -e

echo "=========================================="
echo "MediaCrawler Backend Deployment"
echo "Server: 39.105.122.26"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please edit it with your configuration!${NC}"
    else
        echo -e "${RED}Error: .env.example not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Function to prompt for confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# Parse command line arguments
COMMAND=${1:-"help"}

case "$COMMAND" in
    build)
        echo -e "${GREEN}Building Docker images...${NC}"
        docker-compose build
        echo -e "${GREEN}Build complete!${NC}"
        ;;

    start|up)
        echo -e "${GREEN}Starting services...${NC}"
        docker-compose up -d
        echo -e "${GREEN}Services started!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Backend API: http://39.105.122.26:8000"
        echo "  - Health Check: http://39.105.122.26:8000/api/health"
        echo "  - Admin Panel: http://39.105.122.26:8000/admin/"
        ;;

    stop|down)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker-compose down
        echo -e "${GREEN}Services stopped!${NC}"
        ;;

    restart)
        echo -e "${YELLOW}Restarting services...${NC}"
        docker-compose restart
        echo -e "${GREEN}Services restarted!${NC}"
        ;;

    logs)
        docker-compose logs -f backend
        ;;

    shell)
        echo -e "${GREEN}Opening shell in backend container...${NC}"
        docker-compose exec backend bash
        ;;

    dbshell)
        echo -e "${GREEN}Opening Django DB shell...${NC}"
        docker-compose exec backend python manage.py dbshell
        ;;

    migrate)
        echo -e "${YELLOW}Running database migrations...${NC}"
        docker-compose exec backend python manage.py migrate
        echo -e "${GREEN}Migrations complete!${NC}"
        ;;

    collectstatic)
        echo -e "${YELLOW}Collecting static files...${NC}"
        docker-compose exec backend python manage.py collectstatic --noinput
        echo -e "${GREEN}Static files collected!${NC}"
        ;;

    createsuperuser)
        echo -e "${YELLOW}Creating superuser...${NC}"
        docker-compose exec backend python manage.py createsuperuser
        ;;

    deploy)
        echo -e "${GREEN}Starting full deployment...${NC}"
        echo "1. Building images..."
        docker-compose build
        echo "2. Starting services..."
        docker-compose up -d
        echo "3. Running migrations..."
        sleep 5
        docker-compose exec backend python manage.py migrate --noinput
        echo "4. Collecting static files..."
        docker-compose exec backend python manage.py collectstatic --noinput
        echo -e "${GREEN}Deployment complete!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Backend API: http://39.105.122.26:8000"
        echo "  - Health Check: http://39.105.122.26:8000/api/health"
        echo "  - Admin Panel: http://39.105.122.26:8000/admin/"
        ;;

    status)
        docker-compose ps
        ;;

    health)
        echo -e "${GREEN}Checking service health...${NC}"
        curl -f http://localhost:8000/api/health || echo -e "${RED}Health check failed!${NC}"
        ;;

    clean)
        if confirm "This will remove all containers, volumes, and images. Continue?"; then
            echo -e "${YELLOW}Cleaning up...${NC}"
            docker-compose down -v --rmi all
            echo -e "${GREEN}Cleanup complete!${NC}"
        fi
        ;;

    help|*)
        echo "MediaCrawler Backend - Deployment Script"
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  build          Build Docker images"
        echo "  start, up      Start services"
        echo "  stop, down     Stop services"
        echo "  restart        Restart services"
        echo "  logs           Show and follow backend logs"
        echo "  shell          Open shell in backend container"
        echo "  dbshell        Open Django DB shell"
        echo "  migrate        Run database migrations"
        echo "  collectstatic  Collect static files"
        echo "  createsuperuser Create Django superuser"
        echo "  deploy         Full deployment (build + start + migrate + collectstatic)"
        echo "  status         Show service status"
        echo "  health         Check API health"
        echo "  clean          Remove all containers, volumes, and images"
        echo "  help           Show this help message"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh deploy"
        echo "  ./deploy.sh logs"
        echo "  ./deploy.sh createsuperuser"
        ;;
esac
