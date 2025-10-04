#!/bin/bash
# SampleMind Control Center v1.0
# Comprehensive management interface for SampleMind AI v6
# Author: SampleMind Team
# License: MIT

set -e

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
LOGS_DIR="$PROJECT_ROOT/logs"
DATA_DIR="$PROJECT_ROOT/data"

# Configuration
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
API_PORT=8000
FRONTEND_PORT=3000

# Utility functions
print_header() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${WHITE}          SampleMind AI v6 - Control Center             ${CYAN}║${NC}"
    echo -e "${CYAN}╠════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${CYAN}║${NC}  🎵 Hybrid AI-Powered Music Production Platform          ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo -e "\n${BLUE}▶ ${WHITE}${1}${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check service status
check_service_status() {
    local service=$1
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}●${NC} Running"
        return 0
    else
        echo -e "${RED}●${NC} Stopped"
        return 1
    fi
}

# Main Dashboard
show_dashboard() {
    print_header
    
    # System Status
    print_section "System Status"
    
    # Check Docker
    if command_exists docker; then
        print_success "Docker installed"
        if docker info >/dev/null 2>&1; then
            print_success "Docker daemon running"
        else
            print_error "Docker daemon not running"
        fi
    else
        print_error "Docker not installed"
    fi
    
    # Check Python
    if [ -f "$VENV_PATH/bin/python" ]; then
        PYTHON_VERSION=$("$VENV_PATH/bin/python" --version 2>&1)
        print_success "Virtual environment: $PYTHON_VERSION"
    else
        print_warning "Virtual environment not found"
    fi
    
    # Services Status
    print_section "Services Status"
    
    if [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo -e "  MongoDB:      $(check_service_status mongodb)"
        echo -e "  Redis:        $(check_service_status redis)"
        echo -e "  ChromaDB:     $(check_service_status chromadb)"
        echo -e "  API Server:   $(check_service_status api)"
        echo -e "  Celery:       $(check_service_status celery)"
    else
        print_warning "docker-compose.yml not found"
    fi
    
    # Resource Usage
    print_section "Resource Usage"
    
    if command_exists docker; then
        echo -e "\n${WHITE}Container Resources:${NC}"
        docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | head -8
    fi
    
    # Disk Usage
    echo -e "\n${WHITE}Disk Usage:${NC}"
    if [ -d "$DATA_DIR" ]; then
        DATA_SIZE=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1)
        echo -e "  Data Directory: ${CYAN}$DATA_SIZE${NC}"
    fi
    if [ -d "$LOGS_DIR" ]; then
        LOGS_SIZE=$(du -sh "$LOGS_DIR" 2>/dev/null | cut -f1)
        echo -e "  Logs Directory: ${CYAN}$LOGS_SIZE${NC}"
    fi
    
    echo ""
}

# Service Management
manage_services() {
    while true; do
        print_header
        print_section "Service Management"
        
        echo -e "${WHITE}1.${NC} Start All Services"
        echo -e "${WHITE}2.${NC} Stop All Services"
        echo -e "${WHITE}3.${NC} Restart All Services"
        echo -e "${WHITE}4.${NC} Start API Server Only"
        echo -e "${WHITE}5.${NC} View Service Logs"
        echo -e "${WHITE}6.${NC} Service Health Check"
        echo -e "${WHITE}0.${NC} Back to Main Menu"
        echo ""
        read -p "Select option: " choice
        
        case $choice in
            1)
                print_info "Starting all services..."
                docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
                print_success "Services started"
                sleep 2
                ;;
            2)
                print_info "Stopping all services..."
                docker-compose -f "$DOCKER_COMPOSE_FILE" down
                print_success "Services stopped"
                sleep 2
                ;;
            3)
                print_info "Restarting all services..."
                docker-compose -f "$DOCKER_COMPOSE_FILE" restart
                print_success "Services restarted"
                sleep 2
                ;;
            4)
                print_info "Starting API server..."
                cd "$PROJECT_ROOT"
                source "$VENV_PATH/bin/activate"
                python -m uvicorn src.samplemind.interfaces.api.main:app --host 0.0.0.0 --port 8000 --reload &
                print_success "API server started on port 8000"
                sleep 2
                ;;
            5)
                view_logs
                ;;
            6)
                health_check
                ;;
            0)
                break
                ;;
            *)
                print_error "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# Log Viewer
view_logs() {
    print_header
    print_section "Service Logs"
    
    echo -e "${WHITE}1.${NC} API Server Logs"
    echo -e "${WHITE}2.${NC} MongoDB Logs"
    echo -e "${WHITE}3.${NC} Redis Logs"
    echo -e "${WHITE}4.${NC} Celery Logs"
    echo -e "${WHITE}5.${NC} All Services (tail -f)"
    echo -e "${WHITE}0.${NC} Back"
    echo ""
    read -p "Select service: " choice
    
    case $choice in
        1) docker-compose logs --tail=100 -f api ;;
        2) docker-compose logs --tail=100 -f mongodb ;;
        3) docker-compose logs --tail=100 -f redis ;;
        4) docker-compose logs --tail=100 -f celery ;;
        5) docker-compose logs --tail=50 -f ;;
        0) return ;;
        *) print_error "Invalid option"; sleep 1 ;;
    esac
}

# Health Check
health_check() {
    print_header
    print_section "Health Check"
    
    print_info "Checking services..."
    echo ""
    
    # Check API
    if curl -s http://localhost:$API_PORT/health >/dev/null 2>&1; then
        print_success "API Server: Healthy (http://localhost:$API_PORT)"
    else
        print_error "API Server: Unreachable"
    fi
    
    # Check MongoDB
    if docker exec samplemind-mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
        print_success "MongoDB: Healthy"
    else
        print_error "MongoDB: Unreachable"
    fi
    
    # Check Redis
    if docker exec samplemind-redis redis-cli ping >/dev/null 2>&1; then
        print_success "Redis: Healthy"
    else
        print_error "Redis: Unreachable"
    fi
    
    # Check ChromaDB
    if curl -s http://localhost:8002/api/v1/heartbeat >/dev/null 2>&1; then
        print_success "ChromaDB: Healthy (http://localhost:8002)"
    else
        print_error "ChromaDB: Unreachable"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

# Database Operations
database_operations() {
    while true; do
        print_header
        print_section "Database Operations"
        
        echo -e "${WHITE}1.${NC} MongoDB Shell"
        echo -e "${WHITE}2.${NC} Redis CLI"
        echo -e "${WHITE}3.${NC} Backup MongoDB"
        echo -e "${WHITE}4.${NC} Backup Redis"
        echo -e "${WHITE}5.${NC} View Database Stats"
        echo -e "${WHITE}6.${NC} Clear Redis Cache"
        echo -e "${WHITE}0.${NC} Back to Main Menu"
        echo ""
        read -p "Select option: " choice
        
        case $choice in
            1)
                print_info "Opening MongoDB shell..."
                docker exec -it samplemind-mongodb mongosh samplemind
                ;;
            2)
                print_info "Opening Redis CLI..."
                docker exec -it samplemind-redis redis-cli
                ;;
            3)
                backup_mongodb
                ;;
            4)
                backup_redis
                ;;
            5)
                show_db_stats
                ;;
            6)
                clear_redis_cache
                ;;
            0)
                break
                ;;
            *)
                print_error "Invalid option"
                sleep 1
                ;;
        esac
    done
}

# Backup MongoDB
backup_mongodb() {
    print_info "Creating MongoDB backup..."
    BACKUP_DIR="$PROJECT_ROOT/backups/mongo_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    docker exec samplemind-mongodb mongodump --db=samplemind --out=/tmp/backup
    docker cp samplemind-mongodb:/tmp/backup "$BACKUP_DIR"
    
    print_success "Backup created: $BACKUP_DIR"
    sleep 2
}

# Backup Redis
backup_redis() {
    print_info "Creating Redis backup..."
    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"
    
    docker exec samplemind-redis redis-cli SAVE
    docker cp samplemind-redis:/data/dump.rdb "$BACKUP_DIR/redis_$(date +%Y%m%d_%H%M%S).rdb"
    
    print_success "Backup created: $BACKUP_DIR"
    sleep 2
}

# Show Database Stats
show_db_stats() {
    print_header
    print_section "Database Statistics"
    
    echo -e "\n${WHITE}MongoDB Collections:${NC}"
    docker exec samplemind-mongodb mongosh samplemind --quiet --eval "
        db.getCollectionNames().forEach(function(col) {
            var count = db[col].countDocuments();
            print(col + ': ' + count + ' documents');
        });
    "
    
    echo -e "\n${WHITE}Redis Info:${NC}"
    docker exec samplemind-redis redis-cli INFO stats | grep -E "^total|^keyspace"
    
    echo ""
    read -p "Press Enter to continue..."
}

# Clear Redis Cache
clear_redis_cache() {
    print_warning "This will clear ALL Redis cache data"
    read -p "Are you sure? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ]; then
        docker exec samplemind-redis redis-cli FLUSHDB
        print_success "Redis cache cleared"
    else
        print_info "Operation cancelled"
    fi
    sleep 2
}

# Test Suite Runner
run_tests() {
    print_header
    print_section "Test Suite Runner"
    
    echo -e "${WHITE}1.${NC} Run All Tests"
    echo -e "${WHITE}2.${NC} Run Unit Tests Only"
    echo -e "${WHITE}3.${NC} Run Integration Tests"
    echo -e "${WHITE}4.${NC} Run E2E Tests"
    echo -e "${WHITE}5.${NC} Run Tests with Coverage"
    echo -e "${WHITE}6.${NC} Run Specific Test File"
    echo -e "${WHITE}0.${NC} Back to Main Menu"
    echo ""
    read -p "Select option: " choice
    
    cd "$PROJECT_ROOT"
    source "$VENV_PATH/bin/activate"
    
    case $choice in
        1) pytest tests/ -v ;;
        2) pytest tests/unit/ -v ;;
        3) pytest tests/integration/ -v ;;
        4) pytest tests/e2e/ -v ;;
        5) pytest --cov=src --cov-report=html tests/ ;;
        6)
            read -p "Enter test file path: " test_file
            pytest "$test_file" -v
            ;;
        0) return ;;
        *) print_error "Invalid option"; sleep 1 ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
}

# Documentation Browser
browse_docs() {
    print_header
    print_section "Documentation Browser"
    
    echo -e "${WHITE}Core Documentation:${NC}"
    echo -e "${WHITE}1.${NC}  QUICK_REFERENCE.md (Master command reference)"
    echo -e "${WHITE}2.${NC}  ARCHITECTURE.md (System architecture)"
    echo -e "${WHITE}3.${NC}  DATABASE_SCHEMA.md (Database design)"
    echo -e "${WHITE}4.${NC}  DEVELOPMENT.md (Developer guide)"
    echo -e "${WHITE}5.${NC}  SECURITY.md (Security documentation)"
    echo -e "${WHITE}6.${NC}  PERFORMANCE.md (Performance guide)"
    echo -e "${WHITE}7.${NC}  USER_GUIDE.md (User manual)"
    echo -e "${WHITE}8.${NC}  TROUBLESHOOTING.md (Problem solving)"
    echo -e "${WHITE}9.${NC}  README.md (Project overview)"
    echo -e "${WHITE}0.${NC}  Back to Main Menu"
    echo ""
    read -p "Select document: " choice
    
    case $choice in
        1) less "$PROJECT_ROOT/QUICK_REFERENCE.md" ;;
        2) less "$PROJECT_ROOT/ARCHITECTURE.md" ;;
        3) less "$PROJECT_ROOT/DATABASE_SCHEMA.md" ;;
        4) less "$PROJECT_ROOT/DEVELOPMENT.md" ;;
        5) less "$PROJECT_ROOT/SECURITY.md" ;;
        6) less "$PROJECT_ROOT/PERFORMANCE.md" ;;
        7) less "$PROJECT_ROOT/docs/guides/USER_GUIDE.md" ;;
        8) less "$PROJECT_ROOT/TROUBLESHOOTING.md" ;;
        9) less "$PROJECT_ROOT/README.md" ;;
        0) return ;;
        *) print_error "Invalid option"; sleep 1 ;;
    esac
}

# Quick Actions
quick_actions() {
    print_header
    print_section "Quick Actions"
    
    echo -e "${WHITE}1.${NC} 🚀 Full System Start (All services + API)"
    echo -e "${WHITE}2.${NC} 🛑 Full System Stop"
    echo -e "${WHITE}3.${NC} 🔄 Quick Restart"
    echo -e "${WHITE}4.${NC} 🧪 Run Quick Test"
    echo -e "${WHITE}5.${NC} 📊 Open API Documentation (browser)"
    echo -e "${WHITE}6.${NC} 🧹 Clean Temporary Files"
    echo -e "${WHITE}7.${NC} 📦 Update Dependencies"
    echo -e "${WHITE}8.${NC} 🔧 Environment Check"
    echo -e "${WHITE}0.${NC} Back to Main Menu"
    echo ""
    read -p "Select action: " choice
    
    case $choice in
        1)
            print_info "Starting full system..."
            docker-compose up -d
            sleep 3
            cd "$PROJECT_ROOT"
            source "$VENV_PATH/bin/activate"
            python -m uvicorn src.samplemind.interfaces.api.main:app --host 0.0.0.0 --port 8000 &
            print_success "System started! API: http://localhost:8000"
            sleep 2
            ;;
        2)
            print_info "Stopping full system..."
            docker-compose down
            pkill -f uvicorn
            print_success "System stopped"
            sleep 2
            ;;
        3)
            print_info "Restarting system..."
            docker-compose restart
            print_success "System restarted"
            sleep 2
            ;;
        4)
            print_info "Running quick test..."
            cd "$PROJECT_ROOT"
            source "$VENV_PATH/bin/activate"
            pytest tests/unit/ -x -q
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            print_info "Opening API documentation..."
            if command_exists xdg-open; then
                xdg-open "http://localhost:8000/api/docs"
            elif command_exists open; then
                open "http://localhost:8000/api/docs"
            else
                print_info "Open browser to: http://localhost:8000/api/docs"
            fi
            sleep 2
            ;;
        6)
            print_info "Cleaning temporary files..."
            find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
            find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
            print_success "Temporary files cleaned"
            sleep 2
            ;;
        7)
            print_info "Updating dependencies..."
            cd "$PROJECT_ROOT"
            source "$VENV_PATH/bin/activate"
            pip install --upgrade pip
            pip install -e ".[dev]"
            print_success "Dependencies updated"
            sleep 2
            ;;
        8)
            print_info "Running environment check..."
            cd "$PROJECT_ROOT"
            source "$VENV_PATH/bin/activate"
            python scripts/verify_setup.py
            echo ""
            read -p "Press Enter to continue..."
            ;;
        0)
            return
            ;;
        *)
            print_error "Invalid option"
            sleep 1
            ;;
    esac
}

# File Organization
file_organization() {
    print_header
    print_section "File Organization"
    
    echo -e "${WHITE}1.${NC} View Project Structure"
    echo -e "${WHITE}2.${NC} Find Large Files (>10MB)"
    echo -e "${WHITE}3.${NC} Count Files by Type"
    echo -e "${WHITE}4.${NC} List Recent Files (24 hours)"
    echo -e "${WHITE}5.${NC} Clean Build Artifacts"
    echo -e "${WHITE}0.${NC} Back to Main Menu"
    echo ""
    read -p "Select option: " choice
    
    case $choice in
        1)
            if command_exists tree; then
                tree -L 3 -I 'node_modules|.venv|__pycache__|.git' "$PROJECT_ROOT"
            else
                find "$PROJECT_ROOT" -maxdepth 3 -type d -not -path '*/.*' -not -path '*/node_modules/*' -not -path '*/.venv/*'
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            print_info "Finding large files..."
            find "$PROJECT_ROOT" -type f -size +10M -exec ls -lh {} \; 2>/dev/null | awk '{print $9, $5}'
            echo ""
            read -p "Press Enter to continue..."
            ;;
        3)
            print_info "Counting files by type..."
            echo -e "\n${WHITE}Python files:${NC} $(find "$PROJECT_ROOT/src" -name "*.py" 2>/dev/null | wc -l)"
            echo -e "${WHITE}Test files:${NC} $(find "$PROJECT_ROOT/tests" -name "*.py" 2>/dev/null | wc -l)"
            echo -e "${WHITE}Markdown docs:${NC} $(find "$PROJECT_ROOT" -name "*.md" 2>/dev/null | wc -l)"
            echo -e "${WHITE}JSON files:${NC} $(find "$PROJECT_ROOT" -name "*.json" 2>/dev/null | wc -l)"
            echo ""
            read -p "Press Enter to continue..."
            ;;
        4)
            print_info "Recent files (last 24 hours)..."
            find "$PROJECT_ROOT" -type f -mtime -1 -not -path '*/.*' -not -path '*/node_modules/*' -not -path '*/.venv/*' 2>/dev/null
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            print_info "Cleaning build artifacts..."
            rm -rf "$PROJECT_ROOT/build" "$PROJECT_ROOT/dist" "$PROJECT_ROOT/*.egg-info"
            find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            print_success "Build artifacts cleaned"
            sleep 2
            ;;
        0)
            return
            ;;
        *)
            print_error "Invalid option"
            sleep 1
            ;;
    esac
}

# Configuration Manager
config_manager() {
    print_header
    print_section "Configuration Manager"
    
    echo -e "${WHITE}1.${NC} View Current Configuration"
    echo -e "${WHITE}2.${NC} Edit .env File"
    echo -e "${WHITE}3.${NC} Validate Configuration"
    echo -e "${WHITE}4.${NC} Show API Keys Status"
    echo -e "${WHITE}5.${NC} Reset to Default Config"
    echo -e "${WHITE}0.${NC} Back to Main Menu"
    echo ""
    read -p "Select option: " choice
    
    case $choice in
        1)
            if [ -f "$PROJECT_ROOT/.env" ]; then
                cat "$PROJECT_ROOT/.env" | grep -v "PASSWORD\|SECRET\|KEY" || echo "No config found"
            else
                print_warning ".env file not found"
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        2)
            ${EDITOR:-nano} "$PROJECT_ROOT/.env"
            ;;
        3)
            print_info "Validating configuration..."
            cd "$PROJECT_ROOT"
            source "$VENV_PATH/bin/activate"
            python -c "from src.samplemind.interfaces.api.config import get_settings; settings = get_settings(); print('✓ Configuration valid')"
            sleep 2
            ;;
        4)
            print_info "Checking API keys..."
            if [ -f "$PROJECT_ROOT/.env" ]; then
                if grep -q "GOOGLE_AI_API_KEY=.*[a-zA-Z0-9]" "$PROJECT_ROOT/.env"; then
                    print_success "Google Gemini API key configured"
                else
                    print_warning "Google Gemini API key not set"
                fi
                if grep -q "OPENAI_API_KEY=.*[a-zA-Z0-9]" "$PROJECT_ROOT/.env"; then
                    print_success "OpenAI API key configured"
                else
                    print_warning "OpenAI API key not set"
                fi
            fi
            echo ""
            read -p "Press Enter to continue..."
            ;;
        5)
            print_warning "This will reset configuration to defaults"
            read -p "Are you sure? (yes/no): " confirm
            if [ "$confirm" = "yes" ]; then
                cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
                print_success "Configuration reset to defaults"
            fi
            sleep 2
            ;;
        0)
            return
            ;;
        *)
            print_error "Invalid option"
            sleep 1
            ;;
    esac
}

# Main Menu
main_menu() {
    while true; do
        show_dashboard
        
        print_section "Main Menu"
        echo -e "${WHITE}1.${NC}  📊 Project Status Dashboard"
        echo -e "${WHITE}2.${NC}  🔧 Service Management"
        echo -e "${WHITE}3.${NC}  📝 Log Viewer & Analysis"
        echo -e "${WHITE}4.${NC}  💾 Database Operations"
        echo -e "${WHITE}5.${NC}  📁 File Organization"
        echo -e "${WHITE}6.${NC}  ⚙️  Configuration Manager"
        echo -e "${WHITE}7.${NC}  🧪 Test Suite Runner"
        echo -e "${WHITE}8.${NC}  📚 Documentation Browser"
        echo -e "${WHITE}9.${NC}  🚀 Quick Actions"
        echo -e "${WHITE}0.${NC}  ❌ Exit"
        echo ""
        read -p "Select option [0-9]: " choice
        
        case $choice in
            1) show_dashboard; read -p "Press Enter to continue..." ;;
            2) manage_services ;;
            3) view_logs ;;
            4) database_operations ;;
            5) file_organization ;;
            6) config_manager ;;
            7) run_tests ;;
            8) browse_docs ;;
            9) quick_actions ;;
            0)
                print_info "Exiting SampleMind Control Center..."
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 0-9."
                sleep 1
                ;;
        esac
    done
}

# Entry point
main() {
    # Check if script is executable
    if [ ! -x "$0" ]; then
        chmod +x "$0"
    fi
    
    # Create required directories
    mkdir -p "$LOGS_DIR" "$DATA_DIR/uploads" "$DATA_DIR/cache"
    
    # Start main menu
    main_menu
}

# Run main function
main "$@"
