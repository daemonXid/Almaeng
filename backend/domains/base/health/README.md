# 🏥 DAEMON Module: Health (`base.health`)

> System Monitoring and Health Probes.

## 🎯 Purpose

Provide Kubernetes-compatible health endpoints to monitor app, database, and cache status.

## ✨ Key Features

- **Liveness Probe**: `/health/live/` (Process status).
- **Readiness Probe**: `/health/ready/` (DB + Redis connectivity).
- **Status Dashboard**: `/health/` (Visual overview).

## 🏗️ Portability

Highly portable. Drop into any Django project to add standard health checks.

## 📝 Usage

Configure your load balancer or orchestrator to point to:

- `http://localhost:2020/health/ready/`
