from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import time

from .models import Topic, Connection, TopicSubscription, Message
from .serializers import (
    TopicSerializer, TopicCreateSerializer, TopicDetailSerializer,
    TopicListResponseSerializer, TopicCreateResponseSerializer,
    TopicDeleteResponseSerializer
)

# Global variable to track system start time
SYSTEM_START_TIME = time.time()


class TopicPagination(PageNumberPagination):
    """Custom pagination for topics"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    try:
        # Get basic counts
        topics_count = Topic.objects.count()
        subscribers_count = TopicSubscription.objects.count()
        uptime_seconds = int(time.time() - SYSTEM_START_TIME)
        
        data = {
            "uptime_sec": uptime_seconds,
            "topics": topics_count,
            "subscribers": subscribers_count
        }
        
        return Response(data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Health check failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_stats(request):
    """Get system statistics"""
    try:
        # Get all topics with their stats
        topics = Topic.objects.all()
        
        stats_data = {
            "topics": {}
        }
        
        for topic in topics:
            # Get message count for this topic
            message_count = Message.objects.filter(topic=topic).count()
            
            # Get subscriber count for this topic
            subscriber_count = TopicSubscription.objects.filter(topic=topic).count()
            
            stats_data["topics"][topic.name] = {
                "messages": message_count,
                "subscribers": subscriber_count
            }
        
        return Response(stats_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get stats: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_topics(request):
    """List all topics"""
    try:
        # Get all topics (since we're now actually deleting them)
        topics = Topic.objects.all()
        
        # Prepare response in the exact format specified
        topics_data = []
        for topic in topics:
            # Get subscriber count for this topic
            subscriber_count = TopicSubscription.objects.filter(topic=topic).count()
            
            topics_data.append({
                "name": topic.name,
                "subscribers": subscriber_count
            })
        
        response_data = {
            "topics": topics_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to list topics: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def create_topic(request):
    """Create a new topic"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Get topic name from request data
        data = json.loads(request.body)
        topic_name = data.get('name', '').strip()
        metadata = data.get('metadata', {})
        
        # Validate topic name
        if not topic_name:
            return JsonResponse(
                {'error': 'Topic name cannot be empty'}, 
                status=400
            )
        
        # Check if topic already exists
        if Topic.objects.filter(name=topic_name).exists():
            return JsonResponse(
                {'error': 'Topic already exists'}, 
                status=409
            )
        
        # Create topic
        topic = Topic.objects.create(
            name=topic_name,
            metadata=metadata
        )
        
        # Prepare response in exact format specified
        response_data = {
            'status': 'created',
            'topic': topic_name
        }
        
        return JsonResponse(response_data, status=201)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to create topic: {str(e)}'}, 
            status=500
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_topic_detail(request, topic_name):
    """Get detailed information about a specific topic"""
    try:
        # Get topic
        try:
            topic = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return Response(
                {'error': 'Topic not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize topic
        serializer = TopicDetailSerializer(topic)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get topic details: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
def delete_topic(request, topic_name):
    """Delete a topic and unsubscribe all subscribers"""
    try:
        with transaction.atomic():
            # Get topic
            try:
                topic = Topic.objects.get(name=topic_name)
            except Topic.DoesNotExist:
                return Response(
                    {'error': 'Topic not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get all active subscriptions for this topic
            subscriptions = TopicSubscription.objects.filter(topic=topic)
            
            # Delete all subscriptions for this topic
            subscriptions.delete()
            
            # Delete all messages for this topic
            messages = Message.objects.filter(topic=topic)
            messages.delete()
            
            # Actually delete the topic from database
            topic.delete()
            
            # Send WebSocket notification to all subscribers
            try:
                from .consumers import PubSubConsumer
                # Use asyncio to run the async notification method
                import asyncio
                import threading
                
                def send_notification():
                    """Send notification in a new event loop"""
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(PubSubConsumer.notify_topic_deleted(topic_name))
                    finally:
                        loop.close()
                
                # Run notification in a separate thread
                notification_thread = threading.Thread(target=send_notification)
                notification_thread.start()
                
                print(f"Topic '{topic_name}' deleted. WebSocket notifications sent to subscribers.")
                
            except Exception as e:
                print(f"Failed to send topic deletion notifications: {e}")
            
            # Prepare response in exact format specified
            response_data = {
                'status': 'deleted',
                'topic': topic_name
            }
            
            return JsonResponse(response_data, status=200)
            
    except Exception as e:
        return JsonResponse(
            {'error': f'Failed to delete topic: {str(e)}'}, 
            status=500
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_topic_subscribers(request, topic_name):
    """Get list of subscribers for a specific topic"""
    try:
        # Get topic
        try:
            topic = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
            return Response(
                {'error': 'Topic not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get all subscriptions
        subscriptions = TopicSubscription.objects.filter(
            topic=topic
        ).select_related('connection')
        
        # Prepare response data
        subscribers_data = []
        for subscription in subscriptions:
            subscribers_data.append({
                'connection_id': str(subscription.connection.id),
                'subscribed_at': subscription.subscribed_at,
                'client_ip': subscription.connection.client_ip,
                'user_agent': subscription.connection.user_agent
            })
        
        return Response({
            'topic': topic_name,
            'subscribers_count': len(subscribers_data),
            'subscribers': subscribers_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get topic subscribers: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_topic_messages(request, topic_name):
    """Get recent messages for a specific topic"""
    try:
        # Get topic
        try:
            topic = Topic.objects.get(name=topic_name)
        except Topic.DoesNotExist:
                    return Response(
            {'error': 'Topic not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
        # Get query parameters
        limit = min(int(request.query_params.get('limit', 50)), 100)
        offset = int(request.query_params.get('offset', 0))
        
        # Get messages
        messages = Message.objects.filter(topic=topic).order_by('-published_at')[
            offset:offset + limit
        ]
        
        # Serialize messages
        serializer = MessageSerializer(messages, many=True)
        
        return Response({
            'topic': topic_name,
            'messages': serializer.data,
            'total_count': topic.message_count,
            'limit': limit,
            'offset': offset
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get topic messages: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def dashboard(request):
    """Dashboard view for the web interface"""
    return render(request, 'dashboard.html')


def websocket_test(request):
    """WebSocket test page view"""
    return render(request, 'websocket_test.html')


def publisher_view(request):
    """Publisher view for publishing messages to topics"""
    return render(request, 'websocket_test.html')


def subscriber_view(request):
    """Subscriber view for real-time message updates"""
    return render(request, 'subscriber_view.html')
