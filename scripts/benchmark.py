#!/usr/bin/env python3
"""
SampleMind AI v7 - API Performance Benchmark Script
Uses locust for load testing and performance metrics
"""

from locust import HttpUser, task, between
import json
import random
import os

class SampleMindUser(HttpUser):
    """Simulates user behavior for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Setup: Login and get authentication token"""
        # Test credentials (update for your environment)
        login_data = {
            "email": os.getenv("TEST_USER_EMAIL", "test@example.com"),
            "password": os.getenv("TEST_USER_PASSWORD", "testpassword")
        }
        
        response = self.client.post("/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}
    
    @task(3)
    def health_check(self):
        """Health endpoint (frequent check)"""
        self.client.get("/health")
    
    @task(2)
    def get_user_profile(self):
        """Get current user profile"""
        self.client.get("/api/v1/auth/me", headers=self.headers)
    
    @task(5)
    def list_audio_files(self):
        """List user's audio files"""
        params = {
            "limit": random.randint(10, 50),
            "offset": random.randint(0, 100)
        }
        self.client.get("/api/v1/audio/files", headers=self.headers, params=params)
    
    @task(2)
    def get_audio_file_detail(self):
        """Get specific audio file details"""
        # Assumes you have some file IDs to test
        file_id = os.getenv("TEST_FILE_ID", "test-file-id")
        self.client.get(f"/api/v1/audio/files/{file_id}", headers=self.headers)
    
    @task(1)
    def search_audio_files(self):
        """Search audio files"""
        search_terms = ["drums", "bass", "synth", "vocal", "melody"]
        query = random.choice(search_terms)
        params = {"q": query, "limit": 20}
        self.client.get("/api/v1/audio/search", headers=self.headers, params=params)
    
    @task(1)
    def get_analysis_status(self):
        """Check analysis task status"""
        task_id = os.getenv("TEST_TASK_ID", "test-task-id")
        self.client.get(f"/api/v1/tasks/status/{task_id}", headers=self.headers)


class WebSocketUser(HttpUser):
    """Tests WebSocket connections for real-time updates"""
    
    wait_time = between(2, 5)
    
    @task
    def websocket_connection(self):
        """Simulate WebSocket connection"""
        # Note: Locust HTTP client doesn't natively support WebSocket
        # You might need websocket-client library for true WebSocket testing
        pass


# Performance test configurations
class QuickLoadTest(SampleMindUser):
    """Quick load test: 10 users"""
    pass


class StandardLoadTest(SampleMindUser):
    """Standard load test: 100 users"""
    pass


class StressTest(SampleMindUser):
    """Stress test: 500 users"""
    pass


if __name__ == "__main__":
    print("""
    🚀 SampleMind AI v7 - Performance Benchmark
    
    Run with locust:
    ================
    
    # Quick test (10 users)
    locust -f scripts/performance/benchmark.py --users 10 --spawn-rate 2 --run-time 5m
    
    # Standard load test (100 users)
    locust -f scripts/performance/benchmark.py --users 100 --spawn-rate 10 --run-time 10m
    
    # Stress test (500 users)
    locust -f scripts/performance/benchmark.py --users 500 --spawn-rate 50 --run-time 15m
    
    # With Web UI
    locust -f scripts/performance/benchmark.py --host=http://localhost:8000
    
    # Headless mode
    locust -f scripts/performance/benchmark.py --host=http://localhost:8000 \\
           --users 100 --spawn-rate 10 --run-time 10m --headless
    
    Environment Variables:
    ======================
    TEST_USER_EMAIL     - Test user email for authentication
    TEST_USER_PASSWORD  - Test user password
    TEST_FILE_ID        - Sample audio file ID for testing
    TEST_TASK_ID        - Sample task ID for testing
    
    Metrics to Watch:
    =================
    - Response Time (P50, P95, P99)
    - Requests per Second (RPS)
    - Failure Rate
    - Average Response Time
    """)
