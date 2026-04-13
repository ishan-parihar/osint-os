#!/usr/bin/env python3
"""
COMPREHENSIVE LOAD TESTING AND BENCHMARKING SUITE
==================================================

Critical production readiness testing for OSINT platform.
Tests all critical endpoints, WebSocket connections, and system performance
under various load conditions.

Author: Performance Specialist
Created: 2025-11-13
Priority: CRITICAL
"""

import asyncio
import time
import json
import uuid
import random
import statistics
import aiohttp
import websockets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import psutil
import threading
import logging
from dataclasses import dataclass
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'load_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class LoadTestConfig:
    """Configuration for load testing scenarios."""
    base_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8000"
    concurrent_users: int = 50
    test_duration: int = 300  # 5 minutes
    ramp_up_time: int = 60   # 1 minute
    requests_per_second: int = 10
    websocket_connections: int = 20
    investigation_count: int = 100
    search_queries: List[str] = None
    
    def __post_init__(self):
        if self.search_queries is None:
            self.search_queries = [
                "cybersecurity threats",
                "dark web monitoring",
                "social media intelligence",
                "network security breaches",
                "threat actor groups",
                "vulnerability assessments",
                "digital forensics",
                "malware analysis",
                "phishing campaigns",
                "data breach investigations"
            ]

@dataclass
class PerformanceMetrics:
    """Performance metrics collection."""
    endpoint: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = None
    errors: List[str] = None
    start_time: datetime = None
    end_time: datetime = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []
        if self.errors is None:
            self.errors = []
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def p95_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=20)[18]  # 95th percentile
    
    @property
    def p99_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.quantiles(self.response_times, n=100)[98]  # 99th percentile

class SystemMonitor:
    """Real-time system monitoring during load tests."""
    
    def __init__(self):
        self.monitoring = False
        self.metrics = {
            'cpu_percent': deque(maxlen=300),  # 5 minutes at 1-second intervals
            'memory_percent': deque(maxlen=300),
            'disk_io': deque(maxlen=300),
            'network_io': deque(maxlen=300),
            'active_connections': deque(maxlen=300)
        }
        self.start_time = None
    
    async def start_monitoring(self):
        """Start system monitoring."""
        self.monitoring = True
        self.start_time = datetime.now()
        logger.info("Starting system monitoring...")
        
        while self.monitoring:
            try:
                # CPU and Memory
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Disk I/O
                disk_io = psutil.disk_io_counters()
                disk_read_mb = disk_io.read_bytes / (1024 * 1024) if disk_io else 0
                disk_write_mb = disk_io.write_bytes / (1024 * 1024) if disk_io else 0
                
                # Network I/O
                net_io = psutil.net_io_counters()
                net_sent_mb = net_io.bytes_sent / (1024 * 1024) if net_io else 0
                net_recv_mb = net_io.bytes_recv / (1024 * 1024) if net_io else 0
                
                # Active connections
                connections = len(psutil.net_connections())
                
                # Store metrics
                self.metrics['cpu_percent'].append(cpu_percent)
                self.metrics['memory_percent'].append(memory.percent)
                self.metrics['disk_io'].append({
                    'read_mb': disk_read_mb,
                    'write_mb': disk_write_mb,
                    'timestamp': datetime.now()
                })
                self.metrics['network_io'].append({
                    'sent_mb': net_sent_mb,
                    'recv_mb': net_recv_mb,
                    'timestamp': datetime.now()
                })
                self.metrics['active_connections'].append(connections)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            await asyncio.sleep(1)
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring = False
        logger.info("System monitoring stopped.")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get monitoring summary."""
        if not self.metrics['cpu_percent']:
            return {}
        
        return {
            'duration_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
            'cpu': {
                'avg': statistics.mean(self.metrics['cpu_percent']),
                'max': max(self.metrics['cpu_percent']),
                'min': min(self.metrics['cpu_percent'])
            },
            'memory': {
                'avg': statistics.mean(self.metrics['memory_percent']),
                'max': max(self.metrics['memory_percent']),
                'min': min(self.metrics['memory_percent'])
            },
            'connections': {
                'avg': statistics.mean(self.metrics['active_connections']),
                'max': max(self.metrics['active_connections']),
                'min': min(self.metrics['active_connections'])
            }
        }

class LoadTestRunner:
    """Main load testing execution engine."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results = defaultdict(PerformanceMetrics)
        self.system_monitor = SystemMonitor()
        self.session = None
        self.websocket_connections = []
        self.user_sessions = []
        
    async def setup(self):
        """Setup test environment."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=50)
        )
        logger.info("Load test environment setup complete.")
    
    async def cleanup(self):
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            try:
                await ws.close()
            except:
                pass
        
        logger.info("Load test cleanup complete.")
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request and measure performance."""
        url = f"{self.config.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            async with self.session.request(method, url, **kwargs) as response:
                response_time = time.time() - start_time
                
                # Update metrics
                if endpoint not in self.results:
                    self.results[endpoint] = PerformanceMetrics(endpoint=endpoint)
                
                metrics = self.results[endpoint]
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                if response.status < 400:
                    metrics.successful_requests += 1
                    return {
                        'success': True,
                        'status': response.status,
                        'response_time': response_time,
                        'data': await response.json() if response.content_type == 'application/json' else await response.text()
                    }
                else:
                    metrics.failed_requests += 1
                    error_msg = f"HTTP {response.status}: {await response.text()}"
                    metrics.errors.append(error_msg)
                    return {
                        'success': False,
                        'status': response.status,
                        'response_time': response_time,
                        'error': error_msg
                    }
        
        except Exception as e:
            response_time = time.time() - start_time
            
            if endpoint not in self.results:
                self.results[endpoint] = PerformanceMetrics(endpoint=endpoint)
            
            metrics = self.results[endpoint]
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.response_times.append(response_time)
            metrics.errors.append(str(e))
            
            return {
                'success': False,
                'response_time': response_time,
                'error': str(e)
            }
    
    async def test_health_endpoints(self):
        """Test health check endpoints."""
        logger.info("Testing health endpoints...")
        
        health_endpoints = [
            '/health',
            '/health/redis',
            '/health/websocket',
            '/health/llm'
        ]
        
        tasks = []
        for _ in range(10):  # 10 requests per endpoint
            for endpoint in health_endpoints:
                tasks.append(self.make_request('GET', endpoint))
        
        await asyncio.gather(*tasks)
        logger.info("Health endpoints testing complete.")
    
    async def test_investigation_crud(self):
        """Test investigation CRUD operations under load."""
        logger.info("Testing investigation CRUD operations...")
        
        tasks = []
        
        # Create investigations
        for i in range(self.config.investigation_count):
            investigation_data = {
                "title": f"Load Test Investigation {i}",
                "description": f"Test investigation for load testing scenario {i}",
                "classification": "CONFIDENTIAL",
                "priority": random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
            }
            tasks.append(self.make_request('POST', '/api/osint/investigations', json=investigation_data))
        
        # Execute creation tasks
        create_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Extract created investigation IDs
        investigation_ids = []
        for result in create_results:
            if isinstance(result, dict) and result.get('success') and result.get('data', {}).get('id'):
                investigation_ids.append(result['data']['id'])
        
        logger.info(f"Created {len(investigation_ids)} investigations")
        
        # Test read operations
        tasks = []
        for investigation_id in investigation_ids:
            for _ in range(5):  # 5 reads per investigation
                tasks.append(self.make_request('GET', f'/api/osint/investigations/{investigation_id}'))
        
        await asyncio.gather(*tasks)
        
        # Test list operations
        tasks = []
        for _ in range(50):  # 50 list requests
            tasks.append(self.make_request('GET', '/api/osint/investigations'))
        
        await asyncio.gather(*tasks)
        
        # Test update operations
        tasks = []
        for investigation_id in investigation_ids[:20]:  # Update 20 investigations
            update_data = {
                "status": random.choice(["ACTIVE", "PAUSED", "COMPLETED"]),
                "current_phase": random.choice(["PLANNING", "RECONNAISSANCE", "COLLECTION", "ANALYSIS"])
            }
            tasks.append(self.make_request('PUT', f'/api/osint/investigations/{investigation_id}', json=update_data))
        
        await asyncio.gather(*tasks)
        
        logger.info("Investigation CRUD testing complete.")
    
    async def test_search_operations(self):
        """Test search functionality under load."""
        logger.info("Testing search operations...")
        
        tasks = []
        
        # Test simple search
        for i in range(200):  # 200 search requests
            query = random.choice(self.config.search_queries)
            tasks.append(self.make_request('POST', '/api/osint/search', 
                                         json={"query": query, "max_results": 10}))
        
        await asyncio.gather(*tasks)
        
        # Test premium search
        tasks = []
        for i in range(100):  # 100 premium search requests
            query = random.choice(self.config.search_queries)
            engines = random.sample(["duckduckgo", "brave", "google", "bing"], k=2)
            tasks.append(self.make_request('POST', '/api/osint/premium-search',
                                         json={
                                             "query": query,
                                             "engines": engines,
                                             "max_pages": 1,
                                             "use_browser": False
                                         }))
        
        await asyncio.gather(*tasks)
        
        # Test search within investigations (need investigation IDs first)
        list_response = await self.make_request('GET', '/api/osint/investigations')
        if list_response['success'] and list_response['data']:
            investigation_id = list_response['data'][0]['id']
            
            tasks = []
            for i in range(50):  # 50 investigation searches
                query = random.choice(self.config.search_queries)
                tasks.append(self.make_request('POST', f'/api/osint/investigations/{investigation_id}/search',
                                             json={"query": query, "max_results": 5}))
            
            await asyncio.gather(*tasks)
        
        logger.info("Search operations testing complete.")
    
    async def test_websocket_connections(self):
        """Test WebSocket connection performance."""
        logger.info(f"Testing {self.config.websocket_connections} WebSocket connections...")
        
        async def websocket_user(user_id: int):
            """Simulate a WebSocket user."""
            try:
                # Connect to investigation WebSocket
                investigation_id = f"test-inv-{user_id}"
                ws_url = f"{self.config.ws_url}/api/osint/ws/{investigation_id}"
                
                async with websockets.connect(ws_url) as websocket:
                    # Send ping messages
                    for i in range(10):
                        ping_msg = {
                            "type": "ping",
                            "user_id": user_id,
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(ping_msg))
                        
                        # Wait for response
                        try:
                            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        except asyncio.TimeoutError:
                            logger.warning(f"WebSocket timeout for user {user_id}")
                            break
                        
                        await asyncio.sleep(1)
                    
                    # Send test messages
                    for i in range(5):
                        test_msg = {
                            "type": "test",
                            "message": f"Test message {i} from user {user_id}",
                            "timestamp": datetime.now().isoformat()
                        }
                        await websocket.send(json.dumps(test_msg))
                        await asyncio.sleep(0.5)
                        
            except Exception as e:
                logger.error(f"WebSocket user {user_id} error: {e}")
        
        # Create concurrent WebSocket connections
        tasks = []
        for i in range(self.config.websocket_connections):
            tasks.append(websocket_user(i))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("WebSocket connection testing complete.")
    
    async def test_concurrent_users(self):
        """Simulate concurrent user activity."""
        logger.info(f"Testing {self.config.concurrent_users} concurrent users...")
        
        async def simulate_user(user_id: int):
            """Simulate a single user's activity."""
            try:
                # User session: mix of different operations
                operations = []
                
                # Health checks
                for _ in range(3):
                    operations.append(self.make_request('GET', '/health'))
                
                # List investigations
                for _ in range(5):
                    operations.append(self.make_request('GET', '/api/osint/investigations'))
                
                # Create investigation
                investigation_data = {
                    "title": f"User {user_id} Investigation",
                    "description": f"Investigation created by user {user_id}",
                    "classification": "CONFIDENTIAL",
                    "priority": "MEDIUM"
                }
                create_result = await self.make_request('POST', '/api/osint/investigations', json=investigation_data)
                
                if create_result['success']:
                    investigation_id = create_result['data']['id']
                    
                    # Get investigation details
                    for _ in range(3):
                        operations.append(self.make_request('GET', f'/api/osint/investigations/{investigation_id}'))
                    
                    # Perform search in investigation
                    query = random.choice(self.config.search_queries)
                    operations.append(self.make_request('POST', f'/api/osint/investigations/{investigation_id}/search',
                                                       json={"query": query, "max_results": 5}))
                    
                    # Create target
                    target_data = {
                        "type": "PERSON",
                        "identifier": f"target-{user_id}",
                        "priority": "MEDIUM"
                    }
                    operations.append(self.make_request('POST', f'/api/osint/investigations/{investigation_id}/targets',
                                                       json=target_data))
                
                # Execute operations with delays
                for i, operation in enumerate(operations):
                    await operation
                    await asyncio.sleep(random.uniform(0.1, 0.5))  # Random delay
                
            except Exception as e:
                logger.error(f"User {user_id} simulation error: {e}")
        
        # Start users with ramp-up
        tasks = []
        users_per_second = self.config.concurrent_users / self.config.ramp_up_time
        
        for i in range(self.config.concurrent_users):
            tasks.append(simulate_user(i))
            
            # Ramp-up delay
            if i < self.config.concurrent_users - 1:
                await asyncio.sleep(1.0 / users_per_second)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Concurrent user testing complete.")
    
    async def run_load_test_suite(self):
        """Execute complete load test suite."""
        logger.info("🚀 STARTING COMPREHENSIVE LOAD TESTING SUITE")
        logger.info(f"Configuration: {self.config}")
        
        start_time = datetime.now()
        
        try:
            # Start system monitoring
            monitor_task = asyncio.create_task(self.system_monitor.start_monitoring())
            
            # Setup test environment
            await self.setup()
            
            # Execute test scenarios
            logger.info("\n" + "="*50)
            logger.info("PHASE 1: HEALTH ENDPOINTS")
            logger.info("="*50)
            await self.test_health_endpoints()
            
            logger.info("\n" + "="*50)
            logger.info("PHASE 2: INVESTIGATION CRUD OPERATIONS")
            logger.info("="*50)
            await self.test_investigation_crud()
            
            logger.info("\n" + "="*50)
            logger.info("PHASE 3: SEARCH OPERATIONS")
            logger.info("="*50)
            await self.test_search_operations()
            
            logger.info("\n" + "="*50)
            logger.info("PHASE 4: WEBSOCKET CONNECTIONS")
            logger.info("="*50)
            await self.test_websocket_connections()
            
            logger.info("\n" + "="*50)
            logger.info("PHASE 5: CONCURRENT USERS")
            logger.info("="*50)
            await self.test_concurrent_users()
            
            # Stop monitoring
            self.system_monitor.stop_monitoring()
            await monitor_task
            
        except Exception as e:
            logger.error(f"Load test suite error: {e}")
        finally:
            await self.cleanup()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n🎯 LOAD TESTING COMPLETED IN {duration:.2f} SECONDS")
        
        # Generate report
        await self.generate_performance_report(start_time, end_time)
    
    async def generate_performance_report(self, start_time: datetime, end_time: datetime):
        """Generate comprehensive performance report."""
        logger.info("\n📊 GENERATING PERFORMANCE REPORT")
        
        report = {
            'test_summary': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'configuration': {
                    'concurrent_users': self.config.concurrent_users,
                    'test_duration': self.config.test_duration,
                    'requests_per_second': self.config.requests_per_second,
                    'websocket_connections': self.config.websocket_connections,
                    'investigation_count': self.config.investigation_count
                }
            },
            'system_metrics': self.system_monitor.get_summary(),
            'endpoint_performance': {},
            'performance_analysis': {},
            'recommendations': []
        }
        
        # Process endpoint results
        total_requests = 0
        total_successful = 0
        total_failed = 0
        all_response_times = []
        
        for endpoint, metrics in self.results.items():
            if metrics.total_requests > 0:
                endpoint_data = {
                    'total_requests': metrics.total_requests,
                    'successful_requests': metrics.successful_requests,
                    'failed_requests': metrics.failed_requests,
                    'success_rate': metrics.success_rate,
                    'avg_response_time': metrics.avg_response_time,
                    'p95_response_time': metrics.p95_response_time,
                    'p99_response_time': metrics.p99_response_time,
                    'min_response_time': min(metrics.response_times) if metrics.response_times else 0,
                    'max_response_time': max(metrics.response_times) if metrics.response_times else 0,
                    'errors_count': len(metrics.errors),
                    'sample_errors': metrics.errors[:5]  # First 5 errors
                }
                
                report['endpoint_performance'][endpoint] = endpoint_data
                
                total_requests += metrics.total_requests
                total_successful += metrics.successful_requests
                total_failed += metrics.failed_requests
                all_response_times.extend(metrics.response_times)
        
        # Overall performance analysis
        report['performance_analysis'] = {
            'overall': {
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'failed_requests': total_failed,
                'overall_success_rate': (total_successful / total_requests * 100) if total_requests > 0 else 0,
                'overall_avg_response_time': statistics.mean(all_response_times) if all_response_times else 0,
                'overall_p95_response_time': statistics.quantiles(all_response_times, n=20)[18] if len(all_response_times) > 20 else max(all_response_times) if all_response_times else 0,
                'requests_per_second': total_requests / (end_time - start_time).total_seconds()
            }
        }
        
        # Generate recommendations
        recommendations = []
        
        # Check success rates
        for endpoint, data in report['endpoint_performance'].items():
            if data['success_rate'] < 95:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Reliability',
                    'endpoint': endpoint,
                    'issue': f"Low success rate: {data['success_rate']:.1f}%",
                    'recommendation': "Investigate errors and improve error handling"
                })
            
            if data['avg_response_time'] > 2.0:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'category': 'Performance',
                    'endpoint': endpoint,
                    'issue': f"High average response time: {data['avg_response_time']:.2f}s",
                    'recommendation': "Optimize database queries and implement caching"
                })
            
            if data['p95_response_time'] > 5.0:
                recommendations.append({
                    'priority': 'HIGH',
                    'category': 'Performance',
                    'endpoint': endpoint,
                    'issue': f"High P95 response time: {data['p95_response_time']:.2f}s",
                    'recommendation': "Investigate outliers and optimize slow operations"
                })
        
        # System resource recommendations
        system_metrics = report['system_metrics']
        if system_metrics.get('cpu', {}).get('avg', 0) > 80:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Capacity',
                'issue': f"High CPU usage: {system_metrics['cpu']['avg']:.1f}%",
                'recommendation': "Scale up CPU resources or optimize CPU-intensive operations"
            })
        
        if system_metrics.get('memory', {}).get('avg', 0) > 85:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Capacity',
                'issue': f"High memory usage: {system_metrics['memory']['avg']:.1f}%",
                'recommendation': "Optimize memory usage and consider memory scaling"
            })
        
        # Performance grading
        overall_success_rate = report['performance_analysis']['overall']['overall_success_rate']
        overall_avg_response = report['performance_analysis']['overall']['overall_avg_response_time']
        
        if overall_success_rate >= 99 and overall_avg_response <= 0.5:
            performance_grade = "A+ (EXCELLENT)"
        elif overall_success_rate >= 95 and overall_avg_response <= 1.0:
            performance_grade = "B+ (GOOD)"
        elif overall_success_rate >= 90 and overall_avg_response <= 2.0:
            performance_grade = "C+ (ACCEPTABLE)"
        else:
            performance_grade = "D (NEEDS IMPROVEMENT)"
        
        report['performance_grade'] = performance_grade
        report['recommendations'] = recommendations
        
        # Save report
        report_filename = f'load_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        self.print_performance_summary(report)
        
        logger.info(f"📄 Detailed report saved to: {report_filename}")
        
        return report
    
    def print_performance_summary(self, report: Dict[str, Any]):
        """Print performance summary to console."""
        print("\n" + "="*80)
        print("🚀 OSINT PLATFORM LOAD TESTING RESULTS")
        print("="*80)
        
        # Test Summary
        summary = report['test_summary']
        print(f"\n📋 TEST SUMMARY")
        print(f"   Duration: {summary['duration_seconds']:.2f} seconds")
        print(f"   Concurrent Users: {summary['configuration']['concurrent_users']}")
        print(f"   WebSocket Connections: {summary['configuration']['websocket_connections']}")
        print(f"   Test Investigations: {summary['configuration']['investigation_count']}")
        
        # Overall Performance
        overall = report['performance_analysis']['overall']
        print(f"\n📊 OVERALL PERFORMANCE")
        print(f"   Total Requests: {overall['total_requests']:,}")
        print(f"   Success Rate: {overall['overall_success_rate']:.2f}%")
        print(f"   Average Response Time: {overall['overall_avg_response_time']:.3f}s")
        print(f"   P95 Response Time: {overall['overall_p95_response_time']:.3f}s")
        print(f"   Requests/Second: {overall['requests_per_second']:.2f}")
        print(f"   Performance Grade: {report['performance_grade']}")
        
        # System Metrics
        system = report['system_metrics']
        if system:
            print(f"\n💻 SYSTEM RESOURCE USAGE")
            print(f"   CPU Usage: {system.get('cpu', {}).get('avg', 0):.1f}% (max: {system.get('cpu', {}).get('max', 0):.1f}%)")
            print(f"   Memory Usage: {system.get('memory', {}).get('avg', 0):.1f}% (max: {system.get('memory', {}).get('max', 0):.1f}%)")
            print(f"   Active Connections: {system.get('connections', {}).get('avg', 0):.0f} (max: {system.get('connections', {}).get('max', 0):.0f})")
        
        # Critical Endpoints
        print(f"\n🔍 CRITICAL ENDPOINTS")
        for endpoint, data in list(report['endpoint_performance'].items())[:10]:
            status = "✅" if data['success_rate'] >= 95 else "⚠️" if data['success_rate'] >= 90 else "❌"
            print(f"   {status} {endpoint}")
            print(f"      Requests: {data['total_requests']:,} | Success: {data['success_rate']:.1f}% | Avg Time: {data['avg_response_time']:.3f}s")
        
        # Top Recommendations
        recommendations = report['recommendations'][:5]
        if recommendations:
            print(f"\n⚠️  TOP RECOMMENDATIONS")
            for i, rec in enumerate(recommendations, 1):
                priority_icon = "🔴" if rec['priority'] == 'HIGH' else "🟡" if rec['priority'] == 'MEDIUM' else "🟢"
                print(f"   {i}. {priority_icon} {rec['issue']}")
                print(f"      💡 {rec['recommendation']}")
        
        print("\n" + "="*80)

async def main():
    """Main execution function."""
    # Load test configuration
    config = LoadTestConfig(
        base_url="http://localhost:8000",
        ws_url="ws://localhost:8000",
        concurrent_users=50,
        test_duration=300,
        ramp_up_time=60,
        requests_per_second=10,
        websocket_connections=20,
        investigation_count=100
    )
    
    # Run load tests
    runner = LoadTestRunner(config)
    await runner.run_load_test_suite()

if __name__ == "__main__":
    print("🚀 STARTING OSINT PLATFORM LOAD TESTING")
    print("⚠️  WARNING: This will generate significant load on the system")
    print("📋 Make sure the backend server is running on http://localhost:8000")
    print("="*80)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Load testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Load testing failed: {e}")
        import traceback
        traceback.print_exc()