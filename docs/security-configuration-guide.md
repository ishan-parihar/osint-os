# 🔒 ScrapeCraft OSINT Platform - Security Configuration Guide

**Intelligence Agency-Grade Security Hardening and Configuration**

**Version**: 2.0  
**Last Updated**: November 13, 2025  
**Classification**: Internal Use - Security Configuration  
**Target Environment**: Enterprise/Intelligence Agency Production  

---

## 🔐 **OVERVIEW**

This guide provides comprehensive security configuration instructions for deploying the ScrapeCraft OSINT platform in production environments with intelligence agency-grade security standards.

### **Security Objectives**
- **Confidentiality**: Protect sensitive investigation data and intelligence
- **Integrity**: Ensure data accuracy and prevent unauthorized modifications
- **Availability**: Maintain continuous operation for critical investigations
- **Auditability**: Comprehensive logging and monitoring of all activities
- **Compliance**: Meet regulatory and government compliance requirements

---

## 🏗️ **SECURITY ARCHITECTURE**

### **Defense in Depth Strategy**
```
┌─────────────────────────────────────────────────────────────┐
│                    External Threat Surface                  │
├─────────────────────────────────────────────────────────────┤
│  Web Application Firewall (WAF) + DDoS Protection          │
├─────────────────────────────────────────────────────────────┤
│  API Gateway + Rate Limiting + Input Validation            │
├─────────────────────────────────────────────────────────────┤
│  Authentication Layer (JWT + RBAC + MFA)                   │
├─────────────────────────────────────────────────────────────┤
│  Application Security (CORS + Security Headers)            │
├─────────────────────────────────────────────────────────────┤
│  Database Security (Encryption + Access Control)           │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure Security (Network + Container Security)     │
├─────────────────────────────────────────────────────────────┤
│  Monitoring & Logging (SIEM + Audit Trails)                │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 **ENVIRONMENT SECURITY CONFIGURATION**

### **1. Production Environment Setup**

#### **Secure Environment Variables**
```bash
# Production .env configuration
# Copy template: cp .env.example .env.production

# === Core Security Settings ===
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-super-secure-jwt-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-signing-secret-256-bits-minimum
JWT_REFRESH_SECRET_KEY=your-refresh-token-secret-256-bits-minimum

# === Database Security ===
DATABASE_URL=postgresql://username:password@encrypted-host:5432/osint_os
DATABASE_SSL_MODE=require
DATABASE_SSL_CERT=/path/to/client-cert.pem
DATABASE_SSL_KEY=/path/to/client-key.pem
DATABASE_SSL_CA=/path/to/ca-cert.pem

# === Redis Security ===
REDIS_URL=redis://username:password@redis-cluster:6379/0
REDIS_SSL=true
REDIS_SSL_CERT=/path/to/redis-cert.pem

# === LLM Provider Security ===
OPENROUTER_API_KEY=sk-or-v1-your-secure-openrouter-key
OPENAI_API_KEY=sk-your-secure-openai-key
CUSTOM_LLM_API_KEY=your-custom-llm-api-key

# === CORS Security (Restrict to allowed domains) ===
CORS_ORIGINS=["https://your-domain.com","https://app.your-domain.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST","PUT","DELETE"]
CORS_ALLOW_HEADERS=["*"]

# === Rate Limiting ===
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60  # seconds
RATE_LIMIT_STORAGE=redis

# === Security Headers ===
SECURITY_ENABLE_HTTPS=true
SECURITY_HSTS_ENABLED=true
SECURITY_HSTS_MAX_AGE=31536000
SECURITY_CSP_ENABLED=true
SECURITY_FRAME_OPTIONS=DENY
SECURITY_CONTENT_TYPE_NOSNIFF=true
```

#### **Security Validation Script**
```python
#!/usr/bin/env python3
"""
Security configuration validation script
Run this before production deployment to ensure security settings are correct.
"""

import os
import re
import sys
from typing import Dict, List, Tuple

def validate_secret_strength(secret: str, name: str) -> List[str]:
    """Validate secret key strength"""
    issues = []
    
    if len(secret) < 32:
        issues.append(f"{name}: Secret key must be at least 32 characters")
    
    if not re.search(r'[A-Z]', secret):
        issues.append(f"{name}: Secret should contain uppercase letters")
    
    if not re.search(r'[a-z]', secret):
        issues.append(f"{name}: Secret should contain lowercase letters")
    
    if not re.search(r'\d', secret):
        issues.append(f"{name}: Secret should contain numbers")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', secret):
        issues.append(f"{name}: Secret should contain special characters")
    
    # Check for common weak patterns
    weak_patterns = ['password', 'secret', 'key', 'admin', 'test', 'demo']
    for pattern in weak_patterns:
        if pattern.lower() in secret.lower():
            issues.append(f"{name}: Secret contains weak pattern '{pattern}'")
    
    return issues

def validate_database_security(url: str) -> List[str]:
    """Validate database security configuration"""
    issues = []
    
    if 'localhost' in url or '127.0.0.1' in url:
        issues.append("Database URL should not use localhost in production")
    
    if 'password=' in url and 'password=password' in url:
        issues.append("Database password should not be 'password'")
    
    if not 'sslmode=' in url or 'sslmode=disable' in url:
        issues.append("Database SSL should be enabled in production")
    
    return issues

def validate_cors_security(origins: List[str]) -> List[str]:
    """Validate CORS configuration"""
    issues = []
    
    if 'localhost' in str(origins) or '127.0.0.1' in str(origins):
        issues.append("CORS origins should not include localhost in production")
    
    if '*' in origins:
        issues.append("CORS origins should not be wildcard (*) in production")
    
    if not origins:
        issues.append("CORS origins should be explicitly configured")
    
    return issues

def main():
    """Main security validation"""
    print("🔍 ScrapeCraft OSINT Security Configuration Validation")
    print("=" * 60)
    
    all_issues = []
    
    # Validate JWT secrets
    jwt_secret = os.getenv('JWT_SECRET_KEY', '')
    refresh_secret = os.getenv('JWT_REFRESH_SECRET_KEY', '')
    
    all_issues.extend(validate_secret_strength(jwt_secret, 'JWT_SECRET_KEY'))
    all_issues.extend(validate_secret_strength(refresh_secret, 'JWT_REFRESH_SECRET_KEY'))
    
    # Validate database configuration
    database_url = os.getenv('DATABASE_URL', '')
    all_issues.extend(validate_database_security(database_url))
    
    # Validate CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', '[]')
    try:
        import json
        origins_list = json.loads(cors_origins)
        all_issues.extend(validate_cors_security(origins_list))
    except:
        all_issues.append("CORS_ORIGINS is not valid JSON")
    
    # Check for development settings in production
    if os.getenv('ENVIRONMENT') == 'production':
        if os.getenv('DEBUG', 'false').lower() == 'true':
            all_issues.append("DEBUG should be false in production")
    
    # Report results
    if all_issues:
        print("❌ SECURITY ISSUES FOUND:")
        for issue in all_issues:
            print(f"  • {issue}")
        print(f"\nTotal Issues: {len(all_issues)}")
        print("Please fix these issues before production deployment.")
        sys.exit(1)
    else:
        print("✅ All security configurations passed validation")
        print("Environment is ready for production deployment.")

if __name__ == "__main__":
    main()
```

---

## 🔐 **AUTHENTICATION & AUTHORIZATION**

### **JWT Configuration**

#### **Secure JWT Implementation**
```python
# backend/app/core/security.py

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

class SecurityManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.refresh_secret_key = os.getenv("JWT_REFRESH_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
        
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create secure JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=self.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def create_refresh_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create secure JWT refresh token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=self.refresh_token_expire_days
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.refresh_secret_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        secret_key = (
            self.secret_key if token_type == "access" 
            else self.refresh_secret_key
        )
        
        try:
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                return None
                
            # Check if token is blacklisted
            jti = payload.get("jti")
            if self.is_token_blacklisted(jti):
                return None
                
            return payload
            
        except JWTError:
            return None
    
    def is_token_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        # Implement Redis-based blacklist check
        return False  # Placeholder
```

#### **Role-Based Access Control (RBAC)**
```python
# backend/app/core/rbac.py

from enum import Enum
from typing import List, Dict, Set

class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class Permission(str, Enum):
    # Investigation permissions
    READ_INVESTIGATIONS = "read_investigations"
    WRITE_INVESTIGATIONS = "write_investigations"
    DELETE_INVESTIGATIONS = "delete_investigations"
    APPROVE_INVESTIGATIONS = "approve_investigations"
    
    # Agent permissions
    READ_AGENTS = "read_agents"
    WRITE_AGENTS = "write_agents"
    EXECUTE_AGENTS = "execute_agents"
    
    # System permissions
    READ_USERS = "read_users"
    WRITE_USERS = "write_users"
    READ_AUDIT_LOGS = "read_audit_logs"
    SYSTEM_CONFIG = "system_config"
    
    # Data permissions
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    ACCESS_RESTRICTED_SOURCES = "access_restricted_sources"

# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.VIEWER: {
        Permission.READ_INVESTIGATIONS,
        Permission.READ_AGENTS,
    },
    
    UserRole.ANALYST: {
        Permission.READ_INVESTIGATIONS,
        Permission.WRITE_INVESTIGATIONS,
        Permission.READ_AGENTS,
        Permission.EXECUTE_AGENTS,
        Permission.EXPORT_DATA,
    },
    
    UserRole.ADMIN: {
        # Admins have all permissions
        *list(Permission)
    }
}

class RBACManager:
    @staticmethod
    def has_permission(user_role: UserRole, permission: Permission) -> bool:
        """Check if user role has specific permission"""
        return permission in ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def get_user_permissions(user_role: UserRole) -> Set[Permission]:
        """Get all permissions for a user role"""
        return ROLE_PERMISSIONS.get(user_role, set())
    
    @staticmethod
    def can_access_resource(
        user_role: UserRole, 
        resource: str, 
        action: str
    ) -> bool:
        """Check if user can perform action on resource"""
        permission_map = {
            ("investigation", "read"): Permission.READ_INVESTIGATIONS,
            ("investigation", "write"): Permission.WRITE_INVESTIGATIONS,
            ("investigation", "delete"): Permission.DELETE_INVESTIGATIONS,
            ("investigation", "approve"): Permission.APPROVE_INVESTIGATIONS,
            ("agent", "read"): Permission.READ_AGENTS,
            ("agent", "write"): Permission.WRITE_AGENTS,
            ("agent", "execute"): Permission.EXECUTE_AGENTS,
            ("user", "read"): Permission.READ_USERS,
            ("user", "write"): Permission.WRITE_USERS,
            ("audit", "read"): Permission.READ_AUDIT_LOGS,
            ("system", "config"): Permission.SYSTEM_CONFIG,
            ("data", "export"): Permission.EXPORT_DATA,
            ("data", "import"): Permission.IMPORT_DATA,
            ("sources", "restricted"): Permission.ACCESS_RESTRICTED_SOURCES,
        }
        
        permission = permission_map.get((resource, action))
        if not permission:
            return False
            
        return RBACManager.has_permission(user_role, permission)
```

---

## 🛡️ **SECURITY MIDDLEWARE**

### **Advanced Security Middleware Implementation**

#### **Security Headers Middleware**
```python
# backend/app/middleware/security.py

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import os

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add comprehensive security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HTTPS enforcement
        if os.getenv("SECURITY_ENABLE_HTTPS", "false").lower() == "true":
            response.headers["Strict-Transport-Security"] = (
                f"max-age={os.getenv('SECURITY_HSTS_MAX_AGE', '31536000')}; "
                "includeSubDomains; preload"
            )
        
        # Content Security Policy
        if os.getenv("SECURITY_CSP_ENABLED", "false").lower() == "true":
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' wss: ws:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            )
            response.headers["Content-Security-Policy"] = csp
        
        # Other security headers
        response.headers["X-Frame-Options"] = os.getenv("SECURITY_FRAME_OPTIONS", "DENY")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=()"
        )
        
        # Remove server information
        response.headers["Server"] = "ScrapeCraft"
        
        return response
```

#### **Rate Limiting Middleware**
```python
# backend/app/middleware/rate_limit.py

import time
import redis
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting with Redis backend"""
    
    def __init__(self, app, redis_url: str = None):
        super().__init__(app)
        self.redis_client = redis.from_url(
            redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        )
        self.requests_per_window = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address or user ID)
        client_id = self._get_client_identifier(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.requests_per_window),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + self.window_seconds)
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_window)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time()) + self.window_seconds
        )
        
        return response
    
    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get authenticated user ID first
        if hasattr(request.state, 'user') and request.state.user:
            return f"user:{request.state.user.id}"
        
        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit"""
        key = f"rate_limit:{client_id}"
        current_requests = await self.redis_client.get(key)
        
        if current_requests is None:
            # First request in window
            await self.redis_client.setex(
                key, 
                self.window_seconds, 
                1
            )
            return True
        
        if int(current_requests) >= self.requests_per_window:
            return False
        
        # Increment counter
        await self.redis_client.incr(key)
        return True
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        key = f"rate_limit:{client_id}"
        current_requests = await self.redis_client.get(key)
        
        if current_requests is None:
            return self.requests_per_window
        
        return max(0, self.requests_per_window - int(current_requests))
```

---

## 🔒 **DATABASE SECURITY**

### **Secure Database Configuration**

#### **PostgreSQL Security Setup**
```sql
-- Database security configuration for production

-- 1. Create secure database user
CREATE USER osint_os_user WITH PASSWORD 'secure_password_here';

-- 2. Create database with restricted permissions
CREATE DATABASE osint_os_prod OWNER osint_os_user;

-- 3. Grant necessary permissions only
GRANT CONNECT ON DATABASE osint_os_prod TO osint_os_user;
GRANT USAGE ON SCHEMA public TO osint_os_user;
GRANT CREATE ON SCHEMA public TO osint_os_user;

-- 4. Set up Row Level Security (RLS)
ALTER TABLE investigations ENABLE ROW LEVEL SECURITY;
ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- 5. Create RLS policies
CREATE POLICY investigation_access ON investigations
    FOR ALL TO osint_os_user
    USING (
        created_by = current_user 
        OR current_user = 'admin'
    );

CREATE POLICY evidence_access ON evidence
    FOR ALL TO osint_os_user
    USING (
        investigation_id IN (
            SELECT id FROM investigations 
            WHERE created_by = current_user 
            OR current_user = 'admin'
        )
    );

-- 6. Audit trigger setup
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, NULL, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, operation, user_id, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, current_user, to_jsonb(OLD), NULL);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 7. Apply audit triggers to sensitive tables
CREATE TRIGGER investigations_audit
    AFTER INSERT OR UPDATE OR DELETE ON investigations
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER evidence_audit
    AFTER INSERT OR UPDATE OR DELETE ON evidence
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
```

#### **Database Connection Security**
```python
# backend/app/core/database.py

import ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Secure database connection configuration
def create_secure_database_engine():
    """Create database engine with security best practices"""
    
    database_url = os.getenv("DATABASE_URL")
    
    # SSL configuration for secure connections
    ssl_context = ssl.create_default_context()
    if os.getenv("DATABASE_SSL_CA"):
        ssl_context.load_verify_locations(os.getenv("DATABASE_SSL_CA"))
    if os.getenv("DATABASE_SSL_CERT") and os.getenv("DATABASE_SSL_KEY"):
        ssl_context.load_cert_chain(
            os.getenv("DATABASE_SSL_CERT"),
            os.getenv("DATABASE_SSL_KEY")
        )
    
    # Create engine with security settings
    engine = create_engine(
        database_url,
        # Connection security
        connect_args={
            "sslcontext": ssl_context,
            "sslmode": os.getenv("DATABASE_SSL_MODE", "require"),
            "connect_timeout": 10,
        },
        # Pool security
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections every hour
        # Query security
        echo=False,  # Disable SQL logging in production
        echo_pool=False,
        # Performance optimization
        isolation_level="READ_COMMITTED",
    )
    
    return engine

# Session management with security
SessionLocal = sessionmaker(
    bind=create_secure_database_engine(),
    autocommit=False,
    autoflush=False,
)

def get_secure_db():
    """Get database session with security context"""
    db = SessionLocal()
    try:
        # Set session security context
        db.execute("SET ROLE osint_os_user")
        yield db
    finally:
        db.close()
```

---

## 📊 **AUDIT LOGGING & MONITORING**

### **Comprehensive Audit System**

#### **Audit Log Configuration**
```python
# backend/app/core/audit.py

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import structlog

class AuditEventType(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIG = "system_config"
    SECURITY_EVENT = "security_event"
    API_ACCESS = "api_access"
    AGENT_EXECUTION = "agent_execution"

class AuditSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLogger:
    def __init__(self):
        self.logger = structlog.get_logger("audit")
    
    def log_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.LOW,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        """Log comprehensive audit event"""
        
        audit_event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type.value,
            "severity": severity.value,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "details": details or {},
            "error_message": error_message,
        }
        
        # Log to structured logger
        if success:
            self.logger.info("audit_event", **audit_event)
        else:
            self.logger.error("audit_event", **audit_event)
        
        # Store in database for long-term storage
        self._store_audit_event(audit_event)
    
    def _store_audit_event(self, event: Dict[str, Any]):
        """Store audit event in database"""
        # Implementation depends on your database setup
        pass

# Usage example
audit_logger = AuditLogger()

# Log authentication attempt
audit_logger.log_event(
    event_type=AuditEventType.AUTHENTICATION,
    user_id="user-123",
    action="login",
    ip_address="192.168.1.100",
    user_agent="Mozilla/5.0...",
    success=True,
    details={"login_method": "password"}
)
```

---

## 🔍 **SECURITY MONITORING**

### **Security Event Monitoring**

#### **Security Dashboard Configuration**
```python
# backend/app/monitoring/security_monitor.py

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis
from dataclasses import dataclass

@dataclass
class SecurityAlert:
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    details: Dict
    user_id: Optional[str] = None
    ip_address: Optional[str] = None

class SecurityMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.alert_thresholds = {
            "failed_login_attempts": 5,
            "unauthorized_access_attempts": 10,
            "data_export_requests": 50,
            "api_requests_per_minute": 1000,
        }
    
    async def detect_anomalies(self) -> List[SecurityAlert]:
        """Detect security anomalies and generate alerts"""
        alerts = []
        
        # Check for failed login attempts
        failed_logins = await self._check_failed_logins()
        if failed_logins:
            alerts.extend(failed_logins)
        
        # Check for unauthorized access attempts
        unauthorized_attempts = await self._check_unauthorized_access()
        if unauthorized_attempts:
            alerts.extend(unauthorized_attempts)
        
        # Check for unusual data access patterns
        data_anomalies = await self._check_data_access_anomalies()
        if data_anomalies:
            alerts.extend(data_anomalies)
        
        # Check for API rate limit violations
        api_anomalies = await self._check_api_anomalies()
        if api_anomalies:
            alerts.extend(api_anomalies)
        
        return alerts
    
    async def _check_failed_logins(self) -> List[SecurityAlert]:
        """Check for excessive failed login attempts"""
        alerts = []
        
        # Get failed login counts from Redis
        pattern = "failed_login:*"
        keys = self.redis.keys(pattern)
        
        for key in keys:
            count = int(self.redis.get(key) or 0)
            if count >= self.alert_thresholds["failed_login_attempts"]:
                ip_address = key.decode().split(":")[-1]
                
                alert = SecurityAlert(
                    alert_type="brute_force_attempt",
                    severity="HIGH",
                    message=f"Excessive failed login attempts from {ip_address}",
                    timestamp=datetime.utcnow(),
                    details={"failed_attempts": count},
                    ip_address=ip_address
                )
                alerts.append(alert)
        
        return alerts
    
    async def _check_unauthorized_access(self) -> List[SecurityAlert]:
        """Check for unauthorized access attempts"""
        alerts = []
        
        # Implementation for checking unauthorized access
        # This would track 403 responses and suspicious patterns
        
        return alerts
    
    async def _check_data_access_anomalies(self) -> List[SecurityAlert]:
        """Check for unusual data access patterns"""
        alerts = []
        
        # Check for excessive data exports
        export_pattern = "data_export:*"
        keys = self.redis.keys(export_pattern)
        
        for key in keys:
            count = int(self.redis.get(key) or 0)
            if count >= self.alert_thresholds["data_export_requests"]:
                user_id = key.decode().split(":")[-1]
                
                alert = SecurityAlert(
                    alert_type="excessive_data_export",
                    severity="MEDIUM",
                    message=f"Excessive data export requests by user {user_id}",
                    timestamp=datetime.utcnow(),
                    details={"export_count": count},
                    user_id=user_id
                )
                alerts.append(alert)
        
        return alerts
    
    async def _check_api_anomalies(self) -> List[SecurityAlert]:
        """Check for API usage anomalies"""
        alerts = []
        
        # Implementation for API anomaly detection
        # This would track unusual API usage patterns
        
        return alerts
```

---

## 🚀 **PRODUCTION DEPLOYMENT SECURITY**

### **Security Deployment Checklist**

#### **Pre-Deployment Security Checklist**
```bash
#!/bin/bash
# security-deployment-checklist.sh

echo "🔒 ScrapeCraft OSINT Security Deployment Checklist"
echo "=================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
}

check_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Environment Security
echo "📋 Environment Security"
if [ "$ENVIRONMENT" = "production" ]; then
    check_pass "Environment set to production"
else
    check_fail "Environment not set to production"
fi

if [ "$DEBUG" = "false" ]; then
    check_pass "Debug mode disabled"
else
    check_fail "Debug mode must be disabled in production"
fi

# 2. Secret Security
echo "🔐 Secret Configuration"
if [ ${#JWT_SECRET_KEY} -ge 32 ]; then
    check_pass "JWT secret key length adequate"
else
    check_fail "JWT secret key too short (min 32 characters)"
fi

if [ "$JWT_SECRET_KEY" != "your-secret-key" ]; then
    check_pass "JWT secret key changed from default"
else
    check_fail "JWT secret key still using default value"
fi

# 3. Database Security
echo "🗄️  Database Security"
if [[ $DATABASE_URL == *"sslmode=require"* ]]; then
    check_pass "Database SSL enabled"
else
    check_fail "Database SSL not enabled"
fi

# 4. CORS Security
echo "🌐 CORS Configuration"
if [[ $CORS_ORIGINS != *"localhost"* ]]; then
    check_pass "CORS origins configured for production"
else
    check_fail "CORS origins include localhost"
fi

# 5. Security Headers
echo "🛡️  Security Headers"
if [ "$SECURITY_ENABLE_HTTPS" = "true" ]; then
    check_pass "HTTPS enforcement enabled"
else
    check_warning "HTTPS enforcement not enabled"
fi

if [ "$SECURITY_CSP_ENABLED" = "true" ]; then
    check_pass "Content Security Policy enabled"
else
    check_warning "Content Security Policy not enabled"
fi

# 6. Monitoring Setup
echo "📊 Monitoring Configuration"
if [ "$AUDIT_LOGGING_ENABLED" = "true" ]; then
    check_pass "Audit logging enabled"
else
    check_fail "Audit logging must be enabled"
fi

if [ "$SECURITY_MONITORING_ENABLED" = "true" ]; then
    check_pass "Security monitoring enabled"
else
    check_warning "Security monitoring not enabled"
fi

echo "=================================================="
echo "Security checklist complete!"
```

---

## 📋 **SECURITY POLICIES**

### **Security Policy Document**

#### **Access Control Policy**
1. **Principle of Least Privilege**: Users only get access to resources they need
2. **Role-Based Access**: Three-tier role system (Viewer, Analyst, Admin)
3. **Multi-Factor Authentication**: Required for admin access
4. **Session Management**: 30-minute session timeout with refresh tokens
5. **IP Restrictions**: Optional IP whitelisting for admin accounts

#### **Data Protection Policy**
1. **Encryption at Rest**: All sensitive data encrypted in database
2. **Encryption in Transit**: TLS 1.3 for all communications
3. **Data Classification**: Public, Internal, Confidential, Secret, Top Secret
4. **Data Retention**: Configurable retention policies based on classification
5. **Data Disposal**: Secure deletion methods for sensitive data

#### **Incident Response Policy**
1. **Detection**: Automated monitoring and alerting
2. **Containment**: Immediate isolation of affected systems
3. **Eradication**: Remove threats and vulnerabilities
4. **Recovery**: Restore operations and verify security
5. **Lessons Learned**: Post-incident analysis and improvement

---

## 🔧 **TROUBLESHOOTING SECURITY ISSUES**

### **Common Security Issues and Solutions**

#### **Authentication Issues**
```bash
# Check JWT configuration
python -c "
import os
print('JWT Secret Length:', len(os.getenv('JWT_SECRET_KEY', '')))
print('JWT Secret Set:', bool(os.getenv('JWT_SECRET_KEY')))
"

# Test token generation
python -c "
from app.core.security import SecurityManager
sm = SecurityManager()
token = sm.create_access_token({'user_id': 'test'})
print('Token Generated:', bool(token))
print('Token Sample:', token[:50] + '...')
"
```

#### **CORS Issues**
```bash
# Test CORS configuration
curl -H "Origin: https://your-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/health -v
```

#### **Rate Limiting Issues**
```bash
# Check Redis connection for rate limiting
redis-cli ping

# Check rate limit keys
redis-cli keys "rate_limit:*"

# Monitor rate limiting in real-time
redis-cli monitor | grep "rate_limit"
```

---

## 📞 **SECURITY SUPPORT**

### **Security Incident Reporting**
- **Email**: security@osint-os.com
- **Emergency**: security-emergency@osint-os.com
- **PGP Key**: Available on request for secure communications

### **Security Team Contacts**
- **Chief Information Security Officer (CISO)**: ciso@osint-os.com
- **Security Engineering**: security-engineering@osint-os.com
- **Incident Response**: incident-response@osint-os.com

---

## 📚 **ADDITIONAL RESOURCES**

### **Security Best Practices**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls](https://www.cisecurity.org/controls/)
- [SANS Security Resources](https://www.sans.org/)

### **Compliance Frameworks**
- [GDPR Compliance](https://gdpr.eu/)
- [CCPA Compliance](https://oag.ca.gov/privacy/ccpa)
- [FedRAMP](https://www.fedramp.gov/)
- [ISO 27001](https://www.iso.org/isoiec-27001-information-security.html)

---

**Document Classification**: Internal Use  
**Next Review**: 6 months from last update  
**Version Control**: Maintained in Git repository  
**Distribution**: Security team, DevOps, System Administrators

---

*This security configuration guide is part of the ScrapeCraft OSINT platform's comprehensive security documentation. For the latest updates and additional security resources, visit the [Security Documentation](./docs/security/).*