"""
🏥 Health Module - System Health Checks

Provides health check endpoints for:
- Kubernetes liveness/readiness probes
- Load balancer health checks
- Docker health checks
- Monitoring systems

Endpoints:
- /health/         - Basic health status
- /health/ready/   - Readiness probe (DB, Redis, etc.)
- /health/live/    - Liveness probe (app running)
"""
