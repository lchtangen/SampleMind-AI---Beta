"""
Real-time Audio Streaming WebSocket Endpoints

WebSocket endpoints for live audio streaming and real-time analysis.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict
import json
import asyncio
from loguru import logger

from samplemind.core.streaming import StreamingAudioProcessor

router = APIRouter(prefix="/stream", tags=["Audio Streaming"])

# Global streaming processor
streaming_processor = StreamingAudioProcessor(
    chunk_size=1024,
    sample_rate=44100
)


# ============================================================================
# WebSocket Endpoints
# ============================================================================

@router.websocket("/audio/{stream_id}")
async def audio_stream_websocket(
    websocket: WebSocket,
    stream_id: str
):
    """
    WebSocket endpoint for real-time audio streaming

    Accepts audio data and streams back real-time analysis results.

    Protocol:
        Client -> Server: Binary audio data (float32 samples)
        Server -> Client: JSON analysis results

    Example client (JavaScript):
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/v1/stream/audio/session_123');

        // Send audio chunk
        ws.send(audioBuffer);  // Float32Array as ArrayBuffer

        // Receive analysis results
        ws.onmessage = (event) => {
            const analysis = JSON.parse(event.data);
            console.log('Tempo:', analysis.tempo);
            console.log('Energy:', analysis.energy);
        };
        ```

    Args:
        stream_id: Unique stream identifier
    """
    await websocket.accept()
    logger.info(f"WebSocket connected: {stream_id}")

    try:
        # Start streaming
        await streaming_processor.start_stream(stream_id, enable_analysis=True)

        # Send initial status
        await websocket.send_json({
            "type": "stream_started",
            "stream_id": stream_id,
            "message": "Real-time audio streaming active"
        })

        # Create analysis update task
        async def send_analysis_updates():
            """Periodically send analysis results"""
            while True:
                await asyncio.sleep(0.1)  # 10Hz update rate

                # Get latest analysis
                result = streaming_processor.get_latest_analysis(stream_id)

                if result:
                    # Send analysis update
                    await websocket.send_json({
                        "type": "analysis",
                        "timestamp": result.timestamp,
                        "tempo": result.tempo,
                        "pitch": result.pitch,
                        "energy": result.energy,
                        "rms": result.rms,
                        "spectral_centroid": result.spectral_centroid,
                        "spectral_rolloff": result.spectral_rolloff,
                        "zero_crossing_rate": result.zero_crossing_rate,
                        "onset_detected": result.onset_detected,
                    })

        # Start analysis update task
        update_task = asyncio.create_task(send_analysis_updates())

        try:
            # Main receive loop
            while True:
                # Receive audio data (binary)
                data = await websocket.receive_bytes()

                # Process audio
                samples_processed = await streaming_processor.process_audio(
                    stream_id,
                    data
                )

                # Optional: Send acknowledgment
                # await websocket.send_json({
                #     "type": "audio_received",
                #     "samples": samples_processed
                # })

        finally:
            # Cancel update task
            update_task.cancel()
            try:
                await update_task
            except asyncio.CancelledError:
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {stream_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass

    finally:
        # Stop stream
        await streaming_processor.stop_stream(stream_id)
        logger.info(f"Stream stopped: {stream_id}")


@router.websocket("/control/{stream_id}")
async def control_websocket(
    websocket: WebSocket,
    stream_id: str
):
    """
    WebSocket endpoint for stream control and monitoring

    Allows controlling stream parameters and receiving status updates.

    Commands:
        - {"command": "get_stats"} - Get stream statistics
        - {"command": "reset_analysis"} - Reset analyzer
        - {"command": "pause"} - Pause processing
        - {"command": "resume"} - Resume processing

    Example:
        ```javascript
        const ws = new WebSocket('ws://localhost:8000/api/v1/stream/control/session_123');

        // Request stats
        ws.send(JSON.stringify({ command: 'get_stats' }));

        // Receive response
        ws.onmessage = (event) => {
            const response = JSON.parse(event.data);
            console.log(response);
        };
        ```
    """
    await websocket.accept()
    logger.info(f"Control WebSocket connected: {stream_id}")

    try:
        while True:
            # Receive command
            data = await websocket.receive_text()
            command_data = json.loads(data)

            command = command_data.get("command")

            if command == "get_stats":
                # Get and send statistics
                stats = streaming_processor.get_stream_stats(stream_id)
                await websocket.send_json({
                    "type": "stats",
                    "stream_id": stream_id,
                    "stats": stats
                })

            elif command == "reset_analysis":
                # Reset analyzer
                if stream_id in streaming_processor.analyzers:
                    streaming_processor.analyzers[stream_id].reset()
                    await websocket.send_json({
                        "type": "command_result",
                        "command": "reset_analysis",
                        "status": "success"
                    })

            elif command == "list_streams":
                # List all active streams
                streams = streaming_processor.get_all_streams()
                await websocket.send_json({
                    "type": "streams_list",
                    "streams": streams
                })

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown command: {command}"
                })

    except WebSocketDisconnect:
        logger.info(f"Control WebSocket disconnected: {stream_id}")

    except Exception as e:
        logger.error(f"Control WebSocket error: {e}")


# ============================================================================
# HTTP Endpoints for Stream Management
# ============================================================================

@router.post("/start/{stream_id}")
async def start_stream(stream_id: str, sample_rate: int = 44100):
    """
    Start audio stream (HTTP endpoint)

    Alternative to WebSocket for manual stream management.

    Example:
        POST /api/v1/stream/start/session_123?sample_rate=44100
    """
    try:
        await streaming_processor.start_stream(
            stream_id,
            sample_rate=sample_rate,
            enable_analysis=True
        )

        return {
            "status": "success",
            "stream_id": stream_id,
            "message": "Stream started",
            "sample_rate": sample_rate
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop/{stream_id}")
async def stop_stream(stream_id: str):
    """
    Stop audio stream

    Example:
        POST /api/v1/stream/stop/session_123
    """
    try:
        await streaming_processor.stop_stream(stream_id)

        return {
            "status": "success",
            "stream_id": stream_id,
            "message": "Stream stopped"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{stream_id}")
async def get_stream_stats(stream_id: str):
    """
    Get stream statistics

    Returns current buffer status, analysis results, and performance metrics.

    Example:
        GET /api/v1/stream/stats/session_123
    """
    stats = streaming_processor.get_stream_stats(stream_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Stream not found")

    return {
        "stream_id": stream_id,
        "stats": stats
    }


@router.get("/list")
async def list_active_streams():
    """
    List all active streams

    Example:
        GET /api/v1/stream/list
    """
    streams = streaming_processor.get_all_streams()

    return {
        "active_streams": streams,
        "count": len(streams)
    }


@router.get("/health")
async def stream_health():
    """
    Check streaming service health

    Example:
        GET /api/v1/stream/health
    """
    streams = streaming_processor.get_all_streams()

    return {
        "status": "healthy",
        "active_streams": len(streams),
        "processor_active": True
    }
