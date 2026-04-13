# -*- coding: utf-8 -*-
"""
Secure Kubernetes Secrets Template Generator for OSINT-OS Platform
This script generates proper Kubernetes secrets without hardcoded values.
"""

import base64
import secrets
import string
import sys
from pathlib import Path


def generate_secure_password(length=32):
    """Generate a cryptographically secure password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for i in range(length))


def generate_secure_key(length=64):
    """Generate a cryptographically secure key."""
    return secrets.token_urlsafe(length)


def generate_secrets_template():
    """Generate a secure Kubernetes secrets template."""

    # Generate secure secrets
    secrets_config = {
        "database_password": generate_secure_password(),
        "jwt_secret": generate_secure_key(64),
        "openrouter_api_key": "SET_IN_ENVIRONMENT",  # Should be set from environment
        "openai_api_key": "SET_IN_ENVIRONMENT",  # Should be set from environment
        "custom_llm_api_key": "SET_IN_ENVIRONMENT",  # Should be set from environment
        "redis_password": generate_secure_password(),
        "scrapegraph_api_key": "SET_IN_ENVIRONMENT",  # Should be set from environment
        "prometheus_remote_write_key": generate_secure_key(48),
        "backup_access_key": generate_secure_key(32),
        "backup_secret_key": generate_secure_key(32),
        "smtp_username": "SET_IN_ENVIRONMENT",  # Should be set from environment
        "smtp_password": "SET_IN_ENVIRONMENT",  # Should be set from environment
    }

    # Generate YAML content
    yaml_content = """---
# Secure Kubernetes Secrets for OSINT-OS Platform
# IMPORTANT: This is a template. Actual secrets should be injected via:
# 1. External secret management systems (HashiCorp Vault, AWS Secrets Manager, etc.)
# 2. Kubernetes Sealed Secrets
# 3. Environment-specific configuration management
# 4. CI/CD pipeline secret injection

apiVersion: v1
kind: Secret
metadata:
  name: scrapecraft-secrets
  namespace: scrapecraft
  labels:
    app.kubernetes.io/name: scrapecraft
    app.kubernetes.io/component: secrets
  annotations:
    secret-generator.v1.mittwald.de/autogenerate: "database-password,jwt-secret,redis-password"
type: Opaque
stringData:
  # Database credentials - Use external secret management in production
  database-password: "${DATABASE_PASSWORD}"
  
  # JWT Secret - Generate unique secret per deployment
  jwt-secret: "${JWT_SECRET}"
  
  # LLM Provider API Keys - Set via environment variables or external secret store
  openrouter-api-key: "${OPENROUTER_API_KEY}"
  openai-api-key: "${OPENAI_API_KEY}"
  custom-llm-api-key: "${CUSTOM_LLM_API_KEY}"
  
  # Redis password - Use strong unique password
  redis-password: "${REDIS_PASSWORD}"
  
  # External service credentials
  scrapegraph-api-key: "${SCRAPEGRAPH_API_KEY}"
  
  # Monitoring and alerting
  prometheus-remote-write-key: "${PROMETHEUS_REMOTE_WRITE_KEY}"
  
  # Backup storage credentials
  backup-access-key: "${BACKUP_ACCESS_KEY}"
  backup-secret-key: "${BACKUP_SECRET_KEY}"
  
  # Email service credentials for alerts
  smtp-username: "${SMTP_USERNAME}"
  smtp-password: "${SMTP_PASSWORD}"

---
# TLS Certificate Secret - Use cert-manager or external certificate management
apiVersion: v1
kind: Secret
metadata:
  name: scrapecraft-tls
  namespace: scrapecraft
  labels:
    app.kubernetes.io/name: scrapecraft
    app.kubernetes.io/component: tls
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
type: kubernetes.io/tls
data:
  # These will be managed by cert-manager
  tls.crt: "${TLS_CRT}"
  tls.key: "${TLS_KEY}"

---
# Docker Registry Secret - Use kubectl create secret docker-registry
apiVersion: v1
kind: Secret
metadata:
  name: scrapecraft-registry-secret
  namespace: scrapecraft
  labels:
    app.kubernetes.io/name: scrapecraft
    app.kubernetes.io/component: registry
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: "${DOCKER_CONFIG_JSON}"

---
# Environment-specific secrets example
apiVersion: v1
kind: ConfigMap
metadata:
  name: scrapecraft-security-config
  namespace: scrapecraft
  labels:
    app.kubernetes.io/name: scrapecraft
    app.kubernetes.io/component: security
data:
  security.yaml: |
    # Security configuration
    cors:
      allowed_origins:
        - "https://your-production-domain.com"
        - "https://your-staging-domain.com"
      allowed_methods:
        - "GET"
        - "POST"
        - "PUT"
        - "DELETE"
      allowed_headers:
        - "Authorization"
        - "Content-Type"
        - "X-API-Key"
      allow_credentials: true
      max_age: 86400
    
    jwt:
      algorithm: "HS256"
      access_token_expire_minutes: 30
      refresh_token_expire_days: 7
    
    rate_limiting:
      requests_per_minute: 100
      burst_size: 200
    
    encryption:
      algorithm: "AES-256-GCM"
      key_rotation_days: 90
"""

    return yaml_content


def create_environment_template():
    """Create .env template for development."""
    env_content = """# OSINT-OS Platform Environment Variables
# Copy this file to .env.local and fill in your actual values

# Database Configuration
DATABASE_PASSWORD=your_secure_database_password_here
DATABASE_URL=postgresql://user:password@localhost:5432/scrapecraft

# JWT Configuration
JWT_SECRET=your_64_character_jwt_secret_here_generated_with_openssl_rand_base64_64

# LLM Provider API Keys
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
CUSTOM_LLM_API_KEY=your_custom_llm_api_key_here

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password_here
REDIS_URL=redis://localhost:6379

# External Service API Keys
SCRAPEGRAPH_API_KEY=your_scrapegraph_api_key_here

# Monitoring Configuration
PROMETHEUS_REMOTE_WRITE_KEY=your_prometheus_remote_write_key_here

# Backup Configuration
BACKUP_ACCESS_KEY=your_backup_access_key_here
BACKUP_SECRET_KEY=your_backup_secret_key_here

# Email Configuration
SMTP_USERNAME=your_smtp_username_here
SMTP_PASSWORD=your_smtp_password_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# TLS Certificates (for development - use cert-manager in production)
TLS_CRT=your_base64_encoded_tls_certificate
TLS_KEY=your_base64_encoded_tls_private_key

# Docker Registry (if using private registry)
DOCKER_CONFIG_JSON=your_base64_encoded_docker_config

# Security Configuration
CORS_ORIGINS=http://localhost:3000,https://your-domain.com
ENCRYPTION_KEY=your_32_character_encryption_key_here
"""

    return env_content


if __name__ == "__main__":
    # Generate the secure secrets template
    secrets_template = generate_secrets_template()
    env_template = create_environment_template()

    # Write to files
    try:
        with open("k8s/secrets-template.yaml", "w") as f:
            f.write(secrets_template)
        print("✅ Generated secure secrets template: k8s/secrets-template.yaml")

        with open(".env.template", "w") as f:
            f.write(env_template)
        print("✅ Generated environment template: .env.template")

        print("\n🔐 SECURITY IMPLEMENTATION GUIDE:")
        print("1. Replace k8s/secrets.yaml with environment-specific secret management")
        print(
            "2. Use external secret stores (HashiCorp Vault, AWS Secrets Manager, etc.)"
        )
        print("3. Implement Kubernetes Sealed Secrets for production")
        print("4. Set up CI/CD pipeline secret injection")
        print("5. Use cert-manager for TLS certificate management")
        print("6. Copy .env.template to .env.local and fill in actual values")
        print("7. Never commit actual secrets to version control")

    except Exception as e:
        print(f"❌ Error generating templates: {e}")
        sys.exit(1)
