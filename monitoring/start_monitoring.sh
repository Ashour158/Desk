#!/bin/bash

# Start Comprehensive Monitoring System
# This script starts all monitoring components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed"
    exit 1
fi

# Check if required packages are installed
print_status "Checking required packages..."

required_packages=(
    "psutil"
    "requests"
    "psycopg2-binary"
    "redis"
    "twilio"
)

missing_packages=()

for package in "${required_packages[@]}"; do
    if ! python3 -c "import ${package//-/_}" 2>/dev/null; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
    print_warning "Missing packages: ${missing_packages[*]}"
    print_status "Installing missing packages..."
    pip3 install "${missing_packages[@]}"
fi

# Create monitoring directories
print_status "Creating monitoring directories..."
mkdir -p monitoring/logs
mkdir -p monitoring/metrics
mkdir -p monitoring/alerts
mkdir -p monitoring/reports

# Check if monitoring is already running
if [ -f monitoring/real_time_monitor.pid ]; then
    print_warning "Real-time monitor already running (PID: $(cat monitoring/real_time_monitor.pid))"
    print_status "Stopping existing monitor..."
    kill $(cat monitoring/real_time_monitor.pid) 2>/dev/null || true
    rm monitoring/real_time_monitor.pid
fi

if [ -f monitoring/alerting_system.pid ]; then
    print_warning "Alerting system already running (PID: $(cat monitoring/alerting_system.pid))"
    print_status "Stopping existing alerting system..."
    kill $(cat monitoring/alerting_system.pid) 2>/dev/null || true
    rm monitoring/alerting_system.pid
fi

if [ -f monitoring/health_checker.pid ]; then
    print_warning "Health checker already running (PID: $(cat monitoring/health_checker.pid))"
    print_status "Stopping existing health checker..."
    kill $(cat monitoring/health_checker.pid) 2>/dev/null || true
    rm monitoring/health_checker.pid
fi

# Start Real-time Monitor
print_status "Starting real-time performance monitor..."
python3 monitoring/real_time_monitor.py --daemon &
REAL_TIME_PID=$!
echo $REAL_TIME_PID > monitoring/real_time_monitor.pid
print_success "Real-time monitor started (PID: $REAL_TIME_PID)"

# Start Alerting System
print_status "Starting alerting system..."
python3 monitoring/alerting_system.py --daemon &
ALERTING_PID=$!
echo $ALERTING_PID > monitoring/alerting_system.pid
print_success "Alerting system started (PID: $ALERTING_PID)"

# Start Health Checker
print_status "Starting health checker..."
python3 monitoring/health_checker.py --daemon &
HEALTH_PID=$!
echo $HEALTH_PID > monitoring/health_checker.pid
print_success "Health checker started (PID: $HEALTH_PID)"

# Wait a moment for services to initialize
sleep 5

# Check if services are running
print_status "Checking service status..."

# Check real-time monitor
if kill -0 $REAL_TIME_PID 2>/dev/null; then
    print_success "Real-time monitor is running"
else
    print_error "Real-time monitor failed to start"
fi

# Check alerting system
if kill -0 $ALERTING_PID 2>/dev/null; then
    print_success "Alerting system is running"
else
    print_error "Alerting system failed to start"
fi

# Check health checker
if kill -0 $HEALTH_PID 2>/dev/null; then
    print_success "Health checker is running"
else
    print_error "Health checker failed to start"
fi

# Create status script
cat > monitoring/status.sh << 'EOF'
#!/bin/bash
echo "=== Monitoring System Status ==="
echo "Real-time Monitor:"
python3 monitoring/real_time_monitor.py --status 2>/dev/null || echo "Not running"

echo -e "\nAlerting System:"
python3 monitoring/alerting_system.py --status 2>/dev/null || echo "Not running"

echo -e "\nHealth Checker:"
python3 monitoring/health_checker.py --status 2>/dev/null || echo "Not running"

echo -e "\nProcess Status:"
if [ -f monitoring/real_time_monitor.pid ]; then
    echo "Real-time Monitor PID: $(cat monitoring/real_time_monitor.pid)"
fi
if [ -f monitoring/alerting_system.pid ]; then
    echo "Alerting System PID: $(cat monitoring/alerting_system.pid)"
fi
if [ -f monitoring/health_checker.pid ]; then
    echo "Health Checker PID: $(cat monitoring/health_checker.pid)"
fi
EOF

chmod +x monitoring/status.sh

# Create stop script
cat > monitoring/stop_monitoring.sh << 'EOF'
#!/bin/bash
echo "Stopping monitoring system..."

if [ -f monitoring/real_time_monitor.pid ]; then
    kill $(cat monitoring/real_time_monitor.pid) 2>/dev/null || true
    rm monitoring/real_time_monitor.pid
    echo "Real-time monitor stopped"
fi

if [ -f monitoring/alerting_system.pid ]; then
    kill $(cat monitoring/alerting_system.pid) 2>/dev/null || true
    rm monitoring/alerting_system.pid
    echo "Alerting system stopped"
fi

if [ -f monitoring/health_checker.pid ]; then
    kill $(cat monitoring/health_checker.pid) 2>/dev/null || true
    rm monitoring/health_checker.pid
    echo "Health checker stopped"
fi

echo "Monitoring system stopped"
EOF

chmod +x monitoring/stop_monitoring.sh

print_success "Monitoring system started successfully!"
print_status "PIDs saved to monitoring/*.pid files"
print_status "Use 'monitoring/status.sh' to check status"
print_status "Use 'monitoring/stop_monitoring.sh' to stop monitoring"
print_status "Logs are available in monitoring/logs/"

# Show initial status
echo ""
print_status "Initial system status:"
python3 monitoring/health_checker.py --check
