import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Topic, Connection, TopicSubscription, Message


class PubSubConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Pub/Sub operations.
    Handles subscribe, unsubscribe, publish, and ping messages.
    """
    
    # Class variable to store all active connections by topic
    _topic_connections = {}  # {topic_name: set(connection_instances)}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_id = None
        self.client_id = None
        self.subscribed_topics = set()
        self.connection = None

    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()
        
        # Generate unique connection ID
        self.connection_id = str(uuid.uuid4())
        
        # Create connection record in database
        await self.create_connection_record()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            "type": "connected",
            "connection_id": self.connection_id,
            "status": "success",
            "timestamp": timezone.now().isoformat()
        }))
        
        print(f"WebSocket connected: {self.connection_id}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.connection_id:
            # Remove this connection from all topic connections
            for topic_name in list(self.subscribed_topics):
                if topic_name in self._topic_connections:
                    self._topic_connections[topic_name].discard(self)
                    if not self._topic_connections[topic_name]:
                        del self._topic_connections[topic_name]
            
            await self.cleanup_connection()
            print(f"WebSocket disconnected: {self.connection_id}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            request_id = data.get('request_id')
            
            # Validate request_id format (should be UUID)
            if not request_id or not self.is_valid_uuid(request_id):
                await self.send_error("Invalid or missing request_id", None)
                return
            
            if message_type == 'subscribe':
                await self.handle_subscribe(data, request_id)
            elif message_type == 'unsubscribe':
                await self.handle_unsubscribe(data, request_id)
            elif message_type == 'publish':
                await self.handle_publish(data, request_id)
            elif message_type == 'ping':
                await self.handle_ping(data, request_id)
            else:
                await self.send_error(f"Unknown message type: {message_type}", request_id)
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format", None)
        except Exception as e:
            await self.send_error(f"Internal error: {str(e)}", None)

    def is_valid_uuid(self, uuid_string):
        """Validate UUID format"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False

    async def handle_subscribe(self, data, request_id):
        """Handle subscribe message"""
        try:
            topic_name = data.get('topic')
            client_id = data.get('client_id')
            last_n = data.get('last_n', 0)
            
            # Validate required fields
            if not topic_name:
                await self.send_error("Missing topic name", request_id)
                return
            
            if not client_id:
                await self.send_error("Missing client_id", request_id)
                return
            
            # Store client_id for this connection
            self.client_id = client_id
            
            # Get or create topic
            topic = await self.get_or_create_topic(topic_name)
            if not topic:
                await self.send_error(f"Failed to get/create topic: {topic_name}", request_id)
                return
            
            # Subscribe to topic
            success = await self.subscribe_to_topic(topic, client_id)
            if not success:
                await self.send_error(f"Failed to subscribe to topic: {topic_name}", request_id)
                return
            
            # Add to local subscribed topics set
            self.subscribed_topics.add(topic_name)
            
            # Add this connection to the topic's active connections for real-time messaging
            if topic_name not in self._topic_connections:
                self._topic_connections[topic_name] = set()
            self._topic_connections[topic_name].add(self)
            
            # Send subscription confirmation
            await self.send(text_data=json.dumps({
                "type": "subscribed",
                "topic": topic_name,
                "client_id": client_id,
                "request_id": request_id,
                "status": "success",
                "timestamp": timezone.now().isoformat()
            }))
            
            # Send last N messages if requested
            if last_n > 0:
                await self.send_last_n_messages_async(topic, last_n, request_id)
                
        except Exception as e:
            await self.send_error(f"Subscribe error: {str(e)}", request_id)

    async def handle_unsubscribe(self, data, request_id):
        """Handle unsubscribe message"""
        try:
            topic_name = data.get('topic')
            client_id = data.get('client_id')
            
            # Validate required fields
            if not topic_name:
                await self.send_error("Missing topic name", request_id)
                return
            
            if not client_id:
                await self.send_error("Missing client_id", request_id)
                return
            
            # Unsubscribe from topic
            success = await self.unsubscribe_from_topic(topic_name, client_id)
            if not success:
                await self.send_error(f"Failed to unsubscribe from topic: {topic_name}", request_id)
                return
            
            # Remove from local subscribed topics set
            self.subscribed_topics.discard(topic_name)
            
            # Remove this connection from the topic's active connections
            if topic_name in self._topic_connections:
                self._topic_connections[topic_name].discard(self)
                # Clean up empty topic sets
                if not self._topic_connections[topic_name]:
                    del self._topic_connections[topic_name]
            
            # Send unsubscription confirmation
            await self.send(text_data=json.dumps({
                "type": "unsubscribed",
                "topic": topic_name,
                "client_id": client_id,
                "request_id": request_id,
                "status": "success",
                "timestamp": timezone.now().isoformat()
            }))
            
        except Exception as e:
            await self.send_error(f"Unsubscribe error: {str(e)}", request_id)

    async def handle_publish(self, data, request_id):
        """Handle publish message"""
        try:
            topic_name = data.get('topic')
            message_data = data.get('message', {})
            client_id = data.get('client_id')  # Extract client_id from top level
            
            # Validate required fields
            if not topic_name:
                await self.send_error("Missing topic name", request_id)
                return
            
            if not message_data:
                await self.send_error("Missing message data", request_id)
                return
            
            if not client_id:
                await self.send_error("Missing client_id", request_id)
                return
            
            # Get topic
            topic = await self.get_topic(topic_name)
            if not topic:
                await self.send_error(f"Topic not found: {topic_name}", request_id)
                return
            
            # Publish message
            message_id = await self.publish_message(topic, message_data, client_id)
            if not message_id:
                await self.send_error(f"Failed to publish message to topic: {topic_name}", request_id)
                return
            
            # Send publish confirmation
            await self.send(text_data=json.dumps({
                "type": "published",
                "topic": topic_name,
                "message_id": message_id,
                "client_id": client_id,
                "request_id": request_id,
                "status": "success",
                "timestamp": timezone.now().isoformat()
            }))
            
            # Broadcast message to all subscribers
            await self.broadcast_message(topic_name, message_data, message_id, client_id)
            
        except Exception as e:
            await self.send_error(f"Publish error: {str(e)}", request_id)

    async def handle_ping(self, data, request_id):
        """Handle ping message"""
        try:
            # Update connection activity
            await self.update_connection_activity()
            
            # Send pong response
            await self.send(text_data=json.dumps({
                "type": "pong",
                "request_id": request_id,
                "timestamp": timezone.now().isoformat()
            }))
            
        except Exception as e:
            await self.send_error(f"Ping error: {str(e)}", request_id)

    @classmethod
    async def notify_topic_deleted(cls, topic_name):
        """Notify all subscribers that a topic has been deleted"""
        try:
            if topic_name in cls._topic_connections:
                notification_data = {
                    "type": "info",
                    "topic": topic_name,
                    "msg": "topic_deleted",
                    "ts": timezone.now().isoformat()
                }
                
                # Get all connections for this topic
                connections = cls._topic_connections[topic_name].copy()
                
                # Send notification to all subscribers
                for connection in connections:
                    try:
                        await connection.send(text_data=json.dumps(notification_data))
                        print(f"Topic deletion notification sent to {connection.connection_id}")
                    except Exception as e:
                        print(f"Failed to send topic deletion notification to {connection.connection_id}: {e}")
                        # Remove failed connection
                        connections.discard(connection)
                
                # Remove the topic from connections (it's deleted)
                del cls._topic_connections[topic_name]
                
                print(f"Topic deletion notifications sent to {len(connections)} subscribers")
                
        except Exception as e:
            print(f"Error notifying topic deletion: {e}")

    async def send_error(self, error_message, request_id):
        """Send error response to client"""
        error_data = {
            "type": "error",
            "error": error_message,
            "timestamp": timezone.now().isoformat()
        }
        
        if request_id:
            error_data["request_id"] = request_id
            
        await self.send(text_data=json.dumps(error_data))

    # Database operations (using database_sync_to_async)
    
    @database_sync_to_async
    def create_connection_record(self):
        """Create connection record in database"""
        try:
            # Get client IP from scope
            client_ip = self.scope.get('client', [''])[0] if self.scope.get('client') else None
            
            # Get user agent from headers
            headers = dict(self.scope.get('headers', []))
            user_agent = headers.get(b'user-agent', b'').decode('utf-8', errors='ignore')
            
            self.connection = Connection.objects.create(
                id=self.connection_id,
                client_ip=client_ip,
                user_agent=user_agent
            )
            return True
        except Exception as e:
            print(f"Error creating connection record: {e}")
            return False

    @database_sync_to_async
    def cleanup_connection(self):
        """Clean up connection and subscriptions"""
        try:
            if self.connection:
                # Remove all subscriptions for this connection
                TopicSubscription.objects.filter(connection=self.connection).delete()
                # Delete the connection
                self.connection.delete()
            return True
        except Exception as e:
            print(f"Error cleaning up connection: {e}")
            return False

    @database_sync_to_async
    def get_or_create_topic(self, topic_name):
        """Get existing topic or create new one"""
        try:
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={'metadata': {}}
            )
            return topic
        except Exception as e:
            print(f"Error getting/creating topic: {e}")
            return None

    @database_sync_to_async
    def get_topic(self, topic_name):
        """Get topic by name"""
        try:
            return Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return None
        except Exception as e:
            print(f"Error getting topic: {e}")
            return None

    @database_sync_to_async
    def subscribe_to_topic(self, topic, client_id):
        """Subscribe connection to topic"""
        try:
            # Check if subscription already exists
            subscription, created = TopicSubscription.objects.get_or_create(
                connection=self.connection,
                topic=topic,
                defaults={'is_active': True}
            )
            
            if not created:
                # Update existing subscription to active
                subscription.is_active = True
                subscription.save()
            
            # Update topic subscriber count CORRECTLY
            active_count = topic.subscriptions.filter(is_active=True).count()
            topic.update_subscriber_count(active_count)
            
            # Update connection activity
            self.connection.update_activity()
            
            return True
        except Exception as e:
            print(f"Error subscribing to topic: {e}")
            return False

    @database_sync_to_async
    def unsubscribe_from_topic(self, topic_name, client_id):
        """Unsubscribe connection from topic"""
        try:
            topic = Topic.objects.get(name=topic_name)
            subscription = TopicSubscription.objects.get(
                connection=self.connection,
                topic=topic
            )
            
            # Mark subscription as inactive
            subscription.is_active = False
            subscription.save()
            
            # Update topic subscriber count CORRECTLY
            active_count = topic.subscriptions.filter(is_active=True).count()
            topic.update_subscriber_count(active_count)
            
            # Update connection activity
            self.connection.update_activity()
            
            return True
        except (Topic.DoesNotExist, TopicSubscription.DoesNotExist):
            return False
        except Exception as e:
            print(f"Error unsubscribing from topic: {e}")
            return False

    @database_sync_to_async
    def publish_message(self, topic, message_data, client_id):
        """Publish message to topic"""
        try:
            # Create message record
            message = Message.objects.create(
                topic=topic,
                publisher_connection=self.connection,
                data=json.dumps(message_data),
                metadata={'client_id': client_id}
            )
            
            # Update topic message count and timestamp
            topic.increment_message_count()
            topic.update_last_published()
            
            # Update connection activity
            self.connection.update_activity()
            
            return str(message.id)
        except Exception as e:
            print(f"Error publishing message: {e}")
            return None

    @database_sync_to_async
    def send_last_n_messages(self, topic, last_n, request_id):
        """Send last N messages to client"""
        try:
            messages = Message.objects.filter(topic=topic).order_by('-published_at')[:last_n]
            
            for message in messages:
                message_data = {
                    "type": "message",
                    "topic": topic.name,
                    "message": {
                        "id": str(message.id),
                        "payload": json.loads(message.data),
                        "timestamp": message.published_at.isoformat()
                    },
                    "request_id": request_id
                }
                
                # Send message to this client - FIXED: use await self.send
                # Note: This method is called from database_sync_to_async, so we need to handle this differently
                # We'll return the message data and send it from the calling method
                yield message_data
                
        except Exception as e:
            print(f"Error sending last N messages: {e}")

    async def send_last_n_messages_async(self, topic, last_n, request_id):
        """Async wrapper to send last N messages"""
        try:
            # Get messages from database
            messages_data = await self.get_last_n_messages(topic, last_n)
            
            # Send each message
            for message_data in messages_data:
                await self.send(text_data=json.dumps(message_data))
                
        except Exception as e:
            print(f"Error sending last N messages: {e}")

    @database_sync_to_async
    def get_last_n_messages(self, topic, last_n):
        """Get last N messages for a topic"""
        try:
            messages = Message.objects.filter(topic=topic).order_by('-published_at')[:last_n]
            
            messages_data = []
            for message in messages:
                message_data = {
                    "type": "message",
                    "topic": topic.name,
                    "message": {
                        "id": str(message.id),
                        "payload": json.loads(message.data),
                        "timestamp": message.published_at.isoformat()
                    }
                }
                messages_data.append(message_data)
            
            return messages_data
                
        except Exception as e:
            print(f"Error getting last N messages: {e}")
            return []

    @database_sync_to_async
    def update_connection_activity(self):
        """Update connection last activity timestamp"""
        try:
            if self.connection:
                self.connection.update_activity()
            return True
        except Exception as e:
            print(f"Error updating connection activity: {e}")
            return False

    async def broadcast_message(self, topic_name, message_data, message_id, publisher_client_id):
        """Broadcast message to all subscribers of the topic"""
        try:
            # Create broadcast message
            broadcast_data = {
                "type": "message",
                "topic": topic_name,
                "message": {
                    "id": message_id,
                    "payload": message_data.get('payload', {}),
                    "timestamp": timezone.now().isoformat()
                },
                "publisher_client_id": publisher_client_id
            }
            
            # Send to all active connections subscribed to this topic
            if topic_name in self._topic_connections:
                active_connections = self._topic_connections[topic_name].copy()
                print(f"Broadcasting message {message_id} to topic {topic_name}")
                print(f"Message data: {broadcast_data}")
                print(f"Active connections: {len(active_connections)}")
                
                # Send message to all subscribers (except the publisher)
                for connection in active_connections:
                    if connection != self:  # Don't send back to publisher
                        try:
                            await connection.send(text_data=json.dumps(broadcast_data))
                            print(f"Message sent to connection: {connection.connection_id}")
                        except Exception as e:
                            print(f"Failed to send message to connection {connection.connection_id}: {e}")
                            # Remove failed connection
                            self._topic_connections[topic_name].discard(connection)
            else:
                print(f"No active connections for topic: {topic_name}")
            
        except Exception as e:
            print(f"Error broadcasting message: {e}")

    @database_sync_to_async
    def get_topic_subscriptions(self, topic_name):
        """Get all active subscriptions for a topic"""
        try:
            topic = Topic.objects.get(name=topic_name)
            return list(TopicSubscription.objects.filter(
                topic=topic,
                is_active=True
            ).select_related('connection'))
        except Topic.DoesNotExist:
            return []
        except Exception as e:
            print(f"Error getting topic subscriptions: {e}")
            return []