# Dockerized Flask Web Application

A complete containerized Flask web application with Docker Compose, multi-stage builds, health checks, and CI/CD pipeline.

## Features

### Required Features ✅
- **Multi-stage Dockerfile** with dependency caching and non-root user
- **Docker Compose** setup with app and Redis services
- **Dev vs Prod configurations** with environment-specific overrides
- **Health checks** with container health monitoring and restart policies

### Bonus Features ✅
- **CI/CD Pipeline** with GitHub Actions for automated builds
- **Image scanning** with Trivy vulnerability scanning
- **Multi-architecture builds** supporting AMD64 and ARM64

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git (for CI/CD features)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd 12-dockerize-a-web-app
   ```

2. **Start development environment**
   ```bash
   docker compose up --build
   ```

3. **Access the application**
   - Web app: http://localhost:5000
   - Health check: http://localhost:5000/health
   - API data: http://localhost:5000/api/data
   - Hit counter: http://localhost:5000/api/hits

### Production Setup

1. **Start production environment**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
   ```

2. **Scale the application**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d --scale web=3
   ```

## Project Structure

```
.
├── .dockerignore        # Build context exclusions
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Multi-stage production Dockerfile
├── docker-compose.yml    # Base compose configuration
├── docker-compose.override.yml  # Development overrides
├── docker-compose.prod.yml      # Production configuration
├── env.base              # Base environment variables
├── env.dev               # Development environment variables
├── env.prod              # Production environment variables
├── docker-bake.hcl       # Advanced build configuration
├── build.sh              # Multi-architecture build script
├── .github/workflows/ci.yml  # CI/CD pipeline
├── CHECKLIST.md          # Progress tracker
├── SPEC.md               # Project requirements
└── README.md
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development` or `production` (defaults to production)
- `FLASK_DEBUG`: Enables the Flask reloader when set to `1` (used in dev overrides)
- `PORT`: Container port for the Flask application (default: 5000)
- `REDIS_HOST` / `REDIS_PORT`: Location of the Redis service (defaults to `redis:6379`)
- `REDIS_URL`: Optional full Redis connection string that overrides host/port

### Development Configuration

The `docker-compose.override.yml` enables:
- Hot reloading of code changes
- Development environment variables
- Debug mode for Flask

### Production Configuration

The `docker-compose.prod.yml` provides:
- Production environment variables
- Service scaling with replicas
- Optimized restart policies

## Docker Features

### Multi-stage Dockerfile
- **Base stage**: Installs dependencies for caching
- **Production stage**: Creates slim runtime image
- **Non-root user**: Enhanced security
- **Health checks**: Built-in health monitoring

### Health Checks
- Application health endpoint: `/health` returns degraded when Redis is unavailable
- Image health check script uses `curl` to mark the container unhealthy on failures
- Redis service monitored separately with `redis-cli ping`

### Multi-architecture Support
- Supports AMD64 and ARM64 architectures
- Automated builds for both platforms
- Compatible with Apple Silicon and traditional servers

## CI/CD Pipeline

### GitHub Actions Workflow
- **Automated testing**: Python syntax and import checks
- **Multi-platform builds**: AMD64 and ARM64
- **Vulnerability scanning**: Trivy security scanning
- **Image caching**: Layer caching for faster builds
- **Automated publishing**: Push to GitHub Container Registry

### Security Scanning
- **Trivy integration**: Scans for vulnerabilities
- **SARIF output**: Detailed security reports
- **Fail on high severity**: Blocks deployment on critical issues

## Development Workflow

### Local Development
```bash
# Start with live reloading
docker compose up

# View logs
docker compose logs -f web

# Run tests
docker compose exec web python -c "import app"

# Stop services
docker compose down
```

### Multi-architecture Builds
```bash
# Build for specific tag
./build.sh v1.0.0

# Build for multiple platforms
./build.sh latest linux/amd64,linux/arm64
```

### Production Deployment
```bash
# Deploy with production config
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Update application
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## API Endpoints

- `GET /` - Welcome message with timestamp
- `GET /health` - Health check endpoint
- `GET /api/data` - Sample API endpoint
- `GET /api/hits` - Redis-backed counter that increments on each request

## Monitoring

### Health Checks
- Application responds to `/health` endpoint and includes Redis status
- Docker health checks run every 30 seconds and fail fast on HTTP errors
- Restart policy restarts containers that exit unexpectedly

### Logs
```bash
# View all logs
docker compose logs

# Follow logs
docker compose logs -f

# View specific service logs
docker compose logs web
```

## Security

- **Non-root user**: Application runs as non-privileged user
- **Minimal base image**: Slim Debian-based Python image
- **Vulnerability scanning**: Automated security checks
- **Dependency updates**: Regular security updates via CI/CD

## Troubleshooting

### Common Issues

1. **Port conflicts**: Change ports in docker-compose.yml
2. **Build failures**: Clear Docker cache with `docker system prune`
3. **Permission issues**: Ensure proper file permissions

### Debug Commands
```bash
# Check container status
docker compose ps

# View container logs
docker compose logs web

# Enter container
docker compose exec web bash

# Check health status
curl http://localhost:5000/health
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `docker compose up`
5. Submit a pull request

## License

This project is licensed under the MIT License.
