from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Topic, Connection, TopicSubscription, Message


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'created_at', 'last_published', 'message_count', 
        'subscriber_count', 'is_active', 'created_at_formatted'
    ]
    list_filter = ['is_active', 'created_at', 'last_published']
    search_fields = ['name']
    readonly_fields = ['created_at', 'message_count', 'subscriber_count']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active', 'metadata')
        }),
        ('Statistics', {
            'fields': ('created_at', 'last_published', 'message_count', 'subscriber_count'),
            'classes': ('collapse',)
        }),
    )
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
    created_at_formatted.short_description = 'Created'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'client_ip', 'user_agent_short', 'connected_at', 
        'last_activity', 'is_active', 'subscription_count'
    ]
    list_filter = ['is_active', 'connected_at', 'last_activity']
    search_fields = ['id', 'client_ip']
    readonly_fields = ['id', 'connected_at']
    ordering = ['-connected_at']
    
    fieldsets = (
        ('Connection Information', {
            'fields': ('id', 'client_ip', 'user_agent', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('connected_at', 'last_activity'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def user_agent_short(self, obj):
        if obj.user_agent:
            return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
        return '-'
    user_agent_short.short_description = 'User Agent'
    
    def subscription_count(self, obj):
        return obj.subscriptions.filter(is_active=True).count()
    subscription_count.short_description = 'Active Subscriptions'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subscriptions')


@admin.register(TopicSubscription)
class TopicSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'topic', 'connection', 'subscribed_at', 'is_active'
    ]
    list_filter = ['is_active', 'subscribed_at', 'topic__is_active']
    search_fields = ['topic__name', 'connection__id']
    readonly_fields = ['subscribed_at']
    ordering = ['-subscribed_at']
    
    fieldsets = (
        ('Subscription Details', {
            'fields': ('topic', 'connection', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('subscribed_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('topic', 'connection')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'topic', 'publisher_connection', 'data_short', 
        'published_at', 'delivery_attempts'
    ]
    list_filter = ['published_at', 'delivery_attempts', 'topic__is_active']
    search_fields = ['topic__name', 'data', 'publisher_connection__id']
    readonly_fields = ['id', 'published_at']
    ordering = ['-published_at']
    
    fieldsets = (
        ('Message Information', {
            'fields': ('id', 'topic', 'publisher_connection', 'data')
        }),
        ('Delivery Status', {
            'fields': ('delivery_attempts', 'max_delivery_attempts'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at',),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def data_short(self, obj):
        if obj.data:
            return obj.data[:100] + '...' if len(obj.data) > 100 else obj.data
        return '-'
    data_short.short_description = 'Message Data'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('topic', 'publisher_connection')





# Customize admin site
admin.site.site_header = "Pub/Sub System Administration"
admin.site.site_title = "Pub/Sub Admin"
admin.site.index_title = "Welcome to Pub/Sub System Administration"
