"""
Load testing configuration for SampleMind AI API
Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000
"""
import random
import json
from locust import HttpUser, task, between, SequentialTaskSet


class UserAuthenticationTasks(SequentialTaskSet):
    """Sequential tasks for user authentication"""
    
    def on_start(self):
        """Register and login user"""
        self.username = f"loadtest_user_{random.randint(1000, 9999)}"
        self.password = "LoadTest123!"
        self.email = f"{self.username}@loadtest.com"
        
        # Register
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.email,
                "username": self.username,
                "password": self.password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            # Login if already registered
            response = self.client.post(
                "/api/v1/auth/login",
                data={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    @task
    def get_current_user(self):
        """Get current user info"""
        self.client.get("/api/v1/auth/me", headers=self.headers)
    
    @task
    def check_health(self):
        """Check API health"""
        self.client.get("/api/v1/health")


class AudioAnalysisTasks(SequentialTaskSet):
    """Tasks for audio analysis workflow"""
    
    @task
    def list_audio_files(self):
        """List audio files"""
        self.client.get(
            "/api/v1/audio/files",
            params={"skip": 0, "limit": 20},
            headers=getattr(self.user, 'headers', {})
        )
    
    @task
    def get_task_status(self):
        """Get task status (simulated)"""
        task_id = f"test_task_{random.randint(1, 100)}"
        self.client.get(
            f"/api/v1/tasks/{task_id}",
            headers=getattr(self.user, 'headers', {}),
            name="/api/v1/tasks/[id]"
        )
    
    @task
    def get_workers_status(self):
        """Get workers status"""
        self.client.get(
            "/api/v1/tasks/workers/status",
            headers=getattr(self.user, 'headers', {})
        )


class SampleMindUser(HttpUser):
    """Simulated user for load testing"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    tasks = {
        UserAuthenticationTasks: 3,  # 30% weight
        AudioAnalysisTasks: 7          # 70% weight
    }
    
    def on_start(self):
        """Initialize user session"""
        # Register and login
        self.username = f"loadtest_user_{random.randint(1000, 9999)}"
        self.password = "LoadTest123!"
        
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": f"{self.username}@loadtest.com",
                "username": self.username,
                "password": self.password
            },
            catch_response=True
        )
        
        if response.status_code in [200, 400]:  # 400 if already exists
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
            else:
                # Login
                response = self.client.post(
                    "/api/v1/auth/login",
                    data={
                        "username": self.username,
                        "password": self.password
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
            
            self.headers = {"Authorization": f"Bearer {self.access_token}"}


# Separate user class for high-load testing
class HighLoadUser(HttpUser):
    """High-load user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very short wait time
    
    @task(10)
    def health_check(self):
        """Frequent health checks"""
        self.client.get("/api/v1/health")
    
    @task(5)
    def list_providers(self):
        """List AI providers"""
        self.client.get("/api/v1/ai/providers")
    
    @task(1)
    def get_queue_stats(self):
        """Get queue statistics"""
        self.client.get("/api/v1/tasks/queues/stats")
