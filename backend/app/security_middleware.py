"""
Security middleware for OSINT-OS platform.
"""

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import RequestResponseEndpoint
import logging
import time
from typing import Callable
from app.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add comprehensive security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        
        # Content Security Policy
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Adjust based on your needs
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # Other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        
        # HSTS in production
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware."""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls  # Number of calls allowed
        self.period = period  # Time period in seconds
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Clean old entries
        self._cleanup_old_entries(current_time)
        
        # Check rate limit
        if client_ip in self.clients:
            requests = self.clients[client_ip]
            if len(requests) >= self.calls:
                # Check if all requests are within the time window
                if current_time - requests[0] < self.period:
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded"
                    )
        
        # Record this request
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        self.clients[client_ip].append(current_time)
        
        return await call_next(request)
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to direct connection
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries outside the time window."""
        cutoff_time = current_time - self.period
        
        for client_ip in list(self.clients.keys()):
            self.clients[client_ip] = [
                req_time for req_time in self.clients[client_ip]
                if req_time > cutoff_time
            ]
            
            # Remove empty client entries
            if not self.clients[client_ip]:
                del self.clients[client_ip]


class InputValidationMiddleware(BaseHTTPMiddleware):
    """Input validation and sanitization middleware."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Request entity too large"
            )
        
        # Validate content type
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith(("application/json", "multipart/form-data", "application/x-www-form-urlencoded")):
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Unsupported media type"
                )
        
        return await call_next(request)


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Audit logging middleware for security monitoring."""
    
    def __init__(self, app):
        super().__init__(app)
        self.sensitive_endpoints = {
            "/api/auth/login", "/api/auth/register", "/api/auth/refresh",
            "/api/investigations", "/api/osint", "/api/admin"
        }
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        
        # Log request
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Log successful request
            if self._should_log_request(request.url.path):
                logger.info(
                    f"API Request: {request.method} {request.url.path} - "
                    f"Status: {status_code} - IP: {client_ip} - "
                    f"User-Agent: {user_agent[:100]}"
                )
            
            return response
            
        except Exception as e:
            # Log error
            logger.error(
                f"API Error: {request.method} {request.url.path} - "
                f"Error: {str(e)} - IP: {client_ip}"
            )
            raise
        
        finally:
            # Log response time
            duration = time.time() - start_time
            if duration > 5.0:  # Log slow requests
                logger.warning(
                    f"Slow Request: {request.method} {request.url.path} - "
                    f"Duration: {duration:.2f}s - IP: {client_ip}"
                )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _should_log_request(self, path: str) -> bool:
        """Determine if request should be logged."""
        # Skip health checks and static files
        skip_patterns = ["/health", "/metrics", "/static/", "/favicon.ico"]
        if any(pattern in path for pattern in skip_patterns):
            return False
        
        # Always log sensitive endpoints
        if any(sensitive in path for sensitive in self.sensitive_endpoints):
            return True
        
        # Log all non-GET requests to sensitive areas
        return True


def configure_security_middleware(app):
    """Configure all security middleware for the application."""
    
    # CORS middleware (already configured in main.py, but we can enhance it)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Requested-With"],
    )
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware, calls=100, period=60)
    
    # Input validation middleware
    app.add_middleware(InputValidationMiddleware)
    
    # Audit logging middleware
    app.add_middleware(AuditLoggingMiddleware)
    
    logger.info("Security middleware configured")
