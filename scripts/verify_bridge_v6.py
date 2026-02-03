import asyncio
import json

import websockets


async def test_daw_client():
    uri = "ws://127.0.0.1:8010/ws"
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to DAW Bridge")

            # Receive handshake
            handshake = await websocket.recv()
            print(f"📥 Received: {handshake}")

            # Send Sync BPM
            msg = {
                "action": "sync_bpm",
                "payload": {"bpm": 128.5}
            }
            await websocket.send(json.dumps(msg))
            print(f"wb Sent: {msg}")

            # Send Load Sample
            msg2 = {
                "action": "load_sample",
                "payload": {"path": "/kick_hard.wav"}
            }
            await websocket.send(json.dumps(msg2))
            print(f"wb Sent: {msg2}")

            # Keep open for a bit
            await asyncio.sleep(1)
            print("✅ Test Complete")

    except ConnectionRefusedError:
        print("❌ Connection refused. Is the server running?")

if __name__ == "__main__":
    asyncio.run(test_daw_client())
