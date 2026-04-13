"""
Comprehensive OSINT Core Features Test Suite

This module provides thorough testing for all OSINT core functionality including:
1. Evidence collection and chain of custody tracking
2. Threat intelligence management (ThreatActor, ThreatIndicator)
3. Data source management and collection jobs
4. Legal hold compliance features
5. Investigation workflow integration

Tests cover:
- Database models and relationships
- Service layer business logic
- API endpoints
- Error handling and edge cases
- Performance and reliability
"""

import pytest
import pytest_asyncio
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
import uuid

# Database imports
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Project imports
from app.services.osint_core_service import OSINTCoreService
from app.models.sqlalchemy.osint_core import (
    DataSource, EvidenceChain, ThreatActor, ThreatIndicator,
    CollectionJob, LegalHold
)
from app.models.sqlalchemy.investigation import CollectedEvidence, Investigation
from app.models.sqlalchemy.base import Base

from tests.conftest import (
    test_db, setup_test_environment, async_session,
    sample_investigation_data, sample_osint_data
)

logger = logging.getLogger(__name__)


class TestOSINTCoreModels:
    """Test OSINT core database models."""
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_data_source_model_creation(self, async_session):
        """Test DataSource model creation and validation."""
        async with async_session() as session:
            # Create data source
            source_data = {
                "name": "test_source",
                "source_type": "web",
                "url": "https://example.com",
                "description": "Test data source",
                "reliability_score": 0.8,
                "is_active": True,
                "credentials_required": False,
                "collection_parameters": {"timeout": 30}
            }
            
            source = DataSource(**source_data)
            session.add(source)
            await session.commit()
            await session.refresh(source)
            
            # Verify creation
            assert source.uuid is not None
            assert source.name == "test_source"
            assert source.source_type == "web"
            assert source.reliability_score == 0.8
            assert source.created_at is not None
            assert source.updated_at is not None
            
            # Test to_dict conversion
            source_dict = source.to_dict()
            assert "uuid" in source_dict
            assert source_dict["name"] == "test_source"
            assert source_dict["reliability_score"] == 0.8
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_evidence_chain_model_creation(self, async_session):
        """Test EvidenceChain model creation and hash validation."""
        async with async_session() as session:
            # Create evidence chain entry
            evidence_uuid = str(uuid.uuid4())
            chain_data = {
                "evidence_uuid": evidence_uuid,
                "handler": "test_user",
                "action": "created",
                "location": "/secure/storage/evidence_001",
                "purpose": "Initial evidence collection",
                "previous_hash": None,
                "current_hash": "abc123def456",
                "metadata": {"source": "automated_tool"}
            }
            
            chain_entry = EvidenceChain(**chain_data)
            session.add(chain_entry)
            await session.commit()
            await session.refresh(chain_entry)
            
            # Verify creation
            assert chain_entry.uuid is not None
            assert chain_entry.evidence_uuid == evidence_uuid
            assert chain_entry.handler == "test_user"
            assert chain_entry.action == "created"
            assert chain_entry.current_hash == "abc123def456"
            
            # Test to_dict conversion
            chain_dict = chain_entry.to_dict()
            assert chain_dict["evidence_uuid"] == evidence_uuid
            assert chain_dict["handler"] == "test_user"
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_threat_actor_model_creation(self, async_session):
        """Test ThreatActor model creation."""
        async with async_session() as session:
            actor_data = {
                "name": "APT-Test-Group",
                "alias": ["TestGroup", "TG-001"],
                "actor_type": "APT",
                "motivation": "espionage",
                "capabilities": ["spear_phishing", "custom_malware"],
                "known_attributions": ["Country X"],
                "threat_level": "high",
                "confidence": 0.85
            }
            
            actor = ThreatActor(**actor_data)
            session.add(actor)
            await session.commit()
            await session.refresh(actor)
            
            # Verify creation
            assert actor.uuid is not None
            assert actor.name == "APT-Test-Group"
            assert actor.actor_type == "APT"
            assert actor.threat_level == "high"
            assert actor.confidence == 0.85
            
            # Test to_dict conversion
            actor_dict = actor.to_dict()
            assert actor_dict["name"] == "APT-Test-Group"
            assert actor_dict["alias"] == ["TestGroup", "TG-001"]
            assert actor_dict["threat_level"] == "high"
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_threat_indicator_model_creation(self, async_session):
        """Test ThreatIndicator model creation."""
        async with async_session() as session:
            indicator_data = {
                "indicator_type": "ip",
                "value": "192.168.1.100",
                "description": "Suspicious IP address",
                "source": "threat_feed_001",
                "confidence": 0.9,
                "severity": "high",
                "is_active": True,
                "tags": ["malware", "c2"],
                "related_actors": ["APT-Test-Group"]
            }
            
            indicator = ThreatIndicator(**indicator_data)
            session.add(indicator)
            await session.commit()
            await session.refresh(indicator)
            
            # Verify creation
            assert indicator.uuid is not None
            assert indicator.indicator_type == "ip"
            assert indicator.value == "192.168.1.100"
            assert indicator.severity == "high"
            assert indicator.confidence == 0.9
            
            # Test to_dict conversion
            indicator_dict = indicator.to_dict()
            assert indicator_dict["indicator_type"] == "ip"
            assert indicator_dict["value"] == "192.168.1.100"
            assert indicator_dict["severity"] == "high"
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_collection_job_model_creation(self, async_session):
        """Test CollectionJob model creation."""
        async with async_session() as session:
            job_data = {
                "job_name": "daily_web_scrape",
                "job_type": "web_scraping",
                "source_id": "source_001",
                "schedule": "0 2 * * *",
                "parameters": {"urls": ["https://example.com"], "depth": 2},
                "status": "scheduled",
                "priority": 8,
                "max_retries": 3,
                "is_active": True
            }
            
            job = CollectionJob(**job_data)
            session.add(job)
            await session.commit()
            await session.refresh(job)
            
            # Verify creation
            assert job.uuid is not None
            assert job.job_name == "daily_web_scrape"
            assert job.job_type == "web_scraping"
            assert job.status == "scheduled"
            assert job.priority == 8
            
            # Test to_dict conversion
            job_dict = job.to_dict()
            assert job_dict["job_name"] == "daily_web_scrape"
            assert job_dict["status"] == "scheduled"
            assert job_dict["priority"] == 8
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_legal_hold_model_creation(self, async_session):
        """Test LegalHold model creation."""
        async with async_session() as session:
            hold_data = {
                "case_name": "Test Investigation v. Suspect",
                "case_number": "CASE-2025-001",
                "description": "Legal hold for evidence preservation",
                "requested_by": "legal_team@example.com",
                "start_date": datetime.now().isoformat(),
                "end_date": (datetime.now() + timedelta(days=90)).isoformat(),
                "status": "active",
                "scope": {"type": ["all_evidence"], "date_range": {"start": "2025-01-01"}},
                "custodians": ["analyst1", "analyst2"],
                "notes": "Preserve all evidence related to investigation"
            }
            
            hold = LegalHold(**hold_data)
            session.add(hold)
            await session.commit()
            await session.refresh(hold)
            
            # Verify creation
            assert hold.uuid is not None
            assert hold.case_name == "Test Investigation v. Suspect"
            assert hold.status == "active"
            assert hold.requested_by == "legal_team@example.com"
            
            # Test to_dict conversion
            hold_dict = hold.to_dict()
            assert hold_dict["case_name"] == "Test Investigation v. Suspect"
            assert hold_dict["status"] == "active"
            assert "scope" in hold_dict


class TestOSINTCoreService:
    """Test OSINT Core Service functionality."""
    
    @pytest.fixture
    def osint_service(self):
        """Create OSINT Core Service instance."""
        return OSINTCoreService()
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_register_data_source(self, osint_service, async_session):
        """Test data source registration."""
        source_data = {
            "name": "test_web_source",
            "source_type": "web",
            "url": "https://test-source.com",
            "description": "Test web data source",
            "reliability_score": 0.75,
            "is_active": True
        }
        
        # Register new source
        result = await osint_service.register_data_source(source_data)
        
        assert result is not None
        assert result["name"] == "test_web_source"
        assert result["source_type"] == "web"
        assert result["reliability_score"] == 0.75
        assert "uuid" in result
        
        # Test updating existing source
        source_data["reliability_score"] = 0.85
        source_data["description"] = "Updated description"
        result = await osint_service.register_data_source(source_data)
        
        assert result["reliability_score"] == 0.85
        assert result["description"] == "Updated description"
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_get_data_sources(self, osint_service, async_session):
        """Test retrieving data sources."""
        # Create test data sources
        sources = [
            {
                "name": "source_1",
                "source_type": "web",
                "url": "https://source1.com",
                "is_active": True
            },
            {
                "name": "source_2",
                "source_type": "api",
                "url": "https://api.source2.com",
                "is_active": False
            }
        ]
        
        for source in sources:
            await osint_service.register_data_source(source)
        
        # Test getting all active sources
        active_sources = await osint_service.get_data_sources(active_only=True)
        assert len(active_sources) >= 1
        for source in active_sources:
            assert source["is_active"] is True
        
        # Test getting all sources
        all_sources = await osint_service.get_data_sources(active_only=False)
        assert len(all_sources) >= len(sources)
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_update_source_reliability(self, osint_service, async_session):
        """Test updating source reliability scores."""
        source_data = {
            "name": "reliability_test_source",
            "source_type": "web",
            "reliability_score": 0.5
        }
        
        # Register source
        await osint_service.register_data_source(source_data)
        
        # Test updating reliability
        success = await osint_service.update_source_reliability("reliability_test_source", 0.9)
        assert success is True
        
        # Test updating non-existent source
        success = await osint_service.update_source_reliability("non_existent", 0.8)
        assert success is False
        
        # Test boundary values
        await osint_service.update_source_reliability("reliability_test_source", 1.5)
        await osint_service.update_source_reliability("reliability_test_source", -0.5)
        
        sources = await osint_service.get_data_sources()
        test_source = next(s for s in sources if s["name"] == "reliability_test_source")
        assert 0.0 <= test_source["reliability_score"] <= 1.0
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_evidence_chain_management(self, osint_service, async_session):
        """Test evidence chain of custody functionality."""
        evidence_uuid = str(uuid.uuid4())
        
        # Add chain entries
        entries = [
            {
                "evidence_uuid": evidence_uuid,
                "handler": "analyst1",
                "action": "created",
                "location": "/secure/storage/evidence_001",
                "purpose": "Initial collection"
            },
            {
                "evidence_uuid": evidence_uuid,
                "handler": "analyst2",
                "action": "accessed",
                "location": "/secure/storage/evidence_001",
                "purpose": "Analysis"
            },
            {
                "evidence_uuid": evidence_uuid,
                "handler": "system",
                "action": "exported",
                "location": "/tmp/export/evidence_001.zip",
                "purpose": "Report generation"
            }
        ]
        
        chain_results = []
        for entry in entries:
            result = await osint_service.add_evidence_chain_entry(**entry)
            chain_results.append(result)
            assert result["evidence_uuid"] == evidence_uuid
            assert result["handler"] == entry["handler"]
            assert "current_hash" in result
        
        # Test getting evidence chain
        chain = await osint_service.get_evidence_chain(evidence_uuid)
        assert len(chain) == 3
        assert chain[0]["handler"] == "analyst1"
        assert chain[1]["handler"] == "analyst2"
        assert chain[2]["handler"] == "system"
        
        # Test hash chain verification
        verification = await osint_service.verify_evidence_integrity(evidence_uuid)
        assert verification["valid"] is True
        assert verification["entries"] == 3
        
        # Test non-existent evidence
        verification = await osint_service.verify_evidence_integrity("non_existent")
        assert verification["valid"] is False
        assert "No chain of custody found" in verification["reason"]
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_threat_intelligence_management(self, osint_service, async_session):
        """Test threat intelligence functionality."""
        # Add threat actor
        actor_data = {
            "name": "TestAPT",
            "alias": ["TAP-001", "GroupX"],
            "actor_type": "APT",
            "motivation": "financial",
            "capabilities": ["ransomware", "phishing"],
            "threat_level": "high",
            "confidence": 0.8
        }
        
        actor_result = await osint_service.add_threat_actor(actor_data)
        assert actor_result["name"] == "TestAPT"
        assert actor_result["threat_level"] == "high"
        
        # Add threat indicators
        indicators = [
            {
                "indicator_type": "ip",
                "value": "10.0.0.100",
                "description": "C2 server IP",
                "source": "internal_analysis",
                "confidence": 0.9,
                "severity": "high",
                "tags": ["malware", "c2"]
            },
            {
                "indicator_type": "domain",
                "value": "malicious-domain.com",
                "description": "C2 domain",
                "source": "threat_feed",
                "confidence": 0.7,
                "severity": "medium",
                "tags": ["c2"]
            }
        ]
        
        indicator_results = []
        for indicator in indicators:
            result = await osint_service.add_threat_indicator(indicator)
            indicator_results.append(result)
            assert result["indicator_type"] == indicator["indicator_type"]
            assert result["value"] == indicator["value"]
        
        # Test searching indicators
        # Search by type
        ip_indicators = await osint_service.search_threat_indicators(indicator_type="ip")
        assert len(ip_indicators) >= 1
        assert all(i["indicator_type"] == "ip" for i in ip_indicators)
        
        # Search by value
        domain_indicators = await osint_service.search_threat_indicators(value="malicious")
        assert len(domain_indicators) >= 1
        assert all("malicious" in i["value"].lower() for i in domain_indicators)
        
        # Search active only
        active_indicators = await osint_service.search_threat_indicators(active_only=True)
        assert len(active_indicators) >= len(indicators)
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_collection_job_management(self, osint_service, async_session):
        """Test collection job functionality."""
        # Create collection job
        job_data = {
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
        }
        
        job_result = await osint_service.create_collection_job(job_data)
        assert job_result["job_name"] == "test_collection_job"
        assert job_result["status"] == "scheduled"
        assert job_result["priority"] == 7
        job_uuid = job_result["uuid"]
        
        # Test getting collection jobs
        all_jobs = await osint_service.get_collection_jobs()
        assert len(all_jobs) >= 1
        assert any(j["uuid"] == job_uuid for j in all_jobs)
        
        # Test filtering by status
        scheduled_jobs = await osint_service.get_collection_jobs(status="scheduled")
        assert len(scheduled_jobs) >= 1
        assert all(j["status"] == "scheduled" for j in scheduled_jobs)
        
        # Test updating job status
        success = await osint_service.update_job_status(job_uuid, "running")
        assert success is True
        
        success = await osint_service.update_job_status(job_uuid, "completed")
        assert success is True
        
        # Verify status update
        updated_jobs = await osint_service.get_collection_jobs(status="completed")
        updated_job = next(j for j in updated_jobs if j["uuid"] == job_uuid)
        assert updated_job["status"] == "completed"
        assert updated_job["success_count"] == 1
        
        # Test failed status
        success = await osint_service.update_job_status(
            job_uuid, 
            "failed", 
            "Connection timeout"
        )
        assert success is True
        
        failed_jobs = await osint_service.get_collection_jobs(status="failed")
        failed_job = next(j for j in failed_jobs if j["uuid"] == job_uuid)
        assert failed_job["error_message"] == "Connection timeout"
        assert failed_job["retry_count"] == 1
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_legal_hold_management(self, osint_service, async_session):
        """Test legal hold functionality."""
        # Create legal hold
        hold_data = {
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
        
        hold_result = await osint_service.create_legal_hold(hold_data)
        assert hold_result["case_name"] == "Test Legal Case"
        assert hold_result["status"] == "active"
        assert hold_result["requested_by"] == "legal@example.com"
        
        # Test getting active legal holds
        active_holds = await osint_service.get_active_legal_holds()
        assert len(active_holds) >= 1
        assert all(h["status"] == "active" for h in active_holds)
        
        # Test legal hold compliance check
        evidence_uuid = str(uuid.uuid4())
        applicable_holds = await osint_service.check_legal_hold_compliance(evidence_uuid)
        assert len(applicable_holds) >= 1
        assert all(h["status"] == "active" for h in applicable_holds)
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_intelligence_synthesis(self, osint_service, async_session):
        """Test intelligence synthesis functionality."""
        investigation_uuid = str(uuid.uuid4())
        
        # Create some test evidence, indicators, and actors
        # Note: This would normally be created through the investigation service
        # For testing, we'll mock the data
        
        # Mock evidence data
        with patch.object(osint_service, '_calculate_overall_reliability', return_value=0.75):
            with patch.object(osint_service, '_assess_threat_level', return_value="medium"):
                with patch.object(osint_service, '_generate_recommendations', return_value=["Monitor threats"]):
                    synthesis = await osint_service.synthesize_intelligence(investigation_uuid)
                    
                    assert synthesis["investigation_uuid"] == investigation_uuid
                    assert "evidence_count" in synthesis
                    assert "threat_indicators" in synthesis
                    assert "threat_actors" in synthesis
                    assert synthesis["reliability_score"] == 0.75
                    assert synthesis["threat_level"] == "medium"
                    assert "Monitor threats" in synthesis["recommendations"]
                    assert "synthesized_at" in synthesis


class TestOSINTErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.fixture
    def osint_service(self):
        """Create OSINT Core Service instance."""
        return OSINTCoreService()
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_data_source_validation_errors(self, osint_service):
        """Test data source validation errors."""
        # Test missing required fields
        with pytest.raises(Exception):
            await osint_service.register_data_source({"source_type": "web"})
        
        # Test invalid reliability score
        invalid_source = {
            "name": "invalid_source",
            "source_type": "web",
            "reliability_score": 1.5  # Invalid > 1.0
        }
        
        # This should handle gracefully in the service
        result = await osint_service.register_data_source(invalid_source)
        assert result["reliability_score"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_evidence_chain_validation(self, osint_service):
        """Test evidence chain validation."""
        # Test missing required fields
        with pytest.raises(Exception):
            await osint_service.add_evidence_chain_entry(
                evidence_uuid="",
                handler="test_user",
                action="created",
                location="/test"
            )
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_threat_actor_uniqueness(self, osint_service, async_session):
        """Test threat actor name uniqueness."""
        actor_data = {
            "name": "UniqueActor",
            "actor_type": "APT",
            "threat_level": "medium"
        }
        
        # Create first actor
        result1 = await osint_service.add_threat_actor(actor_data)
        assert result1["name"] == "UniqueActor"
        
        # Update existing actor (should not create duplicate)
        actor_data["threat_level"] = "high"
        result2 = await osint_service.add_threat_actor(actor_data)
        assert result2["uuid"] == result1["uuid"]  # Same UUID, updated
        assert result2["threat_level"] == "high"
    
    @pytest.mark.unit
    @pytest.mark.osint
    async def test_collection_job_status_validation(self, osint_service):
        """Test collection job status validation."""
        # Test updating non-existent job
        success = await osint_service.update_job_status("non_existent_uuid", "completed")
        assert success is False


class TestOSINTPerformance:
    """Test OSINT performance under load."""
    
    @pytest.fixture
    def osint_service(self):
        """Create OSINT Core Service instance."""
        return OSINTCoreService()
    
    @pytest.mark.performance
    @pytest.mark.osint
    async def test_bulk_data_source_operations(self, osint_service, async_session):
        """Test performance of bulk data source operations."""
        import time
        
        # Create multiple data sources
        sources = []
        start_time = time.time()
        
        for i in range(50):
            source_data = {
                "name": f"perf_test_source_{i}",
                "source_type": "web",
                "url": f"https://test{i}.com",
                "reliability_score": 0.5 + (i % 10) * 0.05
            }
            sources.append(await osint_service.register_data_source(source_data))
        
        creation_time = time.time() - start_time
        
        # Test retrieval performance
        start_time = time.time()
        retrieved_sources = await osint_service.get_data_sources()
        retrieval_time = time.time() - start_time
        
        # Assertions
        assert len(sources) == 50
        assert len(retrieved_sources) >= 50
        assert creation_time < 10.0  # Should complete in < 10 seconds
        assert retrieval_time < 1.0   # Retrieval should be fast
        
        logger.info(f"Bulk source creation: {creation_time:.2f}s, retrieval: {retrieval_time:.2f}s")
    
    @pytest.mark.performance
    @pytest.mark.osint
    async def test_evidence_chain_performance(self, osint_service, async_session):
        """Test evidence chain performance with long chains."""
        evidence_uuid = str(uuid.uuid4())
        
        # Create long evidence chain
        start_time = time.time()
        
        for i in range(100):
            await osint_service.add_evidence_chain_entry(
                evidence_uuid=evidence_uuid,
                handler=f"user_{i % 5}",
                action=f"action_{i}",
                location=f"/location_{i}",
                purpose=f"purpose_{i}"
            )
        
        chain_creation_time = time.time() - start_time
        
        # Test chain retrieval
        start_time = time.time()
        chain = await osint_service.get_evidence_chain(evidence_uuid)
        chain_retrieval_time = time.time() - start_time
        
        # Test integrity verification
        start_time = time.time()
        verification = await osint_service.verify_evidence_integrity(evidence_uuid)
        verification_time = time.time() - start_time
        
        # Assertions
        assert len(chain) == 100
        assert verification["valid"] is True
        assert chain_creation_time < 15.0
        assert chain_retrieval_time < 2.0
        assert verification_time < 1.0
        
        logger.info(f"Chain performance: creation={chain_creation_time:.2f}s, "
                   f"retrieval={chain_retrieval_time:.2f}s, verification={verification_time:.2f}s")


class TestOSINTIntegration:
    """Test OSINT integration with other platform components."""
    
    @pytest.mark.integration
    @pytest.mark.osint
    async def test_investigation_workflow_integration(self, osint_service, async_session):
        """Test OSINT integration with investigation workflow."""
        # This would normally involve creating an investigation first
        # For now, we'll test the intelligence synthesis part
        
        investigation_uuid = str(uuid.uuid4())
        
        # Mock some related data
        with patch('sqlalchemy.orm.Session.query') as mock_query:
            # Mock evidence query
            mock_evidence = Mock()
            mock_evidence.configure_mock(**{
                'reliability_score': 0.8,
                'investigation_uuid': investigation_uuid
            })
            
            # Mock indicators query
            mock_indicator = Mock()
            mock_indicator.configure_mock(**{
                'severity': 'high',
                'is_active': True
            })
            
            # Mock actors query
            mock_actor = Mock()
            mock_actor.configure_mock(**{
                'threat_level': 'high',
                'confidence': 0.9
            })
            
            # Configure query mock
            mock_query.return_value.filter.return_value.all.side_effect = [
                [mock_evidence] * 5,  # 5 evidence items
                [mock_indicator] * 3, # 3 indicators
                [mock_actor] * 2      # 2 actors
            ]
            
            synthesis = await osint_service.synthesize_intelligence(investigation_uuid)
            
            assert synthesis["investigation_uuid"] == investigation_uuid
            assert synthesis["evidence_count"] == 5
            assert synthesis["threat_indicators"] == 3
            assert synthesis["threat_actors"] == 2


# Test data generators
@pytest.fixture
def sample_data_source():
    """Generate sample data source for testing."""
    return {
        "name": "test_source",
        "source_type": "web",
        "url": "https://example.com",
        "description": "Test source",
        "reliability_score": 0.8,
        "is_active": True
    }


@pytest.fixture
def sample_threat_actor():
    """Generate sample threat actor for testing."""
    return {
        "name": "TestActor",
        "alias": ["TA-001"],
        "actor_type": "APT",
        "motivation": "espionage",
        "capabilities": ["phishing"],
        "threat_level": "medium",
        "confidence": 0.7
    }


@pytest.fixture
def sample_threat_indicator():
    """Generate sample threat indicator for testing."""
    return {
        "indicator_type": "domain",
        "value": "malicious.example.com",
        "description": "Suspicious domain",
        "source": "test_feed",
        "confidence": 0.8,
        "severity": "medium",
        "is_active": True
    }


@pytest.fixture
def sample_collection_job():
    """Generate sample collection job for testing."""
    return {
        "job_name": "test_job",
        "job_type": "web_scraping",
        "parameters": {"urls": ["https://example.com"]},
        "status": "scheduled",
        "priority": 5
    }


@pytest.fixture
def sample_legal_hold():
    """Generate sample legal hold for testing."""
    return {
        "case_name": "Test Case",
        "requested_by": "legal@example.com",
        "start_date": datetime.now().isoformat(),
        "status": "active",
        "scope": {"type": ["all_evidence"]}
    }