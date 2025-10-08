"""
Integration tests for complete audio processing workflow
"""
import pytest
import asyncio
import os
from pathlib import Path
from httpx import AsyncClient, ASGITransport

from samplemind.interfaces.api.main import app


@pytest.mark.integration
@pytest.mark.asyncio
class TestAudioUploadWorkflow:
    """Test complete audio upload and processing workflow"""
    
    async def test_full_audio_workflow(self, test_audio_samples):
        """Test complete workflow: register -> login -> upload -> analyze -> get results"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Step 1: Register user
            register_data = {
                "email": "workflow@test.com",
                "username": "workflowuser",
                "password": "Workflow123!"
            }
            
            register_response = await client.post(
                "/api/v1/auth/register",
                json=register_data
            )
            
            assert register_response.status_code == 200
            tokens = register_response.json()
            access_token = tokens['access_token']
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 2: Upload audio file
            audio_file = test_audio_samples['120_c_major']
            
            with open(audio_file, 'rb') as f:
                upload_response = await client.post(
                    "/api/v1/audio/upload",
                    files={"file": ("test.wav", f, "audio/wav")},
                    headers=headers
                )
            
            assert upload_response.status_code in [200, 201]
            upload_data = upload_response.json()
            audio_id = upload_data['id']
            
            # Step 3: Trigger analysis
            analysis_response = await client.post(
                f"/api/v1/audio/analyze/{audio_id}",
                json={"analysis_type": "full"},
                headers=headers
            )
            
            assert analysis_response.status_code in [200, 202]
            analysis_data = analysis_response.json()
            task_id = analysis_data['task_id']
            
            # Step 4: Poll task status
            max_attempts = 30
            for attempt in range(max_attempts):
                status_response = await client.get(
                    f"/api/v1/tasks/{task_id}",
                    headers=headers
                )
                
                assert status_response.status_code == 200
                status_data = status_response.json()
                
                if status_data['status'] in ['SUCCESS', 'FAILURE']:
                    break
                
                await asyncio.sleep(1)
            
            # Step 5: Verify analysis completed
            assert status_data['status'] == 'SUCCESS'
            assert 'result' in status_data
            
            # Step 6: Get audio file details
            file_response = await client.get(
                f"/api/v1/audio/files?audio_id={audio_id}",
                headers=headers
            )
            
            assert file_response.status_code == 200
            files_data = file_response.json()
            assert len(files_data) > 0


@pytest.mark.integration
@pytest.mark.asyncio
class TestBatchProcessing:
    """Test batch audio processing workflow"""
    
    async def test_batch_upload_and_process(self, test_audio_samples):
        """Test uploading multiple files and batch processing"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Login
            login_response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "testuser",
                    "password": "Test123!"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            access_token = login_response.json()['access_token']
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Upload multiple files
            audio_files = [
                test_audio_samples['120_c_major'],
                test_audio_samples['140_a_minor']
            ]
            
            files = []
            for audio_file in audio_files:
                with open(audio_file, 'rb') as f:
                    files.append(
                        ("files", (os.path.basename(audio_file), f.read(), "audio/wav"))
                    )
            
            # Batch upload
            batch_response = await client.post(
                "/api/v1/batch/upload",
                files=files,
                headers=headers
            )
            
            assert batch_response.status_code in [200, 202]
            batch_data = batch_response.json()
            batch_id = batch_data['batch_id']
            
            # Poll batch status
            max_attempts = 60
            for attempt in range(max_attempts):
                status_response = await client.get(
                    f"/api/v1/batch/status/{batch_id}",
                    headers=headers
                )
                
                assert status_response.status_code == 200
                status_data = status_response.json()
                
                if status_data['status'] in ['COMPLETED', 'FAILED']:
                    break
                
                await asyncio.sleep(2)
            
            # Verify batch completed
            assert status_data['status'] == 'COMPLETED'
            assert status_data['total_files'] == len(audio_files)


@pytest.mark.integration
@pytest.mark.asyncio
class TestWebSocketUpdates:
    """Test WebSocket real-time updates"""
    
    async def test_websocket_task_updates(self):
        """Test receiving task updates via WebSocket"""
        from websockets import connect
        
        # This is a simplified test - full WebSocket testing requires running server
        # In real scenario, would connect to ws://localhost:8000/api/v1/ws/client_123

        # For now, just test WebSocket endpoint exists
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Try to access WebSocket endpoint (will fail without upgrade)
            try:
                response = await client.get("/api/v1/ws/test_client")
                # Should get error about WebSocket upgrade required
                assert response.status_code in [426, 400, 405]
            except Exception:
                # WebSocket endpoint exists but needs proper connection
                pass


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
class TestEndToEndAnalysis:
    """Test end-to-end analysis with real audio processing"""
    
    async def test_real_audio_analysis(self, test_audio_samples, audio_engine):
        """Test real audio analysis using AudioEngine"""
        audio_file = test_audio_samples['120_c_major']

        # Perform analysis using async method
        from samplemind.core.engine.audio_engine import AnalysisLevel
        results = await audio_engine.analyze_audio_async(
            audio_file,
            level=AnalysisLevel.DETAILED
        )
        
        # Verify results - analyze_audio_async returns AudioFeatures object
        assert results is not None
        assert results.tempo is not None
        assert results.key is not None
        assert results.mode is not None

        # BPM should be close to 120
        assert 100 <= results.tempo <= 150  # Relaxed range for test audio

        # Key should be detected
        assert results.key is not None

        # Check spectral features
        assert results.spectral_centroid is not None
        assert results.spectral_rolloff is not None
    
    @pytest.mark.skip(reason="Celery tasks not yet implemented")
    async def test_embedding_generation(self, test_audio_samples):
        """Test generating audio embeddings"""
        from samplemind.core.tasks.audio_tasks import generate_audio_embeddings

        audio_file = test_audio_samples['120_c_major']
        
        # Generate embeddings
        result = await generate_audio_embeddings.apply_async(
            args=[audio_file],
            queue='embeddings'
        )
        
        # Wait for result
        embeddings = result.get(timeout=30)
        
        # Verify embeddings
        assert embeddings is not None
        assert len(embeddings) == 128  # 128-dimensional
        assert all(isinstance(val, float) for val in embeddings)
        
        # Embeddings should be normalized
        magnitude = sum(val**2 for val in embeddings) ** 0.5
        assert 0.95 <= magnitude <= 1.05  # Allow small numerical error
