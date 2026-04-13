"""
Enhanced WebSocket service with proper authentication and security for OSINT-OS.
"""

from fastapi import WebSocket, HTTPException, status
from typing import Dict, List, Any, Optional, cast
import json
import asyncio
import logging
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

logger = logging.getLogger(__name__)


class SecureConnectionManager:
    """Manages secure WebSocket connections with authentication."""

    db_persistence: Optional[Any]
    active_connections: Dict[str, List[WebSocket]]
    pipeline_states: Dict[str, Dict[str, Any]]
    connection_metadata: Dict[str, Dict[str, Any]]
    is_healthy: bool
    last_health_check: datetime
    authenticated_connections: Dict[str, Dict[str, Any]]

    def __init__(self) -> None:
        # Initialize database persistence service
        try:
            from .database import DatabasePersistenceService

            self.db_persistence = DatabasePersistenceService()
            self.db_persistence.initialize_database()
            logger.info("WebSocket database persistence service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket database persistence: {e}")
            self.db_persistence = None

        # Connection management
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.pipeline_states: Dict[str, Dict[str, Any]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.authenticated_connections: Dict[str, Dict[str, Any]] = {}

        # Health tracking
        self.is_healthy = True
        self.last_health_check = datetime.now()

        # Rate limiting
        self.connection_attempts: Dict[str, List[datetime]] = {}
        self.max_connections_per_ip = 10
        self.connection_timeout = 300  # 5 minutes

        logger.info("Secure WebSocket connection manager initialized")

    def _get_client_ip(self, websocket: WebSocket) -> str:
        """Extract client IP from WebSocket connection."""
        client_host = websocket.client.host if websocket.client else "unknown"
        forwarded_for = websocket.headers.get("x-forwarded-for")
        if forwarded_for:
            client_host = forwarded_for.split(",")[0].strip()
        return client_host

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client has exceeded connection rate limit."""
        now = datetime.now()
        if client_ip not in self.connection_attempts:
            self.connection_attempts[client_ip] = []

        # Remove old attempts (older than 1 hour)
        self.connection_attempts[client_ip] = [
            attempt
            for attempt in self.connection_attempts[client_ip]
            if now - attempt < timedelta(hours=1)
        ]

        # Check if under limit (max 30 connections per hour)
        if len(self.connection_attempts[client_ip]) >= 30:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False

        self.connection_attempts[client_ip].append(now)
        return True

    async def _authenticate_websocket(
        self, websocket: WebSocket
    ) -> Optional[Dict[str, Any]]:
        """Authenticate WebSocket connection using JWT token or API key."""
        try:
            # Method 1: JWT Token in Authorization header
            auth_header = websocket.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                try:
                    payload = jwt.decode(
                        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
                    )
                    user_id = payload.get("sub")
                    if user_id:
                        return {
                            "user_id": user_id,
                            "method": "jwt",
                            "permissions": payload.get("permissions", []),
                            "exp": payload.get("exp"),
                        }
                except JWTError as e:
                    logger.warning(f"JWT authentication failed: {e}")

            # Method 2: API Key in headers
            api_key = websocket.headers.get("x-api-key")
            if api_key:
                # Validate API key (implement your validation logic)
                if await self._validate_api_key(api_key):
                    return {
                        "user_id": f"api_key_{api_key[:8]}",
                        "method": "api_key",
                        "permissions": ["read", "write"],
                        "exp": None,
                    }

            # Method 3: Query parameter (less secure, for development only)
            if settings.ENVIRONMENT == "development":
                token_param = websocket.query_params.get("token")
                if token_param:
                    try:
                        payload = jwt.decode(
                            token_param,
                            settings.JWT_SECRET,
                            algorithms=[settings.JWT_ALGORITHM],
                        )
                        user_id = payload.get("sub")
                        if user_id:
                            return {
                                "user_id": user_id,
                                "method": "query_param",
                                "permissions": payload.get("permissions", []),
                                "exp": payload.get("exp"),
                            }
                    except JWTError:
                        pass

            logger.warning(
                "WebSocket authentication failed - no valid credentials provided"
            )
            return None

        except Exception as e:
            logger.error(f"Error during WebSocket authentication: {e}")
            return None

    async def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key against database or external service."""
        try:
            # Implement your API key validation logic here
            # For now, basic format validation
            if len(api_key) >= 32 and api_key.startswith("osint_"):
                return True
            return False
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return False

    async def connect(self, websocket: WebSocket, pipeline_id: str) -> bool:
        """
        Accept and authenticate a new WebSocket connection.
        Returns True if connection is successful, False otherwise.
        """
        client_ip = self._get_client_ip(websocket)

        # Rate limiting check
        if not self._check_rate_limit(client_ip):
            await websocket.close(code=429, reason="Rate limit exceeded")
            return False

        # Authentication
        auth_info = await self._authenticate_websocket(websocket)
        if not auth_info:
            await websocket.close(code=4011, reason="Unauthorized")
            return False

        # Check token expiration
        if auth_info.get("exp"):
            try:
                exp_timestamp = auth_info["exp"]
                if datetime.now().timestamp() > exp_timestamp:
                    await websocket.close(code=4011, reason="Token expired")
                    return False
            except Exception as e:
                logger.error(f"Token expiration check failed: {e}")
                await websocket.close(code=4011, reason="Invalid token")
                return False

        # Accept connection
        try:
            await websocket.accept()

            # Store connection with metadata
            connection_id = f"{auth_info['user_id']}_{datetime.now().timestamp()}"

            if pipeline_id not in self.active_connections:
                self.active_connections[pipeline_id] = []
                self.pipeline_states[pipeline_id] = {
                    "urls": [],
                    "schema": {},
                    "generated_code": "",
                    "status": "connected",
                    "created_at": datetime.now().isoformat(),
                }

            # Add connection
            self.active_connections[pipeline_id].append(websocket)

            # Store authentication metadata
            self.authenticated_connections[connection_id] = {
                "websocket": websocket,
                "auth_info": auth_info,
                "pipeline_id": pipeline_id,
                "connected_at": datetime.now(),
                "client_ip": client_ip,
                "last_activity": datetime.now(),
            }

            # Store connection metadata
            self.connection_metadata[connection_id] = {
                "user_id": auth_info["user_id"],
                "auth_method": auth_info["method"],
                "permissions": auth_info["permissions"],
                "client_ip": client_ip,
                "connected_at": datetime.now().isoformat(),
                "pipeline_id": pipeline_id,
            }

            logger.info(
                f"WebSocket authenticated and connected: {auth_info['user_id']} to {pipeline_id}"
            )

            # Send welcome message
            await self.send_personal_message(
                {
                    "type": "connection_established",
                    "connection_id": connection_id,
                    "pipeline_id": pipeline_id,
                    "timestamp": datetime.now().isoformat(),
                    "permissions": auth_info["permissions"],
                },
                websocket,
            )

            return True

        except Exception as e:
            logger.error(f"Error accepting WebSocket connection: {e}")
            try:
                await websocket.close(code=4000, reason="Connection error")
            except:
                pass
            return False

    async def disconnect(self, websocket: WebSocket, pipeline_id: str) -> None:
        """Remove a WebSocket connection and clean up authentication data."""
        try:
            # Find and remove from active connections
            if pipeline_id in self.active_connections:
                if websocket in self.active_connections[pipeline_id]:
                    self.active_connections[pipeline_id].remove(websocket)

                # Clean up empty pipeline states
                if not self.active_connections[pipeline_id]:
                    del self.active_connections[pipeline_id]
                    if pipeline_id in self.pipeline_states:
                        del self.pipeline_states[pipeline_id]

            # Find and remove authentication data
            connections_to_remove = []
            for conn_id, conn_data in self.authenticated_connections.items():
                if conn_data["websocket"] == websocket:
                    connections_to_remove.append(conn_id)

            for conn_id in connections_to_remove:
                del self.authenticated_connections[conn_id]
                if conn_id in self.connection_metadata:
                    del self.connection_metadata[conn_id]

            logger.info(f"WebSocket disconnected from pipeline: {pipeline_id}")

        except Exception as e:
            logger.error(f"Error during WebSocket disconnect: {e}")

    async def check_permissions(
        self, websocket: WebSocket, required_permission: str
    ) -> bool:
        """Check if WebSocket connection has required permission."""
        try:
            # Find connection authentication data
            for conn_data in self.authenticated_connections.values():
                if conn_data["websocket"] == websocket:
                    permissions = conn_data["auth_info"].get("permissions", [])
                    return required_permission in permissions or "admin" in permissions
            return False
        except Exception as e:
            logger.error(f"Error checking WebSocket permissions: {e}")
            return False

    async def send_personal_message(
        self, message: Dict[str, Any], websocket: WebSocket
    ) -> None:
        """Send a message to a specific authenticated WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            # Connection might be closed, schedule cleanup
            asyncio.create_task(self._cleanup_connection(websocket))

    async def _cleanup_connection(self, websocket: WebSocket) -> None:
        """Clean up a closed or failed connection."""
        try:
            for pipeline_id, connections in self.active_connections.items():
                if websocket in connections:
                    await self.disconnect(websocket, pipeline_id)
                    break
        except Exception as e:
            logger.error(f"Error during connection cleanup: {e}")

    async def broadcast_to_pipeline(
        self, message: Dict[str, Any], pipeline_id: str
    ) -> None:
        """Broadcast a message to all authenticated connections in a pipeline."""
        if pipeline_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[pipeline_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected.append(connection)

            # Clean up disconnected connections
            for connection in disconnected:
                await self.disconnect(connection, pipeline_id)

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about authenticated connections."""
        total_connections = sum(
            len(conns) for conns in self.active_connections.values()
        )
        unique_users = len(
            set(
                conn_data["auth_info"]["user_id"]
                for conn_data in self.authenticated_connections.values()
            )
        )

        auth_methods: Dict[str, int] = {}
        for conn_data in self.authenticated_connections.values():
            method = conn_data["auth_info"]["method"]
            auth_methods[method] = auth_methods.get(method, 0) + 1

        return {
            "total_connections": total_connections,
            "unique_users": unique_users,
            "auth_methods": auth_methods,
            "pipeline_count": len(self.active_connections),
            "authenticated_connections": len(self.authenticated_connections),
            "is_healthy": self.is_healthy,
            "last_health_check": self.last_health_check.isoformat(),
        }


# Global secure connection manager instance
secure_connection_manager = SecureConnectionManager()

# For backward compatibility, create aliases
connection_manager = secure_connection_manager
ConnectionManager = SecureConnectionManager
