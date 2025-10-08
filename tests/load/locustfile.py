"""
SampleMind AI - Comprehensive Load Testing Suite
Phase 6: Production Deployment - Task 6.1

Load test scenarios simulating production traffic patterns.

Usage:
    # Web UI mode
    locust -f tests/load/locustfile.py --host=http://localhost:8000

    # Headless mode with stages
    locust -f tests/load/locustfile.py --host=http://localhost:8000 \
           --users 1000 --spawn-rate 50 --run-time 10m --headless

    # With custom stages
    locust -f tests/load/locustfile.py --host=http://localhost:8000 \
           --headless --users 1000 --spawn-rate 50 --run-time 10m

Success Criteria:
    - Handle 1000 concurrent users
    - p95 response time < 500ms
    - Error rate < 0.1%
    - No memory leaks
    - CPU usage < 80%
"""

import json
import random
import time
from typing import Dict, Any, Optional
from io import BytesIO

from locust import HttpUser, task, between, events, TaskSet
from locust.runners import MasterRunner


# Test data for realistic scenarios
SAMPLE_AUDIO_FILES = [
    "test_120bpm_c_major.wav",
    "test_140bpm_a_minor.wav",
    "test_noise.wav",
]

SAMPLE_GENRES = ["House", "Techno", "Hip Hop", "Trap", "Ambient", "DnB"]
SAMPLE_KEYS = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
SAMPLE_SCALES = ["Major", "Minor", "Dorian", "Phrygian", "Lydian", "Mixolydian"]


class MetricsCollector:
    """Collects and aggregates metrics during load testing"""
    
    def __init__(self):
        self.total_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.errors_by_endpoint = {}
        
    def record_request(self, response_time: float, success: bool, endpoint: str):
        """Record a request metric"""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
            self.errors_by_endpoint[endpoint] = self.errors_by_endpoint.get(endpoint, 0) + 1
        self.response_times.append(response_time)
    
    def get_error_rate(self) -> float:
        """Calculate current error rate"""
        if self.total_requests == 0:
            return 0.0
        return (self.failed_requests / self.total_requests) * 100
    
    def get_percentile(self, percentile: int) -> float:
        """Calculate response time percentile"""
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(len(sorted_times) * (percentile / 100))
        return sorted_times[min(index, len(sorted_times) - 1)]


# Global metrics collector
metrics = MetricsCollector()


class AudioAnalysisUser(HttpUser):
    """
    Simulates typical user behavior with weighted tasks.
    
    This user represents the most common usage pattern:
    - Analyzing audio files (primary operation)
    - Uploading new files
    - Viewing analysis results
    - Browsing file library
    - Searching for specific samples
    
    Wait time: 1-5 seconds between tasks (realistic user interaction)
    """
    wait_time = between(1, 5)
    weight = 5  # Most common user type
    
    def on_start(self):
        """Setup: Login and get auth token"""
        self.auth_token = None
        self.file_ids = []
        self.login()
    
    def login(self):
        """Authenticate user and get JWT token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": f"test_user_{random.randint(1, 1000)}@example.com",
            "password": "test_password_123"
        })
        
        if response.status_code == 200:
            self.auth_token = response.json().get("access_token")
        else:
            # Use guest mode if login fails
            self.auth_token = "guest_token"
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
    
    @task(3)
    def analyze_audio(self):
        """
        Most common operation: Analyze an audio file
        Weight: 3 (happens most frequently)
        """
        if not self.file_ids:
            # Upload a file first if none exist
            self.upload_file()
            return
        
        file_id = random.choice(self.file_ids)
        start_time = time.time()
        
        with self.client.post(
            f"/api/v1/audio/{file_id}/analyze",
            headers=self.headers,
            json={
                "analysis_type": "full",
                "extract_features": True,
                "detect_key": True,
                "detect_bpm": True
            },
            catch_response=True,
            name="/api/v1/audio/[id]/analyze"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "analyze_audio")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def upload_file(self):
        """
        File upload operation
        Weight: 1 (less frequent than analysis)
        """
        # Simulate audio file upload
        filename = random.choice(SAMPLE_AUDIO_FILES)
        file_data = BytesIO(b"fake_audio_data" * 1000)  # ~14KB fake file
        
        start_time = time.time()
        
        with self.client.post(
            "/api/v1/audio/upload",
            headers=self.headers,
            files={"file": (filename, file_data, "audio/wav")},
            data={
                "genre": random.choice(SAMPLE_GENRES),
                "tags": json.dumps(["test", "load-test"])
            },
            catch_response=True,
            name="/api/v1/audio/upload"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code in [200, 201]
            metrics.record_request(response_time, success, "upload_file")
            
            if success:
                file_id = response.json().get("file_id")
                if file_id:
                    self.file_ids.append(file_id)
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def view_results(self):
        """
        View analysis results
        Weight: 2 (common operation)
        """
        if not self.file_ids:
            return
        
        file_id = random.choice(self.file_ids)
        start_time = time.time()
        
        with self.client.get(
            f"/api/v1/audio/{file_id}/results",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/audio/[id]/results"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "view_results")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def list_files(self):
        """
        Browse file library
        Weight: 2 (common operation)
        """
        start_time = time.time()
        
        with self.client.get(
            "/api/v1/audio/files",
            headers=self.headers,
            params={
                "page": random.randint(1, 5),
                "limit": 20,
                "sort": random.choice(["created_at", "name", "bpm"])
            },
            catch_response=True,
            name="/api/v1/audio/files"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "list_files")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def search_files(self):
        """
        Search functionality
        Weight: 1 (less frequent)
        """
        search_params = {
            "query": random.choice(["kick", "snare", "bass", "synth"]),
            "genre": random.choice(SAMPLE_GENRES + [None]),
            "key": random.choice(SAMPLE_KEYS + [None]),
            "min_bpm": random.choice([None, 120, 130, 140]),
            "max_bpm": random.choice([None, 150, 160, 170])
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        start_time = time.time()
        
        with self.client.get(
            "/api/v1/audio/search",
            headers=self.headers,
            params=search_params,
            catch_response=True,
            name="/api/v1/audio/search"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "search_files")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class APIUser(HttpUser):
    """
    Simulates API client behavior (programmatic access).
    
    This user represents automated systems and integrations:
    - API-based audio analysis
    - Batch processing jobs
    - Status monitoring
    
    Wait time: 0.5-2 seconds (faster than human users)
    """
    wait_time = between(0.5, 2)
    weight = 3  # Moderate weight for API users
    
    def on_start(self):
        """Setup: Get API key"""
        self.api_key = f"sk_test_{random.randint(10000, 99999)}"
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get API key headers"""
        return {"X-API-Key": self.api_key}
    
    @task(5)
    def api_analyze(self):
        """
        API-based analysis
        Weight: 5 (primary API operation)
        """
        start_time = time.time()
        
        with self.client.post(
            "/api/v1/analyze",
            headers=self.headers,
            json={
                "audio_url": f"https://example.com/audio/{random.randint(1, 1000)}.wav",
                "features": ["bpm", "key", "genre"],
                "webhook_url": "https://example.com/webhook"
            },
            catch_response=True,
            name="/api/v1/analyze (API)"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code in [200, 202]
            metrics.record_request(response_time, success, "api_analyze")
            
            if success:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def api_batch_process(self):
        """
        Batch processing API
        Weight: 2 (less frequent but important)
        """
        start_time = time.time()
        
        with self.client.post(
            "/api/v1/batch",
            headers=self.headers,
            json={
                "files": [
                    {"url": f"https://example.com/audio/{i}.wav"}
                    for i in range(random.randint(5, 20))
                ],
                "analysis_type": "quick",
                "priority": random.choice(["low", "normal", "high"])
            },
            catch_response=True,
            name="/api/v1/batch (API)"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code in [200, 202]
            metrics.record_request(response_time, success, "api_batch_process")
            
            if success:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(3)
    def api_get_status(self):
        """
        Check job status
        Weight: 3 (frequent polling)
        """
        job_id = f"job_{random.randint(1, 10000)}"
        start_time = time.time()
        
        with self.client.get(
            f"/api/v1/jobs/{job_id}",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/jobs/[id] (API)"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code in [200, 404]  # 404 is acceptable
            metrics.record_request(response_time, success, "api_get_status")
            
            if success:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class AdminUser(HttpUser):
    """
    Simulates admin operations.
    
    This user represents administrators and monitoring:
    - System dashboard viewing
    - User management
    - Health checks
    
    Wait time: 5-10 seconds (less frequent operations)
    """
    wait_time = between(5, 10)
    weight = 1  # Lowest weight (fewest users)
    
    def on_start(self):
        """Setup: Login as admin"""
        self.admin_token = "admin_token_placeholder"
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get admin authorization headers"""
        return {"Authorization": f"Bearer {self.admin_token}"}
    
    @task(3)
    def view_dashboard(self):
        """
        View admin dashboard
        Weight: 3 (most common admin operation)
        """
        start_time = time.time()
        
        with self.client.get(
            "/api/v1/admin/dashboard",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/admin/dashboard"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "view_dashboard")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def manage_users(self):
        """
        User management operations
        Weight: 1 (less frequent)
        """
        start_time = time.time()
        
        with self.client.get(
            "/api/v1/admin/users",
            headers=self.headers,
            params={"page": 1, "limit": 50},
            catch_response=True,
            name="/api/v1/admin/users"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "manage_users")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def system_health_check(self):
        """
        System health monitoring
        Weight: 2 (regular monitoring)
        """
        start_time = time.time()
        
        with self.client.get(
            "/api/v1/health",
            headers=self.headers,
            catch_response=True,
            name="/api/v1/health"
        ) as response:
            response_time = (time.time() - start_time) * 1000
            success = response.status_code == 200
            metrics.record_request(response_time, success, "system_health_check")
            
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


# Event handlers for metrics collection and reporting

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Initialize test and print start message"""
    print("\n" + "="*70)
    print("🚀 SampleMind AI Load Test Started")
    print("="*70)
    print(f"Target host: {environment.host}")
    print(f"User types: AudioAnalysisUser (50%), APIUser (30%), AdminUser (10%)")
    print("\nSuccess Criteria:")
    print("  ✓ Handle 1000 concurrent users")
    print("  ✓ p95 response time < 500ms")
    print("  ✓ Error rate < 0.1%")
    print("  ✓ No memory leaks")
    print("  ✓ CPU usage < 80%")
    print("="*70 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Print final metrics and success criteria evaluation"""
    print("\n" + "="*70)
    print("🏁 SampleMind AI Load Test Completed")
    print("="*70)
    
    error_rate = metrics.get_error_rate()
    p50 = metrics.get_percentile(50)
    p95 = metrics.get_percentile(95)
    p99 = metrics.get_percentile(99)
    
    print("\n📊 Performance Metrics:")
    print(f"  Total Requests: {metrics.total_requests:,}")
    print(f"  Failed Requests: {metrics.failed_requests:,}")
    print(f"  Error Rate: {error_rate:.3f}%")
    print(f"\n  Response Times:")
    print(f"    p50: {p50:.2f}ms")
    print(f"    p95: {p95:.2f}ms")
    print(f"    p99: {p99:.2f}ms")
    
    if metrics.errors_by_endpoint:
        print(f"\n  Errors by Endpoint:")
        for endpoint, count in sorted(metrics.errors_by_endpoint.items(), 
                                      key=lambda x: x[1], reverse=True):
            print(f"    {endpoint}: {count}")
    
    print("\n✅ Success Criteria Evaluation:")
    
    # Evaluate error rate
    error_rate_pass = error_rate < 0.1
    print(f"  {'✓' if error_rate_pass else '✗'} Error rate < 0.1%: "
          f"{error_rate:.3f}% {'PASS' if error_rate_pass else 'FAIL'}")
    
    # Evaluate p95 response time
    p95_pass = p95 < 500
    print(f"  {'✓' if p95_pass else '✗'} p95 response time < 500ms: "
          f"{p95:.2f}ms {'PASS' if p95_pass else 'FAIL'}")
    
    # Overall result
    all_pass = error_rate_pass and p95_pass
    print(f"\n{'🎉 ALL TESTS PASSED!' if all_pass else '⚠️  SOME TESTS FAILED'}")
    print("="*70 + "\n")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Final cleanup"""
    if isinstance(environment.runner, MasterRunner):
        print("\n🔄 Master runner shutting down...")


# Load test stage definitions for progressive load testing
# Can be used with custom Locust shape class if needed

class LoadTestStages:
    """
    Define load test stages for progressive testing:
    
    Stage 1: Baseline (100 users, 1 min)
    Stage 2: Normal Load (500 users, 5 min)
    Stage 3: Peak Load (1000 users, 10 min)
    Stage 4: Stress Test (2000 users, 5 min)
    """
    
    STAGES = [
        {"duration": 60, "users": 100, "spawn_rate": 10},   # Stage 1: Baseline
        {"duration": 300, "users": 500, "spawn_rate": 20},  # Stage 2: Normal
        {"duration": 600, "users": 1000, "spawn_rate": 50}, # Stage 3: Peak
        {"duration": 300, "users": 2000, "spawn_rate": 100} # Stage 4: Stress
    ]
    
    @classmethod
    def get_stage(cls, elapsed_time: float) -> Optional[Dict[str, Any]]:
        """Get the current stage based on elapsed time"""
        cumulative_time = 0
        for stage in cls.STAGES:
            cumulative_time += stage["duration"]
            if elapsed_time < cumulative_time:
                return stage
        return None
