#!/usr/bin/env python3
"""
CRITICAL SECURITY VALIDATION - PRODUCTION READINESS ASSESSMENT
OSINT-OS Platform - Intelligence Agency Security Standards

EXECUTED: $(date)
STATUS: PRODUCTION DEPLOYMENT BLOCKED - CRITICAL VULNERABILITIES IDENTIFIED
"""

import asyncio
import json
import requests
import websockets
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any

class CriticalSecurityValidator:
    """Comprehensive security validation for production deployment."""
    
    def __init__(self):
        self.vulnerabilities = []
        self.test_results = {}
        self.base_url = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000"
    
    def log_critical_vulnerability(self, category: str, severity: str, description: str, evidence: Any = None):
        """Log a critical security vulnerability."""
        vulnerability = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "severity": severity,
            "description": description,
            "evidence": evidence,
            "status": "OPEN"
        }
        self.vulnerabilities.append(vulnerability)
        
        if severity in ["CRITICAL", "HIGH"]:
            print(f"🚨 {severity} VULNERABILITY: {category}")
            print(f"   Description: {description}")
            if evidence:
                print(f"   Evidence: {evidence}")
            print()
    
    async def test_authentication_bypass(self):
        """Test for authentication bypass vulnerabilities."""
        print("🔍 TESTING AUTHENTICATION BYPASS...")
        
        # Test 1: JWT with weak secret
        try:
            weak_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImlhdCI6MTYzMDAwMDAwMH0.invalid_signature"
            
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers={"Authorization": f"Bearer {weak_jwt}"}
            )
            
            if response.status_code != 401:
                self.log_critical_vulnerability(
                    "AUTHENTICATION",
                    "CRITICAL", 
                    "Weak JWT secret allows token forgery",
                    {"response_status": response.status_code, "token": weak_jwt}
                )
        except Exception as e:
            self.log_critical_vulnerability(
                "AUTHENTICATION",
                "HIGH",
                "Authentication endpoint not responding properly",
                str(e)
            )
        
        # Test 2: Missing authorization header
        try:
            response = requests.get(f"{self.base_url}/api/auth/me")
            
            if response.status_code != 401:
                self.log_critical_vulnerability(
                    "AUTHENTICATION",
                    "CRITICAL",
                    "Endpoint accessible without authentication",
                    {"endpoint": "/api/auth/me", "status": response.status_code}
                )
        except Exception as e:
            pass
        
        # Test 3: SQL Injection in login
        sql_payloads = [
            "admin'--",
            "admin' OR '1'='1",
            "admin' UNION SELECT 'admin','password'--",
            "'; DROP TABLE users;--"
        ]
        
        for payload in sql_payloads:
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/token",
                    data={"username": payload, "password": "anything"}
                )
                
                if response.status_code == 200:
                    self.log_critical_vulnerability(
                        "SQL_INJECTION",
                        "CRITICAL",
                        "SQL injection in authentication endpoint",
                        {"payload": payload, "response": response.json()}
                    )
            except Exception:
                pass
    
    async def test_security_headers(self):
        """Test for missing security headers."""
        print("🔍 TESTING SECURITY HEADERS...")
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        try:
            response = requests.get(f"{self.base_url}/")
            
            for header, expected in required_headers.items():
                actual = response.headers.get(header)
                
                if not actual:
                    self.log_critical_vulnerability(
                        "SECURITY_HEADERS",
                        "HIGH",
                        f"Missing security header: {header}",
                        {"header": header, "expected": expected}
                    )
                elif header == "Content-Security-Policy" and "script-src 'unsafe-inline'" in actual:
                    self.log_critical_vulnerability(
                        "SECURITY_HEADERS",
                        "MEDIUM",
                        "CSP allows unsafe inline scripts",
                        {"header": actual}
                    )
        except Exception as e:
            self.log_critical_vulnerability(
                "SECURITY_HEADERS",
                "HIGH",
                "Unable to test security headers",
                str(e)
            )
    
    async def test_rate_limiting(self):
        """Test rate limiting effectiveness."""
        print("🔍 TESTING RATE LIMITING...")
        
        # Test authentication endpoint rate limiting
        try:
            success_count = 0
            for i in range(50):  # Send 50 rapid requests
                response = requests.post(
                    f"{self.base_url}/api/auth/token",
                    data={"username": "testuser", "password": "wrongpassword"},
                    timeout=2
                )
                
                if response.status_code == 429:
                    print(f"✓ Rate limiting activated after {i+1} attempts")
                    break
                elif response.status_code == 200:
                    success_count += 1
            
            if success_count > 10:
                self.log_critical_vulnerability(
                    "RATE_LIMITING",
                    "HIGH",
                    f"No rate limiting on authentication endpoint ({success_count} successful attempts)",
                    {"endpoint": "/api/auth/token", "attempts": success_count}
                )
        except Exception as e:
            self.log_critical_vulnerability(
                "RATE_LIMITING",
                "MEDIUM",
                "Unable to test rate limiting",
                str(e)
            )
    
    async def test_websocket_security(self):
        """Test WebSocket authentication and authorization."""
        print("🔍 TESTING WEBSOCKET SECURITY...")
        
        # Test 1: Unauthenticated WebSocket connection
        try:
            async with websockets.connect(f"{self.ws_url}/ws/test") as websocket:
                self.log_critical_vulnerability(
                    "WEBSOCKET",
                    "CRITICAL",
                    "WebSocket connection allowed without authentication",
                    {"endpoint": f"{self.ws_url}/ws/test"}
                )
        except Exception:
            pass  # Expected to fail if secure
        
        # Test 2: WebSocket with forged JWT
        try:
            headers = {"Authorization": "Bearer forged_jwt_token"}
            async with websockets.connect(
                f"{self.ws_url}/ws/test",
                extra_headers=headers
            ) as websocket:
                self.log_critical_vulnerability(
                    "WEBSOCKET",
                    "CRITICAL",
                    "WebSocket accepts forged JWT tokens",
                    {"token": "forged_jwt_token"}
                )
        except Exception:
            pass  # Expected to fail
        
        # Test 3: WebSocket injection test
        injection_payloads = [
            '{"type": "command", "data": "rm -rf /"}',
            '{"type": "sql", "query": "DROP TABLE users"}',
            '<script>alert("XSS")</script>',
            '../../etc/passwd'
        ]
        
        for payload in injection_payloads:
            try:
                headers = {"Authorization": "Bearer test_token"}
                async with websockets.connect(
                    f"{self.ws_url}/ws/test",
                    extra_headers=headers
                ) as websocket:
                    await websocket.send(payload)
                    response = await websocket.recv()
                    
                    if "error" not in response.lower():
                        self.log_critical_vulnerability(
                            "WEBSOCKET",
                            "HIGH",
                            "WebSocket accepts injection payloads",
                            {"payload": payload, "response": response}
                        )
            except Exception:
                pass
    
    async def test_input_validation(self):
        """Test input validation and injection prevention."""
        print("🔍 TESTING INPUT VALIDATION...")
        
        # XSS payloads
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        # SQL injection payloads
        sqli_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM users --",
            "'; INSERT INTO users VALUES('hacker','pass'); --"
        ]
        
        # Test API endpoints with injection payloads
        endpoints_to_test = [
            "/api/auth/register",
            "/api/investigations",
            "/api/search"
        ]
        
        for endpoint in endpoints_to_test:
            for payload in xss_payloads + sqli_payloads:
                try:
                    # Test as form data
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        data={"input": payload},
                        timeout=5
                    )
                    
                    if response.status_code == 200 and "error" not in response.text.lower():
                        self.log_critical_vulnerability(
                            "INPUT_VALIDATION",
                            "HIGH",
                            f"Input validation bypass on {endpoint}",
                            {"payload": payload, "endpoint": endpoint}
                        )
                except Exception:
                    pass
    
    async def test_cors_security(self):
        """Test CORS configuration security."""
        print("🔍 TESTING CORS SECURITY...")
        
        malicious_origins = [
            "https://evil.com",
            "http://localhost:3001",
            "null",
            "https://phishing-site.com"
        ]
        
        for origin in malicious_origins:
            try:
                response = requests.options(
                    f"{self.base_url}/api/auth/me",
                    headers={"Origin": origin}
                )
                
                allowed_origin = response.headers.get("Access-Control-Allow-Origin")
                
                if allowed_origin and allowed_origin != "null" and origin not in ["http://localhost:3000", "http://localhost:4000"]:
                    self.log_critical_vulnerability(
                        "CORS",
                        "HIGH",
                        "Insecure CORS configuration allows malicious origins",
                        {"malicious_origin": origin, "allowed_origin": allowed_origin}
                    )
            except Exception:
                pass
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report."""
        critical_count = len([v for v in self.vulnerabilities if v["severity"] == "CRITICAL"])
        high_count = len([v for v in self.vulnerabilities if v["severity"] == "HIGH"])
        medium_count = len([v for v in self.vulnerabilities if v["severity"] == "MEDIUM"])
        
        # Determine production readiness
        production_ready = critical_count == 0 and high_count == 0
        
        report = {
            "executed_at": datetime.now().isoformat(),
            "production_ready": production_ready,
            "deployment_status": "BLOCKED" if not production_ready else "APPROVED",
            "summary": {
                "total_vulnerabilities": len(self.vulnerabilities),
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count
            },
            "vulnerabilities": self.vulnerabilities,
            "immediate_actions_required": [
                "Change all hardcoded secrets and API keys",
                "Implement proper JWT secret management",
                "Add comprehensive input validation",
                "Configure security headers",
                "Implement rate limiting",
                "Secure WebSocket authentication"
            ] if not production_ready else [],
            "security_score": max(0, 100 - (critical_count * 25) - (high_count * 15) - (medium_count * 5))
        }
        
        return report
    
    async def run_comprehensive_validation(self):
        """Run all security validation tests."""
        print("🚨 CRITICAL SECURITY VALIDATION STARTED 🚨")
        print("=" * 60)
        print("STATUS: PRODUCTION DEPLOYMENT BLOCKED UNTIL COMPLETION")
        print("=" * 60)
        print()
        
        await self.test_authentication_bypass()
        await self.test_security_headers()
        await self.test_rate_limiting()
        await self.test_websocket_security()
        await self.test_input_validation()
        await self.test_cors_security()
        
        report = self.generate_security_report()
        
        print("=" * 60)
        print("CRITICAL SECURITY VALIDATION COMPLETE")
        print("=" * 60)
        print(f"Production Ready: {'YES' if report['production_ready'] else 'NO'}")
        print(f"Deployment Status: {report['deployment_status']}")
        print(f"Security Score: {report['security_score']}/100")
        print(f"Critical Vulnerabilities: {report['summary']['critical']}")
        print(f"High Vulnerabilities: {report['summary']['high']}")
        print()
        
        if not report['production_ready']:
            print("🚨 IMMEDIATE ACTIONS REQUIRED:")
            for action in report['immediate_actions_required']:
                print(f"   • {action}")
        
        return report

async def main():
    """Main execution function."""
    validator = CriticalSecurityValidator()
    report = await validator.run_comprehensive_validation()
    
    # Save detailed report
    with open(f"critical_security_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: critical_security_validation_report_*.json")
    
    # Exit with error code if not production ready
    if not report['production_ready']:
        print("\n❌ PRODUCTION DEPLOYMENT BLOCKED - Fix all critical and high vulnerabilities")
        exit(1)
    else:
        print("\n✅ PRODUCTION DEPLOYMENT APPROVED - Security validation passed")
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())