#!/usr/bin/env python3
"""
Test Multiple Subscribers Receiving Real-time Messages
Demonstrates the pub/sub system with multiple subscribers
"""

import asyncio
import websockets
import json
import uuid
import time

async def subscriber(name, topic_name):
    """Simulate a subscriber"""
    uri = "ws://localhost:8000/ws/"
    
    print(f"🔌 {name}: Connecting to WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ {name}: Connected successfully!")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            connection_id = data.get('connection_id')
            print(f"🆔 {name}: Connection ID: {connection_id}")
            
            # Subscribe to topic
            subscribe_msg = {
                "type": "subscribe",
                "topic": topic_name,
                "client_id": name,
                "last_n": 0,
                "request_id": str(uuid.uuid4())
            }
            
            print(f"📝 {name}: Subscribing to topic '{topic_name}'")
            await websocket.send(json.dumps(subscribe_msg))
            
            response = await websocket.recv()
            data = json.loads(response)
            if data.get('type') == 'subscribed':
                print(f"✅ {name}: Successfully subscribed to '{topic_name}'")
            else:
                print(f"❌ {name}: Failed to subscribe")
                return
            
            # Listen for messages
            print(f"👂 {name}: Listening for messages on topic '{topic_name}'...")
            message_count = 0
            
            while True:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(response)
                    
                    if data.get('type') == 'message':
                        message_count += 1
                        print(f"📨 {name}: Received message #{message_count}")
                        print(f"   Topic: {data.get('topic')}")
                        print(f"   Message ID: {data.get('message', {}).get('id')}")
                        print(f"   Payload: {data.get('message', {}).get('payload')}")
                        print(f"   Publisher: {data.get('publisher_client_id')}")
                        print()
                    else:
                        print(f"📡 {name}: Received: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print(f"⏰ {name}: No messages received in 30 seconds, stopping...")
                    break
                    
    except Exception as e:
        print(f"❌ {name}: Error: {e}")

async def publisher(topic_name, num_messages=3):
    """Simulate a publisher"""
    uri = "ws://localhost:8000/ws/"
    
    print(f"🔌 Publisher: Connecting to WebSocket...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"✅ Publisher: Connected successfully!")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            data = json.loads(response)
            connection_id = data.get('connection_id')
            print(f"🆔 Publisher: Connection ID: {connection_id}")
            
            # Wait a bit for subscribers to connect
            print("⏳ Publisher: Waiting 3 seconds for subscribers to connect...")
            await asyncio.sleep(3)
            
            # Publish messages
            for i in range(num_messages):
                message_data = {
                    "type": "publish",
                    "topic": topic_name,
                    "client_id": "publisher",
                    "message": {
                        "id": f"msg-{i+1:03d}",
                        "payload": {
                            "content": f"Hello from publisher! Message #{i+1}",
                            "timestamp": time.time(),
                            "sequence": i + 1
                        }
                    },
                    "request_id": str(uuid.uuid4())
                }
                
                print(f"📤 Publisher: Publishing message #{i+1}")
                await websocket.send(json.dumps(message_data))
                
                response = await websocket.recv()
                data = json.loads(response)
                if data.get('type') == 'published':
                    print(f"✅ Publisher: Message #{i+1} published successfully")
                else:
                    print(f"❌ Publisher: Failed to publish message #{i+1}")
                
                # Wait between messages
                await asyncio.sleep(2)
            
            print("✅ Publisher: Finished publishing all messages")
            
    except Exception as e:
        print(f"❌ Publisher: Error: {e}")

async def main():
    """Main test function"""
    topic_name = "test-topic"
    
    print("🚀 Starting Multiple Subscribers Test")
    print("=" * 50)
    
    # Start subscribers
    subscriber_tasks = [
        subscriber("Alice", topic_name),
        subscriber("Bob", topic_name),
        subscriber("Charlie", topic_name)
    ]
    
    # Start publisher
    publisher_task = publisher(topic_name, num_messages=3)
    
    # Run all tasks concurrently
    all_tasks = subscriber_tasks + [publisher_task]
    await asyncio.gather(*all_tasks, return_exceptions=True)
    
    print("\n🎉 Test completed!")
    print("Check the logs above to see if all subscribers received the messages.")

if __name__ == "__main__":
    print("🔌 Make sure the WebSocket server is running on port 8000")
    print("📱 You can also test with the web interface:")
    print("   - Publisher: http://localhost:8000/api/publisher/")
    print("   - Subscriber: http://localhost:8000/api/subscriber/")
    print()
    
    asyncio.run(main())
