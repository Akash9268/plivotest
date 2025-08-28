from django.urls import path
from . import views

app_name = 'pubsub'

urlpatterns = [
    # Web interface
    path('', views.dashboard, name='dashboard'),
    path('publisher/', views.publisher_view, name='publisher_view'),
    path('subscriber/', views.subscriber_view, name='subscriber_view'),
    
    # Health and monitoring endpoints
    path('health/', views.health_check, name='health_check'),
    path('stats/', views.get_stats, name='get_stats'),
    
    # Topic management endpoints
    path('topics/', views.list_topics, name='list_topics'),
    path('topics/create/', views.create_topic, name='create_topic'),
    path('topics/<str:topic_name>/', views.get_topic_detail, name='get_topic_detail'),
    path('topics/<str:topic_name>/delete/', views.delete_topic, name='delete_topic'),
    path('topics/<str:topic_name>/subscribers/', views.get_topic_subscribers, name='get_topic_subscribers'),
    path('topics/<str:topic_name>/messages/', views.get_topic_messages, name='get_topic_messages'),
]
