"""
Integration tests for authentication API endpoints
"""
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    async def test_register_user(self, api_client, sample_user_data):
        """Test user registration"""
        response = await api_client.post(
            "/api/v1/auth/register",
            json=sample_user_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    async def test_register_duplicate_user(self, api_client, sample_user_data):
        """Test registering duplicate user"""
        # First registration
        await api_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Second registration (should fail)
        response = await api_client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_register_invalid_email(self, api_client):
        """Test registration with invalid email"""
        invalid_data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "TestPassword123!"
        }
        
        response = await api_client.post("/api/v1/auth/register", json=invalid_data)
        
        assert response.status_code == 422
    
    async def test_login_success(self, api_client, sample_user_data):
        """Test successful login"""
        # Register first
        await api_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "username": sample_user_data["username"],
            "password": sample_user_data["password"]
        }
        response = await api_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_login_wrong_password(self, api_client, sample_user_data):
        """Test login with wrong password"""
        # Register first
        await api_client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with wrong password
        login_data = {
            "username": sample_user_data["username"],
            "password": "WrongPassword123!"
        }
        response = await api_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert response.status_code == 401
    
    async def test_get_current_user(self, api_client, authenticated_user):
        """Test getting current user info"""
        response = await api_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {authenticated_user['access_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["user"]["username"]
        assert data["email"] == authenticated_user["user"]["email"]
    
    async def test_get_current_user_unauthorized(self, api_client):
        """Test getting current user without token"""
        response = await api_client.get("/api/v1/auth/me")
        
        assert response.status_code == 401
    
    async def test_refresh_token(self, api_client, authenticated_user):
        """Test token refresh"""
        response = await api_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": authenticated_user["refresh_token"]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_change_password(self, api_client, authenticated_user, sample_user_data):
        """Test password change"""
        new_password = "NewSecurePassword456!"
        
        response = await api_client.post(
            "/api/v1/auth/change-password",
            json={
                "current_password": sample_user_data["password"],
                "new_password": new_password
            },
            headers={"Authorization": f"Bearer {authenticated_user['access_token']}"}
        )
        
        assert response.status_code == 200
        
        # Try logging in with new password
        login_data = {
            "username": sample_user_data["username"],
            "password": new_password
        }
        login_response = await api_client.post(
            "/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        assert login_response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
class TestHealthEndpoints:
    """Test health check endpoints"""
    
    async def test_health_check(self, api_client):
        """Test basic health check"""
        response = await api_client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_health_live(self, api_client):
        """Test liveness probe"""
        response = await api_client.get("/api/v1/health/live")
        
        assert response.status_code == 200
    
    async def test_health_ready(self, api_client):
        """Test readiness probe"""
        response = await api_client.get("/api/v1/health/ready")
        
        assert response.status_code == 200
