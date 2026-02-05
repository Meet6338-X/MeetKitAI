# Microservices Architecture Template

> Distributed system with multiple services and API gateway.

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# - API Gateway: http://localhost:8080
# - Auth Service: http://localhost:8001
# - User Service: http://localhost:8002
```

## Structure

```
microservices/
├── services/
│   ├── gateway/           # API Gateway (Kong/Traefik)
│   │   ├── app/
│   │   └── Dockerfile
│   ├── auth-service/      # Authentication
│   │   ├── app/
│   │   ├── tests/
│   │   └── Dockerfile
│   ├── user-service/      # User management
│   │   ├── app/
│   │   ├── tests/
│   │   └── Dockerfile
│   └── notification-service/  # Notifications
│       ├── app/
│       ├── tests/
│       └── Dockerfile
├── shared/
│   ├── common/            # Shared utilities
│   └── proto/             # gRPC definitions
├── infrastructure/
│   ├── kubernetes/        # K8s manifests
│   ├── terraform/         # IaC
│   └── monitoring/        # Prometheus/Grafana
├── docker-compose.yml
├── docker-compose.dev.yml
└── README.md
```

## Architecture

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │   (Port 8080)   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Auth Service  │   │ User Service  │   │ Notification  │
│  (Port 8001)  │   │  (Port 8002)  │   │  (Port 8003)  │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   Redis       │   │  PostgreSQL   │   │   RabbitMQ    │
└───────────────┘   └───────────────┘   └───────────────┘
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8080 | API routing, rate limiting |
| Auth | 8001 | JWT, OAuth2 |
| User | 8002 | User CRUD, profiles |
| Notification | 8003 | Email, SMS, push |

## Technologies

- **Gateway**: FastAPI / Kong
- **Services**: FastAPI + SQLAlchemy
- **Database**: PostgreSQL
- **Cache**: Redis
- **Queue**: RabbitMQ
- **Monitoring**: Prometheus + Grafana
