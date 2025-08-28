from django.db import models
from django.utils import timezone
import uuid


class Topic(models.Model):
    """
    Model representing a topic in the Pub/Sub system.
    Topics act as message channels that publishers can send to
    and subscribers can listen to.
    """
    name = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_published = models.DateTimeField(null=True, blank=True)
    message_count = models.PositiveIntegerField(default=0)
    subscriber_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'pubsub_topics'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Topic: {self.name}"
    
    def update_last_published(self):
        """Update the last published timestamp"""
        self.last_published = timezone.now()
        self.save(update_fields=['last_published'])
    
    def increment_message_count(self):
        """Increment the message count"""
        self.message_count += 1
        self.save(update_fields=['message_count'])
    
    def update_subscriber_count(self, count):
        """Update the subscriber count"""
        self.subscriber_count = count
        self.save(update_fields=['subscriber_count'])


class Connection(models.Model):
    """
    Model representing a WebSocket connection.
    This tracks active connections and their subscriptions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    connected_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'pubsub_connections'
        ordering = ['-connected_at']
    
    def __str__(self):
        return f"Connection: {self.id}"
    
    def update_activity(self):
        """Update the last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def deactivate(self):
        """Mark connection as inactive"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class TopicSubscription(models.Model):
    """
    Model representing a subscription relationship between
    a connection and a topic.
    """
    connection = models.ForeignKey(
        Connection, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        related_name='subscriptions'
    )
    subscribed_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'pubsub_topic_subscriptions'
        unique_together = ['connection', 'topic']
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.connection.id} -> {self.topic.name}"


class Message(models.Model):
    """
    Model representing a message published to a topic.
    This stores message history for auditing and debugging.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(
        Topic, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    publisher_connection = models.ForeignKey(
        Connection, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='published_messages'
    )
    data = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)
    delivery_attempts = models.PositiveIntegerField(default=0)
    max_delivery_attempts = models.PositiveIntegerField(default=3)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'pubsub_messages'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['topic', 'published_at']),
            models.Index(fields=['publisher_connection', 'published_at']),
        ]
    
    def __str__(self):
        return f"Message {self.id} on {self.topic.name}"
    
    def increment_delivery_attempts(self):
        """Increment delivery attempts"""
        self.delivery_attempts += 1
        self.save(update_fields=['delivery_attempts'])



