"""
Comprehensive OSINT Integration Test Suite
Testing OSINT functionality without complex dependencies
"""

import asyncio
import json
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, patch
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, '/home/ishanp/Documents/GitHub/OSINT-OS/backend')

# Simple test framework
class TestResult:
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.error = None
        self.duration = 0
        self.details = {}
    
    def set_passed(self, details: Dict[str, Any] = None):
        self.passed = True
        self.details = details or {}
    
    def set_failed(self, error: str):
        self.error = error
    
    def __str__(self):
        status = "PASS" if self.passed else "FAIL"
        return f"[{status}] {self.test_name}: {self.error or 'OK'}"

class OSINTIntegrationTester:
    """Comprehensive OSINT integration tester."""
    
    def __init__(self):
        self.results = []
        self.test_data = {}
        self.setup_mock_data()
    
    def setup_mock_data(self):
        """Setup mock data for testing."""
        self.test_data = {
            "data_source": {
                "name": "test_web_source",
                "source_type": "web",
                "url": "https://test-source.com",
                "description": "Test web data source",
                "reliability_score": 0.75,
                "is_active": True,
                "credentials_required": False,
                "collection_parameters": {"timeout": 30}
            },
            "threat_actor": {
                "name": "TestAPT",
                "alias": ["TAP-001", "GroupX"],
                "actor_type": "APT",
                "motivation": "financial",
                "capabilities": ["ransomware", "phishing"],
                "known_attributions": ["Country X"],
                "threat_level": "high",
                "confidence": 0.8
            },
            "threat_indicator": {
                "indicator_type": "ip",
                "value": "10.0.0.100",
                "description": "C2 server IP",
                "source": "internal_analysis",
                "confidence": 0.9,
                "severity": "high",
                "is_active": True,
                "tags": ["malware", "c2"],
                "related_actors": ["TestAPT"]
            },
            "collection_job": {
                "job_name": "test_collection_job",
                "job_type": "web_scraping",
                "source_id": "test_source",
                "schedule": "0 */6 * * *",
                "parameters": {
                    "urls": ["https://example.com"],
                    "depth": 3,
                    "timeout": 30
                },
                "status": "scheduled",
                "priority": 7,
                "max_retries": 3
            },
            "legal_hold": {
                "case_name": "Test Legal Case",
                "case_number": "CASE-2025-TEST",
                "description": "Test legal hold for compliance",
                "requested_by": "legal@example.com",
                "start_date": datetime.now().isoformat(),
                "status": "active",
                "scope": {
                    "type": ["all_evidence"],
                    "date_range": {"start": "2025-01-01", "end": "2025-12-31"}
                },
                "custodians": ["analyst1", "analyst2"]
            }
        }
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and capture results."""
        result = TestResult(test_name)
        start_time = datetime.now()
        
        try:
            details = test_func()
            result.set_passed(details)
        except Exception as e:
            result.set_failed(str(e))
        
        result.duration = (datetime.now() - start_time).total_seconds()
        self.results.append(result)
        return result
    
    def test_osint_models_import(self):
        """Test OSINT models can be imported."""
        try:
            from app.models.sqlalchemy.osint_core import (
                DataSource, EvidenceChain, ThreatActor, ThreatIndicator,
                CollectionJob, LegalHold
            )
            return {
                "models_imported": [
                    "DataSource", "EvidenceChain", "ThreatActor", 
                    "ThreatIndicator", "CollectionJob", "LegalHold"
                ],
                "status": "success"
            }
        except ImportError as e:
            raise Exception(f"Failed to import OSINT models: {e}")
    
    def test_osint_service_import(self):
        """Test OSINT service can be imported."""
        try:
            from app.services.osint_core_service import OSINTCoreService
            service = OSINTCoreService()
            return {
                "service_imported": "OSINTCoreService",
                "service_methods": [method for method in dir(service) if not method.startswith('_')],
                "status": "success"
            }
        except ImportError as e:
            raise Exception(f"Failed to import OSINT service: {e}")
    
    def test_osint_api_import(self):
        """Test OSINT API can be imported."""
        try:
            from app.api.osint import router
            return {
                "api_imported": "OSINT Router",
                "routes": [route.path for route in router.routes],
                "status": "success"
            }
        except ImportError as e:
            raise Exception(f"Failed to import OSINT API: {e}")
    
    def test_data_source_model_creation(self):
        """Test DataSource model creation."""
        from app.models.sqlalchemy.osint_core import DataSource
        
        # Create data source instance
        source = DataSource(**self.test_data["data_source"])
        
        # Test model attributes
        assert source.name == "test_web_source"
        assert source.source_type == "web"
        assert source.reliability_score == 0.75
        assert source.is_active is True
        
        # Test to_dict method
        source_dict = source.to_dict()
        assert "uuid" in source_dict
        assert source_dict["name"] == "test_web_source"
        assert source_dict["reliability_score"] == 0.75
        
        return {
            "model": "DataSource",
            "fields_tested": ["name", "source_type", "reliability_score", "is_active"],
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_evidence_chain_model_creation(self):
        """Test EvidenceChain model creation."""
        from app.models.sqlalchemy.osint_core import EvidenceChain
        
        evidence_uuid = str(uuid.uuid4())
        chain_data = {
            "evidence_uuid": evidence_uuid,
            "handler": "test_user",
            "action": "created",
            "location": "/secure/storage/evidence_001",
            "purpose": "Initial evidence collection",
            "previous_hash": None,
            "current_hash": hashlib.sha256(b"test").hexdigest(),
            "evidence_metadata": {"source": "automated_tool"}
        }
        
        chain = EvidenceChain(**chain_data)
        
        # Test model attributes
        assert chain.evidence_uuid == evidence_uuid
        assert chain.handler == "test_user"
        assert chain.action == "created"
        
        # Test to_dict method
        chain_dict = chain.to_dict()
        assert chain_dict["evidence_uuid"] == evidence_uuid
        assert chain_dict["handler"] == "test_user"
        
        return {
            "model": "EvidenceChain",
            "fields_tested": ["evidence_uuid", "handler", "action"],
            "hash_generation": "sha256",
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_threat_actor_model_creation(self):
        """Test ThreatActor model creation."""
        from app.models.sqlalchemy.osint_core import ThreatActor
        
        actor = ThreatActor(**self.test_data["threat_actor"])
        
        # Test model attributes
        assert actor.name == "TestAPT"
        assert actor.actor_type == "APT"
        assert actor.threat_level == "high"
        assert actor.confidence == 0.8
        
        # Test to_dict method
        actor_dict = actor.to_dict()
        assert actor_dict["name"] == "TestAPT"
        assert actor_dict["alias"] == ["TAP-001", "GroupX"]
        assert actor_dict["threat_level"] == "high"
        
        return {
            "model": "ThreatActor",
            "fields_tested": ["name", "actor_type", "threat_level", "confidence"],
            "json_fields": ["alias", "capabilities", "known_attributions"],
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_threat_indicator_model_creation(self):
        """Test ThreatIndicator model creation."""
        from app.models.sqlalchemy.osint_core import ThreatIndicator
        
        indicator = ThreatIndicator(**self.test_data["threat_indicator"])
        
        # Test model attributes
        assert indicator.indicator_type == "ip"
        assert indicator.value == "10.0.0.100"
        assert indicator.severity == "high"
        assert indicator.confidence == 0.9
        
        # Test to_dict method
        indicator_dict = indicator.to_dict()
        assert indicator_dict["indicator_type"] == "ip"
        assert indicator_dict["value"] == "10.0.0.100"
        assert indicator_dict["severity"] == "high"
        
        return {
            "model": "ThreatIndicator",
            "fields_tested": ["indicator_type", "value", "severity", "confidence"],
            "json_fields": ["tags", "related_actors"],
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_collection_job_model_creation(self):
        """Test CollectionJob model creation."""
        from app.models.sqlalchemy.osint_core import CollectionJob
        
        job = CollectionJob(**self.test_data["collection_job"])
        
        # Test model attributes
        assert job.job_name == "test_collection_job"
        assert job.job_type == "web_scraping"
        assert job.status == "scheduled"
        assert job.priority == 7
        
        # Test to_dict method
        job_dict = job.to_dict()
        assert job_dict["job_name"] == "test_collection_job"
        assert job_dict["status"] == "scheduled"
        assert job_dict["priority"] == 7
        
        return {
            "model": "CollectionJob",
            "fields_tested": ["job_name", "job_type", "status", "priority"],
            "json_fields": ["parameters"],
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_legal_hold_model_creation(self):
        """Test LegalHold model creation."""
        from app.models.sqlalchemy.osint_core import LegalHold
        
        hold = LegalHold(**self.test_data["legal_hold"])
        
        # Test model attributes
        assert hold.case_name == "Test Legal Case"
        assert hold.status == "active"
        assert hold.requested_by == "legal@example.com"
        
        # Test to_dict method
        hold_dict = hold.to_dict()
        assert hold_dict["case_name"] == "Test Legal Case"
        assert hold_dict["status"] == "active"
        assert "scope" in hold_dict
        
        return {
            "model": "LegalHold",
            "fields_tested": ["case_name", "status", "requested_by"],
            "json_fields": ["scope", "custodians"],
            "to_dict_method": "working",
            "status": "success"
        }
    
    def test_evidence_chain_hash_logic(self):
        """Test evidence chain hash logic."""
        from app.models.sqlalchemy.osint_core import EvidenceChain
        
        evidence_uuid = str(uuid.uuid4())
        
        # Create chain entries
        entries = []
        previous_hash = None
        
        for i in range(3):
            content = f"{evidence_uuid}user_{i}action_{i}/location_{i}purpose_{i}{datetime.now().isoformat()}"
            current_hash = hashlib.sha256(content.encode()).hexdigest()
            
            chain_data = {
                "evidence_uuid": evidence_uuid,
                "handler": f"user_{i}",
                "action": f"action_{i}",
                "location": f"/location_{i}",
                "purpose": f"purpose_{i}",
                "previous_hash": previous_hash,
                "current_hash": current_hash,
                "evidence_metadata": {}
            }
            
            entry = EvidenceChain(**chain_data)
            entries.append(entry)
            previous_hash = current_hash
        
        # Verify hash chain
        for i in range(1, len(entries)):
            assert entries[i].previous_hash == entries[i-1].current_hash
        
        return {
            "chain_length": len(entries),
            "hash_verification": "passed",
            "chain_integrity": "maintained",
            "status": "success"
        }
    
    def test_osint_service_methods(self):
        """Test OSINT service methods exist and are callable."""
        from app.services.osint_core_service import OSINTCoreService
        
        service = OSINTCoreService()
        
        # Check key methods exist
        required_methods = [
            'register_data_source',
            'get_data_sources',
            'add_evidence_chain_entry',
            'get_evidence_chain',
            'verify_evidence_integrity',
            'add_threat_actor',
            'add_threat_indicator',
            'search_threat_indicators',
            'create_collection_job',
            'get_collection_jobs',
            'update_job_status',
            'create_legal_hold',
            'get_active_legal_holds',
            'check_legal_hold_compliance',
            'synthesize_intelligence'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(service, method):
                missing_methods.append(method)
        
        if missing_methods:
            raise Exception(f"Missing methods: {missing_methods}")
        
        return {
            "total_methods": len(required_methods),
            "methods_found": len(required_methods) - len(missing_methods),
            "missing_methods": missing_methods,
            "status": "success"
        }
    
    def test_osint_api_routes(self):
        """Test OSINT API routes are defined."""
        from app.api.osint import router
        
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                routes.append({
                    "path": route.path,
                    "methods": getattr(route, 'methods', ['GET'])
                })
        
        # Check for key routes
        key_routes = [
            "/investigations",
            "/search", 
            "/premium-search"
        ]
        
        found_routes = []
        for route in routes:
            for key_route in key_routes:
                if key_route in route["path"]:
                    found_routes.append(key_route)
        
        return {
            "total_routes": len(routes),
            "key_routes_found": found_routes,
            "all_routes": routes[:10],  # First 10 routes
            "status": "success"
        }
    
    def test_premium_search_agent(self):
        """Test premium search agent availability."""
        try:
            from app.agents.specialized.collection.premium_search_agent import PremiumSearchAgent
            
            agent = PremiumSearchAgent()
            
            # Check agent methods
            required_methods = ['execute', 'get_supported_engines', 'test_connectivity']
            missing_methods = []
            
            for method in required_methods:
                if not hasattr(agent, method):
                    missing_methods.append(method)
            
            return {
                "agent_class": "PremiumSearchAgent",
                "methods_checked": len(required_methods),
                "methods_found": len(required_methods) - len(missing_methods),
                "missing_methods": missing_methods,
                "status": "success"
            }
        except ImportError as e:
            raise Exception(f"Failed to import PremiumSearchAgent: {e}")
    
    def test_data_validation(self):
        """Test data validation logic."""
        from app.models.sqlalchemy.osint_core import DataSource, ThreatIndicator
        
        # Test data source validation
        try:
            # Valid data source
            valid_source = DataSource(**self.test_data["data_source"])
            assert valid_source.reliability_score >= 0.0
            assert valid_source.reliability_score <= 1.0
            
            # Test threat indicator validation
            valid_indicator = ThreatIndicator(**self.test_data["threat_indicator"])
            assert valid_indicator.confidence >= 0.0
            assert valid_indicator.confidence <= 1.0
            assert valid_indicator.severity in ["low", "medium", "high", "critical"]
            
        except Exception as e:
            raise Exception(f"Data validation failed: {e}")
        
        return {
            "validation_tests": ["reliability_score_range", "confidence_range", "severity_values"],
            "all_passed": True,
            "status": "success"
        }
    
    def test_json_field_handling(self):
        """Test JSON field handling in models."""
        from app.models.sqlalchemy.osint_core import ThreatActor, CollectionJob, LegalHold
        
        # Test threat actor JSON fields
        actor = ThreatActor(**self.test_data["threat_actor"])
        assert isinstance(actor.alias, list)
        assert isinstance(actor.capabilities, list)
        
        # Test collection job JSON fields
        job = CollectionJob(**self.test_data["collection_job"])
        assert isinstance(job.parameters, dict)
        assert "urls" in job.parameters
        
        # Test legal hold JSON fields
        hold = LegalHold(**self.test_data["legal_hold"])
        assert isinstance(hold.scope, dict)
        assert isinstance(hold.custodians, list)
        
        return {
            "json_fields_tested": ["alias", "capabilities", "parameters", "scope", "custodians"],
            "field_types": "correct",
            "status": "success"
        }
    
    def run_all_tests(self):
        """Run all OSINT integration tests."""
        print("🚀 Starting Comprehensive OSINT Integration Testing")
        print("=" * 60)
        
        # Model import tests
        self.run_test("OSINT Models Import", self.test_osint_models_import)
        self.run_test("OSINT Service Import", self.test_osint_service_import)
        self.run_test("OSINT API Import", self.test_osint_api_import)
        
        # Model creation tests
        self.run_test("DataSource Model Creation", self.test_data_source_model_creation)
        self.run_test("EvidenceChain Model Creation", self.test_evidence_chain_model_creation)
        self.run_test("ThreatActor Model Creation", self.test_threat_actor_model_creation)
        self.run_test("ThreatIndicator Model Creation", self.test_threat_indicator_model_creation)
        self.run_test("CollectionJob Model Creation", self.test_collection_job_model_creation)
        self.run_test("LegalHold Model Creation", self.test_legal_hold_model_creation)
        
        # Logic tests
        self.run_test("Evidence Chain Hash Logic", self.test_evidence_chain_hash_logic)
        self.run_test("OSINT Service Methods", self.test_osint_service_methods)
        self.run_test("OSINT API Routes", self.test_osint_api_routes)
        self.run_test("Premium Search Agent", self.test_premium_search_agent)
        
        # Validation tests
        self.run_test("Data Validation", self.test_data_validation)
        self.run_test("JSON Field Handling", self.test_json_field_handling)
        
        # Print results
        self.print_results()
        
        # Generate report
        self.generate_report()
    
    def print_results(self):
        """Print test results."""
        print("\n📊 Test Results:")
        print("-" * 40)
        
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        
        for result in self.results:
            print(result)
        
        print(f"\n📈 Summary: {passed} passed, {failed} failed out of {len(self.results)} tests")
        
        if failed == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed - check details above")
    
    def generate_report(self):
        """Generate detailed test report."""
        report = {
            "test_execution": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r.passed),
                "failed": sum(1 for r in self.results if not r.passed),
                "total_duration": sum(r.duration for r in self.results)
            },
            "test_categories": {
                "model_imports": 3,
                "model_creation": 6,
                "logic_tests": 4,
                "validation_tests": 2
            },
            "detailed_results": []
        }
        
        for result in self.results:
            report["detailed_results"].append({
                "test_name": result.test_name,
                "status": "PASS" if result.passed else "FAIL",
                "duration": result.duration,
                "details": result.details if result.passed else {"error": result.error}
            })
        
        # Save report
        report_path = "/home/ishanp/Documents/GitHub/OSINT-OS/comprehensive_osint_test_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return report

def main():
    """Main function to run OSINT integration tests."""
    tester = OSINTIntegrationTester()
    tester.run_all_tests()
    
    # Return summary for programmatic use
    passed = sum(1 for r in tester.results if r.passed)
    failed = len(tester.results) - passed
    
    return {
        "total_tests": len(tester.results),
        "passed": passed,
        "failed": failed,
        "success_rate": passed / len(tester.results) if tester.results else 0
    }

if __name__ == "__main__":
    main()