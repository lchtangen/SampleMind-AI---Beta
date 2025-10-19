"""
Audio endpoint tests
"""

import pytest
from io import BytesIO


def test_list_audio_empty(client, auth_headers):
    """Test listing audio with no files"""
    response = client.get("/api/v1/audio", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_audio_with_files(client, auth_headers, test_audio):
    """Test listing audio with files"""
    response = client.get("/api/v1/audio", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] == 1
    assert data["items"][0]["filename"] == "test.mp3"


def test_list_audio_pagination(client, auth_headers, test_audio):
    """Test audio list pagination"""
    response = client.get(
        "/api/v1/audio?page=1&page_size=10",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "page" in data
    assert "page_size" in data


def test_list_audio_unauthorized(client):
    """Test listing audio without authentication"""
    response = client.get("/api/v1/audio")
    assert response.status_code in [401, 403]


def test_get_audio_by_id(client, auth_headers, test_audio):
    """Test getting specific audio file"""
    response = client.get(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_audio.id
    assert data["filename"] == "test.mp3"
    assert data["format"] == "mp3"


def test_get_nonexistent_audio(client, auth_headers):
    """Test getting non-existent audio"""
    response = client.get("/api/v1/audio/999", headers=auth_headers)
    assert response.status_code == 404


def test_upload_audio_mock(client, auth_headers):
    """Test audio upload (mocked)"""
    # Create fake audio file
    audio_data = BytesIO(b"fake audio content")
    audio_data.name = "test.mp3"
    
    response = client.post(
        "/api/v1/audio/upload",
        headers=auth_headers,
        files={"file": ("test.mp3", audio_data, "audio/mpeg")},
    )
    
    # Should return 201 or appropriate status
    assert response.status_code in [200, 201]


def test_upload_audio_unauthorized(client):
    """Test upload without authentication"""
    audio_data = BytesIO(b"fake audio content")
    
    response = client.post(
        "/api/v1/audio/upload",
        files={"file": ("test.mp3", audio_data, "audio/mpeg")},
    )
    assert response.status_code in [401, 403]


def test_analyze_audio(client, auth_headers, test_audio):
    """Test audio analysis"""
    response = client.post(
        "/api/v1/audio/analyze",
        headers=auth_headers,
        json={
            "audio_id": test_audio.id,
            "analysis_type": "full",
            "extract_features": True,
            "ai_analysis": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "audio_id" in data
    assert data["audio_id"] == test_audio.id


def test_analyze_nonexistent_audio(client, auth_headers):
    """Test analyzing non-existent audio"""
    response = client.post(
        "/api/v1/audio/analyze",
        headers=auth_headers,
        json={
            "audio_id": 999,
            "analysis_type": "full",
        },
    )
    assert response.status_code == 404


def test_delete_audio(client, auth_headers, test_audio):
    """Test deleting audio file"""
    response = client.delete(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(
        f"/api/v1/audio/{test_audio.id}",
        headers=auth_headers
    )
    assert get_response.status_code == 404


def test_delete_nonexistent_audio(client, auth_headers):
    """Test deleting non-existent audio"""
    response = client.delete("/api/v1/audio/999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_audio_unauthorized(client, test_audio):
    """Test deleting without authentication"""
    response = client.delete(f"/api/v1/audio/{test_audio.id}")
    assert response.status_code in [401, 403]
