"""
AI Backend Bridge for OSINT Collection Agents

This module provides a bridge between AI agents and backend scraping services,
enabling state synchronization and task coordination between AI agents and
backend services.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, cast
from datetime import datetime
from enum import Enum

# Using dynamic import to avoid circular import issues
import importlib.util
import os

# Import the state module dynamically
state_module_path = os.path.join(os.path.dirname(__file__), 'state.py')
spec = importlib.util.spec_from_file_location("state", state_module_path)
if spec is not None and spec.loader is not None:
    state_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(state_module)
    InvestigationState = state_module.InvestigationState
    InvestigationPhase = state_module.InvestigationPhase
    InvestigationStatus = state_module.InvestigationStatus
else:
    raise ImportError("Could not load state module")

# Dynamically import the BackendScrapingClient to avoid import issues
import importlib.util
import os

# Import the client module dynamically
client_module_path = os.path.join(os.path.dirname(__file__), 'backend_scraping_client.py')
spec = importlib.util.spec_from_file_location("backend_scraping_client", client_module_path)
if spec is not None and spec.loader is not None:
    backend_scraping_client_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend_scraping_client_module)
    BackendScrapingClient = backend_scraping_client_module.BackendScrapingClient
else:
    raise ImportError("Could not load backend scraping client module")


logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks that can be coordinated through the bridge"""
    SCRAPING = "scraping"
    SEARCH = "search"
    ANALYSIS = "analysis"
    INTELLIGENCE = "intelligence"


class TaskStatus(Enum):
    """Status of tasks in the bridge system"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIBackendBridge:
    """
    Bridge between AI agents and backend scraping services.
    
    This class provides a unified interface for AI agents to interact with
    backend scraping services, manage tasks, and synchronize investigation state.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.client = BackendScrapingClient(base_url)
        self.logger = logging.getLogger(f"{__name__}.AIBackendBridge")
        
    async def __aenter__(self) -> "AIBackendBridge":
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def sync_investigation_state(
        self, 
        investigation_id: str, 
        state: Dict[str, Any]  # Using Dict instead of dynamic InvestigationState
    ) -> Dict[str, Any]:
        """
        Synchronize investigation state with backend services.
        
        Args:
            investigation_id: Unique ID of the investigation
            state: Current investigation state
            
        Returns:
            Synchronization result
        """
        url = f"{self.client.base_url}/api/investigation/{investigation_id}/state"
        
        # Prepare state data for sync
        current_phase = state.get("current_phase")
        overall_status = state.get("overall_status")
        
        # Handle enum values safely
        current_phase_value = current_phase.value if current_phase and hasattr(current_phase, 'value') else str(current_phase or "")
        overall_status_value = overall_status.value if overall_status and hasattr(overall_status, 'value') else str(overall_status or "")
        
        sync_data = {
            "investigation_id": investigation_id,
            "current_phase": current_phase_value,
            "overall_status": overall_status_value,
            "progress_percentage": state.get("progress_percentage", 0),
            "sources_used": state.get("sources_used", []),
            "agents_participated": state.get("agents_participated", []),
            "confidence_level": state.get("confidence_level", 0.0),
            "errors_count": len(state.get("errors", [])),
            "warnings_count": len(state.get("warnings", [])),
            "total_execution_time": state.get("total_execution_time", 0.0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(url, json=sync_data) as response:
                if response.status == 200:
                    result = await response.json()
                    # Cast result to expected type
                    return cast(Dict[str, Any], result)
                else:
                    error_text = await response.text()
                    self.logger.error(f"State sync failed: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}", "success": False}
        except Exception as e:
            error_msg = str(e)  # Explicitly convert to string
            self.logger.error(f"State sync error: {error_msg}")
            return {"error": error_msg, "success": False}
    
    async def submit_scraping_task(
        self, 
        investigation_id: str, 
        urls: List[str], 
        prompt: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Submit a scraping task to backend services and track it.
        
        Args:
            investigation_id: Investigation ID this task belongs to
            urls: URLs to scrape
            prompt: Natural language prompt for extraction
            schema: Optional schema for structured extraction
            
        Returns:
            Task submission result with task ID
        """
        # First submit the scraping task
        submission_result = await self.client.execute_scraping(urls, prompt, schema)
        
        # Ensure we have a properly typed result
        if not isinstance(submission_result, dict):
            submission_result = {"success": False, "error": "Invalid response from scraping service"}
        
        if not submission_result.get("success"):
            return submission_result
        
        task_id = submission_result.get("task_id")
        if not task_id:
            return {
                "success": False,
                "error": "No task ID returned from backend"
            }
        
        # Create task tracking entry
        tracking_data = {
            "task_id": task_id,
            "investigation_id": investigation_id,
            "task_type": TaskType.SCRAPING.value,
            "urls": urls,
            "prompt": prompt,
            "created_at": datetime.utcnow().isoformat(),
            "status": TaskStatus.PENDING.value
        }
        
        # Register the task in the backend task tracking system
        tracking_url = f"{self.client.base_url}/api/tasks/register"
        try:
            async with self.client.session.post(tracking_url, json=tracking_data) as response:
                if response.status == 200:
                    tracking_result = await response.json()
                    return {
                        "success": True,
                        "task_id": task_id,
                        "tracking_result": cast(Dict[str, Any], tracking_result)
                    }
                else:
                    error_text = await response.text()
                    self.logger.error(f"Task tracking registration failed: {response.status} - {error_text}")
                    # Still return the original task ID since backend task was created
                    return {
                        "success": True,
                        "task_id": task_id,
                        "warning": f"Task created but tracking registration failed: {error_text}"
                    }
        except Exception as e:
            error_msg = str(e)  # Explicitly convert to string
            self.logger.error(f"Task tracking error: {error_msg}")
            # Still return the original task ID since backend task was created
            return {
                "success": True,
                "task_id": task_id,
                "warning": f"Task created but tracking registration failed: {error_msg}"
            }
    
    async def submit_search_task(
        self,
        investigation_id: str,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Submit a search task to backend services.
        
        Args:
            investigation_id: Investigation ID this task belongs to
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Task submission result
        """
        url = f"{self.client.base_url}/api/tasks/search"
        payload = {
            "investigation_id": investigation_id,
            "query": query,
            "max_results": max_results,
            "task_type": TaskType.SEARCH.value
        }
        
        try:
            async with self.client.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return cast(Dict[str, Any], result)
                else:
                    error_text = await response.text()
                    logger.error(f"Search task submission failed: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}", "success": False}
        except Exception as e:
            error_msg = str(e)  # Explicitly convert to string
            logger.error(f"Search task submission error: {error_msg}")
            return {"error": error_msg, "success": False}
    
    async def get_task_results_with_cache(
        self, 
        task_id: str
    ) -> Dict[str, Any]:
        """
        Get task results with caching to avoid repeated backend calls.
        
        Args:
            task_id: Backend task ID to get results for
            
        Returns:
            Task results
        """
        # For now, just return the results from backend
        # In a real implementation, we would cache results
        result = await self.client.get_task_results(task_id)
        # Ensure we return the expected type
        if isinstance(result, dict):
            return result
        else:
            return {"results": result, "task_id": task_id}
    
    async def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a task in the backend system.
        
        Args:
            task_id: Backend task ID to update
            status: New status
            details: Additional status details
            
        Returns:
            Update result
        """
        url = f"{self.client.base_url}/api/tasks/{task_id}/status"
        payload = {
            "status": status.value,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            async with self.client.session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return cast(Dict[str, Any], result)
                else:
                    error_text = await response.text()
                    logger.error(f"Task status update failed: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}", "success": False}
        except Exception as e:
            error_msg = str(e)  # Explicitly convert to string
            logger.error(f"Task status update error: {error_msg}")
            return {"error": error_msg, "success": False}


# Global bridge instance
_bridge_instance = None


async def get_global_ai_bridge() -> AIBackendBridge:
    """
    Get the global AI backend bridge instance.
    Note: This returns a new instance each time, as proper async singleton handling
    would require more complex implementation with connection management.
    """
    global _bridge_instance
    if _bridge_instance is None:
        # Dynamically import the IntegrationConfig to avoid import issues
        import importlib.util
        import os
        
        # Import the config module dynamically
        config_module_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'integration_config.py')
        spec = importlib.util.spec_from_file_location("integration_config", config_module_path)
        if spec is not None and spec.loader is not None:
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            IntegrationConfig = config_module.IntegrationConfig
        else:
            raise ImportError("Could not load integration config module")
        
        config = IntegrationConfig()
        _bridge_instance = AIBackendBridge(base_url=config.backend_scraping_base_url)
    return _bridge_instance


async def close_global_ai_bridge() -> None:
    """
    Close the global AI backend bridge instance.
    """
    global _bridge_instance
    if _bridge_instance:
        await _bridge_instance.__aexit__(None, None, None)
        _bridge_instance = None