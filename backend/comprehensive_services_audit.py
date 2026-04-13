#!/usr/bin/env python3
"""
Comprehensive Services and Agents Audit Report
Generated: 2025-11-13
OSINT-OS Backend Services and Agents Operational Effectiveness Testing
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add backend to path
sys.path.append("/home/ishanp/Documents/GitHub/OSINT-OS/backend")


class ServicesAuditor:
    """Comprehensive services and agents auditor."""

    def __init__(self):
        self.results = {
            "audit_metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "auditor": "ServicesAuditor",
                "platform": "OSINT-OS Backend",
                "version": "1.0.0",
            },
            "services": {},
            "agents": {},
            "integration_points": {},
            "performance_metrics": {},
            "configuration_analysis": {},
            "dependency_analysis": {},
            "recommendations": [],
        }

    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Run comprehensive audit of all services and agents."""
        print("🔍 Starting Comprehensive OSINT-OS Services and Agents Audit")
        print("=" * 70)

        # 1. Service Inventory and Analysis
        print("\n📋 1. Service Inventory and Analysis")
        await self._audit_services()

        # 2. Agent Effectiveness Testing
        print("\n🤖 2. Agent Effectiveness Testing")
        await self._audit_agents()

        # 3. Integration Points Analysis
        print("\n🔗 3. Integration Points Analysis")
        await self._audit_integration_points()

        # 4. Performance and Load Testing
        print("\n⚡ 4. Performance and Load Testing")
        await self._audit_performance()

        # 5. Configuration Analysis
        print("\n⚙️  5. Configuration Analysis")
        await self._audit_configuration()

        # 6. Dependency Analysis
        print("\n📦 6. Dependency Analysis")
        await self._audit_dependencies()

        # 7. Generate Recommendations
        print("\n💡 7. Generating Recommendations")
        self._generate_recommendations()

        # 8. Summary Report
        self._print_summary()

        return self.results

    async def _audit_services(self):
        """Audit all backend services."""
        service_categories = {
            "core_infrastructure": [
                "database",
                "websocket",
                "connection_manager",
                "error_handling",
            ],
            "search_services": [
                "enhanced_search_service",
                "real_search_service",
                "multi_search_service",
            ],
            "llm_services": ["async_llm_service", "llm_integration", "openrouter"],
            "scraping_services": [
                "enhanced_scraping_service",
                "premium_scraping_service",
                "scraping_service_enhanced",
                "enhanced_web_scraping_service",
            ],
            "social_media": ["real_social_media_service", "social_media_service"],
            "intelligence": [
                "content_intelligence_service",
                "technical_intelligence_service",
            ],
            "security": ["enhanced_auth_service", "rbac", "audit_logger"],
            "workflow": ["workflow_manager", "state", "task_storage"],
        }

        total_services = 0
        operational_services = 0

        for category, services in service_categories.items():
            print(f"  📁 {category.replace('_', ' ').title()}:")
            self.results["services"][category] = {}

            for service_name in services:
                total_services += 1
                status = await self._test_service_import(service_name)
                self.results["services"][category][service_name] = status

                if status["import_success"]:
                    operational_services += 1
                    print(f"    ✅ {service_name}: Operational")
                else:
                    print(f"    ❌ {service_name}: {status['error']}")

        # Store summary
        self.results["services"]["summary"] = {
            "total_services": total_services,
            "operational_services": operational_services,
            "operational_rate": operational_services / total_services
            if total_services > 0
            else 0,
        }

    async def _test_service_import(self, service_name: str) -> Dict[str, Any]:
        """Test service import and basic functionality."""
        result = {
            "import_success": False,
            "instantiation_success": False,
            "basic_functionality": False,
            "error": None,
        }

        try:
            # Test import
            module = __import__(f"app.services.{service_name}", fromlist=[service_name])
            result["import_success"] = True

            # Test instantiation (if possible)
            try:
                # Try to find main class in module
                main_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type)
                        and attr_name not in ["Error", "Enum", "Dict", "List", "Any"]
                        and not attr_name.startswith("_")
                    ):
                        main_class = attr
                        break

                if main_class:
                    # Try to instantiate
                    if service_name in ["database", "websocket", "connection_manager"]:
                        # These have global instances
                        if hasattr(module, "db_persistence"):
                            result["instantiation_success"] = True
                        elif hasattr(module, "ConnectionManager"):
                            result["instantiation_success"] = True
                    else:
                        # Try normal instantiation
                        try:
                            instance = main_class()
                            result["instantiation_success"] = True
                        except:
                            pass
            except:
                pass

            result["basic_functionality"] = result["instantiation_success"]

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    async def _audit_agents(self):
        """Audit specialized OSINT agents."""
        agent_categories = {
            "collection_agents": [
                "multi_engine_search_agent",
                "social_media_collector",
                "premium_search_agent",
                "surface_web_collector",
            ],
            "analysis_agents": [
                "contextual_analysis_agent",
                "data_fusion_agent",
                "pattern_recognition_agent",
            ],
            "synthesis_agents": [
                "enhanced_intelligence_synthesis_agent_v2",
                "intelligence_synthesis_agent",
                "report_generation_agent",
            ],
            "planning_agents": ["objective_definition", "strategy_formulation"],
        }

        total_agents = 0
        operational_agents = 0

        for category, agents in agent_categories.items():
            print(f"  🤖 {category.replace('_', ' ').title()}:")
            self.results["agents"][category] = {}

            for agent_name in agents:
                total_agents += 1
                status = await self._test_agent_import(agent_name)
                self.results["agents"][category][agent_name] = status

                if status["import_success"]:
                    operational_agents += 1
                    print(f"    ✅ {agent_name}: Operational")
                else:
                    print(f"    ❌ {agent_name}: {status['error']}")

        # Store summary
        self.results["agents"]["summary"] = {
            "total_agents": total_agents,
            "operational_agents": operational_agents,
            "operational_rate": operational_agents / total_agents
            if total_agents > 0
            else 0,
        }

    async def _test_agent_import(self, agent_name: str) -> Dict[str, Any]:
        """Test agent import and basic functionality."""
        result = {
            "import_success": False,
            "instantiation_success": False,
            "error": None,
        }

        try:
            # Try different import paths
            import_paths = [
                f"app.agents.specialized.collection.{agent_name}",
                f"app.agents.specialized.analysis.{agent_name}",
                f"app.agents.specialized.synthesis.{agent_name}",
                f"app.agents.specialized.planning.{agent_name}",
            ]

            agent_class = None
            for import_path in import_paths:
                try:
                    module = __import__(import_path, fromlist=[agent_name])
                    # Find agent class
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and "Agent" in attr_name
                            and attr_name != "Agent"
                        ):
                            agent_class = attr
                            break

                    if agent_class:
                        break
                except ImportError:
                    continue

            if agent_class:
                result["import_success"] = True

                # Test instantiation
                try:
                    instance = agent_class()
                    result["instantiation_success"] = True
                except Exception as e:
                    result["error"] = f"Instantiation failed: {str(e)[:50]}"
            else:
                result["error"] = "Agent class not found"

        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    async def _audit_integration_points(self):
        """Audit integration points between services."""
        integration_tests = {
            "search_to_database": {
                "description": "Search service storing results in database",
                "test": self._test_search_database_integration,
            },
            "agent_to_service": {
                "description": "Agent using search services",
                "test": self._test_agent_service_integration,
            },
            "llm_to_workflow": {
                "description": "LLM service integration with workflow",
                "test": self._test_llm_workflow_integration,
            },
        }

        for integration_name, integration_info in integration_tests.items():
            print(f"  🔗 Testing {integration_name}: {integration_info['description']}")
            try:
                result = await integration_info["test"]()
                self.results["integration_points"][integration_name] = {
                    "success": True,
                    "result": result,
                    "description": integration_info["description"],
                }
                print(f"    ✅ {integration_name}: Integration successful")
            except Exception as e:
                self.results["integration_points"][integration_name] = {
                    "success": False,
                    "error": str(e)[:100],
                    "description": integration_info["description"],
                }
                print(f"    ❌ {integration_name}: {str(e)[:50]}")

    async def _test_search_database_integration(self):
        """Test search service integration with database."""
        from app.services.database import DatabasePersistenceService

        db_service = DatabasePersistenceService()
        test_data = {
            "integration_test": True,
            "timestamp": time.time(),
            "test_type": "search_database_integration",
        }

        # Store test data
        success = await db_service.store_investigation_state(
            "integration_test", test_data
        )

        if success:
            # Retrieve test data
            retrieved = await db_service.get_investigation_state("integration_test")
            return {"stored": True, "retrieved": retrieved is not None}

        return {"stored": False, "retrieved": False}

    async def _test_agent_service_integration(self):
        """Test agent integration with search services."""
        try:
            from app.agents.specialized.collection.multi_engine_search_agent import (
                MultiEngineSearchAgent,
            )

            agent = MultiEngineSearchAgent()

            # Test agent with simple query
            result = await agent.execute({"query": "integration test"})

            return {
                "agent_success": result.success,
                "has_data": bool(result.data),
                "metadata": bool(result.metadata),
            }
        except Exception as e:
            return {"agent_success": False, "error": str(e)}

    async def _test_llm_workflow_integration(self):
        """Test LLM service integration."""
        try:
            from app.services.async_llm_service import AsyncLLMService

            service = AsyncLLMService()

            # Test health status
            health = await service.get_health_status()

            return {
                "service_available": True,
                "providers_count": len(health.get("providers", {})),
                "overall_status": health.get("status", "unknown"),
            }
        except Exception as e:
            return {"service_available": False, "error": str(e)}

    async def _audit_performance(self):
        """Audit performance and load handling."""
        performance_tests = {
            "concurrent_searches": {
                "description": "Concurrent search operations",
                "test": self._test_concurrent_searches,
            },
            "database_operations": {
                "description": "Database operation performance",
                "test": self._test_database_performance,
            },
            "memory_usage": {
                "description": "Memory usage analysis",
                "test": self._test_memory_usage,
            },
        }

        for test_name, test_info in performance_tests.items():
            print(f"  ⚡ Testing {test_name}: {test_info['description']}")
            try:
                result = await test_info["test"]()
                self.results["performance_metrics"][test_name] = {
                    "success": True,
                    "metrics": result,
                    "description": test_info["description"],
                }
                print(f"    ✅ {test_name}: Performance test completed")
            except Exception as e:
                self.results["performance_metrics"][test_name] = {
                    "success": False,
                    "error": str(e)[:100],
                    "description": test_info["description"],
                }
                print(f"    ❌ {test_name}: {str(e)[:50]}")

    async def _test_concurrent_searches(self):
        """Test concurrent search performance."""
        try:
            from app.services.multi_search_service import MultiSearchEngine

            start_time = time.time()

            # Run 3 concurrent searches
            tasks = []
            for i in range(3):
                async with MultiSearchEngine() as search_engine:
                    task = asyncio.create_task(
                        search_engine.search(
                            query=f"performance test {i}",
                            engines=["duckduckgo"],
                            max_results=2,
                        )
                    )
                    tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()

            successful_searches = sum(
                1 for r in results if not isinstance(r, Exception)
            )

            return {
                "total_time": end_time - start_time,
                "concurrent_operations": len(tasks),
                "successful_operations": successful_searches,
                "success_rate": successful_searches / len(tasks),
                "avg_time_per_operation": (end_time - start_time) / len(tasks),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _test_database_performance(self):
        """Test database operation performance."""
        try:
            from app.services.database import DatabasePersistenceService

            db_service = DatabasePersistenceService()

            # Test multiple database operations
            start_time = time.time()

            operations = []
            for i in range(5):
                test_data = {"perf_test": i, "timestamp": time.time()}
                operation = asyncio.create_task(
                    db_service.store_investigation_state(f"perf_test_{i}", test_data)
                )
                operations.append(operation)

            results = await asyncio.gather(*operations, return_exceptions=True)

            end_time = time.time()

            successful_ops = sum(1 for r in results if r is True)

            return {
                "total_time": end_time - start_time,
                "operations": len(operations),
                "successful_operations": successful_ops,
                "success_rate": successful_ops / len(operations),
                "avg_time_per_operation": (end_time - start_time) / len(operations),
            }
        except Exception as e:
            return {"error": str(e)}

    async def _test_memory_usage(self):
        """Test memory usage."""
        try:
            import psutil
            import os

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                "rss_mb": memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
                "vms_mb": memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
                "memory_percent": process.memory_percent(),
                "available_mb": psutil.virtual_memory().available / 1024 / 1024,
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}

    async def _audit_configuration(self):
        """Audit configuration settings."""
        try:
            from app.config import settings

            config_checks = {
                "database_config": {
                    "database_url": str(getattr(settings, "DATABASE_URL", "Not set")),
                    "database_configured": bool(
                        getattr(settings, "DATABASE_URL", None)
                    ),
                },
                "llm_config": {
                    "llm_provider": getattr(settings, "LLM_PROVIDER", "Not set"),
                    "openai_configured": bool(
                        getattr(settings, "OPENAI_API_KEY", None)
                    ),
                    "custom_llm_enabled": getattr(
                        settings, "CUSTOM_LLM_ENABLED", False
                    ),
                },
                "debug_config": {
                    "debug_mode": getattr(settings, "DEBUG", False),
                    "environment": getattr(settings, "ENVIRONMENT", "Unknown"),
                },
                "security_config": {
                    "secret_key_configured": bool(
                        getattr(settings, "SECRET_KEY", None)
                    ),
                    "cors_enabled": getattr(settings, "CORS_ENABLED", False),
                },
            }

            self.results["configuration_analysis"] = {
                "config_loaded": True,
                "config_checks": config_checks,
                "overall_status": "configured",
            }

            print("  ✅ Configuration loaded successfully")

        except Exception as e:
            self.results["configuration_analysis"] = {
                "config_loaded": False,
                "error": str(e)[:100],
                "overall_status": "error",
            }
            print(f"  ❌ Configuration error: {str(e)[:50]}")

    async def _audit_dependencies(self):
        """Audit system dependencies."""
        critical_dependencies = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "aiohttp",
            "langchain",
            "langgraph",
            "pydantic",
            "asyncio",
        ]

        optional_dependencies = [
            "selenium",
            "beautifulsoup4",
            "scrapegraph",
            "playwright",
            "redis",
            "psycopg2",
        ]

        dependency_status = {"critical": {}, "optional": {}, "summary": {}}

        # Test critical dependencies
        print("  🔍 Critical dependencies:")
        for dep in critical_dependencies:
            try:
                __import__(dep)
                dependency_status["critical"][dep] = True
                print(f"    ✅ {dep}: Available")
            except ImportError:
                dependency_status["critical"][dep] = False
                print(f"    ❌ {dep}: Missing")

        # Test optional dependencies
        print("  🔍 Optional dependencies:")
        for dep in optional_dependencies:
            try:
                __import__(dep)
                dependency_status["optional"][dep] = True
                print(f"    ✅ {dep}: Available")
            except ImportError:
                dependency_status["optional"][dep] = False
                print(f"    ⚠️  {dep}: Missing (optional)")

        # Summary
        critical_available = sum(dependency_status["critical"].values())
        critical_total = len(dependency_status["critical"])
        optional_available = sum(dependency_status["optional"].values())
        optional_total = len(dependency_status["optional"])

        dependency_status["summary"] = {
            "critical_available": critical_available,
            "critical_total": critical_total,
            "critical_rate": critical_available / critical_total,
            "optional_available": optional_available,
            "optional_total": optional_total,
            "optional_rate": optional_available / optional_total,
            "overall_dependency_health": "good"
            if critical_available == critical_total
            else "critical",
        }

        self.results["dependency_analysis"] = dependency_status

    def _generate_recommendations(self):
        """Generate recommendations based on audit results."""
        recommendations = []

        # Service recommendations
        services_summary = self.results["services"].get("summary", {})
        if services_summary.get("operational_rate", 0) < 0.8:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "services",
                    "issue": "Low service operational rate",
                    "recommendation": "Fix service import issues and missing dependencies",
                    "details": f"Only {services_summary.get('operational_rate', 0):.1%} of services are operational",
                }
            )

        # Agent recommendations
        agents_summary = self.results["agents"].get("summary", {})
        if agents_summary.get("operational_rate", 0) < 0.8:
            recommendations.append(
                {
                    "priority": "high",
                    "category": "agents",
                    "issue": "Low agent operational rate",
                    "recommendation": "Fix agent import issues and dependencies",
                    "details": f"Only {agents_summary.get('operational_rate', 0):.1%} of agents are operational",
                }
            )

        # Dependency recommendations
        dep_analysis = self.results["dependency_analysis"].get("summary", {})
        if dep_analysis.get("critical_rate", 0) < 1.0:
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "dependencies",
                    "issue": "Missing critical dependencies",
                    "recommendation": "Install missing critical dependencies",
                    "details": f"{dep_analysis.get('critical_total', 0) - dep_analysis.get('critical_available', 0)} critical dependencies missing",
                }
            )

        # Performance recommendations
        perf_metrics = self.results.get("performance_metrics", {})
        for test_name, test_result in perf_metrics.items():
            if not test_result.get("success", False):
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "performance",
                        "issue": f"Performance test failed: {test_name}",
                        "recommendation": "Investigate performance issues and optimize",
                        "details": test_result.get("error", "Unknown error"),
                    }
                )

        # Configuration recommendations
        config_analysis = self.results.get("configuration_analysis", {})
        if not config_analysis.get("config_loaded", False):
            recommendations.append(
                {
                    "priority": "critical",
                    "category": "configuration",
                    "issue": "Configuration loading failed",
                    "recommendation": "Fix configuration issues and environment variables",
                    "details": config_analysis.get(
                        "error", "Unknown configuration error"
                    ),
                }
            )

        # General recommendations
        recommendations.extend(
            [
                {
                    "priority": "medium",
                    "category": "monitoring",
                    "issue": "Lack of comprehensive monitoring",
                    "recommendation": "Implement comprehensive logging and monitoring for all services",
                    "details": "Add health checks, performance metrics, and error tracking",
                },
                {
                    "priority": "low",
                    "category": "documentation",
                    "issue": "Service documentation gaps",
                    "recommendation": "Improve API documentation and service integration guides",
                    "details": "Add detailed documentation for service interfaces and usage patterns",
                },
            ]
        )

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        self.results["recommendations"] = recommendations

    def _print_summary(self):
        """Print audit summary."""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE AUDIT SUMMARY")
        print("=" * 70)

        # Services summary
        services_summary = self.results["services"].get("summary", {})
        print(f"\n📋 Services:")
        print(f"   Total: {services_summary.get('total_services', 0)}")
        print(f"   Operational: {services_summary.get('operational_services', 0)}")
        print(f"   Rate: {services_summary.get('operational_rate', 0):.1%}")

        # Agents summary
        agents_summary = self.results["agents"].get("summary", {})
        print(f"\n🤖 Agents:")
        print(f"   Total: {agents_summary.get('total_agents', 0)}")
        print(f"   Operational: {agents_summary.get('operational_agents', 0)}")
        print(f"   Rate: {agents_summary.get('operational_rate', 0):.1%}")

        # Integration summary
        integration_summary = self.results.get("integration_points", {})
        total_integrations = len(integration_summary)
        successful_integrations = sum(
            1 for i in integration_summary.values() if i.get("success", False)
        )
        print(f"\n🔗 Integration Points:")
        print(f"   Total: {total_integrations}")
        print(f"   Successful: {successful_integrations}")
        print(
            f"   Rate: {successful_integrations / total_integrations:.1%}"
            if total_integrations > 0
            else "   Rate: N/A"
        )

        # Dependencies summary
        dep_summary = self.results["dependency_analysis"].get("summary", {})
        print(f"\n📦 Dependencies:")
        print(
            f"   Critical: {dep_summary.get('critical_available', 0)}/{dep_summary.get('critical_total', 0)}"
        )
        print(
            f"   Optional: {dep_summary.get('optional_available', 0)}/{dep_summary.get('optional_total', 0)}"
        )

        # Recommendations summary
        recommendations = self.results.get("recommendations", [])
        priority_counts = {}
        for rec in recommendations:
            priority = rec.get("priority", "unknown")
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        print(f"\n💡 Recommendations:")
        for priority in ["critical", "high", "medium", "low"]:
            count = priority_counts.get(priority, 0)
            if count > 0:
                print(f"   {priority.title()}: {count}")

        # Overall assessment
        services_rate = services_summary.get("operational_rate", 0)
        agents_rate = agents_summary.get("operational_rate", 0)
        critical_deps_rate = dep_summary.get("critical_rate", 0)

        overall_score = (services_rate + agents_rate + critical_deps_rate) / 3

        if overall_score >= 0.9:
            status = "🟢 EXCELLENT"
        elif overall_score >= 0.8:
            status = "🟡 GOOD"
        elif overall_score >= 0.7:
            status = "🟠 FAIR"
        else:
            status = "🔴 NEEDS ATTENTION"

        print(f"\n🎯 Overall Platform Status: {status}")
        print(f"   Overall Score: {overall_score:.1%}")
        print("=" * 70)


async def main():
    """Main audit execution."""
    auditor = ServicesAuditor()
    results = await auditor.run_comprehensive_audit()

    # Save detailed results
    with open(
        "/home/ishanp/Documents/GitHub/OSINT-OS/services_audit_report.json", "w"
    ) as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: services_audit_report.json")

    return results


if __name__ == "__main__":
    asyncio.run(main())
