# ScrapeCraft Deployment Guide

## Overview

This guide covers deploying the ScrapeCraft OSINT platform to production environments using Kubernetes, Docker, and various cloud providers. The platform is designed as a cloud-native microservices architecture with comprehensive monitoring and scaling capabilities.

## Architecture Overview

### Production Stack
- **Container Orchestration**: Kubernetes 1.28+
- **Container Runtime**: Docker 24.0+
- **Ingress Controller**: NGINX Ingress Controller
- **Load Balancer**: Cloud Provider LB (AWS ELB, GCP Load Balancer, etc.)
- **Database**: PostgreSQL 15+ with read replicas
- **Cache**: Redis 7+ with cluster mode
- **Monitoring**: Prometheus + Grafana + AlertManager
- **Logging**: ELK Stack (Elasticsearch + Logstash + Kibana)
- **Secrets Management**: Kubernetes Secrets + External Secret Operator
- **CI/CD**: GitHub Actions + ArgoCD

## Prerequisites

### Infrastructure Requirements

#### Minimum Production Setup
- **Kubernetes Cluster**: 3 nodes (1 control plane, 2 workers)
- **Node Specifications**: 
  - Control Plane: 4 CPU, 8GB RAM, 100GB SSD
  - Workers: 8 CPU, 16GB RAM, 200GB SSD each
- **Database**: Managed PostgreSQL service (AWS RDS, GCP Cloud SQL)
- **Redis**: Managed Redis service (AWS ElastiCache, GCP Memorystore)

#### Recommended Production Setup
- **Kubernetes Cluster**: 5+ nodes (3 control plane, 5+ workers)
- **Node Specifications**:
  - Control Plane: 8 CPU, 16GB RAM, 200GB SSD
  - Workers: 16 CPU, 32GB RAM, 500GB SSD each
- **High Availability Database**: PostgreSQL with read replicas
- **Redis Cluster**: Multi-AZ Redis cluster

### Tool Requirements
- **kubectl**: 1.28+
- **helm**: 3.14+
- **docker**: 24.0+
- **git**: 2.40+
- **AWS CLI/GCP CLI**: Latest version

## Environment Configuration

### 1. Kubernetes Namespace Setup

```bash
# Create production namespace
kubectl create namespace scrapecraft-prod

# Set default namespace
kubectl config set-context --current --namespace=scrapecraft-prod
```

### 2. Secrets Configuration

#### Application Secrets
```bash
# Create secrets for application
kubectl create secret generic scrapecraft-secrets \
  --from-literal=database-url="postgresql://user:pass@postgres:5432/scrapecraft" \
  --from-literal=redis-url="redis://redis:6379/0" \
  --from-literal=jwt-secret="your-jwt-secret-key" \
  --from-literal=openai-api-key="your-openai-key" \
  --from-literal=openrouter-api-key="your-openrouter-key"
```

#### Docker Registry Secrets
```bash
# Create docker registry secret
kubectl create secret docker-registry docker-registry-secret \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  --docker-email=your-email@example.com
```

### 3. ConfigMaps Configuration

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scrapecraft-config
  namespace: scrapecraft-prod
data:
  NODE_ENV: "production"
  LOG_LEVEL: "INFO"
  API_VERSION: "v1"
  CORS_ORIGINS: "https://app.scrapecraft.com"
  MAX_WORKERS: "4"
  UPLOAD_LIMIT: "10485760"
  RATE_LIMIT_WINDOW: "900000"
  RATE_LIMIT_MAX: "100"
```

Apply the config:
```bash
kubectl apply -f configmap.yaml
```

## Database Setup

### 1. PostgreSQL Configuration

#### Using Managed Service (Recommended)
```bash
# AWS RDS Example
aws rds create-db-instance \
  --db-instance-identifier scrapecraft-prod \
  --db-instance-class db.m5.large \
  --engine postgres \
  --engine-version 15.4 \
  --master-username scrapecraft \
  --master-user-password your-secure-password \
  --allocated-storage 100 \
  --storage-type gp2 \
  --vpc-security-group-ids sg-xxxxxxxxx \
  --db-subnet-group-name default \
  --backup-retention-period 7 \
  --multi-az \
  --storage-encrypted
```

#### Database Initialization
```bash
# Connect to database and create schema
psql -h your-db-host -U scrapecraft -d postgres

CREATE DATABASE scrapecraft;
CREATE USER scrapecraft_app WITH PASSWORD 'app-password';
GRANT ALL PRIVILEGES ON DATABASE scrapecraft TO scrapecraft_app;

# Run migrations
cd backend
DATABASE_URL="postgresql://scrapecraft_app:app-password@your-db-host:5432/scrapecraft" \
alembic upgrade head
```

### 2. Redis Configuration

#### Using Managed Service
```bash
# AWS ElastiCache Example
aws elasticache create-cache-cluster \
  --cache-cluster-id scrapecraft-redis \
  --cache-node-type cache.m5.large \
  --engine redis \
  --num-cache-nodes 1 \
  --security-group-ids sg-xxxxxxxxx \
  --subnet-group-name default \
  --automatic-failover-enabled \
  --multi-az-enabled
```

## Application Deployment

### 1. Build and Push Docker Images

#### Backend Image
```bash
cd backend

# Build production image
docker build -f Dockerfile.production -t scrapecraft/backend:v1.0.0 .

# Tag and push to registry
docker tag scrapecraft/backend:v1.0.0 your-registry.com/scrapecraft/backend:v1.0.0
docker push your-registry.com/scrapecraft/backend:v1.0.0
```

#### Frontend Image
```bash
cd frontend

# Build production image
docker build -t scrapecraft/frontend:v1.0.0 .

# Tag and push to registry
docker tag scrapecraft/frontend:v1.0.0 your-registry.com/scrapecraft/frontend:v1.0.0
docker push your-registry.com/scrapecraft/frontend:v1.0.0
```

### 2. Deploy with Helm

#### Install Helm Chart
```bash
# Add Helm repository (if using)
helm repo add scrapecraft https://charts.scrapecraft.com
helm repo update

# Deploy application
helm install scrapecraft-prod scrapecraft/scrapecraft \
  --namespace scrapecraft-prod \
  --values helm/values-prod.yaml \
  --set image.tag=v1.0.0 \
  --set ingress.host=scrapecraft.com \
  --set database.host=your-db-host \
  --set redis.host=your-redis-host
```

#### Production Values Configuration
```yaml
# helm/values-prod.yaml
image:
  repository: your-registry.com/scrapecraft
  tag: v1.0.0
  pullPolicy: IfNotPresent

replicaCount:
  backend: 3
  frontend: 2
  worker: 2

resources:
  backend:
    limits:
      cpu: 1000m
      memory: 2Gi
    requests:
      cpu: 500m
      memory: 1Gi
  frontend:
    limits:
      cpu: 500m
      memory: 1Gi
    requests:
      cpu: 250m
      memory: 512Mi
  worker:
    limits:
      cpu: 2000m
      memory: 4Gi
    requests:
      cpu: 1000m
      memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
  hosts:
    - host: scrapecraft.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: scrapecraft-tls
      hosts:
        - scrapecraft.com

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

### 3. Verify Deployment

```bash
# Check pod status
kubectl get pods -l app=scrapecraft

# Check services
kubectl get services

# Check ingress
kubectl get ingress

# View logs
kubectl logs -l app=scrapecraft-backend --tail=100

# Port forward for testing
kubectl port-forward service/scrapecraft-backend 8000:8000
```

## Monitoring and Observability

### 1. Prometheus Monitoring

#### Service Monitor Configuration
```yaml
# monitoring/service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: scrapecraft-metrics
  namespace: scrapecraft-prod
spec:
  selector:
    matchLabels:
      app: scrapecraft-backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

#### Apply Monitoring
```bash
kubectl apply -f monitoring/
```

### 2. Grafana Dashboards

#### Import Dashboards
```bash
# Import ScrapeCraft dashboards
kubectl create configmap grafana-dashboards \
  --from-file=monitoring/grafana/dashboards/ \
  --namespace=monitoring

# Apply dashboard configuration
kubectl apply -f monitoring/grafana/
```

### 3. Alerting Rules

#### Prometheus Rules
```yaml
# monitoring/alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: scrapecraft-alerts
  namespace: scrapecraft-prod
spec:
  groups:
  - name: scrapecraft.rules
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: High error rate detected
        description: "Error rate is {{ $value }} errors per second"
    
    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: High memory usage
        description: "Memory usage is above 90%"
```

## Security Configuration

### 1. Network Policies

```yaml
# security/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scrapecraft-network-policy
  namespace: scrapecraft-prod
spec:
  podSelector:
    matchLabels:
      app: scrapecraft-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: scrapecraft-frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### 2. Pod Security Policies

```yaml
# security/pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: scrapecraft-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Backup and Disaster Recovery

### 1. Database Backups

#### Automated Backups
```bash
# Create backup cronjob
kubectl apply -f backup/postgres-backup-cronjob.yaml

# Manual backup
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%Y%m%d)
```

#### Backup Script
```yaml
# backup/postgres-backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: scrapecraft-prod
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:15
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h $DATABASE_HOST -U $DATABASE_USER -d scrapecraft | \
              gzip > /backup/scrapecraft-$(date +%Y%m%d_%H%M%S).sql.gz
              aws s3 cp /backup/scrapecraft-$(date +%Y%m%d_%H%M%S).sql.gz \
              s3://scrapecraft-backups/database/
            env:
            - name: DATABASE_HOST
              valueFrom:
                secretKeyRef:
                  name: scrapecraft-secrets
                  key: database-host
            - name: DATABASE_USER
              valueFrom:
                secretKeyRef:
                  name: scrapecraft-secrets
                  key: database-user
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: scrapecraft-secrets
                  key: database-password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### 2. Application State Backups

```bash
# Backup Kubernetes configurations
kubectl get all,configmaps,secrets,pvc -n scrapecraft-prod -o yaml > cluster-backup-$(date +%Y%m%d).yaml

# Backup to S3
aws s3 cp cluster-backup-$(date +%Y%m%d).yaml s3://scrapecraft-backups/k8s/
```

## Scaling and Performance

### 1. Horizontal Pod Autoscaling

```yaml
# scaling/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: scrapecraft-backend-hpa
  namespace: scrapecraft-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: scrapecraft-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 2. Cluster Autoscaling

#### AWS EKS Cluster Autoscaler
```bash
# Deploy cluster autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Configure for your cluster
kubectl patch deployment cluster-autoscaler \
  -n kube-system \
  -p '{"spec":{"template":{"spec":{"containers":[{"name":"cluster-autoscaler","command":["cluster-autoscaler","--v=4","--stderrthreshold=info","--cloud-provider=aws","--skip-nodes-with-local-storage=false","--expander=least-waste","--node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/scrapecraft-prod"]}]}}}}'
```

## CI/CD Pipeline

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    tags:
      - 'v*'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run tests
      run: |
        cd backend && pytest
        cd frontend && npm test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-west-2
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker images
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: scrapecraft
        IMAGE_TAG: ${{ github.sha }}
      run: |
        # Build backend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY/backend:$IMAGE_TAG ./backend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY/backend:$IMAGE_TAG
        
        # Build frontend
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY/frontend:$IMAGE_TAG ./frontend
        docker push $ECR_REGISTRY/$ECR_REPOSITORY/frontend:$IMAGE_TAG
    
    - name: Deploy to Kubernetes
      run: |
        aws eks update-kubeconfig --name scrapecraft-prod
        helm upgrade --install scrapecraft-prod ./helm \
          --set image.tag=$IMAGE_TAG \
          --values helm/values-prod.yaml
```

## Troubleshooting

### Common Issues

#### Pod Startup Failures
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name> --previous

# Check resource usage
kubectl top pods
```

#### Database Connection Issues
```bash
# Test database connectivity
kubectl exec -it <backend-pod> -- psql -h $DATABASE_HOST -U $DATABASE_USER -d scrapecraft

# Check database logs
kubectl logs -l app=postgres --tail=100
```

#### Performance Issues
```bash
# Check resource usage
kubectl top nodes
kubectl top pods

# Check HPA status
kubectl get hpa
kubectl describe hpa scrapecraft-backend-hpa

# Check metrics
kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta1/namespaces/scrapecraft-prod/pods/*/http_requests_per_second"
```

### Emergency Procedures

#### Rollback Deployment
```bash
# Rollback to previous revision
helm rollback scrapecraft-prod 1

# Or rollback to specific version
helm upgrade --install scrapecraft-prod ./helm \
  --set image.tag=previous-version-tag \
  --values helm/values-prod.yaml
```

#### Emergency Scale Down
```bash
# Scale down all deployments
kubectl scale deployment --replicas=0 --all

# Scale back up
kubectl scale deployment scrapecraft-backend --replicas=3
kubectl scale deployment scrapecraft-frontend --replicas=2
```

---

This deployment guide provides comprehensive instructions for deploying ScrapeCraft to production. For specific cloud provider configurations or custom requirements, refer to the additional documentation in the infrastructure repository.