# 🚀 Pub/Sub System

A real-time, in-memory Pub/Sub system built with Django, Django Channels, and WebSockets. Features include topic management, real-time message publishing/subscribing, and a comprehensive web dashboard.

## ✨ Features

- **🔌 Real-time WebSocket Communication** - Instant message delivery
- **📱 Dedicated Publisher & Subscriber Views** - Clean interfaces for different use cases
- **🎯 Topic Management** - Create, delete, and monitor topics
- **📊 Live Statistics** - Real-time system monitoring
- **🐳 Docker Support** - Easy deployment and development
- **🌐 Web Dashboard** - User-friendly management interface
- **🔴 Redis Support** - Scalable channel layer (though currently using in-memory)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Dashboard     │    │   Publisher     │    │   Subscriber    │
│                 │    │                 │    │                 │
│ • Topic Mgmt    │    │ • WebSocket     │    │ • WebSocket     │
│ • System Health │    │ • Publish Msgs  │    │ • Subscribe     │
│ • Statistics    │    │ • Templates     │    │ • Real-time     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  WebSocket      │
                    │  Server (/ws)   │
                    │                 │
                    │ • Real-time     │
                    │ • Broadcasting  │
                    │ • Pub/Sub       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Optional)    │
                    │                 │
                    │ • Channel Layer │
                    │ • Scalability   │
                    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)

**Verify Installation:**
```bash
docker --version
docker-compose --version
```

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd plivo-test

# Verify files are present
ls -la
```

**Expected files:**
- `docker-compose.yml`
- `Dockerfile`
- `requirements.txt`
- `manage.py`
- `pubsub_project/` directory
- `pubsub/` directory
- `templates/` directory

### 2. Start the System

```bash
# Start all services (automatically builds image if needed)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

**Note**: The first time you run `docker-compose up -d`, it will automatically build the Docker image. Subsequent runs will use the existing image, making startup much faster.

**Expected output:**
```
[+] Running 2/2
 ✔ Container plivo-test-redis-1  Started
 ✔ Container plivo-test-web-1    Started
```

### 3. Verify System is Running

```bash
# Check if containers are running
docker-compose ps

# Check if web service is responding
curl http://localhost:8000/api/health/
```

### 4. Access the System

- **Main Dashboard**: http://localhost:8000/api/
- **Publisher View**: http://localhost:8000/api/publisher/
- **Subscriber View**: http://localhost:8000/api/subscriber/

## 📡 API Endpoints

### Health & Monitoring

#### GET /api/health/
**Health check endpoint**
```bash
curl http://localhost:8000/api/health/
```

**Response:**
```json
{
  "uptime_sec": 123,
  "topics": 2,
  "subscribers": 4
}
```

#### GET /api/stats/
**System statistics**
```bash
curl http://localhost:8000/api/stats/
```

**Response:**
```json
{
  "topics": {
    "orders": {
      "messages": 42,
      "subscribers": 3
    },
    "notifications": {
      "messages": 15,
      "subscribers": 1
    }
  }
}
```

### Topic Management

#### GET /api/topics/
**List all topics**
```bash
curl http://localhost:8000/api/topics/
```

**Response:**
```json
{
  "topics": [
    {
      "name": "orders",
      "subscribers": 3,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### POST /api/topics/create/
**Create a new topic**
```bash
curl -X POST http://localhost:8000/api/topics/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-topic",
    "metadata": {
      "description": "Topic description"
    }
  }'
```

**Response:**
```json
{
  "status": "created",
  "topic": "new-topic"
}
```

#### DELETE /api/topics/{name}/
**Delete a topic**
```bash
curl -X DELETE http://localhost:8000/api/topics/orders/
```

**Response:**
```json
{
  "status": "deleted",
  "topic": "orders"
}
```

#### GET /api/topics/{name}/
**Get topic details**
```bash
curl http://localhost:8000/api/topics/orders/
```

#### GET /api/topics/{name}/subscribers/
**Get topic subscribers**
```bash
curl http://localhost:8000/api/topics/orders/subscribers/
```

#### GET /api/topics/{name}/messages/
**Get topic messages**
```bash
curl "http://localhost:8000/api/topics/orders/messages/?limit=10&offset=0"
```

## 🔌 WebSocket Endpoints

### WebSocket Connection
**Connect to WebSocket server**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/');
```

### Message Types

#### Subscribe to Topic
```json
{
  "type": "subscribe",
  "topic": "orders",
  "client_id": "subscriber1",
  "last_n": 5,
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### Unsubscribe from Topic
```json
{
  "type": "unsubscribe",
  "topic": "orders",
  "client_id": "subscriber1",
  "request_id": "340e8400-e29b-41d4-a716-4466554480098"
}
```

#### Publish Message
```json
{
  "type": "publish",
  "topic": "orders",
  "client_id": "publisher1",
  "message": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "payload": {
      "order_id": "ORD-123",
      "amount": "99.50",
      "currency": "USD"
    }
  },
  "request_id": "340e8400-e29b-41d4-a716-4466554480098"
}
```

#### Ping
```json
{
  "type": "ping",
  "request_id": "570t8400-e29b-41d4-a716-4466554412345"
}
```

## 🌐 Web Dashboard

### Main Dashboard
**URL**: http://localhost:8000/api/

**Features:**
- System overview with live statistics
- Topic management (create, delete, list)
- System health monitoring
- Quick access to Publisher and Subscriber views

### Publisher View
**URL**: http://localhost:8000/api/publisher/

**Features:**
- WebSocket connection management
- Message publishing to topics
- Pre-built message templates
- Publishing statistics
- Real-time activity logs

### Subscriber View
**URL**: http://localhost:8000/api/subscriber/

**Features:**
- WebSocket connection management
- Topic subscription management
- Real-time message reception
- Live statistics and connection monitoring
- Message history

## 🧪 Testing

### Python Test Scripts

#### Test Multiple Subscribers
```bash
# Make sure the system is running first
docker-compose up -d

# Run the test script
python test_multiple_subscribers.py
```

#### Demo Script (Opens Browser Windows)
```bash
# Make sure the system is running first
docker-compose up -d

# Run the demo script
python demo_pub_sub.py
```

### Manual Testing with curl

#### Create a Topic
```bash
curl -X POST http://localhost:8000/api/topics/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "test-topic", "metadata": {"description": "Test topic"}}'
```

#### Check Health
```bash
curl http://localhost:8000/api/health/
```

#### Get Stats
```bash
curl http://localhost:8000/api/stats/
```

### WebSocket Testing

#### Test WebSocket Connection
```bash
# Install websocat for command-line WebSocket testing
# On macOS: brew install websocat
# On Ubuntu: sudo apt install websocat

# Test connection
websocat ws://localhost:8000/ws/
```

## 🐳 Docker Commands

### Basic Operations
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart web service (after code changes)
docker-compose restart web

# View logs
docker-compose logs -f web

# View all logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### Development Workflow
```bash
# After making code changes
docker-compose restart web

# If you need to rebuild the image (after major changes)
docker-compose up -d --build

# View real-time logs
docker-compose logs -f web

# Access container shell
docker-compose exec web bash

# Run Django commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Troubleshooting
```bash
# Clean restart (removes containers and data)
docker-compose down --remove-orphans
docker-compose up -d

# Force rebuild image (after major changes or issues)
docker-compose down
docker-compose up -d --build

# Complete rebuild (removes all images and containers)
docker-compose down --rmi all --volumes --remove-orphans
docker-compose up -d

# Check container resources
docker stats
```

## 📁 Project Structure

```
plivo-test/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Web service container definition
├── requirements.txt            # Python dependencies
├── manage.py                   # Django management script
├── pubsub_project/            # Django project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   ├── wsgi.py                # WSGI configuration
│   └── asgi.py                # ASGI configuration for WebSockets
├── pubsub/                    # Main application
│   ├── models.py              # Database models
│   ├── views.py               # HTTP API views
│   ├── consumers.py           # WebSocket consumers
│   ├── urls.py                # App URL routing
│   ├── routing.py             # WebSocket URL routing
│   └── serializers.py         # Data serializers
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── dashboard.html         # Main dashboard
│   ├── websocket_test.html    # Publisher view
│   └── subscriber_view.html   # Subscriber view
├── test_*.py                  # Test scripts
├── demo_pub_sub.py            # Demo script
└── db.sqlite3                 # SQLite database (auto-created)
```

## 🔧 Configuration

### Environment Variables
The system uses default Django settings. For production, consider setting:

```bash
# In docker-compose.yml or .env file
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com
```

### Port Configuration
- **HTTP/WebSocket**: 8000 (configurable in docker-compose.yml)
- **Redis**: 6379 (optional, for production scaling)
- **Database**: SQLite (in-memory for development)

### Channel Layer Configuration
Currently using in-memory channel layer for development:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}
```

For production, consider Redis:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}
```

## 🚨 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
- Ensure the web service is running: `docker-compose ps`
- Check logs: `docker-compose logs web`
- Verify port 8000 is accessible
- Check if Redis is running: `docker-compose logs redis`

#### Topic Creation Fails
- Check if CSRF exemption is working
- Verify the web service was restarted after code changes
- Check server logs for specific error messages
- Ensure the database is accessible

#### Messages Not Broadcasting
- Ensure subscribers are connected to the same topic
- Check WebSocket connection status
- Verify the topic exists and is active
- Check channel layer configuration

#### Docker Issues
- **Port already in use**: Change port in docker-compose.yml
- **Permission denied**: Run with `sudo` or add user to docker group
- **Image build fails**: Check Dockerfile and requirements.txt

### Debug Commands
```bash
# Check service status
docker-compose ps

# View real-time logs
docker-compose logs -f web

# Access container
docker-compose exec web bash

# Check Django logs
docker-compose exec web python manage.py shell

# Check Redis
docker-compose exec redis redis-cli ping
```

### System Requirements
- **Minimum**: 2GB RAM, 1 CPU
- **Recommended**: 4GB RAM, 2 CPU
- **Storage**: 1GB free space

## 📚 API Reference

### Response Formats

#### Success Response
```json
{
  "status": "success",
  "data": {...}
}
```

#### Error Response
```json
{
  "error": "Error description"
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error

### WebSocket Status Codes
- `1000` - Normal closure
- `1001` - Going away
- `1002` - Protocol error
- `1006` - Abnormal closure

## 🔒 Security Considerations

### Development vs Production
- **Development**: CSRF exemptions for API endpoints
- **Production**: Enable CSRF protection, use HTTPS
- **Authentication**: Currently none, add for production
- **Rate Limiting**: Consider implementing for production

### Environment Variables
```bash
# Production settings
DEBUG=False
SECRET_KEY=your-very-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## 🚀 Production Deployment

### Recommended Setup
1. **Use PostgreSQL** instead of SQLite
2. **Enable Redis** for channel layers
3. **Use Gunicorn** with Daphne
4. **Set up Nginx** as reverse proxy
5. **Enable HTTPS** with SSL certificates
6. **Set up monitoring** and logging

### Docker Production
```bash
# Build production image
docker build -t pubsub-system:prod .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  -e DEBUG=0 \
  -e SECRET_KEY=your-secret \
  pubsub-system:prod
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review server logs: `docker-compose logs web`
3. Test with the provided curl examples
4. Check Docker status: `docker-compose ps`
5. Open an issue with detailed error information

### Getting Help
- **Docker issues**: Check `docker-compose logs`
- **WebSocket issues**: Check browser console and server logs
- **API issues**: Test with curl examples
- **Performance issues**: Check `docker stats`

---

**Happy Publishing and Subscribing! 🎉**
