"""
Integration tests for complete user flows
"""

import pytest
from io import BytesIO


def test_complete_registration_flow(client):
    """Test complete user registration and login flow"""
    # Register
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "integration@example.com",
            "password": "testpass123",
            "full_name": "Integration Test"
        }
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["email"] == "integration@example.com"
    
    # Login with new user
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "integration@example.com",
            "password": "testpass123"
        }
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # Use access token
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "integration@example.com"


def test_upload_and_list_flow(client, auth_headers):
    """Test upload file and list it"""
    # Upload file
    audio_data = BytesIO(b"fake audio content")
    upload_response = client.post(
        "/api/v1/audio/upload",
        headers=auth_headers,
        files={"file": ("test.mp3", audio_data, "audio/mpeg")}
    )
    assert upload_response.status_code in [200, 201]
    
    # List files
    list_response = client.get("/api/v1/audio", headers=auth_headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert "items" in data
    assert "total" in data


def test_complete_audio_workflow(client, auth_headers, test_audio):
    """Test complete audio workflow: get, analyze, delete"""
    # Get audio details
    get_response = client.get(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    audio_data = get_response.json()
    assert audio_data["id"] == test_audio.id
    
    # Analyze audio
    analyze_response = client.post(
        "/api/v1/audio/analyze",
        headers=auth_headers,
        json={
            "audio_id": test_audio.id,
            "analysis_type": "full",
            "extract_features": True,
            "ai_analysis": True
        }
    )
    assert analyze_response.status_code == 200
    analysis_data = analyze_response.json()
    assert analysis_data["audio_id"] == test_audio.id
    assert "features" in analysis_data
    
    # Delete audio
    delete_response = client.delete(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204
    
    # Verify deleted
    get_after_delete = client.get(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert get_after_delete.status_code == 404


def test_token_refresh_flow(client, test_user):
    """Test token refresh workflow"""
    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    # Use access token
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    
    # Refresh token
    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    
    # Use new access token
    new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    me_response_2 = client.get("/api/v1/auth/me", headers=new_headers)
    assert me_response_2.status_code == 200


def test_unauthorized_access_flow(client):
    """Test that unauthorized requests are properly blocked"""
    # Try to access protected endpoint without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code in [401, 403]
    
    # Try to upload without token
    audio_data = BytesIO(b"fake audio content")
    upload_response = client.post(
        "/api/v1/audio/upload",
        files={"file": ("test.mp3", audio_data, "audio/mpeg")}
    )
    assert upload_response.status_code in [401, 403]
    
    # Try to list audio without token
    list_response = client.get("/api/v1/audio")
    assert list_response.status_code in [401, 403]


def test_pagination_flow(client, auth_headers, test_audio):
    """Test pagination in list endpoints"""
    # Get first page
    page1_response = client.get(
        "/api/v1/audio?page=1&page_size=1",
        headers=auth_headers
    )
    assert page1_response.status_code == 200
    page1_data = page1_response.json()
    assert "items" in page1_data
    assert "total" in page1_data
    assert "page" in page1_data
    assert "pages" in page1_data
    assert page1_data["page"] == 1
    assert len(page1_data["items"]) <= 1
