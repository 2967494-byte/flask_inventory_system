#!/bin/bash

# SYNAPSE Deployment Script
# This script rebuilds and restarts the necessary services

echo "🚀 SYNAPSE Deployment Script"
echo "=============================="
echo ""

# Check if docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Function to restart a specific service
restart_service() {
    local service=$1
    echo "🔄 Restarting $service..."
    docker compose restart $service
    if [ $? -eq 0 ]; then
        echo "✅ $service restarted successfully"
    else
        echo "❌ Failed to restart $service"
        return 1
    fi
}

# Function to rebuild and restart a service
rebuild_service() {
    local service=$1
    echo "🔨 Rebuilding $service..."
    docker compose build $service
    if [ $? -eq 0 ]; then
        echo "✅ $service built successfully"
        restart_service $service
    else
        echo "❌ Failed to build $service"
        return 1
    fi
}

# Main menu
echo "Select an option:"
echo "1. Restart bot only (fixes login issue)"
echo "2. Rebuild and restart frontend (fixes design updates)"
echo "3. Rebuild and restart all services"
echo "4. View logs"
echo "5. Check service status"
echo ""
read -p "Enter option (1-5): " option

case $option in
    1)
        restart_service bot
        ;;
    2)
        rebuild_service frontend
        ;;
    3)
        echo "🔨 Rebuilding all services..."
        docker compose down
        docker compose up -d --build
        echo "✅ All services rebuilt and started"
        ;;
    4)
        echo "Select service to view logs:"
        echo "1. Backend"
        echo "2. Bot"
        echo "3. Frontend"
        echo "4. Database"
        echo "5. All"
        read -p "Enter option (1-5): " log_option
        case $log_option in
            1) docker compose logs -f backend ;;
            2) docker compose logs -f bot ;;
            3) docker compose logs -f frontend ;;
            4) docker compose logs -f db ;;
            5) docker compose logs -f ;;
        esac
        ;;
    5)
        docker compose ps
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "✨ Done!"
