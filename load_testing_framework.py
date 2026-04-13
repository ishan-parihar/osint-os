#!/usr/bin/env python3
"""
OSINT Platform Comprehensive Load Testing and Benchmarking Framework
======================================================================

This framework provides comprehensive load testing and benchmarking capabilities
specifically designed for OSINT operational workloads and intelligence agency demands.

Features:
- API endpoint stress testing
- OSINT data collection performance testing
- WebSocket connection stress testing
- Database query performance benchmarking
- Concurrent user capacity testing
- Real-time performance monitoring
- Automated performance report generation
"""

import asyncio
import time
import json
import uuid
import statistics
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import psutil
import httpx
import websockets
from locust import HttpUser, task, between, events
import pytest
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    endpoint: str
    response_time: float
    status_code: int
    success: bool
    timestamp: datetime
    user_id: str
    memory_usage: float
    cpu_usage: float
    error_message: Optional[str] = None

@dataclass
class LoadTestConfig:
    """Load test configuration"""
    base_url: str = "http://localhost:8000"
    concurrent_users: int = 10
    test_duration: int = 300  # seconds
    ramp_up_time: int = 60   # seconds
    requests_per_second: int = 5
    websocket_connections: int = 5
    database_queries: int = 100
    
class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.metrics_history = []
        self.monitoring = False
        self.start_time = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        self.monitoring = True
        self.start_time = datetime.now()
        logger.info("Performance monitoring started")
        
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        logger.info("Performance monitoring stopped")
        
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system performance metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "disk_usage_percent": psutil.disk_usage('/').percent,
            "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
        }
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric"""
        self.metrics_history.append(metric)
        
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.metrics_history:
            return {}
            
        response_times = [m.response_time for m in self.metrics_history if m.success]
        success_rate = sum(1 for m in self.metrics_history if m.success) / len(self.metrics_history)
        
        return {
            "total_requests": len(self.metrics_history),
            "successful_requests": sum(1 for m in self.metrics_history if m.success),
            "failed_requests": sum(1 for m in self.metrics_history if not m.success),
            "success_rate": success_rate,
            "avg_response_time": statistics.mean(response_times) if response_times else 0,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "p95_response_time": np.percentile(response_times, 95) if response_times else 0,
            "p99_response_time": np.percentile(response_times, 99) if response_times else 0,
            "requests_per_second": len(self.metrics_history) / ((datetime.now() - self.start_time).total_seconds() if self.start_time else 1)
        }

class OSINTLoadTester:
    """Main OSINT load testing framework"""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.monitor = PerformanceMonitor()
        self.results = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def setup_test_environment(self):
        """Setup test environment with sample data"""
        logger.info("Setting up test environment...")
        
        # Create test investigation
        investigation_data = {
            "title": "Load Test Investigation",
            "description": "Investigation for load testing purposes",
            "classification": "CONFIDENTIAL",
            "priority": "HIGH"
        }
        
        try:
            response = await self.client.post(
                f"{self.config.base_url}/investigations",
                json=investigation_data
            )
            if response.status_code == 200:
                investigation = response.json()
                self.test_investigation_id = investigation["id"]
                logger.info(f"Created test investigation: {self.test_investigation_id}")
            else:
                logger.error(f"Failed to create test investigation: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error setting up test environment: {e}")
            return False
            
        return True
    
    async def test_investigation_endpoints(self, user_id: str) -> List[PerformanceMetrics]:
        """Test investigation CRUD endpoints"""
        metrics = []
        
        # Test list investigations
        start_time = time.time()
        try:
            response = await self.client.get(f"{self.config.base_url}/investigations")
            response_time = time.time() - start_time
            
            metric = PerformanceMetrics(
                endpoint="GET /investigations",
                response_time=response_time,
                status_code=response.status_code,
                success=response.status_code == 200,
                timestamp=datetime.now(),
                user_id=user_id,
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent()
            )
            metrics.append(metric)
            
        except Exception as e:
            metric = PerformanceMetrics(
                endpoint="GET /investigations",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                error_message=str(e)
            )
            metrics.append(metric)
        
        # Test get specific investigation
        if hasattr(self, 'test_investigation_id'):
            start_time = time.time()
            try:
                response = await self.client.get(
                    f"{self.config.base_url}/investigations/{self.test_investigation_id}"
                )
                response_time = time.time() - start_time
                
                metric = PerformanceMetrics(
                    endpoint=f"GET /investigations/{{id}}",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=response.status_code == 200,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent()
                )
                metrics.append(metric)
                
            except Exception as e:
                metric = PerformanceMetrics(
                    endpoint=f"GET /investigations/{{id}}",
                    response_time=time.time() - start_time,
                    status_code=500,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent(),
                    error_message=str(e)
                )
                metrics.append(metric)
        
        return metrics
    
    async def test_search_endpoints(self, user_id: str) -> List[PerformanceMetrics]:
        """Test search endpoints under load"""
        metrics = []
        test_queries = [
            "cybersecurity threat intelligence",
            "dark web monitoring",
            "social media analysis",
            "geopolitical intelligence",
            "financial crime investigation"
        ]
        
        for query in test_queries:
            # Test basic search
            start_time = time.time()
            try:
                response = await self.client.post(
                    f"{self.config.base_url}/search",
                    json={"query": query, "max_results": 10}
                )
                response_time = time.time() - start_time
                
                metric = PerformanceMetrics(
                    endpoint="POST /search",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=response.status_code == 200,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent()
                )
                metrics.append(metric)
                
            except Exception as e:
                metric = PerformanceMetrics(
                    endpoint="POST /search",
                    response_time=time.time() - start_time,
                    status_code=500,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent(),
                    error_message=str(e)
                )
                metrics.append(metric)
            
            # Test premium search
            start_time = time.time()
            try:
                response = await self.client.post(
                    f"{self.config.base_url}/premium-search",
                    json={
                        "query": query,
                        "engines": ["duckduckgo", "brave"],
                        "max_pages": 1,
                        "use_browser": False
                    }
                )
                response_time = time.time() - start_time
                
                metric = PerformanceMetrics(
                    endpoint="POST /premium-search",
                    response_time=response_time,
                    status_code=response.status_code,
                    success=response.status_code == 200,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent()
                )
                metrics.append(metric)
                
            except Exception as e:
                metric = PerformanceMetrics(
                    endpoint="POST /premium-search",
                    response_time=time.time() - start_time,
                    status_code=500,
                    success=False,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent(),
                    error_message=str(e)
                )
                metrics.append(metric)
        
        return metrics
    
    async def test_websocket_connections(self, user_id: str) -> List[PerformanceMetrics]:
        """Test WebSocket connection performance"""
        metrics = []
        
        if not hasattr(self, 'test_investigation_id'):
            return metrics
            
        try:
            # Test WebSocket connection
            start_time = time.time()
            uri = f"ws://localhost:8000/ws/{self.test_investigation_id}"
            
            async with websockets.connect(uri) as websocket:
                connect_time = time.time() - start_time
                
                # Send test message
                message_start = time.time()
                await websocket.send(json.dumps({"type": "test", "message": "load test"}))
                response = await websocket.recv()
                message_time = time.time() - message_start
                
                metric = PerformanceMetrics(
                    endpoint="WebSocket /ws/{investigation_id}",
                    response_time=connect_time + message_time,
                    status_code=200,
                    success=True,
                    timestamp=datetime.now(),
                    user_id=user_id,
                    memory_usage=psutil.virtual_memory().percent,
                    cpu_usage=psutil.cpu_percent()
                )
                metrics.append(metric)
                
        except Exception as e:
            metric = PerformanceMetrics(
                endpoint="WebSocket /ws/{investigation_id}",
                response_time=time.time() - start_time,
                status_code=500,
                success=False,
                timestamp=datetime.now(),
                user_id=user_id,
                memory_usage=psutil.virtual_memory().percent,
                cpu_usage=psutil.cpu_percent(),
                error_message=str(e)
            )
            metrics.append(metric)
        
        return metrics
    
    async def simulate_user_workload(self, user_id: str) -> List[PerformanceMetrics]:
        """Simulate realistic OSINT user workload"""
        all_metrics = []
        
        # Simulate investigation workflow
        all_metrics.extend(await self.test_investigation_endpoints(user_id))
        
        # Simulate search operations
        all_metrics.extend(await self.test_search_endpoints(user_id))
        
        # Simulate WebSocket usage
        all_metrics.extend(await self.test_websocket_connections(user_id))
        
        return all_metrics
    
    async def run_concurrent_load_test(self):
        """Run concurrent load test with multiple users"""
        logger.info(f"Starting load test with {self.config.concurrent_users} concurrent users")
        
        self.monitor.start_monitoring()
        
        # Create tasks for concurrent users
        tasks = []
        for i in range(self.config.concurrent_users):
            user_id = f"user_{i}_{uuid.uuid4().hex[:8]}"
            task = asyncio.create_task(self.simulate_user_workload(user_id))
            tasks.append(task)
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all metrics
        for result in results:
            if isinstance(result, list):
                for metric in result:
                    self.monitor.record_metric(metric)
            elif isinstance(result, Exception):
                logger.error(f"User workload failed: {result}")
        
        self.monitor.stop_monitoring()
        
        return self.monitor.get_summary_stats()
    
    async def run_sustained_load_test(self):
        """Run sustained load test over time"""
        logger.info(f"Starting sustained load test for {self.config.test_duration} seconds")
        
        self.monitor.start_monitoring()
        start_time = time.time()
        
        while time.time() - start_time < self.config.test_duration:
            # Run batch of concurrent users
            batch_tasks = []
            for i in range(min(self.config.concurrent_users, 10)):  # Smaller batches
                user_id = f"user_{uuid.uuid4().hex[:8]}"
                task = asyncio.create_task(self.simulate_user_workload(user_id))
                batch_tasks.append(task)
            
            await asyncio.gather(*batch_tasks, return_exceptions=True)
            await asyncio.sleep(1.0 / self.config.requests_per_second)
        
        self.monitor.stop_monitoring()
        
        return self.monitor.get_summary_stats()
    
    def generate_performance_report(self, test_results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report = {
            "test_metadata": {
                "timestamp": datetime.now().isoformat(),
                "test_duration": self.config.test_duration,
                "concurrent_users": self.config.concurrent_users,
                "requests_per_second": self.config.requests_per_second,
                "base_url": self.config.base_url
            },
            "performance_summary": test_results,
            "system_metrics": self.monitor.collect_system_metrics(),
            "detailed_metrics": [asdict(m) for m in self.monitor.metrics_history[-100:]],  # Last 100 metrics
            "recommendations": self._generate_recommendations(test_results)
        }
        
        # Save report to file
        report_filename = f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Performance report saved to {report_filename}")
        return report_filename
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations based on results"""
        recommendations = []
        
        if results.get("success_rate", 0) < 0.95:
            recommendations.append("Success rate below 95% - investigate error handling and retry mechanisms")
        
        if results.get("avg_response_time", 0) > 2.0:
            recommendations.append("Average response time above 2s - consider optimization and caching")
        
        if results.get("p95_response_time", 0) > 5.0:
            recommendations.append("95th percentile response time above 5s - optimize critical paths")
        
        if results.get("requests_per_second", 0) < self.config.requests_per_second * 0.8:
            recommendations.append("Throughput below target - consider scaling and load balancing")
        
        system_metrics = self.monitor.collect_system_metrics()
        if system_metrics.get("cpu_percent", 0) > 80:
            recommendations.append("High CPU usage - consider scaling compute resources")
        
        if system_metrics.get("memory_percent", 0) > 80:
            recommendations.append("High memory usage - investigate memory leaks and optimize data structures")
        
        return recommendations
    
    async def cleanup(self):
        """Cleanup test environment"""
        await self.client.aclose()

class LocustOSINTUser(HttpUser):
    """Locust user class for distributed load testing"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.investigation_id = None
        
    @task(3)
    def test_investigation_list(self):
        """Test investigation listing"""
        self.client.get("/investigations")
    
    @task(2)
    def test_search(self):
        """Test search functionality"""
        self.client.post("/search", json={"query": "test query", "max_results": 10})
    
    @task(1)
    def test_premium_search(self):
        """Test premium search"""
        self.client.post("/premium-search", json={
            "query": "test premium search",
            "engines": ["duckduckgo"],
            "max_pages": 1
        })
    
    @task(1)
    def test_create_investigation(self):
        """Test investigation creation"""
        if not self.investigation_id:
            response = self.client.post("/investigations", json={
                "title": "Load Test Investigation",
                "description": "Test investigation",
                "classification": "CONFIDENTIAL",
                "priority": "MEDIUM"
            })
            if response.status_code == 200:
                self.investigation_id = response.json()["id"]

async def main():
    """Main execution function"""
    print("=" * 80)
    print("OSINT PLATFORM COMPREHENSIVE LOAD TESTING & BENCHMARKING")
    print("=" * 80)
    
    # Load test configuration
    config = LoadTestConfig(
        base_url="http://localhost:8000",
        concurrent_users=20,
        test_duration=300,
        ramp_up_time=60,
        requests_per_second=10,
        websocket_connections=10
    )
    
    # Initialize load tester
    tester = OSINTLoadTester(config)
    
    try:
        # Setup test environment
        if not await tester.setup_test_environment():
            logger.error("Failed to setup test environment")
            return
        
        print("\n🚀 Starting Load Testing...")
        
        # Run concurrent load test
        print("\n1. Running Concurrent Load Test...")
        concurrent_results = await tester.run_concurrent_load_test()
        print(f"   ✓ Concurrent test completed: {concurrent_results.get('success_rate', 0):.2%} success rate")
        
        # Run sustained load test
        print("\n2. Running Sustained Load Test...")
        sustained_results = await tester.run_sustained_load_test()
        print(f"   ✓ Sustained test completed: {sustained_results.get('success_rate', 0):.2%} success rate")
        
        # Generate comprehensive report
        print("\n3. Generating Performance Report...")
        all_results = {
            "concurrent_test": concurrent_results,
            "sustained_test": sustained_results
        }
        report_file = tester.generate_performance_report(all_results)
        
        # Display summary
        print("\n" + "=" * 80)
        print("LOAD TESTING RESULTS SUMMARY")
        print("=" * 80)
        print(f"Concurrent Users: {config.concurrent_users}")
        print(f"Test Duration: {config.test_duration}s")
        print(f"Average Response Time: {concurrent_results.get('avg_response_time', 0):.3f}s")
        print(f"95th Percentile: {concurrent_results.get('p95_response_time', 0):.3f}s")
        print(f"Success Rate: {concurrent_results.get('success_rate', 0):.2%}")
        print(f"Requests/Second: {concurrent_results.get('requests_per_second', 0):.2f}")
        print(f"\nReport saved to: {report_file}")
        
        # Performance assessment
        print("\n" + "=" * 80)
        print("PRODUCTION READINESS ASSESSMENT")
        print("=" * 80)
        
        success_rate = concurrent_results.get('success_rate', 0)
        avg_response = concurrent_results.get('avg_response_time', 0)
        p95_response = concurrent_results.get('p95_response_time', 0)
        
        if success_rate >= 0.95 and avg_response <= 1.0 and p95_response <= 3.0:
            print("🟢 READY FOR PRODUCTION")
            print("   • Success rate meets requirements (≥95%)")
            print("   • Response times within acceptable limits")
            print("   • System demonstrates stability under load")
        elif success_rate >= 0.90 and avg_response <= 2.0 and p95_response <= 5.0:
            print("🟡 CONDITIONAL PRODUCTION READY")
            print("   • Performance acceptable with monitoring")
            print("   • Consider optimization for better user experience")
            print("   • Implement scaling strategies for peak loads")
        else:
            print("🔴 NOT PRODUCTION READY")
            print("   • Performance issues need immediate attention")
            print("   • Conduct optimization before production deployment")
            print("   • Review architecture and implement improvements")
        
    except Exception as e:
        logger.error(f"Load testing failed: {e}")
        print(f"\n❌ Load testing failed: {e}")
    
    finally:
        await tester.cleanup()
        print("\n✅ Load testing completed")

if __name__ == "__main__":
    asyncio.run(main())