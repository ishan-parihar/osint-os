# BMad Framework Architecture Documentation

## Overview

The BMad (Build Management and Development) Framework is a sophisticated CLI-based development tooling system designed to streamline project creation, management, and deployment workflows. It implements a modular agent-based architecture with comprehensive workflow automation and extensible plugin system.

## Architecture Stack

### Core Framework
- **Python 3.11+**: Core framework implementation
- **Click**: Command-line interface framework
- **Rich**: Enhanced terminal UI and formatting
- **Pydantic**: Configuration validation and management
- **PyYAML**: YAML configuration parsing

### Agent System
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Agent Registry**: Dynamic agent discovery and management
- **Workflow Orchestration**: Coordinated multi-agent workflows
- **State Management**: Persistent workflow state tracking

### Configuration Management
- **TOML Configuration**: Human-readable configuration format
- **Environment-Specific Configs**: Development, staging, production
- **Validation Schema**: Configuration validation and error handling
- **Hot Reloading**: Runtime configuration updates

### Plugin System
- **Modular Architecture**: Extensible plugin framework
- **Hook System**: Event-driven plugin integration
- **Dependency Management**: Plugin dependency resolution
- **Version Management**: Plugin version compatibility

## Project Structure

```
.bmad/
├── bmm/                          # BMad Framework Core
│   ├── agents/                   # Agent implementations
│   │   ├── analyst.md           # Analyst agent documentation
│   │   ├── architect.md         # Architect agent documentation
│   │   ├── dev.md               # Development agent documentation
│   │   ├── pm.md                # Project management agent
│   │   ├── sm.md                # Systems management agent
│   │   ├── tea.md               # Testing and evaluation agent
│   │   ├── tech-writer.md       # Technical writing agent
│   │   └── ux-designer.md       # UX design agent
│   ├── workflows/               # Workflow definitions
│   │   ├── document-project/    # Documentation workflow
│   │   │   ├── documentation-requirements.csv
│   │   │   ├── workflows/
│   │   │   │   ├── full-scan-instructions.md
│   │   │   │   ├── quick-scan-instructions.md
│   │   │   │   └── targeted-scan-instructions.md
│   │   │   └── workflow-config.yaml
│   │   ├── create-project/      # Project creation workflow
│   │   ├── deploy-project/      # Deployment workflow
│   │   └── analyze-project/     # Analysis workflow
│   ├── tasks/                   # Task management
│   │   ├── common/              # Common task utilities
│   │   ├── documentation/       # Documentation tasks
│   │   ├── deployment/          # Deployment tasks
│   │   └── analysis/            # Analysis tasks
│   ├── tools/                   # Framework tools
│   │   ├── config-manager.py    # Configuration management
│   │   ├── agent-registry.py    # Agent registry
│   │   ├── workflow-engine.py   # Workflow orchestration
│   │   └── plugin-manager.py    # Plugin management
│   └── docs/                    # Framework documentation
│       ├── user-guide.md        # User documentation
│       ├── api-reference.md     # API reference
│       └── plugin-development.md # Plugin development guide
├── _cfg/                        # Configuration storage
│   ├── agents/                  # Agent configurations
│   │   ├── analyst.toml         # Analyst agent config
│   │   ├── architect.toml       # Architect agent config
│   │   ├── dev.toml             # Development agent config
│   │   ├── pm.toml              # PM agent config
│   │   ├── sm.toml              # SM agent config
│   │   ├── tea.toml             # TEA agent config
│   │   ├── tech-writer.toml     # Tech writer config
│   │   └── ux-designer.toml     # UX designer config
│   ├── workflows/               # Workflow configurations
│   │   ├── document-project.yaml
│   │   ├── create-project.yaml
│   │   └── deploy-project.yaml
│   └── global.yaml              # Global configuration
└── agent-manifest.csv           # Agent registry manifest
```

## Agent Architecture

### Agent System Design

```python
# Base Agent Interface
class BaseAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.state = AgentState.IDLE
        self.context = AgentContext()
    
    async def activate(self) -> AgentResult:
        """Activate the agent with current configuration"""
        pass
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a specific task"""
        pass
    
    async def collaborate(self, other_agent: BaseAgent) -> CollaborationResult:
        """Collaborate with another agent"""
        pass
    
    def get_capabilities(self) -> List[Capability]:
        """Return agent capabilities"""
        pass
```

### Agent Registry

```python
class AgentRegistry:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.capabilities: Dict[str, List[Capability]] = {}
    
    def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent with the registry"""
        self.agents[agent_id] = agent
        self.capabilities[agent_id] = agent.get_capabilities()
    
    def find_agent(self, capability: str) -> BaseAgent:
        """Find an agent with specific capability"""
        for agent_id, capabilities in self.capabilities.items():
            if capability in capabilities:
                return self.agents[agent_id]
        raise AgentNotFoundError(f"No agent found with capability: {capability}")
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
```

### Specialized Agents

#### 1. Analyst Agent
```yaml
# _cfg/agents/analyst.toml
[agent]
name = "BMad Analyst"
version = "1.0.0"
description = "Project analysis and documentation specialist"
type = "analysis"

[capabilities]
- "project-analysis"
- "documentation-generation"
- "architecture-review"
- "code-analysis"

[tools]
- "file-scanner"
- "dependency-analyzer"
- "architecture-detector"
- "documentation-generator"

[personality]
style = "analytical"
tone = "professional"
detail_level = "comprehensive"
```

#### 2. Architect Agent
```yaml
# _cfg/agents/architect.toml
[agent]
name = "BMad Architect"
version = "1.0.0"
description = "System architecture and design specialist"
type = "architecture"

[capabilities]
- "system-design"
- "architecture-planning"
- "technology-selection"
- "integration-design"

[tools]
- "architecture-designer"
- "technology-advisor"
- "integration-planner"
- "scalability-analyzer"

[personality]
style = "strategic"
tone = "authoritative"
detail_level = "high-level"
```

#### 3. Development Agent
```yaml
# _cfg/agents/dev.toml
[agent]
name = "BMad Developer"
version = "1.0.0"
description = "Code development and implementation specialist"
type = "development"

[capabilities]
- "code-generation"
- "implementation"
- "testing"
- "debugging"

[tools]
- "code-generator"
- "test-generator"
- "debugger"
- "refactoring-tools"

[personality]
style = "practical"
tone = "technical"
detail_level = "implementation-focused"
```

## Workflow Architecture

### Workflow Engine

```python
class WorkflowEngine:
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.current_step = None
        self.state = WorkflowState()
        self.agent_registry = AgentRegistry()
    
    async def execute_workflow(self, workflow_id: str) -> WorkflowResult:
        """Execute a complete workflow"""
        workflow = self.load_workflow(workflow_id)
        
        for step in workflow.steps:
            self.current_step = step
            result = await self.execute_step(step)
            
            if not result.success:
                return WorkflowResult(
                    success=False,
                    error=result.error,
                    completed_steps=self.state.completed_steps
                )
            
            self.state.completed_steps.append(step.id)
        
        return WorkflowResult(success=True, completed_steps=self.state.completed_steps)
    
    async def execute_step(self, step: WorkflowStep) -> StepResult:
        """Execute a single workflow step"""
        agent = self.agent_registry.get_agent(step.required_capability)
        
        try:
            result = await agent.execute_task(step.task)
            return StepResult(success=True, result=result)
        except Exception as e:
            return StepResult(success=False, error=str(e))
```

### Document Project Workflow

```yaml
# bmm/workflows/document-project/workflow-config.yaml
workflow:
  name: "document-project"
  description: "Generate comprehensive project documentation"
  version: "1.2.0"
  
  steps:
    - id: "step_1"
      name: "Project Classification"
      agent: "analyst"
      capability: "project-analysis"
      description: "Classify project type and structure"
      
    - id: "step_2"
      name: "Documentation Discovery"
      agent: "analyst"
      capability: "documentation-analysis"
      description: "Discover existing documentation"
      
    - id: "step_3"
      name: "Technology Stack Analysis"
      agent: "analyst"
      capability: "technology-analysis"
      description: "Analyze technology stack and dependencies"
      
    - id: "step_4"
      name: "Conditional Analysis"
      agent: "analyst"
      capability: "conditional-analysis"
      description: "Perform project-type-specific analysis"
      
    - id: "step_5"
      name: "Source Tree Analysis"
      agent: "analyst"
      capability: "source-analysis"
      description: "Analyze source code structure"
      
    - id: "step_6"
      name: "Development Setup Analysis"
      agent: "analyst"
      capability: "development-analysis"
      description: "Analyze development and deployment setup"
      
    - id: "step_7"
      name: "Integration Architecture"
      agent: "architect"
      capability: "integration-analysis"
      description: "Document integration architecture"
      
    - id: "step_8"
      name: "Generate Architecture Documentation"
      agent: "tech-writer"
      capability: "documentation-generation"
      description: "Generate architecture documentation"
      
    - id: "step_9"
      name: "Generate Supporting Documentation"
      agent: "tech-writer"
      capability: "documentation-generation"
      description: "Generate supporting documentation"
      
    - id: "step_10"
      name: "Create Master Index"
      agent: "tech-writer"
      capability: "documentation-generation"
      description: "Create comprehensive documentation index"
      
    - id: "step_11"
      name: "Validation and Review"
      agent: "tea"
      capability: "validation"
      description: "Validate documentation quality"
      
    - id: "step_12"
      name: "Finalization"
      agent: "pm"
      capability: "project-finalization"
      description: "Finalize documentation and deliver"
```

## Configuration Architecture

### Configuration Management

```python
class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = {}
        self.watchers = []
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from files"""
        config_files = glob.glob(f"{self.config_path}/**/*.yaml", recursive=True)
        
        for config_file in config_files:
            with open(config_file, 'r') as f:
                file_config = yaml.safe_load(f)
                self._merge_config(file_config)
        
        return self.config
    
    def get_agent_config(self, agent_id: str) -> AgentConfig:
        """Get configuration for specific agent"""
        agent_config_path = f"{self.config_path}/agents/{agent_id}.toml"
        
        with open(agent_config_path, 'r') as f:
            config_dict = toml.load(f)
        
        return AgentConfig(**config_dict)
    
    def watch_config_changes(self, callback: Callable):
        """Watch for configuration changes"""
        # Implementation for file watching
        pass
```

### Global Configuration

```yaml
# _cfg/global.yaml
bmad:
  version: "1.2.0"
  default_workspace: "./workspace"
  
agents:
  registry_path: "./_cfg/agents"
  auto_discovery: true
  
workflows:
  registry_path: "./bmm/workflows"
  default_timeout: 3600  # 1 hour
  
plugins:
  enabled: true
  registry_path: "./plugins"
  auto_load: true
  
logging:
  level: "INFO"
  format: "rich"
  file: "./logs/bmad.log"
  
security:
  validate_configs: true
  sandbox_agents: false
  restricted_file_access: true
```

## CLI Architecture

### Command Structure

```python
import click
from rich.console import Console
from rich.table import Table

@click.group()
@click.version_option()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """BMad Framework - Build Management and Development"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose

@cli.group()
def agent():
    """Agent management commands"""
    pass

@agent.command()
@click.argument('agent_id')
@click.pass_context
def activate(ctx, agent_id):
    """Activate a specific agent"""
    config_manager = ConfigManager(ctx.obj.get('config', './_cfg'))
    agent_registry = AgentRegistry()
    
    # Load and activate agent
    agent_config = config_manager.get_agent_config(agent_id)
    agent = AgentFactory.create_agent(agent_id, agent_config)
    
    console = Console()
    console.print(f"Activating agent: {agent_id}", style="bold green")
    
    result = asyncio.run(agent.activate())
    
    if result.success:
        console.print("Agent activated successfully!", style="bold green")
    else:
        console.print(f"Agent activation failed: {result.error}", style="bold red")

@cli.group()
def workflow():
    """Workflow management commands"""
    pass

@workflow.command()
@click.argument('workflow_id')
@click.option('--scan-level', default='deep', help='Scan level: quick, deep, targeted')
@click.pass_context
def execute(ctx, workflow_id, scan_level):
    """Execute a workflow"""
    config_manager = ConfigManager(ctx.obj.get('config', './_cfg'))
    workflow_engine = WorkflowEngine(config_manager.get_workflow_config())
    
    console = Console()
    console.print(f"Executing workflow: {workflow_id}", style="bold blue")
    
    with console.status("[bold green]Executing workflow..."):
        result = asyncio.run(workflow_engine.execute_workflow(workflow_id))
    
    if result.success:
        console.print("Workflow completed successfully!", style="bold green")
        console.print(f"Completed steps: {len(result.completed_steps)}")
    else:
        console.print(f"Workflow failed: {result.error}", style="bold red")
```

### Rich Terminal UI

```python
class BMadConsole:
    def __init__(self):
        self.console = Console()
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        )
    
    def show_agent_status(self, agents: List[BaseAgent]):
        """Display agent status table"""
        table = Table(title="Agent Registry")
        
        table.add_column("Agent ID", style="cyan")
        table.add_column("Name", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Capabilities", style="blue")
        
        for agent in agents:
            capabilities = ", ".join([cap.name for cap in agent.get_capabilities()])
            status = "🟢 Active" if agent.state == AgentState.ACTIVE else "⚪ Idle"
            
            table.add_row(
                agent.config.agent_id,
                agent.config.name,
                agent.config.type,
                status,
                capabilities
            )
        
        self.console.print(table)
    
    def show_workflow_progress(self, workflow: Workflow):
        """Display workflow progress"""
        with self.progress as progress:
            task = progress.add_task(f"[cyan]Executing {workflow.name}...", total=100)
            
            for step in workflow.steps:
                progress.update(task, description=f"[cyan]{step.name}...", advance=100/len(workflow.steps))
                time.sleep(1)  # Simulate work
```

## Plugin Architecture

### Plugin System

```python
class PluginManager:
    def __init__(self, plugin_path: str):
        self.plugin_path = plugin_path
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Hook]] = {}
    
    def load_plugins(self):
        """Load all plugins from plugin directory"""
        plugin_dirs = glob.glob(f"{self.plugin_path}/*")
        
        for plugin_dir in plugin_dirs:
            plugin = self._load_plugin(plugin_dir)
            if plugin:
                self.register_plugin(plugin)
    
    def register_plugin(self, plugin: Plugin):
        """Register a plugin with the manager"""
        self.plugins[plugin.name] = plugin
        
        # Register hooks
        for hook in plugin.hooks:
            if hook.event not in self.hooks:
                self.hooks[hook.event] = []
            self.hooks[hook.event].append(hook)
    
    def execute_hooks(self, event: str, context: Dict[str, Any]) -> List[HookResult]:
        """Execute all hooks for a specific event"""
        results = []
        
        if event in self.hooks:
            for hook in self.hooks[event]:
                result = hook.execute(context)
                results.append(result)
        
        return results

class Plugin:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.hooks: List[Hook] = []
        self.dependencies: List[str] = []
    
    def register_hook(self, hook: Hook):
        """Register a hook with the plugin"""
        self.hooks.append(hook)
    
    def initialize(self):
        """Initialize the plugin"""
        pass
    
    def cleanup(self):
        """Cleanup plugin resources"""
        pass
```

### Example Plugin

```python
# plugins/documentation-enhancer/plugin.py
class DocumentationEnhancerPlugin(Plugin):
    def __init__(self):
        super().__init__("documentation-enhancer", "1.0.0")
        
        # Register hooks
        self.register_hook(Hook("documentation-generated", self.enhance_docs))
        self.register_hook(Hook("workflow-completed", self.generate_index))
    
    def enhance_docs(self, context: Dict[str, Any]) -> HookResult:
        """Enhance generated documentation"""
        docs = context.get('documentation', [])
        
        # Add enhancements
        enhanced_docs = []
        for doc in docs:
            enhanced_doc = self._add_enhancements(doc)
            enhanced_docs.append(enhanced_doc)
        
        return HookResult(success=True, data={'enhanced_docs': enhanced_docs})
    
    def generate_index(self, context: Dict[str, Any]) -> HookResult:
        """Generate documentation index"""
        docs = context.get('documentation', [])
        
        index = self._create_index(docs)
        
        return HookResult(success=True, data={'index': index})
    
    def _add_enhancements(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Add enhancements to documentation"""
        # Add table of contents
        doc['table_of_contents'] = self._generate_toc(doc['content'])
        
        # Add navigation
        doc['navigation'] = self._generate_navigation(doc)
        
        # Add metadata
        doc['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'enhanced_by': 'documentation-enhancer-plugin'
        }
        
        return doc
```

## Integration Architecture

### External Service Integration

```python
class ServiceIntegrator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services: Dict[str, ExternalService] = {}
    
    def register_service(self, service_name: str, service: ExternalService):
        """Register an external service"""
        self.services[service_name] = service
    
    def get_service(self, service_name: str) -> ExternalService:
        """Get a registered service"""
        if service_name not in self.services:
            raise ServiceNotFoundError(f"Service {service_name} not found")
        return self.services[service_name]

class GitHubService(ExternalService):
    def __init__(self, token: str):
        self.token = token
        self.client = Github(token)
    
    async def create_repository(self, name: str, description: str) -> str:
        """Create a new repository"""
        repo = self.client.get_user().create_repo(
            name=name,
            description=description,
            private=True
        )
        return repo.html_url
    
    async def create_issue(self, repo: str, title: str, body: str) -> str:
        """Create an issue in repository"""
        repository = self.client.get_repo(repo)
        issue = repository.create_issue(title=title, body=body)
        return issue.html_url

class SlackService(ExternalService):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_notification(self, message: str, channel: str = None):
        """Send notification to Slack"""
        payload = {
            "text": message,
            "channel": channel
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)
```

## Testing Architecture

### Agent Testing Framework

```python
class AgentTestFramework:
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.mock_services: Dict[str, MockService] = {}
    
    def add_test_case(self, test_case: TestCase):
        """Add a test case"""
        self.test_cases.append(test_case)
    
    def run_agent_tests(self, agent: BaseAgent) -> TestResult:
        """Run tests for a specific agent"""
        results = []
        
        for test_case in self.test_cases:
            if test_case.agent_type == agent.config.type:
                result = self._run_single_test(agent, test_case)
                results.append(result)
        
        return TestResult(results=results)
    
    def _run_single_test(self, agent: BaseAgent, test_case: TestCase) -> SingleTestResult:
        """Run a single test case"""
        try:
            # Setup mock services
            self._setup_mocks(test_case.mocks)
            
            # Execute test
            result = asyncio.run(agent.execute_task(test_case.task))
            
            # Validate results
            validation = self._validate_result(result, test_case.expected_output)
            
            return SingleTestResult(
                test_case=test_case.name,
                success=validation.success,
                message=validation.message,
                duration=result.duration
            )
        except Exception as e:
            return SingleTestResult(
                test_case=test_case.name,
                success=False,
                message=str(e),
                duration=0
            )
```

## Performance Architecture

### Agent Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics: Dict[str, List[Metric]] = {}
        self.thresholds: Dict[str, float] = {
            'execution_time': 300.0,  # 5 minutes
            'memory_usage': 1024.0,   # 1GB
            'cpu_usage': 80.0         # 80%
        }
    
    def start_monitoring(self, agent_id: str):
        """Start monitoring an agent"""
        if agent_id not in self.metrics:
            self.metrics[agent_id] = []
    
    def record_metric(self, agent_id: str, metric: Metric):
        """Record a performance metric"""
        if agent_id in self.metrics:
            self.metrics[agent_id].append(metric)
    
    def check_thresholds(self, agent_id: str) -> List[ThresholdViolation]:
        """Check for threshold violations"""
        violations = []
        
        if agent_id in self.metrics:
            recent_metrics = self.metrics[agent_id][-10:]  # Last 10 metrics
            
            for metric in recent_metrics:
                if metric.name in self.thresholds:
                    threshold = self.thresholds[metric.name]
                    if metric.value > threshold:
                        violations.append(
                            ThresholdViolation(
                                agent_id=agent_id,
                                metric=metric.name,
                                value=metric.value,
                                threshold=threshold
                            )
                        )
        
        return violations
```

## Security Architecture

### Agent Sandbox

```python
class AgentSandbox:
    def __init__(self, sandbox_config: SandboxConfig):
        self.config = sandbox_config
        self.active_processes: Dict[str, subprocess.Popen] = {}
    
    async def execute_agent(self, agent: BaseAgent, task: Task) -> TaskResult:
        """Execute an agent in a sandboxed environment"""
        # Create isolated environment
        env = self._create_isolated_env()
        
        # Set resource limits
        limits = self.config.resource_limits
        
        try:
            # Execute agent in subprocess
            process = await asyncio.create_subprocess_exec(
                'python', '-m', 'bmad.agent_executor',
                agent.config.agent_id,
                task.json(),
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                limit=limits.max_memory
            )
            
            self.active_processes[agent.config.agent_id] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=limits.max_execution_time
                )
                
                if process.returncode == 0:
                    result = TaskResult.from_json(stdout.decode())
                else:
                    result = TaskResult(
                        success=False,
                        error=stderr.decode()
                    )
                
            except asyncio.TimeoutError:
                process.kill()
                result = TaskResult(
                    success=False,
                    error="Agent execution timed out"
                )
            
        finally:
            if agent.config.agent_id in self.active_processes:
                del self.active_processes[agent.config.agent_id]
        
        return result
    
    def _create_isolated_env(self) -> Dict[str, str]:
        """Create isolated environment for agent execution"""
        env = os.environ.copy()
        
        # Restrict file system access
        env['BMAD_SANDBOX'] = 'true'
        env['BMAD_ALLOWED_PATHS'] = ','.join(self.config.allowed_paths)
        
        # Restrict network access
        if self.config.restrict_network:
            env['BMAD_NETWORK_RESTRICTED'] = 'true'
        
        return env
```

## Conclusion

The BMad Framework represents a sophisticated, extensible architecture for development automation and project management. Its multi-agent system, comprehensive workflow orchestration, and plugin architecture provide:

- **Modularity**: Extensible agent and plugin system
- **Flexibility**: Configurable workflows and tooling
- **Scalability**: Performance monitoring and optimization
- **Security**: Sandboxed agent execution
- **Usability**: Rich CLI interface and comprehensive documentation
- **Integration**: External service connectivity
- **Quality**: Built-in testing and validation

This architecture enables the BMad Framework to handle complex development workflows while maintaining security, performance, and extensibility standards. The framework serves as the foundation for the ScrapeCraft project's development tooling and automation capabilities.