"""
Core OSINT service for evidence management and intelligence operations.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy import create_engine, text, and_, or_
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings
from app.models.sqlalchemy.osint_core import (
    DataSource, EvidenceChain, ThreatActor, ThreatIndicator,
    CollectionJob, LegalHold
)
from app.models.sqlalchemy.investigation import CollectedEvidence

logger = logging.getLogger(__name__)


class OSINTCoreService:
    """Core service for OSINT operations and evidence management."""
    
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # Data Source Management
    async def register_data_source(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new data source."""
        with self.get_session() as session:
            try:
                # Check if source already exists
                existing = session.query(DataSource).filter(
                    DataSource.name == source_data["name"]
                ).first()
                
                if existing:
                    # Update existing source
                    for key, value in source_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.now()
                    source = existing
                else:
                    # Create new source
                    source = DataSource(**source_data)
                    session.add(source)
                
                session.commit()
                return source.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error registering data source: {e}")
                raise
    
    async def get_data_sources(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all data sources."""
        with self.get_session() as session:
            query = session.query(DataSource)
            if active_only:
                query = query.filter(DataSource.is_active == True)
            
            sources = query.all()
            return [source.to_dict() for source in sources]
    
    async def update_source_reliability(self, source_name: str, reliability_score: float) -> bool:
        """Update source reliability score."""
        with self.get_session() as session:
            try:
                source = session.query(DataSource).filter(
                    DataSource.name == source_name
                ).first()
                
                if source:
                    source.reliability_score = max(0.0, min(1.0, reliability_score))
                    source.updated_at = datetime.now()
                    session.commit()
                    return True
                return False
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating source reliability: {e}")
                return False
    
    # Evidence Chain of Custody
    async def add_evidence_chain_entry(
        self, 
        evidence_uuid: str,
        handler: str,
        action: str,
        location: str,
        purpose: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add entry to evidence chain of custody."""
        with self.get_session() as session:
            try:
                # Get previous hash
                previous_entry = session.query(EvidenceChain).filter(
                    EvidenceChain.evidence_uuid == evidence_uuid
                ).order_by(EvidenceChain.created_at.desc()).first()
                
                previous_hash = previous_entry.current_hash if previous_entry else None
                
                # Generate content hash
                content = f"{evidence_uuid}{handler}{action}{location}{purpose}{datetime.now().isoformat()}"
                current_hash = hashlib.sha256(content.encode()).hexdigest()
                
                chain_entry = EvidenceChain(
                    evidence_uuid=evidence_uuid,
                    handler=handler,
                    action=action,
                    location=location,
                    purpose=purpose,
                    previous_hash=previous_hash,
                    current_hash=current_hash,
                    metadata=metadata or {}
                )
                
                session.add(chain_entry)
                session.commit()
                
                return chain_entry.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding evidence chain entry: {e}")
                raise
    
    async def get_evidence_chain(self, evidence_uuid: str) -> List[Dict[str, Any]]:
        """Get complete chain of custody for evidence."""
        with self.get_session() as session:
            chain = session.query(EvidenceChain).filter(
                EvidenceChain.evidence_uuid == evidence_uuid
            ).order_by(EvidenceChain.created_at.asc()).all()
            
            return [entry.to_dict() for entry in chain]
    
    async def verify_evidence_integrity(self, evidence_uuid: str) -> Dict[str, Any]:
        """Verify evidence integrity using chain of custody."""
        with self.get_session() as session:
            chain = session.query(EvidenceChain).filter(
                EvidenceChain.evidence_uuid == evidence_uuid
            ).order_by(EvidenceChain.created_at.asc()).all()
            
            if not chain:
                return {"valid": False, "reason": "No chain of custody found"}
            
            # Verify hash chain
            for i, entry in enumerate(chain):
                if i > 0:
                    if entry.previous_hash != chain[i-1].current_hash:
                        return {"valid": False, "reason": f"Hash chain broken at entry {i}"}
            
            return {"valid": True, "entries": len(chain)}
    
    # Threat Intelligence Management
    async def add_threat_actor(self, actor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add or update threat actor."""
        with self.get_session() as session:
            try:
                existing = session.query(ThreatActor).filter(
                    ThreatActor.name == actor_data["name"]
                ).first()
                
                if existing:
                    for key, value in actor_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    existing.updated_at = datetime.now()
                    actor = existing
                else:
                    actor = ThreatActor(**actor_data)
                    session.add(actor)
                
                session.commit()
                return actor.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding threat actor: {e}")
                raise
    
    async def add_threat_indicator(self, indicator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add or update threat indicator."""
        with self.get_session() as session:
            try:
                indicator = ThreatIndicator(**indicator_data)
                session.add(indicator)
                session.commit()
                
                return indicator.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error adding threat indicator: {e}")
                raise
    
    async def search_threat_indicators(
        self, 
        indicator_type: Optional[str] = None,
        value: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Search threat indicators."""
        with self.get_session() as session:
            query = session.query(ThreatIndicator)
            
            if indicator_type:
                query = query.filter(ThreatIndicator.indicator_type == indicator_type)
            
            if value:
                query = query.filter(ThreatIndicator.value.contains(value))
            
            if active_only:
                query = query.filter(ThreatIndicator.is_active == True)
            
            indicators = query.all()
            return [indicator.to_dict() for indicator in indicators]
    
    # Collection Job Management
    async def create_collection_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new collection job."""
        with self.get_session() as session:
            try:
                job = CollectionJob(**job_data)
                session.add(job)
                session.commit()
                
                return job.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating collection job: {e}")
                raise
    
    async def get_collection_jobs(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get collection jobs."""
        with self.get_session() as session:
            query = session.query(CollectionJob)
            
            if status:
                query = query.filter(CollectionJob.status == status)
            
            jobs = query.order_by(CollectionJob.priority.desc()).all()
            return [job.to_dict() for job in jobs]
    
    async def update_job_status(self, job_uuid: str, status: str, error_message: Optional[str] = None) -> bool:
        """Update collection job status."""
        with self.get_session() as session:
            try:
                job = session.query(CollectionJob).filter(
                    CollectionJob.uuid == job_uuid
                ).first()
                
                if job:
                    job.status = status
                    job.updated_at = datetime.now()
                    
                    if status == "completed":
                        job.success_count += 1
                        job.last_run = datetime.now()
                    elif status == "failed":
                        job.retry_count += 1
                        job.error_message = error_message
                    
                    session.commit()
                    return True
                return False
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error updating job status: {e}")
                return False
    
    # Legal Hold Management
    async def create_legal_hold(self, hold_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new legal hold."""
        with self.get_session() as session:
            try:
                hold = LegalHold(**hold_data)
                session.add(hold)
                session.commit()
                
                return hold.to_dict()
                
            except Exception as e:
                session.rollback()
                logger.error(f"Error creating legal hold: {e}")
                raise
    
    async def get_active_legal_holds(self) -> List[Dict[str, Any]]:
        """Get all active legal holds."""
        with self.get_session() as session:
            holds = session.query(LegalHold).filter(
                LegalHold.status == "active"
            ).all()
            
            return [hold.to_dict() for hold in holds]
    
    async def check_legal_hold_compliance(self, evidence_uuid: str) -> List[Dict[str, Any]]:
        """Check if evidence is under legal hold."""
        with self.get_session() as session:
            active_holds = session.query(LegalHold).filter(
                LegalHold.status == "active"
            ).all()
            
            applicable_holds = []
            for hold in active_holds:
                scope = hold.scope if isinstance(hold.scope, dict) else {}
                # Simple scope checking - can be enhanced
                if "all_evidence" in scope.get("type", []):
                    applicable_holds.append(hold.to_dict())
            
            return applicable_holds
    
    # Intelligence Synthesis
    async def synthesize_intelligence(self, investigation_uuid: str) -> Dict[str, Any]:
        """Synthesize intelligence from collected data."""
        with self.get_session() as session:
            try:
                # Get all evidence for investigation
                evidence = session.query(CollectedEvidence).filter(
                    CollectedEvidence.investigation_uuid == investigation_uuid
                ).all()
                
                # Get threat indicators
                indicators = session.query(ThreatIndicator).all()
                
                # Get threat actors
                actors = session.query(ThreatActor).all()
                
                # Basic synthesis logic
                synthesis = {
                    "investigation_uuid": investigation_uuid,
                    "evidence_count": len(evidence),
                    "threat_indicators": len(indicators),
                    "threat_actors": len(actors),
                    "reliability_score": self._calculate_overall_reliability(evidence),
                    "threat_level": self._assess_threat_level(evidence, indicators, actors),
                    "recommendations": self._generate_recommendations(evidence, indicators, actors),
                    "synthesized_at": datetime.now().isoformat()
                }
                
                return synthesis
                
            except Exception as e:
                logger.error(f"Error synthesizing intelligence: {e}")
                raise
    
    def _calculate_overall_reliability(self, evidence_list) -> float:
        """Calculate overall reliability score."""
        if not evidence_list:
            return 0.0
        
        total_score = sum(getattr(ev, 'reliability_score', 0.5) for ev in evidence_list)
        return total_score / len(evidence_list)
    
    def _assess_threat_level(self, evidence_list, indicators, actors) -> str:
        """Assess overall threat level."""
        # Simple threat assessment - can be enhanced with ML
        high_severity_indicators = sum(1 for i in indicators if getattr(i, 'severity', 'medium') == 'high')
        active_actors = sum(1 for a in actors if getattr(a, 'threat_level', 'unknown') in ['high', 'critical'])
        
        if high_severity_indicators > 5 or active_actors > 2:
            return "critical"
        elif high_severity_indicators > 2 or active_actors > 0:
            return "high"
        elif high_severity_indicators > 0:
            return "medium"
        else:
            return "low"
    
    def _generate_recommendations(self, evidence_list, indicators, actors) -> List[str]:
        """Generate intelligence recommendations."""
        recommendations = []
        
        if len(evidence_list) < 5:
            recommendations.append("Consider collecting additional evidence to strengthen analysis")
        
        high_risk_indicators = [i for i in indicators if getattr(i, 'severity', 'medium') == 'high']
        if high_risk_indicators:
            recommendations.append(f"Priority attention required for {len(high_risk_indicators)} high-severity indicators")
        
        if actors:
            recommendations.append(f"Monitor {len(actors)} identified threat actors for further activity")
        
        return recommendations


# Global service instance
osint_core_service = OSINTCoreService()
