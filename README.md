# 🚀 Pub/Sub System

A real-time, in-memory Pub/Sub system built with Django, Django Channels, and WebSockets. Features include topic management, real-time message publishing/subscribing, and a comprehensive web dashboard.

## ✨ Features

- **🔌 Real-time WebSocket Communication** - Instant message delivery
- **📱 Dedicated Publisher & Subscriber Views** - Clean interfaces for different use cases
- **🎯 Topic Management** - Create, delete, and monitor topics
- **📊 Live Statistics** - Real-time system monitoring
- **🐳 Docker Support** - Easy deployment and development
- **🌐 Web Dashboard** - User-friendly management interface

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
```

## 🚀 Quick Start

### Prerequisites

- Docker
- Docker Compose

### 1. Clone and Setup

```bash
git clone <your-repo>
cd plivo-test
```

### 2. Start the System

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web
```

### 3. Access the System

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
python test_multiple_subscribers.py
```

#### Demo Script (Opens Browser Windows)
```bash
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

# Rebuild containers
docker-compose down
docker-compose build --no-cache
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
├── pubsub_project/            # Django project settings
│   ├── settings.py            # Django configuration
│   ├── urls.py                # Main URL routing
│   └── asgi.py                # ASGI configuration for WebSockets
├── pubsub/                    # Main application
│   ├── models.py              # Database models
│   ├── views.py               # HTTP API views
│   ├── consumers.py           # WebSocket consumers
│   ├── urls.py                # App URL routing
│   └── routing.py             # WebSocket URL routing
├── templates/                  # HTML templates
│   ├── base.html              # Base template
│   ├── dashboard.html         # Main dashboard
│   ├── websocket_test.html    # Publisher view
│   └── subscriber_view.html   # Subscriber view
└── test_*.py                  # Test scripts
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
- **Database**: SQLite (in-memory for development)

## 🚨 Troubleshooting

### Common Issues

#### WebSocket Connection Failed
- Ensure the web service is running: `docker-compose ps`
- Check logs: `docker-compose logs web`
- Verify port 8000 is accessible

#### Topic Creation Fails
- Check if CSRF exemption is working
- Verify the web service was restarted after code changes
- Check server logs for specific error messages

#### Messages Not Broadcasting
- Ensure subscribers are connected to the same topic
- Check WebSocket connection status
- Verify the topic exists and is active

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
```

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
4. Open an issue with detailed error information

---

**Happy Publishing and Subscribing! 🎉**
