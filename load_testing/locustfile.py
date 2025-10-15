"""
Load Testing Suite with Locust
Comprehensive load testing for performance and scalability
"""

from locust import HttpUser, task, between
import random
import json
import time
from datetime import datetime


class HelpdeskUser(HttpUser):
    """Simulate helpdesk user behavior"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.login()
    
    def login(self):
        """Login to the system"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": f"testuser{random.randint(1, 1000)}@example.com",
            "password": "testpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        else:
            # If login fails, try to register
            self.register()
    
    def register(self):
        """Register a new user"""
        response = self.client.post("/api/v1/auth/register/", json={
            "email": f"testuser{random.randint(1, 1000)}@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        })
        
        if response.status_code == 201:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(3)
    def view_dashboard(self):
        """View dashboard (most common task)"""
        self.client.get("/api/v1/dashboard/")
    
    @task(2)
    def view_tickets(self):
        """View tickets list"""
        self.client.get("/api/v1/tickets/")
    
    @task(1)
    def create_ticket(self):
        """Create a new ticket"""
        ticket_data = {
            "subject": f"Load Test Ticket {random.randint(1, 10000)}",
            "description": "This is a load test ticket created during performance testing",
            "priority": random.choice(["low", "medium", "high"]),
            "category": random.choice(["technical", "billing", "general"])
        }
        
        response = self.client.post("/api/v1/tickets/", json=ticket_data)
        
        if response.status_code == 201:
            self.ticket_id = response.json().get("id")
    
    @task(1)
    def view_ticket_detail(self):
        """View ticket detail"""
        if hasattr(self, 'ticket_id'):
            self.client.get(f"/api/v1/tickets/{self.ticket_id}/")
    
    @task(1)
    def add_ticket_comment(self):
        """Add comment to ticket"""
        if hasattr(self, 'ticket_id'):
            comment_data = {
                "content": f"Load test comment {random.randint(1, 10000)}",
                "is_internal": random.choice([True, False])
            }
            self.client.post(f"/api/v1/tickets/{self.ticket_id}/comments/", json=comment_data)
    
    @task(1)
    def search_knowledge_base(self):
        """Search knowledge base"""
        search_terms = ["password", "login", "billing", "technical", "support"]
        query = random.choice(search_terms)
        self.client.get(f"/api/v1/knowledge-base/search/?q={query}")
    
    @task(1)
    def view_analytics(self):
        """View analytics dashboard"""
        self.client.get("/api/v1/analytics/dashboard/")
    
    @task(1)
    def update_profile(self):
        """Update user profile"""
        profile_data = {
            "first_name": f"Test{random.randint(1, 1000)}",
            "last_name": f"User{random.randint(1, 1000)}",
            "phone": f"+123456789{random.randint(0, 9)}"
        }
        self.client.put("/api/v1/profile/", json=profile_data)


class AdminUser(HttpUser):
    """Simulate admin user behavior"""
    
    wait_time = between(2, 5)  # Wait 2-5 seconds between tasks
    
    def on_start(self):
        """Called when an admin user starts"""
        self.login()
    
    def login(self):
        """Login as admin"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": "admin@example.com",
            "password": "adminpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(3)
    def view_admin_dashboard(self):
        """View admin dashboard"""
        self.client.get("/api/v1/admin/dashboard/")
    
    @task(2)
    def manage_tickets(self):
        """Manage tickets"""
        self.client.get("/api/v1/admin/tickets/")
    
    @task(1)
    def assign_ticket(self):
        """Assign ticket to agent"""
        ticket_id = random.randint(1, 100)
        assignment_data = {
            "agent_id": random.randint(1, 10),
            "note": "Load test assignment"
        }
        self.client.post(f"/api/v1/admin/tickets/{ticket_id}/assign/", json=assignment_data)
    
    @task(1)
    def view_analytics(self):
        """View analytics"""
        self.client.get("/api/v1/admin/analytics/")
    
    @task(1)
    def manage_users(self):
        """Manage users"""
        self.client.get("/api/v1/admin/users/")
    
    @task(1)
    def view_reports(self):
        """View reports"""
        self.client.get("/api/v1/admin/reports/")


class APIUser(HttpUser):
    """Simulate API user behavior"""
    
    wait_time = between(0.5, 2)  # Wait 0.5-2 seconds between tasks
    
    def on_start(self):
        """Called when an API user starts"""
        self.login()
    
    def login(self):
        """Login for API access"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": f"apiuser{random.randint(1, 100)}@example.com",
            "password": "apipass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(5)
    def api_get_tickets(self):
        """API: Get tickets"""
        self.client.get("/api/v1/tickets/")
    
    @task(3)
    def api_create_ticket(self):
        """API: Create ticket"""
        ticket_data = {
            "subject": f"API Load Test Ticket {random.randint(1, 10000)}",
            "description": "API load test ticket",
            "priority": random.choice(["low", "medium", "high"])
        }
        self.client.post("/api/v1/tickets/", json=ticket_data)
    
    @task(2)
    def api_get_ticket_detail(self):
        """API: Get ticket detail"""
        ticket_id = random.randint(1, 100)
        self.client.get(f"/api/v1/tickets/{ticket_id}/")
    
    @task(1)
    def api_search_tickets(self):
        """API: Search tickets"""
        query = random.choice(["open", "closed", "high", "technical"])
        self.client.get(f"/api/v1/tickets/search/?q={query}")
    
    @task(1)
    def api_get_analytics(self):
        """API: Get analytics"""
        self.client.get("/api/v1/analytics/")
    
    @task(1)
    def api_health_check(self):
        """API: Health check"""
        self.client.get("/api/v1/health/")


class StressTestUser(HttpUser):
    """Simulate stress test user behavior"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    def on_start(self):
        """Called when a stress test user starts"""
        self.login()
    
    def login(self):
        """Login for stress testing"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": f"stressuser{random.randint(1, 1000)}@example.com",
            "password": "stresspass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(10)
    def rapid_requests(self):
        """Make rapid requests"""
        endpoints = [
            "/api/v1/health/",
            "/api/v1/tickets/",
            "/api/v1/dashboard/",
            "/api/v1/analytics/"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)
    
    @task(5)
    def rapid_creates(self):
        """Make rapid create requests"""
        ticket_data = {
            "subject": f"Stress Test Ticket {random.randint(1, 100000)}",
            "description": "Stress test ticket",
            "priority": "high"
        }
        self.client.post("/api/v1/tickets/", json=ticket_data)
    
    @task(3)
    def rapid_updates(self):
        """Make rapid update requests"""
        ticket_id = random.randint(1, 1000)
        update_data = {
            "status": random.choice(["open", "in_progress", "resolved"]),
            "priority": random.choice(["low", "medium", "high"])
        }
        self.client.put(f"/api/v1/tickets/{ticket_id}/", json=update_data)


class DatabaseLoadUser(HttpUser):
    """Simulate database load testing"""
    
    wait_time = between(0.1, 1)
    
    def on_start(self):
        """Called when a database load user starts"""
        self.login()
    
    def login(self):
        """Login for database load testing"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": f"dbloaduser{random.randint(1, 1000)}@example.com",
            "password": "dbloadpass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(5)
    def complex_queries(self):
        """Test complex database queries"""
        # Test analytics queries
        self.client.get("/api/v1/analytics/dashboard/")
        self.client.get("/api/v1/analytics/reports/")
        self.client.get("/api/v1/analytics/metrics/")
    
    @task(3)
    def search_operations(self):
        """Test search operations"""
        search_terms = ["ticket", "user", "organization", "report", "analytics"]
        query = random.choice(search_terms)
        self.client.get(f"/api/v1/tickets/search/?q={query}")
        self.client.get(f"/api/v1/users/search/?q={query}")
    
    @task(2)
    def bulk_operations(self):
        """Test bulk operations"""
        # Test bulk ticket operations
        self.client.get("/api/v1/tickets/?page=1&page_size=100")
        self.client.get("/api/v1/tickets/?page=2&page_size=100")
    
    @task(1)
    def report_generation(self):
        """Test report generation"""
        self.client.get("/api/v1/reports/generate/")
        self.client.get("/api/v1/reports/export/")


class WebSocketUser(HttpUser):
    """Simulate WebSocket load testing"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a WebSocket user starts"""
        self.login()
    
    def login(self):
        """Login for WebSocket testing"""
        response = self.client.post("/api/v1/auth/login/", json={
            "email": f"wsuser{random.randint(1, 1000)}@example.com",
            "password": "wspass123"
        })
        
        if response.status_code == 200:
            self.token = response.json().get("access")
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
    
    @task(3)
    def websocket_connection(self):
        """Test WebSocket connection"""
        # Test WebSocket endpoints
        self.client.get("/socket.io/")
        self.client.get("/api/v1/realtime/status/")
    
    @task(2)
    def realtime_updates(self):
        """Test real-time updates"""
        self.client.get("/api/v1/realtime/notifications/")
        self.client.get("/api/v1/realtime/events/")
    
    @task(1)
    def live_chat(self):
        """Test live chat functionality"""
        self.client.get("/api/v1/chat/status/")
        self.client.get("/api/v1/chat/messages/")


# Test configuration
class LoadTestConfig:
    """Load test configuration"""
    
    # User classes and their weights
    USER_CLASSES = [
        (HelpdeskUser, 40),      # 40% regular users
        (AdminUser, 10),         # 10% admin users
        (APIUser, 30),           # 30% API users
        (StressTestUser, 15),    # 15% stress test users
        (DatabaseLoadUser, 3),   # 3% database load users
        (WebSocketUser, 2),      # 2% WebSocket users
    ]
    
    # Test scenarios
    SCENARIOS = {
        "light_load": {
            "users": 10,
            "spawn_rate": 2,
            "duration": "5m"
        },
        "medium_load": {
            "users": 50,
            "spawn_rate": 5,
            "duration": "10m"
        },
        "heavy_load": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "15m"
        },
        "stress_test": {
            "users": 200,
            "spawn_rate": 20,
            "duration": "10m"
        },
        "spike_test": {
            "users": 500,
            "spawn_rate": 50,
            "duration": "5m"
        }
    }


# Performance monitoring
class PerformanceMonitor:
    """Monitor performance during load testing"""
    
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "error_rates": [],
            "throughput": [],
            "memory_usage": [],
            "cpu_usage": []
        }
    
    def record_metric(self, metric_type, value):
        """Record a performance metric"""
        if metric_type in self.metrics:
            self.metrics[metric_type].append({
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
    
    def get_summary(self):
        """Get performance summary"""
        summary = {}
        
        for metric_type, values in self.metrics.items():
            if values:
                summary[metric_type] = {
                    "min": min(v["value"] for v in values),
                    "max": max(v["value"] for v in values),
                    "avg": sum(v["value"] for v in values) / len(values),
                    "count": len(values)
                }
        
        return summary


# Global performance monitor
performance_monitor = PerformanceMonitor()


# Custom Locust events
def on_request_success(request_type, name, response_time, response_length):
    """Called when a request succeeds"""
    performance_monitor.record_metric("response_times", response_time)
    performance_monitor.record_metric("throughput", 1)


def on_request_failure(request_type, name, response_time, response_length, exception):
    """Called when a request fails"""
    performance_monitor.record_metric("error_rates", 1)


# Export configuration for Locust
def get_user_classes():
    """Get user classes for Locust"""
    return [cls for cls, weight in LoadTestConfig.USER_CLASSES]


def get_test_scenarios():
    """Get test scenarios"""
    return LoadTestConfig.SCENARIOS


def get_performance_monitor():
    """Get performance monitor"""
    return performance_monitor
