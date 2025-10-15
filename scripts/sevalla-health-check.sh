#!/bin/bash

# OBCMS Sevalla Health Check Script
# Monitors application health and provides diagnostic information
# Usage: ./scripts/sevalla-health-check.sh [OPTIONS]

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${1:-staging}"
DOMAIN="${2:-localhost:8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# HTTP health check
check_http_health() {
    log "Checking HTTP health at $DOMAIN..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/health/" 2>/dev/null || echo "000")
    local response_body=$(curl -s "http://$DOMAIN/health/" 2>/dev/null || echo "{}")
    
    echo "HTTP Status: $response_code"
    echo "Response Body: $response_body"
    
    if [[ "$response_code" == "200" ]]; then
        success "HTTP health check passed"
        return 0
    else
        error "HTTP health check failed - Status: $response_code"
        return 1
    fi
}

# HTTPS health check
check_https_health() {
    if [[ "$DOMAIN" == "localhost"* ]]; then
        log "Skipping HTTPS check for localhost"
        return 0
    fi
    
    log "Checking HTTPS health at $DOMAIN..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN/health/" 2>/dev/null || echo "000")
    local ssl_check=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "SSL_NA")
    
    echo "HTTPS Status: $response_code"
    echo "SSL Certificate: $ssl_check"
    
    if [[ "$response_code" == "200" ]]; then
        success "HTTPS health check passed"
        return 0
    else
        error "HTTPS health check failed - Status: $response_code"
        return 1
    fi
}

# Readiness check
check_readiness() {
    log "Checking application readiness..."
    
    local response=$(curl -s "http://$DOMAIN/health/" 2>/dev/null || echo "{}")
    
    # Extract status using python (more reliable than text processing)
    local status=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data.get('status', 'unknown'))
except:
    print('error')
")
    
    echo "Application Status: $status"
    
    if [[ "$status" == "ready" || "$status" == "healthy" ]]; then
        success "Readiness check passed"
        return 0
    else
        error "Readiness check failed - Status: $status"
        return 1
    fi
}

# Database connectivity check (via health endpoint)
check_database() {
    log "Checking database connectivity..."
    
    local response=$(curl -s "http://$DOMAIN/health/" 2>/dev/null || echo "{}")
    
    local db_status=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    checks = data.get('checks', {})
    print(checks.get('database', 'unknown'))
except:
    print('error')
")
    
    echo "Database Status: $db_status"
    
    if [[ "$db_status" == "True" || "$db_status" == "healthy" ]]; then
        success "Database connectivity check passed"
        return 0
    else
        error "Database connectivity check failed - Status: $db_status"
        return 1
    fi
}

# Cache connectivity check
check_cache() {
    log "Checking cache connectivity..."
    
    local response=$(curl -s "http://$DOMAIN/health/" 2>/dev/null || echo "{}")
    
    local cache_status=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    checks = data.get('checks', {})
    print(checks.get('cache', 'unknown'))
except:
    print('error')
")
    
    echo "Cache Status: $cache_status"
    
    if [[ "$cache_status" == "True" || "$cache_status" == "healthy" ]]; then
        success "Cache connectivity check passed"
        return 0
    else
        error "Cache connectivity check failed - Status: $cache_status"
        return 1
    fi
}

# Performance check
check_performance() {
    log "Checking application performance..."
    
    local start_time=$(date +%s%N)
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/" 2>/dev/null || echo "000")
    local end_time=$(date +%s%N)
    
    local response_time=$(((end_time - start_time) / 1000000))  # Convert to milliseconds
    
    echo "Home Page Response Time: ${response_time}ms"
    echo "Home Page Status Code: $response_code"
    
    if [[ "$response_time" -lt 2000 && "$response_code" == "200" ]]; then
        success "Performance check passed (Response time: ${response_time}ms)"
        return 0
    else
        warn "Performance check warning (Response time: ${response_time}ms, Status: $response_code)"
        return 1
    fi
}

# Static files check
check_static_files() {
    log "Checking static files..."
    
    local css_response=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/static/css/output.css" 2>/dev/null || echo "000")
    local js_response=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/static/js/output.js" 2>/dev/null || echo "000")
    
    echo "CSS File Status: $css_response"
    echo "JS File Status: $js_response"
    
    if [[ "$css_response" == "200" && "$js_response" == "200" ]]; then
        success "Static files check passed"
        return 0
    else
        error "Static files check failed"
        return 1
    fi
}

# Admin panel check
check_admin_panel() {
    log "Checking admin panel accessibility..."
    
    local response_code=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN/admin/" 2>/dev/null || echo "000")
    
    echo "Admin Panel Status: $response_code"
    
    if [[ "$response_code" == "200" || "$response_code" == "302" ]]; then
        success "Admin panel check passed"
        return 0
    else
        error "Admin panel check failed - Status: $response_code"
        return 1
    fi
}

# Configuration check
check_configuration() {
    log "Checking application configuration..."
    
    local response=$(curl -s "http://$DOMAIN/health/" 2>/dev/null || echo "{}")
    
    # Extract version and service info
    local version=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data.get('version', 'unknown'))
except:
    print('unknown')
")
    
    local service=$(echo "$response" | python3 -c "
import json
import sys
try:
    data = json.load(sys.stdin)
    print(data.get('service', 'unknown'))
except:
    print('unknown')
")
    
    echo "Service: $service"
    echo "Version: $version"
    
    if [[ "$service" == "obcms" && "$version" != "unknown" ]]; then
        success "Configuration check passed"
        return 0
    else
        error "Configuration check failed"
        return 1
    fi
}

# Generate health report
generate_report() {
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    log "Generating comprehensive health report..."
    
    echo ""
    echo "======================================"
    echo "       OBCMS HEALTH CHECK REPORT"
    echo "======================================"
    echo "Environment: $ENVIRONMENT"
    echo "Domain: $DOMAIN"
    echo "Timestamp: $(date)"
    echo "======================================"
    
    # Run all checks and count results
    if check_http_health; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_https_health; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_readiness; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_database; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_cache; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_performance; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_static_files; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_admin_panel; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    if check_configuration; then ((passed_tests++)); else ((failed_tests++)); fi
    ((total_tests++))
    
    echo "======================================"
    echo "            SUMMARY"
    echo "======================================"
    echo "Total Tests: $total_tests"
    echo "Passed: $passed_tests"
    echo "Failed: $failed_tests"
    
    local pass_rate=$((passed_tests * 100 / total_tests))
    echo "Pass Rate: ${pass_rate}%"
    echo "======================================"
    
    if [[ $failed_tests -eq 0 ]]; then
        success "All health checks passed! 🎉"
        return 0
    elif [[ $pass_rate -ge 80 ]]; then
        warn "Most health checks passed (${pass_rate}%)"
        return 1
    else
        error "Many health checks failed (${pass_rate}%)"
        return 2
    fi
}

# Continuous monitoring mode
monitor_mode() {
    log "Starting continuous monitoring (Ctrl+C to stop)..."
    
    while true; do
        echo ""
        log "Health check at $(date)"
        
        if check_http_health; then
            success "Application is healthy"
        else
            error "Application health check failed"
        fi
        
        sleep 60  # Check every minute
    done
}

# Help function
show_help() {
    cat << EOF
OBCMS Sevalla Health Check Script

Usage: $0 [ENVIRONMENT] [DOMAIN] [OPTIONS]

ENVIRONMENT:
  staging     Check staging environment
  production  Check production environment
  (default)   Uses 'staging' if not specified

DOMAIN:
  Full domain or host to check
  (default)   Uses 'localhost:8000' if not specified

OPTIONS:
  --monitor     Enable continuous monitoring mode
  --quick       Quick health check (HTTP only)
  --verbose     Enable verbose output
  --help        Show this help message

EXAMPLES:
  $0                                    # Quick check of localhost:8000
  $0 staging                           # Check staging environment
  $0 production bmms.barmm.gov.ph       # Check production domain
  $0 staging --monitor                  # Continuous monitoring
  $0 staging --quick                    # Quick check only

HEALTH CHECKS PERFORMED:
  ✓ HTTP connectivity
  ✓ HTTPS connectivity (if applicable)
  ✓ Application readiness
  ✓ Database connectivity
  ✓ Cache connectivity
  ✓ Performance response time
  ✓ Static files serving
  ✓ Admin panel accessibility
  ✓ Configuration validation

For troubleshooting, see:
docs/deployment/SEVALLA_TROUBLESHOOTING.md

EOF
}

# Parse command line arguments
case "${3:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --monitor)
        monitor_mode
        exit 0
        ;;
    --quick)
        log "Quick health check..."
        check_http_health
        exit $?
        ;;
    --verbose)
        set -x  # Enable verbose output
        generate_report
        ;;
    *)
        generate_report
        ;;
esac
