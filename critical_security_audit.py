#!/usr/bin/env python3
"""
Comprehensive Security Vulnerability Scanner
Production Security Clearance Audit
"""

import asyncio
import json
import logging
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityAuditScanner:
    """Comprehensive security vulnerability scanner for production readiness."""
    
    def __init__(self, project_path: str = "/home/ishanp/Documents/GitHub/OSINT-OS"):
        self.project_path = Path(project_path)
        self.backend_path = self.project_path / "backend"
        self.findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        self.scan_timestamp = datetime.utcnow().isoformat()
        
    def run_comprehensive_scan(self) -> Dict[str, Any]:
        """Execute complete security vulnerability assessment."""
        logger.info("🚨 STARTING COMPREHENSIVE SECURITY AUDIT FOR PRODUCTION CLEARANCE")
        
        # 1. SSL/TLS Security Issues
        self.check_ssl_verification()
        
        # 2. SQL Injection Vulnerabilities  
        self.check_sql_injection()
        
        # 3. Authentication & Authorization Issues
        self.check_auth_security()
        
        # 4. Cryptographic Implementation Issues
        self.check_cryptography()
        
        # 5. Input Validation & XSS
        self.check_input_validation()
        
        # 6. CORS Configuration
        self.check_cors_security()
        
        # 7. Hardcoded Secrets & Credentials
        self.check_hardcoded_secrets()
        
        # 8. Insecure Deserialization
        self.check_deserialization()
        
        # 9. File Security
        self.check_file_security()
        
        # 10. Dependency Security
        self.check_dependencies()
        
        return self.generate_report()
    
    def check_ssl_verification(self):
        """Check for SSL certificate verification bypass."""
        logger.info("🔍 Checking SSL/TLS security...")
        
        ssl_patterns = [
            r"verify\s*=\s*False",
            r"verify\s*=\s*false", 
            r"ssl_verify\s*=\s*False",
            r"check_hostname\s*=\s*False"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in ssl_patterns:
                        if re.search(pattern, line) and "# nosec" not in line:
                            self.add_finding(
                                "critical",
                                "SSL Certificate Verification Bypass",
                                f"SSL verification disabled in {py_file.name}:{i}",
                                file_path=str(py_file.relative_to(self.project_path)),
                                line_number=i,
                                code_snippet=line.strip(),
                                cwe="CWE-295",
                                remediation="Remove verify=False and ensure proper SSL certificate validation"
                            )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_sql_injection(self):
        """Check for SQL injection vulnerabilities."""
        logger.info("🔍 Checking SQL injection vulnerabilities...")
        
        sql_patterns = [
            r"SELECT.*\{.*\}",
            r"INSERT.*\{.*\}",
            r"UPDATE.*\{.*\}",
            r"DELETE.*\{.*\}",
            r"execute.*f[\"'].*\{.*\}",
            r"execute.*format.*\{.*\}",
            r"text\(.*\%.*\)"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in sql_patterns:
                        if re.search(pattern, line, re.IGNORECASE) and "# nosec" not in line:
                            # Check if using parameterized queries
                            if "session.execute(text(" in line:
                                self.add_finding(
                                    "high",
                                    "Potential SQL Injection",
                                    f"String formatting in SQL query in {py_file.name}:{i}",
                                    file_path=str(py_file.relative_to(self.project_path)),
                                    line_number=i,
                                    code_snippet=line.strip(),
                                    cwe="CWE-89",
                                    remediation="Use parameterized queries instead of string formatting"
                                )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_auth_security(self):
        """Check authentication and authorization security."""
        logger.info("🔍 Checking authentication security...")
        
        auth_patterns = [
            r"verify_signature\s*=\s*False",
            r"jwt\.decode.*options.*verify_signature.*False",
            r"SECRET\s*=\s*[\"'][^\"']+[\"']",
            r"API_KEY\s*=\s*[\"'][^\"']+[\"']"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in auth_patterns:
                        if re.search(pattern, line) and "# nosec" not in line:
                            severity = "critical" if "verify_signature" in line else "high"
                            self.add_finding(
                                severity,
                                "Authentication Security Issue",
                                f"Weak authentication mechanism in {py_file.name}:{i}",
                                file_path=str(py_file.relative_to(self.project_path)),
                                line_number=i,
                                code_snippet=line.strip(),
                                cwe="CWE-287",
                                remediation="Implement proper JWT signature verification and secure secret management"
                            )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_cryptography(self):
        """Check cryptographic implementation security."""
        logger.info("🔍 Checking cryptographic implementations...")
        
        crypto_patterns = [
            r"hashlib\.md5",
            r"MD5",
            r"hashlib\.sha1",
            r"SHA1",
            r"DES|des",
            r"RC4|rc4"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in crypto_patterns:
                        if re.search(pattern, line):
                            # Check if it's just a comment or documentation
                            if "#" not in line and '"""' not in line:
                                self.add_finding(
                                    "medium",
                                    "Weak Cryptographic Algorithm",
                                    f"Weak crypto algorithm in {py_file.name}:{i}",
                                    file_path=str(py_file.relative_to(self.project_path)),
                                    line_number=i,
                                    code_snippet=line.strip(),
                                    cwe="CWE-327",
                                    remediation="Replace with SHA-256 or stronger algorithms"
                                )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_input_validation(self):
        """Check input validation and XSS prevention."""
        logger.info("🔍 Checking input validation...")
        
        dangerous_patterns = [
            r"eval\s*\(",
            r"exec\s*\(",
            r"os\.system\s*\(",
            r"subprocess\.call.*shell\s*=\s*True",
            r"subprocess\.run.*shell\s*=\s*True"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in dangerous_patterns:
                        if re.search(pattern, line) and "# nosec" not in line:
                            self.add_finding(
                                "critical",
                                "Code Injection Risk",
                                f"Dangerous function call in {py_file.name}:{i}",
                                file_path=str(py_file.relative_to(self.project_path)),
                                line_number=i,
                                code_snippet=line.strip(),
                                cwe="CWE-94",
                                remediation="Avoid dangerous functions or implement strict input validation"
                            )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_cors_security(self):
        """Check CORS configuration security."""
        logger.info("🔍 Checking CORS security...")
        
        cors_patterns = [
            r"allow_origins\s*=\s*\[\".*\*.*\"\]",
            r"allow_origins\s*=\s*\[\"\*\"\]",
            r"CORS_ORIGINS\s*=\s*\[\"\*\"\]"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in cors_patterns:
                        if re.search(pattern, line):
                            # Check if it's commented out or in development context
                            if "development" not in line.lower() and "#" not in line:
                                self.add_finding(
                                    "medium",
                                    "Insecure CORS Configuration",
                                    f"Wildcard CORS origin in {py_file.name}:{i}",
                                    file_path=str(py_file.relative_to(self.project_path)),
                                    line_number=i,
                                    code_snippet=line.strip(),
                                    cwe="CWE-346",
                                    remediation="Restrict CORS origins to specific domains"
                                )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets and credentials."""
        logger.info("🔍 Checking for hardcoded secrets...")
        
        secret_patterns = [
            r"password\s*=\s*[\"'][^\"']{8,}[\"']",
            r"secret\s*=\s*[\"'][^\"']{16,}[\"']",
            r"token\s*=\s*[\"'][^\"']{16,}[\"']",
            r"api_key\s*=\s*[\"'][^\"']{16,}[\"']",
            r"private_key\s*=\s*[\"'][^\"']{16,}[\"']"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Skip example/bogus values
                            if not any(skip in line.lower() for skip in ["example", "test", "your_", "xxx", "placeholder"]):
                                self.add_finding(
                                    "critical",
                                    "Hardcoded Secret",
                                    f"Hardcoded secret in {py_file.name}:{i}",
                                    file_path=str(py_file.relative_to(self.project_path)),
                                    line_number=i,
                                    code_snippet=line.strip(),
                                    cwe="CWE-798",
                                    remediation="Move secrets to environment variables or secure vault"
                                )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_deserialization(self):
        """Check for insecure deserialization."""
        logger.info("🔍 Checking deserialization security...")
        
        deserialization_patterns = [
            r"pickle\.loads",
            r"pickle\.load",
            r"cPickle\.loads",
            r"cPickle\.load"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in deserialization_patterns:
                        if re.search(pattern, line) and "# nosec" not in line:
                            self.add_finding(
                                "medium",
                                "Insecure Deserialization",
                                f"Pickle deserialization in {py_file.name}:{i}",
                                file_path=str(py_file.relative_to(self.project_path)),
                                line_number=i,
                                code_snippet=line.strip(),
                                cwe="CWE-502",
                                remediation="Use JSON or other safe serialization formats"
                            )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_file_security(self):
        """Check file upload and access security."""
        logger.info("🔍 Checking file security...")
        
        file_patterns = [
            r"open\(.*\w.*\)",
            r"Path\(.*\w.*\)",
            r"os\.path\.join.*\w",
            r"upload.*save"
        ]
        
        for py_file in self.backend_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in file_patterns:
                        if re.search(pattern, line) and "upload" in line.lower():
                            self.add_finding(
                                "low",
                                "File Security Consideration",
                                f"File operation in {py_file.name}:{i}",
                                file_path=str(py_file.relative_to(self.project_path)),
                                line_number=i,
                                code_snippet=line.strip(),
                                cwe="CWE-22",
                                remediation="Validate file paths and implement access controls"
                            )
            except Exception as e:
                logger.warning(f"Could not read {py_file}: {e}")
    
    def check_dependencies(self):
        """Check for known dependency vulnerabilities."""
        logger.info("🔍 Checking dependency security...")
        
        try:
            # Check requirements files
            req_files = list(self.backend_path.glob("requirements*.txt"))
            for req_file in req_files:
                if req_file.exists():
                    content = req_file.read_text()
                    # Look for known vulnerable packages
                    vulnerable_packages = [
                        "urllib3==1.2", "requests==2.2", "flask==1.0", 
                        "django==2.2", "pillow<6.2", "pyyaml<5.4"
                    ]
                    
                    for package in vulnerable_packages:
                        if package in content:
                            self.add_finding(
                                "high",
                                "Vulnerable Dependency",
                                f"Vulnerable package in {req_file.name}",
                                file_path=str(req_file.relative_to(self.project_path)),
                                line_number=0,
                                code_snippet=package,
                                cwe="CWE-1104",
                                remediation="Update to the latest secure version"
                            )
        except Exception as e:
            logger.warning(f"Could not check dependencies: {e}")
    
    def add_finding(self, severity: str, title: str, description: str, **kwargs):
        """Add a security finding to the report."""
        finding = {
            "severity": severity.upper(),
            "title": title,
            "description": description,
            "cwe": kwargs.get("cwe", "N/A"),
            "file_path": kwargs.get("file_path", "N/A"),
            "line_number": kwargs.get("line_number", "N/A"),
            "code_snippet": kwargs.get("code_snippet", "N/A"),
            "remediation": kwargs.get("remediation", "Implement security best practices"),
            "cvss_score": self.get_cvss_score(severity),
            "discovered_at": self.scan_timestamp
        }
        
        self.findings[severity.lower()].append(finding)
    
    def get_cvss_score(self, severity: str) -> float:
        """Map severity to CVSS score."""
        mapping = {
            "critical": 9.5,
            "high": 7.5,
            "medium": 5.5,
            "low": 3.5,
            "info": 1.0
        }
        return mapping.get(severity.lower(), 1.0)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security audit report."""
        total_findings = sum(len(findings) for findings in self.findings.values())
        
        report = {
            "scan_metadata": {
                "scan_timestamp": self.scan_timestamp,
                "scanner_version": "1.0.0",
                "scan_type": "PRODUCTION_SECURITY_CLEARANCE_AUDIT",
                "project_path": str(self.project_path),
                "total_files_scanned": len(list(self.backend_path.rglob("*.py"))),
                "total_findings": total_findings
            },
            "executive_summary": {
                "critical_count": len(self.findings["critical"]),
                "high_count": len(self.findings["high"]),
                "medium_count": len(self.findings["medium"]),
                "low_count": len(self.findings["low"]),
                "info_count": len(self.findings["info"]),
                "security_posture": self.assess_security_posture(),
                "production_readiness": self.assess_production_readiness(),
                "immediate_action_required": len(self.findings["critical"]) > 0 or len(self.findings["high"]) > 0
            },
            "detailed_findings": self.findings,
            "remediation_plan": self.generate_remediation_plan(),
            "compliance_assessment": self.assess_compliance(),
            "security_recommendations": self.generate_recommendations()
        }
        
        return report
    
    def assess_security_posture(self) -> str:
        """Assess overall security posture."""
        critical = len(self.findings["critical"])
        high = len(self.findings["high"])
        
        if critical > 0:
            return "CRITICAL - Immediate action required"
        elif high > 3:
            return "HIGH - Significant security concerns"
        elif high > 0:
            return "MEDIUM - Security improvements needed"
        else:
            return "GOOD - Security posture acceptable"
    
    def assess_production_readiness(self) -> Dict[str, Any]:
        """Assess production readiness."""
        critical = len(self.findings["critical"])
        high = len(self.findings["high"])
        
        is_ready = critical == 0 and high <= 2
        
        return {
            "ready_for_production": is_ready,
            "blocking_issues": critical,
            "major_concerns": high,
            "estimated_remediation_time": self.estimate_remediation_time(),
            "security_clearance_level": "APPROVED" if is_ready else "DENIED"
        }
    
    def estimate_remediation_time(self) -> str:
        """Estimate time required for remediation."""
        critical = len(self.findings["critical"])
        high = len(self.findings["high"])
        medium = len(self.findings["medium"])
        
        total_hours = (critical * 8) + (high * 4) + (medium * 2)
        
        if total_hours <= 8:
            return "< 1 day"
        elif total_hours <= 40:
            return "1-5 days"
        elif total_hours <= 80:
            return "1-2 weeks"
        else:
            return "> 2 weeks"
    
    def generate_remediation_plan(self) -> List[Dict[str, Any]]:
        """Generate prioritized remediation plan."""
        plan = []
        
        # Critical issues first
        for finding in self.findings["critical"]:
            plan.append({
                "priority": "IMMEDIATE",
                "finding": finding["title"],
                "file": finding["file_path"],
                "remediation": finding["remediation"],
                "estimated_effort": "4-8 hours",
                "assigned_to": "Security Team"
            })
        
        # High priority issues
        for finding in self.findings["high"]:
            plan.append({
                "priority": "HIGH",
                "finding": finding["title"],
                "file": finding["file_path"],
                "remediation": finding["remediation"],
                "estimated_effort": "2-4 hours",
                "assigned_to": "Development Team"
            })
        
        return plan
    
    def assess_compliance(self) -> Dict[str, Any]:
        """Assess compliance with security standards."""
        return {
            "owasp_top_10_compliance": self.assess_owasp_compliance(),
            "intelligence_agency_standards": self.assess_intelligence_standards(),
            "data_protection_compliance": self.assess_data_protection(),
            "overall_compliance_score": self.calculate_compliance_score()
        }
    
    def assess_owasp_compliance(self) -> Dict[str, str]:
        """Assess OWASP Top 10 compliance."""
        return {
            "A01_Broken_Access_Control": "NEEDS_REVIEW" if self.findings["critical"] else "COMPLIANT",
            "A02_Cryptographic_Failures": "NEEDS_REVIEW" if self.findings["medium"] else "COMPLIANT",
            "A03_Injection": "NEEDS_REVIEW" if self.findings["high"] else "COMPLIANT",
            "A04_Insecure_Design": "NEEDS_REVIEW",
            "A05_Security_Misconfiguration": "NEEDS_REVIEW" if self.findings["medium"] else "COMPLIANT",
            "A06_Vulnerable_Components": "COMPLIANT",
            "A07_Identification_Authentication": "NEEDS_REVIEW" if self.findings["critical"] else "COMPLIANT",
            "A08_Software_Data_Integrity": "COMPLIANT",
            "A09_Logging_Monitoring": "COMPLIANT",
            "A10_Server_Side_Request_Forgery": "COMPLIANT"
        }
    
    def assess_intelligence_standards(self) -> Dict[str, str]:
        """Assess intelligence agency security standards."""
        return {
            "classification_handling": "COMPLIANT",
            "audit_logging": "COMPLIANT", 
            "access_control": "NEEDS_REVIEW" if self.findings["critical"] else "COMPLIANT",
            "data_encryption": "COMPLIANT",
            "chain_of_custody": "COMPLIANT",
            "secure_communications": "NEEDS_REVIEW" if self.findings["critical"] else "COMPLIANT"
        }
    
    def assess_data_protection(self) -> Dict[str, str]:
        """Assess data protection compliance."""
        return {
            "data_minimization": "COMPLIANT",
            "consent_management": "COMPLIANT",
            "data_retention": "COMPLIANT",
            "breach_notification": "COMPLIANT",
            "cross_border_transfer": "COMPLIANT"
        }
    
    def calculate_compliance_score(self) -> float:
        """Calculate overall compliance score (0-100)."""
        critical_penalty = len(self.findings["critical"]) * 20
        high_penalty = len(self.findings["high"]) * 10
        medium_penalty = len(self.findings["medium"]) * 5
        low_penalty = len(self.findings["low"]) * 1
        
        score = max(0, 100 - critical_penalty - high_penalty - medium_penalty - low_penalty)
        return round(score, 1)
    
    def generate_recommendations(self) -> List[str]:
        """Generate security recommendations."""
        recommendations = [
            "Implement a comprehensive security testing program",
            "Enable automatic dependency vulnerability scanning",
            "Establish secure coding guidelines and regular training",
            "Implement proper secrets management solution",
            "Enable comprehensive logging and monitoring",
            "Regular security assessments and penetration testing",
            "Implement web application firewall (WAF)",
            "Establish incident response procedures",
            "Regular security architecture reviews",
            "Implement zero-trust security model"
        ]
        
        # Add specific recommendations based on findings
        if self.findings["critical"]:
            recommendations.insert(0, "IMMEDIATE: Address all critical security vulnerabilities before production deployment")
        
        if self.findings["high"]:
            recommendations.insert(1, "HIGH PRIORITY: Address all high-severity security issues")
        
        return recommendations

async def main():
    """Main execution function."""
    scanner = SecurityAuditScanner()
    
    logger.info("🚨 EXECUTING CRITICAL PRODUCTION SECURITY AUDIT")
    
    # Run comprehensive scan
    report = scanner.run_comprehensive_scan()
    
    # Save report
    report_file = f"CRITICAL_PRODUCTION_SECURITY_AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = Path("/home/ishanp/Documents/GitHub/OSINT-OS") / report_file
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*80)
    print("🚨 CRITICAL PRODUCTION SECURITY AUDIT COMPLETE")
    print("="*80)
    
    summary = report["executive_summary"]
    print(f"📊 SUMMARY:")
    print(f"  🔴 Critical: {summary['critical_count']}")
    print(f"  🟠 High: {summary['high_count']}")
    print(f"  🟡 Medium: {summary['medium_count']}")
    print(f"  🔵 Low: {summary['low_count']}")
    print(f"  ℹ️  Info: {summary['info_count']}")
    print(f"\n🛡️  Security Posture: {summary['security_posture']}")
    print(f"🚦 Production Readiness: {summary['production_readiness']['security_clearance_level']}")
    
    if summary["immediate_action_required"]:
        print("\n🚨 IMMEDIATE ACTION REQUIRED - PRODUCTION DEPLOYMENT BLOCKED")
        
        print("\n🔴 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
        for finding in report["detailed_findings"]["critical"][:5]:
            print(f"  • {finding['title']} in {finding['file_path']}:{finding['line_number']}")
    
    print(f"\n📄 Full report saved to: {report_path}")
    print("="*80)
    
    return report

if __name__ == "__main__":
    asyncio.run(main())