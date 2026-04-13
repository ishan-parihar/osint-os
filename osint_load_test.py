#!/usr/bin/env python3
"""
CRITICAL OSINT SYSTEM LOAD TESTING FRAMEWORK
IMMEDIATE PRODUCTION READINESS ASSESSMENT

Comprehensive load testing for OSINT platform including:
- API endpoint stress testing
- Concurrent investigation management
- Search operation performance
- WebSocket connection limits
- Database query performance
- Memory and CPU monitoring
"""

import asyncio
import aiohttp
import time
import json
import uuid
import random
import statistics
import threading
import psutil
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging

# Configure logging for performance monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LoadTestResult:
    """Load test result data structure"""
    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]

@dataclass
class SystemMetrics:
    """System performance metrics during test"""
    cpu_usage: float
    memory_usage: float
    memory_available: float
    disk_usage: float
    network_io: Dict[str, int]
    timestamp: datetime

class OSINTLoadTester:
    """Comprehensive OSINT Load Testing Framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = []
        self.system_metrics = []
        self.active_connections = 0
        self.max_connections = 0
        
        # OSINT-specific test data
        self.test_queries = [
            "cybersecurity threats 2024",
            "dark web marketplaces",
            "social media intelligence",
            "geopolitical intelligence",
            "corporate espionage indicators",
            "insider threat detection",
            "supply chain vulnerabilities",
            "emerging malware families",
            "threat actor groups",
            "digital forensics techniques"
        ]
        
        self.investigation_targets = [
            "suspicious domain analysis",
            "threat actor attribution", 
            "vulnerability assessment",
            "malware investigation",
            "network intrusion analysis",
            "data breach investigation",
            "phishing campaign analysis",
            "APT group tracking"
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=1000,
            limit_per_host=500,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'OSINT-LoadTester/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def start_system_monitoring(self):
        """Start background system monitoring"""
        def monitor():
            while True:
                try:
                    cpu = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    network = psutil.net_io_counters()
                    
                    metrics = SystemMetrics(
                        cpu_usage=cpu,
                        memory_usage=memory.percent,
                        memory_available=memory.available / (1024**3),  # GB
                        disk_usage=disk.percent,
                        network_io={
                            'bytes_sent': network.bytes_sent,
                            'bytes_recv': network.bytes_recv
                        },
                        timestamp=datetime.now()
                    )
                    
                    self.system_metrics.append(metrics)
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"System monitoring error: {e}")
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        logger.info("System monitoring started")
    
    async def test_endpoint_load(self, endpoint: str, method: str = 'GET', 
                               data: Dict = None, concurrent_users: int = 50, 
                               duration: int = 60) -> LoadTestResult:
        """
        Perform comprehensive load test on specific endpoint
        
        Args:
            endpoint: API endpoint to test
            method: HTTP method
            data: Request data for POST requests
            concurrent_users: Number of concurrent users
            duration: Test duration in seconds
        """
        logger.info(f"Starting load test: {method} {endpoint} - {concurrent_users} users for {duration}s")
        
        url = f"{self.base_url}{endpoint}"
        response_times = []
        errors = []
        start_time = time.time()
        
        async def make_request():
            """Make individual request"""
            request_start = time.time()
            try:
                if method.upper() == 'GET':
                    async with self.session.get(url) as response:
                        await response.text()
                        request_end = time.time()
                        return request_end - request_start, response.status, None
                elif method.upper() == 'POST':
                    async with self.session.post(url, json=data) as response:
                        await response.text()
                        request_end = time.time()
                        return request_end - request_start, response.status, None
            except Exception as e:
                request_end = time.time()
                return request_end - request_start, 0, str(e)
        
        async def user_simulation():
            """Simulate individual user behavior"""
            user_response_times = []
            user_errors = []
            user_start = time.time()
            
            while time.time() - user_start < duration:
                response_time, status, error = await make_request()
                
                if error or status >= 400:
                    user_errors.append(error or f"HTTP {status}")
                else:
                    user_response_times.append(response_time)
                
                # Realistic think time between requests
                await asyncio.sleep(random.uniform(0.5, 2.0))
            
            return user_response_times, user_errors
        
        # Execute concurrent user simulations
        tasks = [user_simulation() for _ in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        # Aggregate results
        for user_times, user_errors in results:
            response_times.extend(user_times)
            errors.extend(user_errors)
        
        # Calculate metrics
        total_time = time.time() - start_time
        successful_requests = len(response_times)
        total_requests = successful_requests + len(errors)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            p99_response_time = statistics.quantiles(response_times, n=100)[98]  # 99th percentile
        else:
            avg_response_time = min_response_time = max_response_time = p95_response_time = p99_response_time = 0
        
        result = LoadTestResult(
            endpoint=endpoint,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=len(errors),
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            requests_per_second=total_requests / total_time,
            error_rate=len(errors) / total_requests if total_requests > 0 else 0,
            errors=errors[:10]  # Keep first 10 errors for analysis
        )
        
        self.results.append(result)
        logger.info(f"Completed load test for {endpoint}: {result.requests_per_second:.2f} RPS, {result.error_rate:.2%} error rate")
        return result
    
    async def test_osint_investigations(self) -> LoadTestResult:
        """Test OSINT investigation management under load"""
        logger.info("Testing OSINT investigation management...")
        
        # Test investigation creation
        investigation_data = {
            "title": random.choice(self.investigation_targets),
            "description": "Load test investigation for performance assessment",
            "classification": "CONFIDENTIAL",
            "priority": "HIGH"
        }
        
        return await self.test_endpoint_load(
            endpoint="/api/osint/investigations",
            method="POST",
            data=investigation_data,
            concurrent_users=20,
            duration=30
        )
    
    async def test_osint_search(self) -> LoadTestResult:
        """Test OSINT search operations"""
        logger.info("Testing OSINT search operations...")
        
        query = random.choice(self.test_queries)
        return await self.test_endpoint_load(
            endpoint=f"/api/osint/search?query={query}&max_results=10",
            method="POST",
            concurrent_users=30,
            duration=45
        )
    
    async def test_premium_search(self) -> LoadTestResult:
        """Test premium search with scraping"""
        logger.info("Testing premium search operations...")
        
        search_data = {
            "query": random.choice(self.test_queries),
            "engines": ["duckduckgo", "brave"],
            "max_pages": 1,
            "use_browser": False
        }
        
        return await self.test_endpoint_load(
            endpoint="/api/osint/premium-search",
            method="POST",
            data=search_data,
            concurrent_users=15,
            duration=60
        )
    
    async def test_ai_investigation(self) -> LoadTestResult:
        """Test AI-powered investigation startup"""
        logger.info("Testing AI investigation operations...")
        
        investigation_data = {
            "target": random.choice(self.investigation_targets),
            "objective": "Comprehensive OSINT collection and analysis",
            "scope": ["web", "social_media", "dark_web"],
            "priority": "HIGH",
            "requirements": {"depth": "comprehensive", "timeline": "24h"}
        }
        
        return await self.test_endpoint_load(
            endpoint="/api/ai-investigation/start",
            method="POST",
            data=investigation_data,
            concurrent_users=10,
            duration=40
        )
    
    async def test_websocket_connections(self, max_connections: int = 100) -> Dict[str, Any]:
        """Test WebSocket connection limits and performance"""
        logger.info(f"Testing WebSocket connections - up to {max_connections} connections")
        
        websocket_results = {
            "successful_connections": 0,
            "failed_connections": 0,
            "connection_times": [],
            "errors": []
        }
        
        async def connect_websocket(connection_id: int):
            """Establish WebSocket connection"""
            start_time = time.time()
            try:
                ws_url = f"ws://localhost:8000/api/ws/test-pipeline-{connection_id}"
                
                # Use aiohttp client session for WebSocket
                async with self.session.ws_connect(ws_url) as ws:
                    connection_time = time.time() - start_time
                    websocket_results["connection_times"].append(connection_time)
                    websocket_results["successful_connections"] += 1
                    
                    # Send ping and wait for response
                    await ws.send_json({"type": "ping", "connection_id": connection_id})
                    response = await ws.receive_json(timeout=5)
                    
                    # Keep connection alive for brief period
                    await asyncio.sleep(2)
                    
            except Exception as e:
                websocket_results["failed_connections"] += 1
                websocket_results["errors"].append(str(e))
        
        # Test incremental connection increases
        for batch_size in [10, 25, 50, 100]:
            if batch_size > max_connections:
                break
                
            logger.info(f"Testing {batch_size} concurrent WebSocket connections...")
            tasks = [connect_websocket(i) for i in range(batch_size)]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Brief pause between batches
            await asyncio.sleep(1)
        
        return websocket_results
    
    async def test_database_performance(self) -> Dict[str, Any]:
        """Test database query performance under load"""
        logger.info("Testing database query performance...")
        
        db_results = {
            "investigation_queries": [],
            "search_queries": [],
            "concurrent_access_results": []
        }
        
        # Test investigation listing with filters
        async def test_investigation_queries():
            for _ in range(50):
                start_time = time.time()
                try:
                    async with self.session.get("/api/osint/investigations") as response:
                        await response.json()
                        query_time = time.time() - start_time
                        db_results["investigation_queries"].append(query_time)
                except Exception as e:
                    logger.error(f"Investigation query error: {e}")
        
        # Test search queries
        async def test_search_queries():
            for _ in range(30):
                query = random.choice(self.test_queries)
                start_time = time.time()
                try:
                    async with self.session.get(f"/api/osint/search?query={query}") as response:
                        await response.json()
                        query_time = time.time() - start_time
                        db_results["search_queries"].append(query_time)
                except Exception as e:
                    logger.error(f"Search query error: {e}")
        
        # Execute concurrent database access
        tasks = [test_investigation_queries(), test_search_queries()]
        await asyncio.gather(*tasks)
        
        return db_results
    
    async def run_comprehensive_load_test(self) -> Dict[str, Any]:
        """Execute complete OSINT load testing suite"""
        logger.info("🚀 STARTING COMPREHENSIVE OSINT LOAD TESTING")
        
        # Start system monitoring
        self.start_system_monitoring()
        
        # Initialize results structure
        test_results = {
            "test_start_time": datetime.now(),
            "endpoint_tests": {},
            "websocket_tests": {},
            "database_tests": {},
            "system_metrics": [],
            "performance_summary": {}
        }
        
        try:
            # Test 1: Health check baseline
            logger.info("Establishing baseline with health check...")
            baseline = await self.test_endpoint_load("/health", concurrent_users=5, duration=10)
            test_results["endpoint_tests"]["health_baseline"] = baseline
            
            # Test 2: OSINT investigations
            test_results["endpoint_tests"]["investigations"] = await self.test_osint_investigations()
            
            # Test 3: Search operations
            test_results["endpoint_tests"]["search"] = await self.test_osint_search()
            
            # Test 4: Premium search
            test_results["endpoint_tests"]["premium_search"] = await self.test_premium_search()
            
            # Test 5: AI investigations
            test_results["endpoint_tests"]["ai_investigation"] = await self.test_ai_investigation()
            
            # Test 6: WebSocket connections
            test_results["websocket_tests"] = await self.test_websocket_connections()
            
            # Test 7: Database performance
            test_results["database_tests"] = await self.test_database_performance()
            
            # Collect final system metrics
            await asyncio.sleep(2)  # Allow final metrics collection
            test_results["system_metrics"] = self.system_metrics
            test_results["test_end_time"] = datetime.now()
            
            # Generate performance summary
            test_results["performance_summary"] = self.generate_performance_summary(test_results)
            
            logger.info("✅ COMPREHENSIVE LOAD TESTING COMPLETED")
            return test_results
            
        except Exception as e:
            logger.error(f"Load testing failed: {e}")
            test_results["error"] = str(e)
            return test_results
    
    def generate_performance_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance analysis"""
        summary = {
            "overall_assessment": "UNKNOWN",
            "critical_issues": [],
            "performance_bottlenecks": [],
            "capacity_recommendations": [],
            "key_metrics": {}
        }
        
        # Analyze endpoint performance
        endpoint_tests = results.get("endpoint_tests", {})
        
        # Calculate overall metrics
        total_requests = sum(test.total_requests for test in endpoint_tests.values())
        total_errors = sum(test.failed_requests for test in endpoint_tests.values())
        overall_error_rate = total_errors / total_requests if total_requests > 0 else 0
        
        avg_rps = statistics.mean([test.requests_per_second for test in endpoint_tests.values()])
        avg_response_time = statistics.mean([test.avg_response_time for test in endpoint_tests.values()])
        
        summary["key_metrics"] = {
            "total_requests_processed": total_requests,
            "overall_error_rate": overall_error_rate,
            "average_requests_per_second": avg_rps,
            "average_response_time": avg_response_time,
            "peak_response_time": max(test.max_response_time for test in endpoint_tests.values()),
            "peak_concurrent_connections": len(self.system_metrics)
        }
        
        # Identify performance issues
        if overall_error_rate > 0.05:  # 5% error rate threshold
            summary["critical_issues"].append(f"High error rate: {overall_error_rate:.2%}")
        
        if avg_response_time > 2.0:  # 2 second response time threshold
            summary["performance_bottlenecks"].append(f"Slow response times: {avg_response_time:.2f}s average")
        
        # WebSocket analysis
        ws_tests = results.get("websocket_tests", {})
        if ws_tests.get("failed_connections", 0) > ws_tests.get("successful_connections", 0) * 0.1:
            summary["critical_issues"].append("WebSocket connection failures exceed 10%")
        
        # System resource analysis
        if self.system_metrics:
            max_cpu = max(m.cpu_usage for m in self.system_metrics)
            max_memory = max(m.memory_usage for m in self.system_metrics)
            
            if max_cpu > 90:
                summary["performance_bottlenecks"].append(f"High CPU usage: {max_cpu:.1f}%")
            
            if max_memory > 90:
                summary["performance_bottlenecks"].append(f"High memory usage: {max_memory:.1f}%")
        
        # Generate recommendations
        if avg_rps < 100:
            summary["capacity_recommendations"].append("Consider optimizing for higher throughput")
        
        if summary["critical_issues"]:
            summary["overall_assessment"] = "CRITICAL ISSUES FOUND"
        elif summary["performance_bottlenecks"]:
            summary["overall_assessment"] = "PERFORMANCE ISSUES DETECTED"
        else:
            summary["overall_assessment"] = "PERFORMANCE ACCEPTABLE"
        
        return summary
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed performance report"""
        report = []
        report.append("=" * 80)
        report.append("OSINT SYSTEM PERFORMANCE LOAD TEST REPORT")
        report.append("=" * 80)
        report.append(f"Test Duration: {results['test_end_time'] - results['test_start_time']}")
        report.append(f"Generated: {datetime.now()}")
        report.append("")
        
        # Performance Summary
        summary = results.get("performance_summary", {})
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"Overall Assessment: {summary.get('overall_assessment', 'UNKNOWN')}")
        report.append("")
        
        # Key Metrics
        metrics = summary.get("key_metrics", {})
        report.append("KEY PERFORMANCE METRICS")
        report.append("-" * 40)
        for key, value in metrics.items():
            if isinstance(value, float):
                report.append(f"{key}: {value:.2f}")
            else:
                report.append(f"{key}: {value}")
        report.append("")
        
        # Endpoint Results
        report.append("ENDPOINT PERFORMANCE RESULTS")
        report.append("-" * 40)
        for endpoint, result in results.get("endpoint_tests", {}).items():
            report.append(f"\n{endpoint.upper()}:")
            report.append(f"  Requests/sec: {result.requests_per_second:.2f}")
            report.append(f"  Avg Response Time: {result.avg_response_time:.3f}s")
            report.append(f"  95th Percentile: {result.p95_response_time:.3f}s")
            report.append(f"  Error Rate: {result.error_rate:.2%}")
            report.append(f"  Total Requests: {result.total_requests}")
            if result.errors:
                report.append(f"  Sample Errors: {result.errors[:3]}")
        
        # Critical Issues
        if summary.get("critical_issues"):
            report.append("\nCRITICAL ISSUES")
            report.append("-" * 40)
            for issue in summary["critical_issues"]:
                report.append(f"❌ {issue}")
        
        # Performance Bottlenecks
        if summary.get("performance_bottlenecks"):
            report.append("\nPERFORMANCE BOTTLENECKS")
            report.append("-" * 40)
            for bottleneck in summary["performance_bottlenecks"]:
                report.append(f"⚠️  {bottleneck}")
        
        # Recommendations
        if summary.get("capacity_recommendations"):
            report.append("\nCAPACITY RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in summary["capacity_recommendations"]:
                report.append(f"💡 {rec}")
        
        # System Metrics Summary
        if results.get("system_metrics"):
            report.append("\nSYSTEM RESOURCE USAGE")
            report.append("-" * 40)
            metrics = results["system_metrics"]
            if metrics:
                max_cpu = max(m.cpu_usage for m in metrics)
                max_memory = max(m.memory_usage for m in metrics)
                avg_cpu = statistics.mean(m.cpu_usage for m in metrics)
                avg_memory = statistics.mean(m.memory_usage for m in metrics)
                
                report.append(f"Peak CPU Usage: {max_cpu:.1f}%")
                report.append(f"Average CPU Usage: {avg_cpu:.1f}%")
                report.append(f"Peak Memory Usage: {max_memory:.1f}%")
                report.append(f"Average Memory Usage: {avg_memory:.1f}%")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

async def main():
    """Execute comprehensive OSINT load testing"""
    logger.info("🔥 INITIATING CRITICAL OSINT LOAD TESTING FOR PRODUCTION READINESS")
    
    async with OSINTLoadTester() as tester:
        results = await tester.run_comprehensive_load_test()
        
        # Generate and save report
        report = tester.generate_performance_report(results)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"OSINT_PERFORMANCE_REPORT_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        # Also save raw results as JSON
        json_file = f"OSINT_LOAD_TEST_RESULTS_{timestamp}.json"
        with open(json_file, 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
            
            json.dump(results, f, indent=2, default=json_serializer)
        
        print(f"\n🎯 LOAD TESTING COMPLETED!")
        print(f"📊 Performance Report: {report_file}")
        print(f"📈 Raw Results: {json_file}")
        print("\n" + report)
        
        return results

if __name__ == "__main__":
    asyncio.run(main())