from rest_framework import serializers
from .models import Topic, Connection, TopicSubscription, Message


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model"""
    class Meta:
        model = Topic
        fields = [
            'name', 'created_at', 'last_published', 
            'message_count', 'subscriber_count', 'is_active', 'metadata'
        ]
        read_only_fields = [
            'created_at', 'last_published', 'message_count', 
            'subscriber_count', 'is_active'
        ]


class TopicCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating topics"""
    class Meta:
        model = Topic
        fields = ['name', 'metadata']
    
    def validate_name(self, value):
        """Validate topic name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Topic name cannot be empty")
        
        return value.strip()


class TopicDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Topic with subscription info"""
    subscriptions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Topic
        fields = [
            'name', 'created_at', 'last_published', 'message_count', 
            'subscriber_count', 'is_active', 'metadata', 'subscriptions_count'
        ]
    
    def get_subscriptions_count(self, obj):
        """Get count of active subscriptions"""
        return obj.subscriptions.filter(is_active=True).count()


class ConnectionSerializer(serializers.ModelSerializer):
    """Serializer for Connection model"""
    class Meta:
        model = Connection
        fields = [
            'id', 'client_ip', 'user_agent', 'connected_at', 
            'last_activity', 'is_active', 'metadata'
        ]
        read_only_fields = ['id', 'connected_at']


class TopicSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for TopicSubscription model"""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    connection_id = serializers.UUIDField(source='connection.id', read_only=True)
    
    class Meta:
        model = TopicSubscription
        fields = [
            'topic_name', 'connection_id', 'subscribed_at', 'is_active'
        ]
        read_only_fields = ['subscribed_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    publisher_id = serializers.UUIDField(source='publisher_connection.id', read_only=True)
    
    class Meta:
        model = Message
        fields = [
            'id', 'topic_name', 'publisher_id', 'data', 'published_at', 
            'delivery_attempts', 'max_delivery_attempts', 'metadata'
        ]
        read_only_fields = ['id', 'published_at', 'delivery_attempts']


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    class Meta:
        model = Message
        fields = ['data', 'metadata']
    
    def validate_data(self, value):
        """Validate message data"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message data cannot be empty")
        return value.strip()


class TopicListResponseSerializer(serializers.Serializer):
    """Serializer for topic list response"""
    topics = TopicSerializer(many=True)
    total_count = serializers.IntegerField()
    page = serializers.IntegerField()
    page_size = serializers.IntegerField()


class TopicCreateResponseSerializer(serializers.Serializer):
    """Serializer for topic creation response"""
    status = serializers.CharField()
    topic = serializers.CharField()


class TopicDeleteResponseSerializer(serializers.Serializer):
    """Serializer for topic deletion response"""
    status = serializers.CharField()
    topic = serializers.CharField()
    deleted_at = serializers.DateTimeField()
