# Infrastructure Architecture Documentation

## Overview

The ScrapeCraft infrastructure is a comprehensive Kubernetes-native deployment architecture designed for scalability, security, and observability. It implements modern cloud-native patterns with comprehensive monitoring, security hardening, and automated deployment capabilities.

## Architecture Stack

### Container Orchestration
- **Kubernetes**: Container orchestration platform
- **Docker**: Container runtime and image management
- **Helm**: Kubernetes package management
- **Docker Compose**: Local development environment

### Ingress & Load Balancing
- **NGINX Ingress Controller**: L7 load balancing and SSL termination
- **Cert-Manager**: Automated TLS certificate management
- **Let's Encrypt**: SSL certificate provider
- **Load Balancer Services**: External traffic distribution

### Storage & Persistence
- **PostgreSQL**: Primary relational database
- **Redis**: In-memory data store and caching
- **Persistent Volumes**: Kubernetes storage abstraction
- **Storage Classes**: Different storage tiers (SSD, HDD)

### Monitoring & Observability
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alert routing and notification
- **Node Exporter**: System metrics collection

### Security & Compliance
- **Network Policies**: Kubernetes network segmentation
- **Pod Security Policies**: Container security constraints
- **RBAC**: Role-based access control
- **Falco**: Runtime security monitoring
- **OPA/Gatekeeper**: Policy enforcement

### CI/CD & Automation
- **GitHub Actions**: Continuous integration and deployment
- **ArgoCD**: GitOps continuous delivery
- **Kaniko**: Secure container image building
- **Trivy**: Container vulnerability scanning

## Cluster Architecture

### Namespace Organization

```yaml
# Production Namespaces
namespaces:
  - name: scrapecraft-prod
    labels:
      environment: production
      app: scrapecraft
    resources:
      - backend deployment
      - frontend deployment
      - database services
      - monitoring stack
  
  - name: scrapecraft-staging
    labels:
      environment: staging
      app: scrapecraft
    resources:
      - staging deployments
      - integration testing
  
  - name: monitoring
    labels:
      purpose: monitoring
    resources:
      - prometheus
      - grafana
      - alertmanager
  
  - name: security
    labels:
      purpose: security
    resources:
      - falco agents
      - policy enforcement
```

### Node Architecture

```yaml
# Node Pool Configuration
node_pools:
  - name: application-nodes
    instance_type: Standard_D4s_v5  # 4 vCPU, 16GB RAM
    autoscaling:
      min_nodes: 2
      max_nodes: 10
    labels:
      workload: application
    taints:
      - key: workload
        value: application
        effect: NoSchedule
    
  - name: database-nodes
    instance_type: Standard_E8s_v3  # 8 vCPU, 32GB RAM
    autoscaling:
      min_nodes: 1
      max_nodes: 3
    labels:
      workload: database
    taints:
      - key: workload
        value: database
        effect: NoSchedule
    
  - name: monitoring-nodes
    instance_type: Standard_D2s_v3  # 2 vCPU, 8GB RAM
    autoscaling:
      min_nodes: 1
      max_nodes: 2
    labels:
      workload: monitoring
```

## Service Architecture

### Backend Service

```yaml
# Backend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: scrapecraft-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: scrapecraft/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: scrapecraft-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: scrapecraft-config
              key: redis-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: scrapecraft-prod
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Frontend Service

```yaml
# Frontend Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: scrapecraft-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: scrapecraft/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        securityContext:
          runAsNonRoot: true
          runAsUser: 101
          allowPrivilegeEscalation: false
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: scrapecraft-prod
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### Database Services

```yaml
# PostgreSQL Deployment
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: scrapecraft-prod
spec:
  serviceName: postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:14
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: scrapecraft
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: ssd-storage
      resources:
        requests:
          storage: 20Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgresql-service
  namespace: scrapecraft-prod
spec:
  selector:
    app: postgresql
  ports:
  - port: 5432
    targetPort: 5432
  type: ClusterIP

# Redis Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: scrapecraft-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
        volumeMounts:
        - name: redis-storage
          mountPath: /data
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: scrapecraft-prod
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
  type: ClusterIP
```

## Ingress Architecture

### Main Application Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: scrapecraft-ingress
  namespace: scrapecraft-prod
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Frame-Options: DENY";
      more_set_headers "X-Content-Type-Options: nosniff";
      more_set_headers "X-XSS-Protection: 1; mode=block";
      more_set_headers "Strict-Transport-Security: max-age=31536000; includeSubDomains";
spec:
  tls:
  - hosts:
    - scrapecraft.example.com
    - api.scrapecraft.example.com
    secretName: scrapecraft-tls
  rules:
  - host: scrapecraft.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: api.scrapecraft.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

### WebSocket Support

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: websocket-ingress
  namespace: scrapecraft-prod
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-connect-timeout: "3600"
    nginx.ingress.kubernetes.io/proxy-buffering: "off"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  tls:
  - hosts:
    - ws.scrapecraft.example.com
    secretName: scrapecraft-tls
  rules:
  - host: ws.scrapecraft.example.com
    http:
      paths:
      - path: /api/ws
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
```

## Security Architecture

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: scrapecraft-network-policy
  namespace: scrapecraft-prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow traffic from ingress controller
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 8000
  # Allow traffic within namespace
  - from:
    - podSelector: {}
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
    - protocol: TCP
      port: 6379  # Redis
    - protocol: TCP
      port: 8000  # Backend
    - protocol: TCP
      port: 80    # Frontend
  # Allow traffic from monitoring
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000  # Backend metrics
    - protocol: TCP
      port: 9187  # PostgreSQL metrics
    - protocol: TCP
      port: 9121  # Redis metrics
  egress:
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
  # Allow external HTTP/HTTPS for scraping
  - to: []
    ports:
    - protocol: TCP
      port: 80
    - protocol: TCP
      port: 443
  # Allow LLM provider APIs
  - to: []
    ports:
    - protocol: TCP
      port: 443
  # Allow communication within namespace
  - to:
    - podSelector: {}
```

### RBAC Configuration

```yaml
# Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: scrapecraft-sa
  namespace: scrapecraft-prod

# Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: scrapecraft-prod
  name: scrapecraft-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch"]

# Role Binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: scrapecraft-rolebinding
  namespace: scrapecraft-prod
subjects:
- kind: ServiceAccount
  name: scrapecraft-sa
  namespace: scrapecraft-prod
roleRef:
  kind: Role
  name: scrapecraft-role
  apiGroup: rbac.authorization.k8s.io
```

### Pod Security Policies

```yaml
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

## Monitoring Architecture

### Prometheus Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
    
    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
        - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
        - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
          action: keep
          regex: default;kubernetes;https
      
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
        - role: node
        relabel_configs:
        - action: labelmap
          regex: __meta_kubernetes_node_label_(.+)
        - target_label: __address__
          replacement: kubernetes.default.svc:443
        - source_labels: [__meta_kubernetes_node_name]
          regex: (.+)
          target_label: __metrics_path__
          replacement: /api/v1/nodes/${1}/proxy/metrics
      
      - job_name: 'scrapecraft-backend'
        kubernetes_sd_configs:
        - role: endpoints
          namespaces:
            names:
            - scrapecraft-prod
        relabel_configs:
        - source_labels: [__meta_kubernetes_service_name]
          action: keep
          regex: backend-service
        - source_labels: [__meta_kubernetes_endpoint_address_target_name]
          action: replace
          target_label: pod
        - source_labels: [__meta_kubernetes_endpoint_port_name]
          action: replace
          target_label: __metrics_path__
          replacement: /metrics
```

### Grafana Dashboards

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  scrapecraft-overview.json: |
    {
      "dashboard": {
        "title": "ScrapeCraft Overview",
        "panels": [
          {
            "title": "Backend Response Time",
            "type": "graph",
            "targets": [
              {
                "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"scrapecraft-backend\"}[5m]))",
                "legendFormat": "95th percentile"
              }
            ]
          },
          {
            "title": "Database Connections",
            "type": "graph",
            "targets": [
              {
                "expr": "pg_stat_database_numbackends{datname=\"scrapecraft\"}",
                "legendFormat": "Active connections"
              }
            ]
          },
          {
            "title": "Redis Memory Usage",
            "type": "graph",
            "targets": [
              {
                "expr": "redis_memory_used_bytes{job=\"redis\"}",
                "legendFormat": "Memory used"
              }
            ]
          }
        ]
      }
    }
```

### Alerting Rules

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  scrapecraft.yml: |
    groups:
    - name: scrapecraft.rules
      rules:
      - alert: BackendDown
        expr: up{job="scrapecraft-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ScrapeCraft backend is down"
          description: "ScrapeCraft backend has been down for more than 1 minute."
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="scrapecraft-backend"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is above 2 seconds."
      
      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends{datname="scrapecraft"} > 80
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database has more than 80 active connections."
      
      - alert: RedisMemoryHigh
        expr: (redis_memory_used_bytes{job="redis"} / redis_memory_max_bytes{job="redis"}) > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Redis memory usage high"
          description: "Redis is using more than 90% of available memory."
```

## Storage Architecture

### Storage Classes

```yaml
# SSD Storage Class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  fsType: ext4
allowVolumeExpansion: true

# HDD Storage Class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: hdd-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: sc1
  fsType: ext4
allowVolumeExpansion: true

# Backup Storage Class
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: backup-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: st1
  fsType: ext4
allowVolumeExpansion: true
```

### Persistent Volume Claims

```yaml
# PostgreSQL PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: scrapecraft-prod
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ssd-storage
  resources:
    requests:
      storage: 50Gi

# Redis PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-pvc
  namespace: scrapecraft-prod
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ssd-storage
  resources:
    requests:
      storage: 10Gi

# Backup PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backup-pvc
  namespace: scrapecraft-prod
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: backup-storage
  resources:
    requests:
      storage: 100Gi
```

## Backup & Disaster Recovery

### Automated Backups

```yaml
# Backup CronJob
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
            image: postgres:14
            command:
            - /bin/bash
            - -c
            - |
              pg_dump $DATABASE_URL | gzip > /backup/scrapecraft-$(date +%Y%m%d-%H%M%S).sql.gz
              # Keep only last 7 days of backups
              find /backup -name "*.sql.gz" -mtime +7 -delete
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: database-url
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Disaster Recovery Plan

```yaml
# Disaster Recovery StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: disaster-recovery
  namespace: scrapecraft-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: disaster-recovery
  template:
    metadata:
      labels:
        app: disaster-recovery
    spec:
      containers:
      - name: dr-orchestrator
        image: scrapecraft/disaster-recovery:latest
        env:
        - name: BACKUP_BUCKET
          value: "s3://scrapecraft-backups"
        - name: AWS_REGION
          value: "us-west-2"
        - name: RESTORE_THRESHOLD
          value: "3"  # Number of failures before triggering restore
        volumeMounts:
        - name: backup-storage
          mountPath: /backup
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
      volumes:
      - name: backup-storage
        persistentVolumeClaim:
          claimName: backup-pvc
```

## Scaling Architecture

### Horizontal Pod Autoscaling

```yaml
# Backend HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: scrapecraft-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-deployment
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60

# Frontend HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend-hpa
  namespace: scrapecraft-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 25
        periodSeconds: 60
```

### Cluster Autoscaling

```yaml
# Cluster Autoscaler Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cluster-autoscaler
  namespace: kube-system
spec:
  replicas: 1
  selector:
    matchLabels:
      app: cluster-autoscaler
  template:
    metadata:
      labels:
        app: cluster-autoscaler
    spec:
      containers:
      - image: k8s.gcr.io/autoscaling/cluster-autoscaler:v1.21.0
        name: cluster-autoscaler
        resources:
          limits:
            cpu: 100m
            memory: 300Mi
          requests:
            cpu: 100m
            memory: 300Mi
        command:
        - ./cluster-autoscaler
        - --v=4
        - --stderrthreshold=info
        - --cloud-provider=aws
        - --skip-nodes-with-local-storage=false
        - --expander=least-waste
        - --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/scrapecraft
```

## Deployment Architecture

### GitOps with ArgoCD

```yaml
# ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: scrapecraft-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/scrapecraft-k8s
    targetRevision: main
    path: manifests
  destination:
    server: https://kubernetes.default.svc
    namespace: scrapecraft-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Progressive Deployment

```yaml
# Progressive Deployment Strategy
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: scrapecraft-backend
  namespace: scrapecraft-prod
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20
      - pause: {duration: 10m}
      - setWeight: 40
      - pause: {duration: 10m}
      - setWeight: 60
      - pause: {duration: 10m}
      - setWeight: 80
      - pause: {duration: 10m}
      analysis:
        templates:
        - templateName: success-rate
        args:
        - name: service-name
          value: scrapecraft-backend
  selector:
    matchLabels:
      app: scrapecraft-backend
  template:
    metadata:
      labels:
        app: scrapecraft-backend
    spec:
      containers:
      - name: backend
        image: scrapecraft/backend:latest
        ports:
        - containerPort: 8000
```

## Conclusion

The ScrapeCraft infrastructure architecture provides a comprehensive, secure, and scalable foundation for OSINT operations. Its cloud-native design ensures:

- **High Availability**: Multi-replica deployments with automatic failover
- **Scalability**: Horizontal and vertical scaling capabilities
- **Security**: Comprehensive security controls and compliance
- **Observability**: Full monitoring, logging, and alerting
- **Disaster Recovery**: Automated backups and recovery procedures
- **GitOps**: Infrastructure as code with automated deployments

This architecture enables the ScrapeCraft platform to handle enterprise-scale OSINT workloads while maintaining security, reliability, and operational excellence standards.