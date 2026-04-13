# 🚀 ScrapeCraft OSINT Platform - Production Deployment Guide

**Intelligence Agency-Grade Production Deployment with Enterprise Security and Monitoring**

**Version**: 2.0  
**Last Updated**: November 13, 2025  
**Classification**: Internal Use - Production Deployment  
**Target Environment**: Enterprise/Intelligence Agency Production

---

## 🔧 **EXECUTIVE SUMMARY**

This guide provides comprehensive, step-by-step instructions for deploying the ScrapeCraft OSINT platform in production environments with intelligence agency-grade security, monitoring, and compliance standards.

### **Deployment Targets**
- **Enterprise Production**: High-security environments with compliance requirements
- **Intelligence Agency**: Government deployments with strict security protocols
- **Cloud-Native**: AWS, GCP, Azure with full automation
- **On-Premises**: Secure air-gapped deployments

### **Time to Production**
- **Quick Deploy**: 2-4 hours (cloud deployment)
- **Enterprise Deploy**: 1-2 days (security review + deployment)
- **Intelligence Agency**: 3-5 days (compliance + hardening + deployment)

---

## 📋 **PREREQUISITES & REQUIREMENTS**

### **Infrastructure Requirements**

#### **Minimum Production Environment**
```yaml
Kubernetes Cluster:
  Control Plane: 3 nodes, 4 CPU, 8GB RAM, 100GB SSD each
  Worker Nodes: 3 nodes, 8 CPU, 16GB RAM, 200GB SSD each
  Network: 10Gbps connectivity, firewall configuration

Database:
  PostgreSQL 15+: 2 vCPU, 8GB RAM, 200GB SSD storage
  Redis 7+: 2 vCPU, 4GB RAM, 50GB SSD storage

Load Balancer:
  Application Load Balancer with SSL termination
  WAF integration with security rules

Storage:
  Block Storage: 500GB for application data
  Object Storage: 1TB for backups and exports
```

#### **Recommended Enterprise Environment**
```yaml
Kubernetes Cluster:
  Control Plane: 5 nodes, 8 CPU, 16GB RAM, 200GB SSD each
  Worker Nodes: 5+ nodes, 16 CPU, 32GB RAM, 500GB SSD each
  Network: 25Gbps connectivity, advanced firewall, DDoS protection

Database:
  PostgreSQL 15+: HA configuration, read replicas
  Primary: 4 vCPU, 16GB RAM, 500GB SSD
  Replicas: 2 vCPU, 8GB RAM, 500GB SSD each
  Redis 7+: Cluster mode, 3 nodes, 4 vCPU, 8GB RAM each

Security:
  Web Application Firewall (WAF)
  DDoS Protection Service
  Intrusion Detection/Prevention System
  Security Information and Event Management (SIEM)

Monitoring:
  Prometheus + Grafana + AlertManager
  ELK Stack for log aggregation
  Jaeger for distributed tracing
```

### **Tool Requirements**
```bash
# Essential Tools
kubectl >= 1.28
helm >= 3.14
docker >= 24.0
git >= 2.40

# Cloud Provider CLIs
aws-cli >= 2.0  # AWS
gcloud >= 470.0 # GCP
az >= 2.50      # Azure

# Security Tools
openssl >= 3.0
gpg >= 2.4
vault >= 1.14   # Optional for secret management
```

### **Security Requirements**
- **TLS 1.3**: All communications must use TLS 1.3
- **Certificate Management**: Automated certificate rotation
- **Secret Management**: Encrypted secrets with rotation policies
- **Network Security**: Firewall rules, network policies, VPC isolation
- **Access Control**: RBAC, MFA, audit logging

---

## 🏗️ **DEPLOYMENT ARCHITECTURE**

### **Production Architecture Overview**
```
┌─────────────────────────────────────────────────────────────┐
│                    External Layer                           │
├─────────────────────────────────────────────────────────────┤
│  WAF + DDoS Protection + CDN + SSL Termination             │
├─────────────────────────────────────────────────────────────┤
│                    Load Balancer Layer                     │
├─────────────────────────────────────────────────────────────┤
│  Application Load Balancer + Health Checks                 │
├─────────────────────────────────────────────────────────────┤
│                  Kubernetes Cluster                        │
├─────────────────────────────────────────────────────────────┤
│  Ingress Controller → Services → Pods → Containers         │
│  Frontend (React)    Backend (FastAPI)    Workers (AI)    │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer                              │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL (Primary + Replicas)  Redis Cluster           │
├─────────────────────────────────────────────────────────────┤
│                  Monitoring Layer                          │
├─────────────────────────────────────────────────────────────┤
│  Prometheus + Grafana + AlertManager + ELK Stack          │
└─────────────────────────────────────────────────────────────┘
```

### **Security Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                 Defense in Depth                           │
├─────────────────────────────────────────────────────────────┤
│  Network Security: VPC, Firewalls, Network Policies        │
├─────────────────────────────────────────────────────────────┤
│  Application Security: WAF, CORS, Security Headers         │
├─────────────────────────────────────────────────────────────┤
│  Authentication: JWT + RBAC + MFA + Session Management     │
├─────────────────────────────────────────────────────────────┤
│  Data Security: Encryption + Access Control + Audit Logs   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Security: Pod Security, Secrets, RBAC      │
├─────────────────────────────────────────────────────────────┤
│  Monitoring: SIEM, Audit Logs, Threat Detection            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 **STEP-BY-STEP DEPLOYMENT**

### **Phase 1: Environment Preparation**

#### **1.1 Kubernetes Cluster Setup**
```bash
# Create production namespace
kubectl create namespace scrapecraft-production
kubectl label namespace scrapecraft-production environment=production

# Set context
kubectl config set-context --current --namespace=scrapecraft-production

# Verify cluster health
kubectl cluster-info
kubectl get nodes
```

#### **1.2 Security Configuration**
```bash
# Create Network Policies
kubectl apply -f k8s/security/network-policies.yaml

# Apply Pod Security Standards
kubectl apply -f k8s/security/pod-security-policy.yaml

# Configure Resource Quotas
kubectl apply -f k8s/security/resource-quota.yaml
```

### **Phase 2: Secret Management**

#### **2.1 Generate Secure Secrets**
```bash
# Generate secure random values
JWT_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
OPENAI_API_KEY="your-openai-api-key"
OPENROUTER_API_KEY="your-openrouter-api-key"

# Create Kubernetes secrets
kubectl create secret generic scrapecraft-secrets \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=database-url="postgresql://scrapecraft:$DB_PASSWORD@postgres:5432/scrapecraft" \
  --from-literal=redis-url="redis://:$REDIS_PASSWORD@redis:6379/0" \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=openrouter-api-key="$OPENROUTER_API_KEY" \
  --from-literal=environment="production"
```

#### **2.2 TLS Certificate Management**
```bash
# Install cert-manager for automatic certificates
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-production
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@yourdomain.com
    privateKeySecretRef:
      name: letsencrypt-production
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### **Phase 3: Database Infrastructure**

#### **3.1 PostgreSQL Deployment**
```bash
# Deploy PostgreSQL with high availability
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgres bitnami/postgresql \
  --namespace scrapecraft-production \
  --set auth.postgresPassword="$DB_PASSWORD" \
  --set auth.username=scrapecraft \
  --set auth.password="$DB_PASSWORD" \
  --set auth.database=scrapecraft \
  --set primary.persistence.size=500Gi \
  --set primary.resources.requests.memory=8Gi \
  --set primary.resources.requests.cpu=2000m \
  --set readReplicas.replicaCount=2 \
  --set readReplicas.resources.requests.memory=4Gi \
  --set readReplicas.resources.requests.cpu=1000m \
  --set metrics.enabled=true
```

#### **3.2 Redis Cluster Deployment**
```bash
# Deploy Redis cluster for caching and task queues
helm install redis bitnami/redis \
  --namespace scrapecraft-production \
  --set auth.enabled=true \
  --set auth.password="$REDIS_PASSWORD" \
  --set cluster.enabled=true \
  --set cluster.slaveCount=2 \
  --set master.persistence.size=100Gi \
  --set replica.persistence.size=100Gi \
  --set metrics.enabled=true
```

#### **3.3 Database Initialization**
```bash
# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=postgres --timeout=300s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis --timeout=300s

# Run database migrations
kubectl run migration --image=your-registry/scrapecraft-backend:v2.0.0 \
  --rm -i --restart=Never \
  --env="DATABASE_URL=postgresql://scrapecraft:$DB_PASSWORD@postgres:5432/scrapecraft" \
  -- alembic upgrade head
```

### **Phase 4: Application Deployment**

#### **4.1 Build and Push Images**
```bash
# Backend production image
cd backend
docker build -f Dockerfile.production -t scrapecraft/backend:v2.0.0 .
docker tag scrapecraft/backend:v2.0.0 your-registry.com/scrapecraft/backend:v2.0.0
docker push your-registry.com/scrapecraft/backend:v2.0.0

# Frontend production image
cd ../frontend
docker build -t scrapecraft/frontend:v2.0.0 .
docker tag scrapecraft/frontend:v2.0.0 your-registry.com/scrapecraft/frontend:v2.0.0
docker push your-registry.com/scrapecraft/frontend:v2.0.0
```

#### **4.2 Deploy Backend Services**
```bash
# Deploy backend API
helm install backend ./helm/backend \
  --namespace scrapecraft-production \
  --set image.repository=your-registry.com/scrapecraft/backend \
  --set image.tag=v2.0.0 \
  --set replicaCount=3 \
  --set resources.requests.cpu=1000m \
  --set resources.requests.memory=2Gi \
  --set resources.limits.cpu=2000m \
  --set resources.limits.memory=4Gi \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=20

# Deploy AI workers
helm install workers ./helm/workers \
  --namespace scrapecraft-production \
  --set image.repository=your-registry.com/scrapecraft/backend \
  --set image.tag=v2.0.0 \
  --set replicaCount=5 \
  --set resources.requests.cpu=2000m \
  --set resources.requests.memory=4Gi \
  --set resources.limits.cpu=4000m \
  --set resources.limits.memory=8Gi
```

#### **4.3 Deploy Frontend**
```bash
# Deploy frontend application
helm install frontend ./helm/frontend \
  --namespace scrapecraft-production \
  --set image.repository=your-registry.com/scrapecraft/frontend \
  --set image.tag=v2.0.0 \
  --set replicaCount=2 \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=1Gi \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=2Gi
```

### **Phase 5: Ingress and SSL**

#### **5.1 Install NGINX Ingress Controller**
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.resources.requests.cpu=500m \
  --set controller.resources.requests.memory=1Gi
```

#### **5.2 Configure Application Ingress**
```bash
# Apply ingress configuration
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scrapecraft-ingress
  namespace: scrapecraft-production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-production
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/ssl-protocols: "TLSv1.3"
    nginx.ingress.kubernetes.io/security-headers: "true"
spec:
  tls:
  - hosts:
    - osint.yourdomain.com
    secretName: scrapecraft-tls
  rules:
  - host: osint.yourdomain.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 3000
EOF
```

### **Phase 6: Monitoring and Observability**

#### **6.1 Deploy Prometheus Stack**
```bash
# Install Prometheus Operator
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=200Gi \
  --set grafana.adminPassword=admin123 \
  --set grafana.persistence.enabled=true \
  --set grafana.persistence.size=50Gi
```

#### **6.2 Configure Application Monitoring**
```bash
# Apply ServiceMonitor for application metrics
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: scrapecraft-metrics
  namespace: scrapecraft-production
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
EOF
```

#### **6.3 Deploy ELK Stack for Logging**
```bash
# Deploy Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace \
  --set replicas=3 \
  --set volumeClaimTemplate.resources.requests.storage=500Gi

# Deploy Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set service.type=LoadBalancer

# Deploy Logstash
helm install logstash elastic/logstash \
  --namespace logging \
  --set replicas=2
```

### **Phase 7: Backup and Disaster Recovery**

#### **7.1 Configure Database Backups**
```bash
# Create backup cronjob
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: scrapecraft-production
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
              pg_dump -h postgres -U scrapecraft -d scrapecraft | \
              gzip > /backup/scrapecraft-$(date +%Y%m%d_%H%M%S).sql.gz
              aws s3 cp /backup/scrapecraft-$(date +%Y%m%d_%H%M%S).sql.gz \
              s3://scrapecraft-backups/database/
            env:
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
EOF
```

#### **7.2 Configure Application State Backups**
```bash
# Create Kubernetes configuration backup
kubectl create configmap backup-script \
  --from-file=scripts/backup-k8s-config.sh

# Create backup cronjob for configurations
kubectl apply -f k8s/backup/config-backup-cronjob.yaml
```

---

## 🔒 **SECURITY HARDENING**

### **Security Configuration Checklist**
```bash
#!/bin/bash
# security-hardening-checklist.sh

echo "🔒 ScrapeCraft OSINT Security Hardening Checklist"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() { echo -e "${GREEN}✅ $1${NC}"; }
check_fail() { echo -e "${RED}❌ $1${NC}"; }
check_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 1. Network Security
echo "🌐 Network Security"
if kubectl get networkpolicy -n scrapecraft-production | grep -q "scrapecraft"; then
    check_pass "Network policies configured"
else
    check_fail "Network policies not configured"
fi

# 2. Pod Security
echo "🛡️  Pod Security"
if kubectl get psp -n scrapecraft-production | grep -q "scrapecraft"; then
    check_pass "Pod security policies configured"
else
    check_warning "Pod security policies not configured"
fi

# 3. Secrets Management
echo "🔐 Secrets Management"
if kubectl get secrets -n scrapecraft-production | grep -q "scrapecraft-secrets"; then
    check_pass "Application secrets configured"
else
    check_fail "Application secrets not configured"
fi

# 4. RBAC Configuration
echo "👥 RBAC Configuration"
if kubectl get rolebinding -n scrapecraft-production | grep -q "scrapecraft"; then
    check_pass "RBAC configured"
else
    check_fail "RBAC not configured"
fi

# 5. TLS Configuration
echo "🔒 TLS Configuration"
if kubectl get certificate -n scrapecraft-production | grep -q "scrapecraft-tls"; then
    check_pass "TLS certificates configured"
else
    check_fail "TLS certificates not configured"
fi

echo "=================================================="
echo "Security hardening check complete!"
```

### **Advanced Security Configuration**
```yaml
# security-context.yaml
apiVersion: v1
kind: PodSecurityContext
metadata:
  name: scrapecraft-security-context
spec:
  runAsNonRoot: true
  runAsUser: 1000
  runAsGroup: 1000
  fsGroup: 1000
  seccompProfile:
    type: RuntimeDefault
---
apiVersion: v1
kind: ContainerSecurityContext
metadata:
  name: scrapecraft-container-security
spec:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities:
    drop:
    - ALL
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
```

---

## 📊 **MONITORING AND ALERTING**

### **Key Performance Indicators**
```yaml
# monitoring/kpis.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scrapecraft-kpis
data:
  availability.yaml: |
    # Service Availability
    availability_target: 99.9%
    response_time_p95: 500ms
    response_time_p99: 1000ms
    
  performance.yaml: |
    # Performance Metrics
    cpu_threshold: 80%
    memory_threshold: 85%
    disk_threshold: 90%
    
  security.yaml: |
    # Security Metrics
    failed_login_threshold: 10/min
    unauthorized_access_threshold: 5/min
    data_export_threshold: 50/min
```

### **Alerting Rules**
```yaml
# monitoring/alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: scrapecraft-alerts
  namespace: scrapecraft-production
spec:
  groups:
  - name: availability.rules
    rules:
    - alert: ServiceDown
      expr: up{job=~"scrapecraft.*"} == 0
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "Service {{ $labels.job }} is down"
        description: "Service {{ $labels.job }} has been down for more than 1 minute"
    
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }} errors per second"
    
    - alert: HighResponseTime
      expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High response time detected"
        description: "95th percentile response time is {{ $value }} seconds"
    
    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage"
        description: "Memory usage is above 90% for {{ $labels.pod }}"
    
    - alert: HighCPUUsage
      expr: rate(container_cpu_usage_seconds_total[5m]) / container_spec_cpu_quota * 100 > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High CPU usage"
        description: "CPU usage is above 80% for {{ $labels.pod }}"
```

---

## 🧪 **DEPLOYMENT VALIDATION**

### **Health Check Script**
```bash
#!/bin/bash
# deployment-validation.sh

echo "🔍 ScrapeCraft OSINT Deployment Validation"
echo "=========================================="

# Configuration
NAMESPACE="scrapecraft-production"
DOMAIN="osint.yourdomain.com"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_pass() { echo -e "${GREEN}✅ $1${NC}"; }
check_fail() { echo -e "${RED}❌ $1${NC}"; }
check_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 1. Check Pod Status
echo "📦 Pod Status Check"
kubectl get pods -n $NAMESPACE
echo ""

# 2. Check Service Status
echo "🔌 Service Status Check"
kubectl get services -n $NAMESPACE
echo ""

# 3. Check Ingress Status
echo "🌐 Ingress Status Check"
kubectl get ingress -n $NAMESPACE
echo ""

# 4. Health Check Endpoints
echo "🏥 Application Health Checks"

# Frontend health
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/health | grep -q "200"; then
    check_pass "Frontend health check"
else
    check_fail "Frontend health check"
fi

# Backend health
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health | grep -q "200"; then
    check_pass "Backend health check"
else
    check_fail "Backend health check"
fi

# API documentation
if curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/docs | grep -q "200"; then
    check_pass "API documentation accessible"
else
    check_fail "API documentation accessible"
fi

echo ""

# 5. Database Connectivity
echo "🗄️  Database Connectivity"
if kubectl exec -n $NAMESPACE deployment/backend -- python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
" | grep -q "successful"; then
    check_pass "Database connectivity"
else
    check_fail "Database connectivity"
fi

echo ""

# 6. Redis Connectivity
echo "🔴 Redis Connectivity"
if kubectl exec -n $NAMESPACE deployment/backend -- python -c "
import os
import redis
try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('Redis connection successful')
except Exception as e:
    print(f'Redis connection failed: {e}')
" | grep -q "successful"; then
    check_pass "Redis connectivity"
else
    check_fail "Redis connectivity"
fi

echo ""

# 7. Security Headers Check
echo "🛡️  Security Headers Check"
SECURITY_HEADERS=$(curl -s -I https://$DOMAIN)
if echo "$SECURITY_HEADERS" | grep -qi "strict-transport-security"; then
    check_pass "HSTS header present"
else
    check_warning "HSTS header missing"
fi

if echo "$SECURITY_HEADERS" | grep -qi "content-security-policy"; then
    check_pass "CSP header present"
else
    check_warning "CSP header missing"
fi

if echo "$SECURITY_HEADERS" | grep -qi "x-frame-options"; then
    check_pass "X-Frame-Options header present"
else
    check_warning "X-Frame-Options header missing"
fi

echo ""

# 8. SSL Certificate Check
echo "🔒 SSL Certificate Check"
SSL_EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
echo "SSL Certificate expires: $SSL_EXPIRY"

echo ""
echo "=========================================="
echo "Deployment validation complete!"
```

---

## 🚨 **TROUBLESHOOTING GUIDE**

### **Common Issues and Solutions**

#### **Pod Startup Failures**
```bash
# Check pod events
kubectl describe pod <pod-name> -n scrapecraft-production

# Check pod logs
kubectl logs <pod-name> -n scrapecraft-production --previous

# Check resource constraints
kubectl top pods -n scrapecraft-production
```

#### **Database Connection Issues**
```bash
# Test database connectivity
kubectl exec -it deployment/backend -n scrapecraft-production -- \
  psql -h postgres -U scrapecraft -d scrapecraft

# Check database logs
kubectl logs -n scrapecraft-production -l app.kubernetes.io/name=postgres --tail=100
```

#### **Ingress/SSL Issues**
```bash
# Check ingress status
kubectl describe ingress scrapecraft-ingress -n scrapecraft-production

# Check certificate status
kubectl describe certificate scrapecraft-tls -n scrapecraft-production

# Check ingress controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx-controller
```

#### **Performance Issues**
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n scrapecraft-production

# Check HPA status
kubectl get hpa -n scrapecraft-production
kubectl describe hpa backend-hpa -n scrapecraft-production

# Check application metrics
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090
```

---

## 🔄 **MAINTENANCE OPERATIONS**

### **Rolling Updates**
```bash
# Update application version
helm upgrade backend ./helm/backend \
  --namespace scrapecraft-production \
  --set image.tag=v2.0.1 \
  --set replicaCount=3 \
  --set rollingUpdate.maxSurge=1 \
  --set rollingUpdate.maxUnavailable=0

# Monitor rollout status
kubectl rollout status deployment/backend -n scrapecraft-production
```

### **Backup Operations**
```bash
# Manual database backup
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%Y%m%d_%H%M%S)

# Verify backup
aws s3 ls s3://scrapecraft-backups/database/ | tail -5
```

### **Scale Operations**
```bash
# Scale up for high load
kubectl scale deployment backend --replicas=10 -n scrapecraft-production
kubectl scale deployment workers --replicas=20 -n scrapecraft-production

# Scale down after load
kubectl scale deployment backend --replicas=3 -n scrapecraft-production
kubectl scale deployment workers --replicas=5 -n scrapecraft-production
```

---

## 📞 **SUPPORT AND EMERGENCY CONTACTS**

### **Production Support**
- **24/7 Emergency**: emergency@osint-os.com
- **Technical Support**: support@osint-os.com
- **Security Incident**: security@osint-os.com

### **Monitoring Dashboards**
- **Grafana**: https://grafana.yourdomain.com
- **Kibana**: https://kibana.yourdomain.com
- **Prometheus**: https://prometheus.yourdomain.com

### **Documentation**
- **API Documentation**: https://osint.yourdomain.com/docs
- **Security Guide**: ./docs/security-configuration-guide.md
- **Troubleshooting**: ./docs/troubleshooting-guide.md

---

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment Checklist**
- [ ] Security review completed
- [ ] Infrastructure requirements validated
- [ ] Database backups created
- [ ] SSL certificates obtained
- [ ] Monitoring configured
- [ ] Backup procedures tested
- [ ] Rollback plan documented
- [ ] Team training completed

### **Post-Deployment Checklist**
- [ ] All pods running healthy
- [ ] Health checks passing
- [ ] SSL certificates valid
- [ ] Monitoring alerts configured
- [ ] Backup jobs scheduled
- [ ] Performance benchmarks met
- [ ] Security scans passed
- [ ] User acceptance testing completed

---

**Document Classification**: Internal Use - Production Deployment  
**Next Review**: 30 days from deployment  
**Version Control**: Maintained in Git repository  
**Distribution**: DevOps Team, Security Team, Operations Team

---

*This production deployment guide is part of the ScrapeCraft OSINT platform's comprehensive documentation suite. For the latest updates and additional resources, visit the [Documentation Index](./docs/).*