#!/usr/bin/env python3
"""
WebSocket Pub/Sub Test Script
Tests subscribe, unsubscribe, and publish operations
"""

import asyncio
import websockets
import json
import uuid
import time

async def test_websocket():
    """Test WebSocket Pub/Sub operations"""
    
    # WebSocket URL - using port 8000 for unified server
    uri = "ws://localhost:8000/ws/"
    
    print("🔌 Connecting to WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📡 Connection response: {json.dumps(data, indent=2)}")
            
            if data.get('type') != 'connected':
                print("❌ Expected 'connected' message type")
                return
            
            connection_id = data.get('connection_id')
            print(f"🆔 Connection ID: {connection_id}")
            
            # Test 1: Subscribe to a topic
            print("\n📝 Test 1: Subscribe to topic 'test-topic'")
            subscribe_msg = {
                "type": "subscribe",
                "topic": "test-topic",
                "client_id": "test-client-1",
                "last_n": 0,
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📤 Sending: {json.dumps(subscribe_msg, indent=2)}")
            await websocket.send(json.dumps(subscribe_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {json.dumps(data, indent=2)}")
            
            if data.get('type') == 'subscribed':
                print("✅ Subscribe successful!")
            else:
                print("❌ Subscribe failed!")
                return
            
            # Test 2: Publish a message
            print("\n📤 Test 2: Publish message to 'test-topic'")
            publish_msg = {
                "type": "publish",
                "topic": "test-topic",
                "client_id": "test-client-1",
                "message": {
                    "id": "msg-001",
                    "payload": {
                        "content": "Hello from Python test client!",
                        "timestamp": time.time(),
                        "test": True
                    }
                },
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📤 Sending: {json.dumps(publish_msg, indent=2)}")
            await websocket.send(json.dumps(publish_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {json.dumps(data, indent=2)}")
            
            if data.get('type') == 'published':
                print("✅ Publish successful!")
                message_id = data.get('message_id')
                print(f"🆔 Message ID: {message_id}")
            else:
                print("❌ Publish failed!")
                return
            
            # Test 3: Subscribe with last_n messages
            print("\n📝 Test 3: Subscribe to 'test-topic' with last 5 messages")
            subscribe_msg2 = {
                "type": "subscribe",
                "topic": "test-topic",
                "client_id": "test-client-2",
                "last_n": 5,
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📤 Sending: {json.dumps(subscribe_msg2, indent=2)}")
            await websocket.send(json.dumps(subscribe_msg2))
            
            # We should receive subscribe confirmation and then last N messages
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {json.dumps(data, indent=2)}")
            
            if data.get('type') == 'subscribed':
                print("✅ Subscribe successful!")
                
                # Check if we receive the last N messages
                try:
                    # Wait a bit for messages
                    await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    response = await websocket.recv()
                    data = json.loads(response)
                    print(f"📥 Last N message: {json.dumps(data, indent=2)}")
                except asyncio.TimeoutError:
                    print("⏰ No last N messages received (timeout)")
            else:
                print("❌ Subscribe failed!")
                return
            
            # Test 4: Ping
            print("\n🏓 Test 4: Send ping")
            ping_msg = {
                "type": "ping",
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📤 Sending: {json.dumps(ping_msg, indent=2)}")
            await websocket.send(json.dumps(ping_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {json.dumps(data, indent=2)}")
            
            if data.get('type') == 'pong':
                print("✅ Pong received!")
            else:
                print("❌ Pong not received!")
                return
            
            # Test 5: Unsubscribe
            print("\n📝 Test 5: Unsubscribe from 'test-topic'")
            unsubscribe_msg = {
                "type": "unsubscribe",
                "topic": "test-topic",
                "client_id": "test-client-1",
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📤 Sending: {json.dumps(unsubscribe_msg, indent=2)}")
            await websocket.send(json.dumps(unsubscribe_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received: {json.dumps(data, indent=2)}")
            
            if data.get('type') == 'unsubscribed':
                print("✅ Unsubscribe successful!")
            else:
                print("❌ Unsubscribe failed!")
                return
            
            print("\n🎉 All tests completed successfully!")
            
    except websockets.exceptions.ConnectionRefused:
        print("❌ Connection refused. Make sure the WebSocket server is running on port 8002.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting WebSocket Pub/Sub Tests...")
    asyncio.run(test_websocket())
