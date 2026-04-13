#!/usr/bin/env python3
"""
Comprehensive Security Validation Test Suite for OSINT-OS Platform
Tests security middleware, authentication, authorization, and vulnerability scenarios
"""

import asyncio
import aiohttp
import hashlib
import json
import time
import uuid
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityTestResult:
    test_name: str
    status: str  # PASS, FAIL, WARN
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    details: Dict[str, Any]
    recommendation: str = ""

class SecurityValidator:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        self.test_results: List[SecurityTestResult] = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def add_result(self, test_name: str, status: str, severity: str, 
                   description: str, details: Dict[str, Any], recommendation: str = ""):
        result = SecurityTestResult(
            test_name=test_name,
            status=status,
            severity=severity,
            description=description,
            details=details,
            recommendation=recommendation
        )
        self.test_results.append(result)
        logger.info(f"Test: {test_name} - {status} ({severity})")
    
    async def test_security_headers(self) -> SecurityTestResult:
        """Test security headers are properly configured"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                headers = dict(response.headers)
                
                required_headers = {
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "DENY",
                    "X-XSS-Protection": "1; mode=block",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                    "Content-Security-Policy": None  # Just check existence
                }
                
                missing_headers = []
                weak_headers = []
                
                for header, expected_value in required_headers.items():
                    if header not in headers:
                        missing_headers.append(header)
                    elif expected_value and headers[header] != expected_value:
                        weak_headers.append(f"{header}: {headers[header]} (expected: {expected_value})")
                
                if missing_headers:
                    status = "FAIL"
                    severity = "HIGH"
                    description = "Missing critical security headers"
                    recommendation = "Configure all security headers in middleware"
                elif weak_headers:
                    status = "WARN"
                    severity = "MEDIUM"
                    description = "Security headers configured but could be stronger"
                    recommendation = "Review and strengthen security header values"
                else:
                    status = "PASS"
                    severity = "LOW"
                    description = "All security headers properly configured"
                    recommendation = ""
                
                self.add_result(
                    "Security Headers Test",
                    status, severity, description,
                    {"headers": headers, "missing": missing_headers, "weak": weak_headers},
                    recommendation
                )
                
        except Exception as e:
            self.add_result(
                "Security Headers Test",
                "FAIL", "HIGH", "Failed to test security headers",
                {"error": str(e)},
                "Ensure server is running and accessible"
            )
    
    async def test_rate_limiting(self) -> SecurityTestResult:
        """Test rate limiting functionality"""
        try:
            # Make rapid requests to test rate limiting
            rapid_requests = []
            start_time = time.time()
            
            for i in range(105):  # Should trigger rate limit if set to 100/min
                async with self.session.get(f"{self.base_url}/health") as response:
                    rapid_requests.append({
                        "request": i + 1,
                        "status": response.status,
                        "timestamp": time.time() - start_time
                    })
                    
                    if response.status == 429:
                        break
            
            # Analyze results
            rate_limit_triggered = any(req["status"] == 429 for req in rapid_requests)
            
            if rate_limit_triggered:
                status = "PASS"
                severity = "LOW"
                description = "Rate limiting is working correctly"
                recommendation = ""
            else:
                status = "FAIL"
                severity = "HIGH"
                description = "Rate limiting not functioning or limits too high"
                recommendation = "Configure proper rate limiting in middleware"
            
            self.add_result(
                "Rate Limiting Test",
                status, severity, description,
                {"requests_made": len(rapid_requests), "rate_limit_triggered": rate_limit_triggered},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "Rate Limiting Test",
                "FAIL", "HIGH", "Failed to test rate limiting",
                {"error": str(e)},
                "Ensure rate limiting middleware is properly configured"
            )
    
    async def test_input_validation(self) -> SecurityTestResult:
        """Test input validation and XSS protection"""
        try:
            # Test various XSS payloads
            xss_payloads = [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "';alert('XSS');//",
                "<svg onload=alert('XSS')>"
            ]
            
            xss_results = []
            
            for payload in xss_payloads:
                # Test in search endpoint
                search_data = {"query": payload}
                async with self.session.post(
                    f"{self.base_url}/api/osint/search",
                    json=search_data
                ) as response:
                    response_text = await response.text()
                    xss_results.append({
                        "payload": payload,
                        "status": response.status,
                        "response_contains_payload": payload in response_text
                    })
            
            # Check if any payload was reflected without sanitization
            vulnerabilities = [r for r in xss_results if r["response_contains_payload"]]
            
            if vulnerabilities:
                status = "FAIL"
                severity = "CRITICAL"
                description = "XSS vulnerabilities detected"
                recommendation = "Implement proper input sanitization and output encoding"
            else:
                status = "PASS"
                severity = "LOW"
                description = "XSS protection working correctly"
                recommendation = ""
            
            self.add_result(
                "Input Validation/XSS Test",
                status, severity, description,
                {"xss_results": xss_results, "vulnerabilities": len(vulnerabilities)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "Input Validation/XSS Test",
                "FAIL", "HIGH", "Failed to test input validation",
                {"error": str(e)},
                "Ensure input validation middleware is properly configured"
            )
    
    async def test_authentication(self) -> SecurityTestResult:
        """Test authentication mechanisms"""
        try:
            auth_results = []
            
            # Test 1: Access protected endpoint without auth
            async with self.session.get(f"{self.base_url}/api/investigations") as response:
                auth_results.append({
                    "test": "unprotected_access",
                    "status": response.status,
                    "expected": 401,
                    "pass": response.status == 401
                })
            
            # Test 2: Login with valid credentials
            login_data = {
                "username": "admin",
                "password": "admin123"  # Default test credentials
            }
            
            async with self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    if "data" in token_data and "access_token" in token_data["data"]:
                        self.auth_token = token_data["data"]["access_token"]
                        auth_results.append({
                            "test": "valid_login",
                            "status": response.status,
                            "expected": 200,
                            "pass": True
                        })
                    else:
                        auth_results.append({
                            "test": "valid_login",
                            "status": response.status,
                            "expected": 200,
                            "pass": False,
                            "error": "No token in response"
                        })
                else:
                    auth_results.append({
                        "test": "valid_login",
                        "status": response.status,
                        "expected": 200,
                        "pass": False
                    })
            
            # Test 3: Access protected endpoint with auth
            if self.auth_token:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                async with self.session.get(
                    f"{self.base_url}/api/investigations",
                    headers=headers
                ) as response:
                    auth_results.append({
                        "test": "protected_access_with_auth",
                        "status": response.status,
                        "expected": 200,
                        "pass": response.status == 200
                    })
            
            # Test 4: Invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token"}
            async with self.session.get(
                f"{self.base_url}/api/investigations",
                headers=invalid_headers
            ) as response:
                auth_results.append({
                    "test": "invalid_token",
                    "status": response.status,
                    "expected": 401,
                    "pass": response.status == 401
                })
            
            # Evaluate results
            failed_tests = [r for r in auth_results if not r.get("pass", False)]
            
            if failed_tests:
                status = "FAIL"
                severity = "HIGH"
                description = "Authentication mechanisms have vulnerabilities"
                recommendation = "Review and fix authentication implementation"
            else:
                status = "PASS"
                severity = "LOW"
                description = "Authentication working correctly"
                recommendation = ""
            
            self.add_result(
                "Authentication Test",
                status, severity, description,
                {"auth_results": auth_results, "failed_tests": len(failed_tests)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "Authentication Test",
                "FAIL", "HIGH", "Failed to test authentication",
                {"error": str(e)},
                "Ensure authentication system is properly configured"
            )
    
    async def test_cors_configuration(self) -> SecurityTestResult:
        """Test CORS configuration security"""
        try:
            cors_results = []
            
            # Test preflight request
            headers = {
                "Origin": "http://malicious-site.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
            
            async with self.session.options(
                f"{self.base_url}/api/health",
                headers=headers
            ) as response:
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
                    "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
                    "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
                    "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
                }
                
                # Check if malicious origin is allowed
                allowed_origin = cors_headers["Access-Control-Allow-Origin"]
                if allowed_origin == "*" or allowed_origin == "http://malicious-site.com":
                    cors_results.append({
                        "test": "malicious_origin_allowed",
                        "pass": False,
                        "details": f"Malicious origin allowed: {allowed_origin}"
                    })
                else:
                    cors_results.append({
                        "test": "malicious_origin_allowed",
                        "pass": True,
                        "details": f"Malicious origin properly blocked: {allowed_origin}"
                    })
            
            # Test valid origin
            valid_headers = {
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
            
            async with self.session.options(
                f"{self.base_url}/api/health",
                headers=valid_headers
            ) as response:
                allowed_origin = response.headers.get("Access-Control-Allow-Origin")
                if allowed_origin in ["http://localhost:3000", "http://localhost:4000", None]:
                    cors_results.append({
                        "test": "valid_origin_allowed",
                        "pass": True,
                        "details": f"Valid origin handled: {allowed_origin}"
                    })
                else:
                    cors_results.append({
                        "test": "valid_origin_allowed",
                        "pass": False,
                        "details": f"Valid origin blocked: {allowed_origin}"
                    })
            
            # Evaluate results
            failed_tests = [r for r in cors_results if not r["pass"]]
            
            if failed_tests:
                status = "FAIL"
                severity = "HIGH"
                description = "CORS configuration allows unauthorized origins"
                recommendation = "Restrict CORS to trusted origins only"
            else:
                status = "PASS"
                severity = "LOW"
                description = "CORS configuration is secure"
                recommendation = ""
            
            self.add_result(
                "CORS Configuration Test",
                status, severity, description,
                {"cors_results": cors_results, "cors_headers": cors_headers},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "CORS Configuration Test",
                "FAIL", "MEDIUM", "Failed to test CORS configuration",
                {"error": str(e)},
                "Review CORS middleware configuration"
            )
    
    async def test_sql_injection(self) -> SecurityTestResult:
        """Test SQL injection protection"""
        try:
            sql_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; SELECT * FROM users; --",
                "' UNION SELECT password FROM users --",
                "'; INSERT INTO users VALUES('hacker','pass'); --"
            ]
            
            sql_results = []
            
            for payload in sql_payloads:
                # Test in search endpoint (most likely to interact with database)
                search_data = {"query": payload}
                async with self.session.post(
                    f"{self.base_url}/api/osint/search",
                    json=search_data
                ) as response:
                    response_text = await response.text()
                    
                    # Check for SQL error messages
                    sql_errors = [
                        "syntax error", "mysql_fetch", "ora-", "microsoft odbc",
                        "sqlite_", "postgresql", "column", "table", "database"
                    ]
                    
                    has_sql_error = any(error.lower() in response_text.lower() for error in sql_errors)
                    
                    sql_results.append({
                        "payload": payload,
                        "status": response.status,
                        "has_sql_error": has_sql_error,
                        "response_length": len(response_text)
                    })
            
            # Check for SQL injection indicators
            vulnerabilities = [r for r in sql_results if r["has_sql_error"]]
            
            if vulnerabilities:
                status = "FAIL"
                severity = "CRITICAL"
                description = "SQL injection vulnerabilities detected"
                recommendation = "Use parameterized queries and input validation"
            else:
                status = "PASS"
                severity = "LOW"
                description = "SQL injection protection working"
                recommendation = ""
            
            self.add_result(
                "SQL Injection Test",
                status, severity, description,
                {"sql_results": sql_results, "vulnerabilities": len(vulnerabilities)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "SQL Injection Test",
                "FAIL", "HIGH", "Failed to test SQL injection protection",
                {"error": str(e)},
                "Ensure proper input validation and parameterized queries"
            )
    
    async def test_websocket_security(self) -> SecurityTestResult:
        """Test WebSocket authentication and security"""
        try:
            websocket_results = []
            
            # Test 1: Unauthenticated WebSocket connection
            try:
                async with self.session.ws_connect(f"{self.base_url.replace('http', 'ws')}/ws") as ws:
                    websocket_results.append({
                        "test": "unauthenticated_connection",
                        "pass": False,
                        "details": "Unauthenticated WebSocket connection allowed"
                    })
            except Exception as e:
                websocket_results.append({
                    "test": "unauthenticated_connection",
                    "pass": True,
                    "details": f"Unauthenticated connection properly rejected: {str(e)[:100]}"
                })
            
            # Test 2: Authenticated WebSocket connection (if we have token)
            if self.auth_token:
                try:
                    headers = {"Authorization": f"Bearer {self.auth_token}"}
                    async with self.session.ws_connect(
                        f"{self.base_url.replace('http', 'ws')}/ws",
                        headers=headers
                    ) as ws:
                        websocket_results.append({
                            "test": "authenticated_connection",
                            "pass": True,
                            "details": "Authenticated WebSocket connection successful"
                        })
                except Exception as e:
                    websocket_results.append({
                        "test": "authenticated_connection",
                        "pass": False,
                        "details": f"Authenticated connection failed: {str(e)[:100]}"
                    })
            
            # Evaluate results
            failed_tests = [r for r in websocket_results if not r["pass"]]
            
            if failed_tests:
                status = "FAIL"
                severity = "HIGH"
                description = "WebSocket security vulnerabilities detected"
                recommendation = "Implement proper WebSocket authentication"
            else:
                status = "PASS"
                severity = "LOW"
                description = "WebSocket security is properly configured"
                recommendation = ""
            
            self.add_result(
                "WebSocket Security Test",
                status, severity, description,
                {"websocket_results": websocket_results, "failed_tests": len(failed_tests)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "WebSocket Security Test",
                "FAIL", "MEDIUM", "Failed to test WebSocket security",
                {"error": str(e)},
                "Ensure WebSocket authentication is properly configured"
            )
    
    async def check_hardcoded_secrets(self) -> SecurityTestResult:
        """Check for hardcoded secrets in configuration"""
        try:
            secret_issues = []
            
            # Check configuration files for hardcoded secrets
            config_files = [
                "/home/ishanp/Documents/GitHub/OSINT-OS/backend/app/config.py"
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        content = f.read()
                        
                        # Check for default/weak secrets
                        if "default-secret-change-in-production" in content:
                            secret_issues.append({
                                "file": config_file,
                                "issue": "Default JWT secret found",
                                "severity": "HIGH"
                            })
                        
                        # Check for hardcoded passwords
                        if "password" in content.lower() and "=" in content:
                            lines = content.split('\n')
                            for i, line in enumerate(lines):
                                if 'password' in line.lower() and '"' in line and not line.strip().startswith('#'):
                                    secret_issues.append({
                                        "file": config_file,
                                        "issue": f"Potential hardcoded password on line {i+1}",
                                        "severity": "MEDIUM",
                                        "line": line.strip()
                                    })
            
            # Check for API keys in code
            api_key_patterns = ["api_key =", "API_KEY = ", "apikey ="]
            for pattern in api_key_patterns:
                for root, dirs, files in os.walk("/home/ishanp/Documents/GitHub/OSINT-OS/backend"):
                    if '__pycache__' in root or '.git' in root:
                        continue
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    content = f.read()
                                    if pattern in content:
                                        secret_issues.append({
                                            "file": file_path,
                                            "issue": f"Potential hardcoded API key pattern: {pattern}",
                                            "severity": "HIGH"
                                        })
                            except:
                                pass
            
            if secret_issues:
                status = "FAIL"
                severity = "HIGH"
                description = "Hardcoded secrets found in codebase"
                recommendation = "Move all secrets to environment variables"
            else:
                status = "PASS"
                severity = "LOW"
                description = "No hardcoded secrets detected"
                recommendation = ""
            
            self.add_result(
                "Hardcoded Secrets Check",
                status, severity, description,
                {"secret_issues": secret_issues, "total_issues": len(secret_issues)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "Hardcoded Secrets Check",
                "FAIL", "MEDIUM", "Failed to check for hardcoded secrets",
                {"error": str(e)},
                "Manually review code for hardcoded secrets"
            )
    
    async def test_csrf_protection(self) -> SecurityTestResult:
        """Test CSRF protection mechanisms"""
        try:
            csrf_results = []
            
            # Test state-changing request without CSRF token
            post_data = {"username": "testuser", "password": "testpass"}
            
            async with self.session.post(
                f"{self.base_url}/api/auth/register",
                json=post_data,
                headers={"Referer": "http://malicious-site.com"}
            ) as response:
                # Check if CSRF protection is in place
                csrf_headers = [
                    "X-CSRF-Token", "CSRF-Token", "X-XSRF-Token"
                ]
                
                has_csrf_header = any(header in response.headers for header in csrf_headers)
                
                if response.status == 200 and not has_csrf_header:
                    csrf_results.append({
                        "test": "csrf_protection_missing",
                        "pass": False,
                        "details": "State-changing request allowed without CSRF token"
                    })
                else:
                    csrf_results.append({
                        "test": "csrf_protection_missing",
                        "pass": True,
                        "details": f"Request handled appropriately: status {response.status}"
                    })
            
            # Evaluate results
            failed_tests = [r for r in csrf_results if not r["pass"]]
            
            if failed_tests:
                status = "WARN"
                severity = "MEDIUM"
                description = "CSRF protection may be insufficient"
                recommendation = "Implement CSRF tokens for state-changing operations"
            else:
                status = "PASS"
                severity = "LOW"
                description = "CSRF protection appears adequate"
                recommendation = ""
            
            self.add_result(
                "CSRF Protection Test",
                status, severity, description,
                {"csrf_results": csrf_results, "failed_tests": len(failed_tests)},
                recommendation
            )
            
        except Exception as e:
            self.add_result(
                "CSRF Protection Test",
                "FAIL", "MEDIUM", "Failed to test CSRF protection",
                {"error": str(e)},
                "Ensure CSRF protection is properly implemented"
            )
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "PASS"])
        failed_tests = len([r for r in self.test_results if r.status == "FAIL"])
        warning_tests = len([r for r in self.test_results if r.status == "WARN"])
        
        critical_issues = [r for r in self.test_results if r.severity == "CRITICAL"]
        high_issues = [r for r in self.test_results if r.severity == "HIGH"]
        medium_issues = [r for r in self.test_results if r.severity == "MEDIUM"]
        low_issues = [r for r in self.test_results if r.severity == "LOW"]
        
        # Determine overall security posture
        if critical_issues:
            overall_status = "CRITICAL"
            risk_level = "HIGH"
        elif high_issues:
            overall_status = "VULNERABLE"
            risk_level = "MEDIUM-HIGH"
        elif medium_issues:
            overall_status = "NEEDS_ATTENTION"
            risk_level = "MEDIUM"
        elif failed_tests:
            overall_status = "FAIR"
            risk_level = "LOW-MEDIUM"
        else:
            overall_status = "SECURE"
            risk_level = "LOW"
        
        report = {
            "executive_summary": {
                "overall_status": overall_status,
                "risk_level": risk_level,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "test_coverage_percentage": round((passed_tests / total_tests) * 100, 1) if total_tests > 0 else 0
            },
            "security_issues_by_severity": {
                "critical": len(critical_issues),
                "high": len(high_issues),
                "medium": len(medium_issues),
                "low": len(low_issues)
            },
            "detailed_results": [],
            "recommendations": [],
            "production_readiness": {
                "ready_for_production": overall_status in ["SECURE", "FAIR"],
                "blocking_issues": len(critical_issues) + len(high_issues),
                "recommended_actions": []
            }
        }
        
        # Add detailed results
        for result in self.test_results:
            report["detailed_results"].append({
                "test_name": result.test_name,
                "status": result.status,
                "severity": result.severity,
                "description": result.description,
                "details": result.details,
                "recommendation": result.recommendation
            })
            
            # Collect recommendations
            if result.recommendation:
                report["recommendations"].append(result.recommendation)
        
        # Add production readiness recommendations
        if critical_issues or high_issues:
            report["production_readiness"]["recommended_actions"].append(
                "CRITICAL: Address all critical and high-severity security issues before production deployment"
            )
        if medium_issues:
            report["production_readiness"]["recommended_actions"].append(
                "MEDIUM: Address medium-severity issues in next development cycle"
            )
        if warning_tests:
            report["production_readiness"]["recommended_actions"].append(
                "LOW: Review and address warnings to improve security posture"
            )
        
        return report
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive security test suite"""
        logger.info("Starting comprehensive security validation...")
        
        # Run all security tests
        await self.test_security_headers()
        await self.test_rate_limiting()
        await self.test_input_validation()
        await self.test_authentication()
        await self.test_cors_configuration()
        await self.test_sql_injection()
        await self.test_websocket_security()
        await self.check_hardcoded_secrets()
        await self.test_csrf_protection()
        
        # Generate and return report
        report = self.generate_security_report()
        
        logger.info(f"Security validation complete. Status: {report['executive_summary']['overall_status']}")
        return report

async def main():
    """Main execution function"""
    async with SecurityValidator() as validator:
        report = await validator.run_all_tests()
        
        # Save detailed report
        with open("/home/ishanp/Documents/GitHub/OSINT-OS/comprehensive_security_validation_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE SECURITY VALIDATION REPORT")
        print("="*80)
        print(f"Overall Status: {report['executive_summary']['overall_status']}")
        print(f"Risk Level: {report['executive_summary']['risk_level']}")
        print(f"Tests Run: {report['executive_summary']['total_tests']}")
        print(f"Passed: {report['executive_summary']['passed']}")
        print(f"Failed: {report['executive_summary']['failed']}")
        print(f"Warnings: {report['executive_summary']['warnings']}")
        print(f"Coverage: {report['executive_summary']['test_coverage_percentage']}%")
        
        print("\nSECURITY ISSUES BY SEVERITY:")
        print(f"Critical: {report['security_issues_by_severity']['critical']}")
        print(f"High: {report['security_issues_by_severity']['high']}")
        print(f"Medium: {report['security_issues_by_severity']['medium']}")
        print(f"Low: {report['security_issues_by_severity']['low']}")
        
        print("\nPRODUCTION READINESS:")
        print(f"Ready for Production: {report['production_readiness']['ready_for_production']}")
        print(f"Blocking Issues: {report['production_readiness']['blocking_issues']}")
        
        if report['recommendations']:
            print("\nTOP RECOMMENDATIONS:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"{i}. {rec}")
        
        if not report['production_readiness']['ready_for_production']:
            print("\n" + "!"*80)
            print("WARNING: SYSTEM IS NOT READY FOR PRODUCTION DEPLOYMENT")
            print("Address all critical and high-severity security issues immediately")
            print("!"*80)
        
        print("\nDetailed report saved to: comprehensive_security_validation_report.json")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())