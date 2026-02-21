#!/bin/bash
# MediaCrawler - Full Stack Deployment Script
# Server: 39.105.122.26

set -e

echo "=========================================="
echo "MediaCrawler Full Stack Deployment"
echo "Server: 39.105.122.26"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Creating from backend/.env.production...${NC}"
    if [ -f backend/.env.production ]; then
        cp backend/.env.production .env
        echo -e "${GREEN}.env file created. Please edit it with your configuration!${NC}"
    else
        echo -e "${RED}Error: backend/.env.production not found. Please create .env manually.${NC}"
        exit 1
    fi
fi

# Parse command line arguments
COMMAND=${1:-"help"}

case "$COMMAND" in
    build)
        echo -e "${GREEN}Building Docker images...${NC}"
        docker compose build
        echo -e "${GREEN}Build complete!${NC}"
        ;;

    start|up)
        echo -e "${GREEN}Starting services...${NC}"
        docker compose up -d
        echo -e "${GREEN}Services started!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Frontend: http://39.105.122.26"
        echo "  - Backend API: http://39.105.122.26:8000"
        echo "  - Health Check: http://39.105.122.26:8000/api/health"
        echo "  - Admin Panel: http://39.105.122.26/admin/"
        ;;

    stop|down)
        echo -e "${YELLOW}Stopping services...${NC}"
        docker compose down
        echo -e "${GREEN}Services stopped!${NC}"
        ;;

    restart)
        echo -e "${YELLOW}Restarting services...${NC}"
        docker compose restart
        echo -e "${GREEN}Services restarted!${NC}"
        ;;

    logs)
        SERVICE=${2:-""}
        if [ -n "$SERVICE" ]; then
            docker compose logs -f "$SERVICE"
        else
            docker compose logs -f
        fi
        ;;

    shell-backend)
        echo -e "${GREEN}Opening shell in backend container...${NC}"
        docker compose exec backend bash
        ;;

    shell-frontend)
        echo -e "${GREEN}Opening shell in frontend container...${NC}"
        docker compose exec frontend sh
        ;;

    dbshell)
        echo -e "${GREEN}Opening Django DB shell...${NC}"
        docker compose exec backend python manage.py dbshell
        ;;

    migrate)
        echo -e "${YELLOW}Running database migrations...${NC}"
        docker compose exec backend python manage.py migrate
        echo -e "${GREEN}Migrations complete!${NC}"
        ;;

    collectstatic)
        echo -e "${YELLOW}Collecting static files...${NC}"
        docker compose exec backend python manage.py collectstatic --noinput
        echo -e "${GREEN}Static files collected!${NC}"
        ;;

    createsuperuser)
        echo -e "${YELLOW}Creating superuser...${NC}"
        docker compose exec backend python manage.py createsuperuser
        ;;

    deploy)
        echo -e "${GREEN}Starting full deployment...${NC}"
        echo "1. Building images..."
        docker compose build
        echo "2. Starting services..."
        docker compose up -d
        echo "3. Waiting for backend to be ready..."
        sleep 10
        echo "4. Running migrations..."
        docker compose exec backend python manage.py migrate --noinput || true
        echo "5. Collecting static files..."
        docker compose exec backend python manage.py collectstatic --noinput || true
        echo -e "${GREEN}Deployment complete!${NC}"
        echo ""
        echo "Access the application at:"
        echo "  - Frontend: http://39.105.122.26"
        echo "  - Backend API: http://39.105.122.26:8000"
        echo "  - Health Check: http://39.105.122.26/api/health"
        echo "  - Admin Panel: http://39.105.122.26/admin/"
        ;;

    status)
        docker compose ps
        ;;

    health)
        echo -e "${GREEN}Checking service health...${NC}"
        echo "Frontend:"
        curl -f http://localhost:80/health 2>/dev/null && echo -e "  ${GREEN}OK${NC}" || echo -e "  ${RED}Failed${NC}"
        echo "Backend:"
        curl -f http://localhost:8000/api/health 2>/dev/null && echo -e "  ${GREEN}OK${NC}" || echo -e "  ${RED}Failed${NC}"
        ;;

    clean)
        if confirm "This will remove all containers, volumes, and images. Continue?"; then
            echo -e "${YELLOW}Cleaning up...${NC}"
            docker compose down -v --rmi all
            echo -e "${GREEN}Cleanup complete!${NC}"
        fi
        ;;

    help|*)
        echo "MediaCrawler - Full Stack Deployment Script"
        echo ""
        echo "Usage: ./deploy.sh [command] [options]"
        echo ""
        echo "Commands:"
        echo "  build          Build Docker images"
        echo "  start, up      Start all services"
        echo "  stop, down     Stop all services"
        echo "  restart        Restart all services"
        echo "  logs [service] Show logs (all services or specific service)"
        echo "  shell-backend  Open shell in backend container"
        echo "  shell-frontend Open shell in frontend container"
        echo "  dbshell        Open Django DB shell"
        echo "  migrate        Run database migrations"
        echo "  collectstatic  Collect static files"
        echo "  createsuperuser Create Django superuser"
        echo "  deploy         Full deployment (build + start + migrate)"
        echo "  status         Show service status"
        echo "  health         Check all service health"
        echo "  clean          Remove all containers, volumes, and images"
        echo "  help           Show this help message"
        echo ""
        echo "Services:"
        echo "  frontend       Frontend Nginx + Vue.js"
        echo "  backend        Django Backend"
        echo "  redis          Redis Cache"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh deploy"
        echo "  ./deploy.sh logs backend"
        echo "  ./deploy.sh createsuperuser"
        ;;
esac
