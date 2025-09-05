"""
Architecture diagram generator for creating comprehensive system architecture diagrams.

This module provides specialized diagram generation for different architectural
patterns and system designs.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from .mermaid_generator import MermaidGenerator

logger = logging.getLogger(__name__)


class ArchitecturePattern(Enum):
    """Common architecture patterns."""
    MVC = "mvc"
    MICROSERVICES = "microservices"
    LAYERED = "layered"
    EVENT_DRIVEN = "event_driven"
    SERVERLESS = "serverless"
    CLEAN_ARCHITECTURE = "clean_architecture"
    HEXAGONAL = "hexagonal"


@dataclass
class SystemComponent:
    """Represents a system component in architecture."""
    name: str
    component_type: str  # service, database, frontend, etc.
    technologies: List[str]
    responsibilities: List[str]
    interfaces: List[str] = None
    deployment_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.interfaces is None:
            self.interfaces = []
        if self.deployment_info is None:
            self.deployment_info = {}


class ArchitectureDiagramGenerator:
    """
    Generates architecture diagrams for different system patterns.
    
    Creates comprehensive architecture diagrams showing system components,
    their relationships, data flows, and deployment architecture.
    """
    
    def __init__(self):
        self.mermaid = MermaidGenerator()
        
    def generate_system_architecture(
        self,
        analysis_data: Dict[str, Any],
        pattern: Optional[ArchitecturePattern] = None
    ) -> str:
        """
        Generate system architecture diagram based on detected pattern.
        
        Args:
            analysis_data: Complete system analysis
            pattern: Optional architecture pattern to use
            
        Returns:
            Mermaid diagram code
        """
        # Detect architecture pattern if not provided
        if pattern is None:
            pattern = self._detect_architecture_pattern(analysis_data)
        
        if pattern == ArchitecturePattern.MVC:
            return self._generate_mvc_architecture(analysis_data)
        elif pattern == ArchitecturePattern.MICROSERVICES:
            return self._generate_microservices_architecture(analysis_data)
        elif pattern == ArchitecturePattern.LAYERED:
            return self._generate_layered_architecture(analysis_data)
        elif pattern == ArchitecturePattern.EVENT_DRIVEN:
            return self._generate_event_driven_architecture(analysis_data)
        else:
            return self._generate_generic_architecture(analysis_data)
    
    def generate_deployment_architecture(
        self,
        deployment_info: Dict[str, Any],
        title: str = "Deployment Architecture"
    ) -> str:
        """Generate deployment architecture diagram."""
        
        lines = [
            "flowchart TB",
            f"    title[\"{title}\"]",
            "",
            "    subgraph \"Cloud Infrastructure\""
        ]
        
        # Extract deployment components
        containers = deployment_info.get('containers', [])
        services = deployment_info.get('services', [])
        databases = deployment_info.get('databases', [])
        external_services = deployment_info.get('external_services', [])
        
        # Add containers
        for container in containers:
            container_id = self.mermaid._sanitize_id(container.get('name', 'container'))
            container_name = container.get('name', 'Container')
            image = container.get('image', 'unknown')
            
            lines.append(f"        {container_id}[[DOCKER] {container_name}<br/>Image: {image}]:::container")
        
        # Add services
        for service in services:
            service_id = self.mermaid._sanitize_id(service.get('name', 'service'))
            service_name = service.get('name', 'Service')
            port = service.get('port', 'N/A')
            
            lines.append(f"        {service_id}[[SVC] {service_name}<br/>Port: {port}]:::service")
        
        # Add databases
        for db in databases:
            db_id = self.mermaid._sanitize_id(db.get('name', 'database'))
            db_name = db.get('name', 'Database')
            db_type = db.get('type', 'SQL')
            
            lines.append(f"        {db_id}[([DB] {db_name}<br/>Type: {db_type})]:::database")
        
        lines.append("    end")
        lines.append("")
        
        # Add external services
        if external_services:
            lines.append("    subgraph \"External Services\"")
            for ext_service in external_services:
                ext_id = self.mermaid._sanitize_id(ext_service.get('name', 'external'))
                ext_name = ext_service.get('name', 'External Service')
                ext_type = ext_service.get('type', 'API')
                
                lines.append(f"        {ext_id}[[EXT] {ext_name}<br/>Type: {ext_type}]:::external")
            
            lines.append("    end")
            lines.append("")
        
        # Add relationships
        relationships = deployment_info.get('relationships', [])
        for rel in relationships:
            from_comp = self.mermaid._sanitize_id(rel.get('from', 'unknown'))
            to_comp = self.mermaid._sanitize_id(rel.get('to', 'unknown'))
            rel_type = rel.get('type', 'connects')
            
            if rel_type == 'http':
                lines.append(f"    {from_comp} -->|HTTP| {to_comp}")
            elif rel_type == 'database':
                lines.append(f"    {from_comp} -.->|SQL| {to_comp}")
            else:
                lines.append(f"    {from_comp} --> {to_comp}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef container fill:#e3f2fd,stroke:#1976d2,stroke-width:2px",
            "    classDef service fill:#e8f5e8,stroke:#388e3c,stroke-width:2px",
            "    classDef database fill:#fff3e0,stroke:#f57c00,stroke-width:2px",
            "    classDef external fill:#fce4ec,stroke:#c2185b,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def generate_data_flow_diagram(
        self,
        data_flows: List[Dict[str, Any]],
        title: str = "Data Flow Architecture"
    ) -> str:
        """Generate data flow diagram."""
        
        lines = [
            "flowchart LR",
            f"    title[\"{title}\"]"
        ]
        
        # Track all nodes
        nodes = set()
        
        for flow in data_flows:
            source = flow.get('source', 'Unknown')
            target = flow.get('target', 'Unknown')
            data_type = flow.get('data_type', 'data')
            flow_type = flow.get('flow_type', 'sync')
            
            source_id = self.mermaid._sanitize_id(source)
            target_id = self.mermaid._sanitize_id(target)
            
            nodes.add((source_id, source))
            nodes.add((target_id, target))
            
            # Different arrow styles for different flow types
            if flow_type == 'async':
                lines.append(f"    {source_id} -.->|{data_type}| {target_id}")
            elif flow_type == 'event':
                lines.append(f"    {source_id} ==>|{data_type}| {target_id}")
            else:
                lines.append(f"    {source_id} -->|{data_type}| {target_id}")
        
        # Add node definitions with styling
        node_lines = []
        for node_id, node_name in sorted(nodes):
            if 'database' in node_name.lower() or 'db' in node_name.lower():
                node_lines.append(f"    {node_id}[([DB] {node_name})]:::database")
            elif 'api' in node_name.lower():
                node_lines.append(f"    {node_id}[[API] {node_name}]:::api")
            elif 'queue' in node_name.lower() or 'broker' in node_name.lower():
                node_lines.append(f"    {node_id}[[QUEUE] {node_name}]:::queue")
            else:
                node_lines.append(f"    {node_id}[[COMP] {node_name}]:::component")
        
        # Insert node definitions at the beginning
        lines[2:2] = node_lines
        lines.append("")
        
        # Add styling
        lines.extend([
            "    classDef database fill:#fff3e0,stroke:#f57c00,stroke-width:2px",
            "    classDef api fill:#e8f5e8,stroke:#388e3c,stroke-width:2px",
            "    classDef queue fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px",
            "    classDef component fill:#e1f5fe,stroke:#0277bd,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def generate_security_architecture(
        self,
        security_components: Dict[str, Any],
        title: str = "Security Architecture"
    ) -> str:
        """Generate security architecture diagram."""
        
        lines = [
            "flowchart TD",
            f"    title[\"{title}\"]",
            "",
            "    subgraph \"External\""
        ]
        
        # External threats and users
        external_actors = security_components.get('external_actors', [])
        for actor in external_actors:
            actor_id = self.mermaid._sanitize_id(actor.get('name', 'actor'))
            actor_name = actor.get('name', 'Actor')
            actor_type = actor.get('type', 'user')
            
            if actor_type == 'threat':
                lines.append(f"        {actor_id}[[THREAT] {actor_name}]:::threat")
            else:
                lines.append(f"        {actor_id}[[USER] {actor_name}]:::user")
        
        lines.extend([
            "    end",
            "",
            "    subgraph \"Security Perimeter\""
        ])
        
        # Security controls
        security_controls = security_components.get('security_controls', [])
        for control in security_controls:
            control_id = self.mermaid._sanitize_id(control.get('name', 'control'))
            control_name = control.get('name', 'Security Control')
            control_type = control.get('type', 'firewall')
            
            if control_type == 'firewall':
                lines.append(f"        {control_id}[[FIREWALL] {control_name}]:::firewall")
            elif control_type == 'auth':
                lines.append(f"        {control_id}[[AUTH] {control_name}]:::auth")
            elif control_type == 'monitor':
                lines.append(f"        {control_id}[[MONITOR] {control_name}]:::monitor")
            else:
                lines.append(f"        {control_id}[[SEC] {control_name}]:::security")
        
        lines.extend([
            "    end",
            "",
            "    subgraph \"Protected Systems\""
        ])
        
        # Protected systems
        protected_systems = security_components.get('protected_systems', [])
        for system in protected_systems:
            system_id = self.mermaid._sanitize_id(system.get('name', 'system'))
            system_name = system.get('name', 'System')
            
            lines.append(f"        {system_id}[[SYS] {system_name}]:::system")
        
        lines.extend([
            "    end",
            ""
        ])
        
        # Add security flows
        security_flows = security_components.get('security_flows', [])
        for flow in security_flows:
            from_comp = self.mermaid._sanitize_id(flow.get('from', 'unknown'))
            to_comp = self.mermaid._sanitize_id(flow.get('to', 'unknown'))
            flow_type = flow.get('type', 'allow')
            
            if flow_type == 'block':
                lines.append(f"    {from_comp} -.x {to_comp}")
            elif flow_type == 'monitor':
                lines.append(f"    {from_comp} -.-> {to_comp}")
            else:
                lines.append(f"    {from_comp} --> {to_comp}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef threat fill:#ffebee,stroke:#d32f2f,stroke-width:3px",
            "    classDef user fill:#e8f5e8,stroke:#388e3c,stroke-width:2px",
            "    classDef firewall fill:#fff3e0,stroke:#f57c00,stroke-width:2px",
            "    classDef auth fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px",
            "    classDef monitor fill:#e1f5fe,stroke:#0277bd,stroke-width:2px",
            "    classDef security fill:#fce4ec,stroke:#c2185b,stroke-width:2px",
            "    classDef system fill:#f9fbe7,stroke:#689f38,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def _detect_architecture_pattern(
        self, 
        analysis_data: Dict[str, Any]
    ) -> ArchitecturePattern:
        """Detect architecture pattern from analysis data."""
        
        frameworks = analysis_data.get('frameworks', [])
        file_structure = analysis_data.get('file_structure', {})
        services = analysis_data.get('services', [])
        
        framework_names = [f.get('name', '').lower() for f in frameworks]
        
        # Check for microservices indicators
        if (len(services) > 3 or 
            any('docker' in str(file_structure).lower() for _ in [1]) or
            any('kubernetes' in fw for fw in framework_names)):
            return ArchitecturePattern.MICROSERVICES
        
        # Check for MVC frameworks
        mvc_frameworks = ['django', 'rails', 'spring', 'asp.net']
        if any(fw in framework_names for fw in mvc_frameworks):
            return ArchitecturePattern.MVC
        
        # Check for serverless indicators
        serverless_indicators = ['lambda', 'serverless', 'azure-functions']
        if any(indicator in fw for fw in framework_names for indicator in serverless_indicators):
            return ArchitecturePattern.SERVERLESS
        
        # Check for layered architecture
        if ('services' in str(file_structure).lower() and 
            'repositories' in str(file_structure).lower()):
            return ArchitecturePattern.LAYERED
        
        # Default to generic
        return ArchitecturePattern.LAYERED
    
    def _generate_mvc_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate MVC architecture diagram."""
        
        components = [
            {'name': 'User Interface', 'type': 'frontend', 'description': 'Presentation Layer'},
            {'name': 'Controller', 'type': 'controller', 'description': 'Request Handler'},
            {'name': 'Model', 'type': 'model', 'description': 'Business Logic'},
            {'name': 'View', 'type': 'view', 'description': 'Data Presentation'},
            {'name': 'Database', 'type': 'database', 'description': 'Data Storage'}
        ]
        
        relationships = [
            {'from': 'User Interface', 'to': 'Controller', 'type': 'http', 'label': 'HTTP Request'},
            {'from': 'Controller', 'to': 'Model', 'type': 'call', 'label': 'Process Data'},
            {'from': 'Model', 'to': 'Database', 'type': 'query', 'label': 'Query/Update'},
            {'from': 'Controller', 'to': 'View', 'type': 'render', 'label': 'Render View'},
            {'from': 'View', 'to': 'User Interface', 'type': 'response', 'label': 'HTTP Response'}
        ]
        
        return self.mermaid.generate_architecture_diagram(
            components, relationships, "MVC Architecture"
        )
    
    def _generate_microservices_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate microservices architecture diagram."""
        
        services = analysis_data.get('services', [])
        if not services:
            # Create example microservices based on detected frameworks
            frameworks = analysis_data.get('frameworks', [])
            services = [
                {'name': 'API Gateway', 'type': 'gateway'},
                {'name': 'Auth Service', 'type': 'service'},
                {'name': 'Business Service', 'type': 'service'},
                {'name': 'Data Service', 'type': 'service'}
            ]
        
        components = []
        relationships = []
        
        # Add API Gateway
        components.append({
            'name': 'API Gateway',
            'type': 'gateway',
            'description': 'Entry Point'
        })
        
        # Add services
        for service in services:
            service_name = service.get('name', 'Service')
            if service_name != 'API Gateway':
                components.append({
                    'name': service_name,
                    'type': 'service',
                    'description': f'{service_name} Microservice'
                })
                
                relationships.append({
                    'from': 'API Gateway',
                    'to': service_name,
                    'type': 'api_call',
                    'label': 'API Call'
                })
        
        # Add shared components
        components.extend([
            {'name': 'Message Queue', 'type': 'queue', 'description': 'Event Bus'},
            {'name': 'Database', 'type': 'database', 'description': 'Shared Data'},
            {'name': 'Cache', 'type': 'cache', 'description': 'Redis Cache'}
        ])
        
        return self.mermaid.generate_architecture_diagram(
            components, relationships, "Microservices Architecture"
        )
    
    def _generate_layered_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate layered architecture diagram."""
        
        components = [
            {'name': 'Presentation Layer', 'type': 'frontend', 'description': 'UI Components'},
            {'name': 'Business Layer', 'type': 'service', 'description': 'Business Logic'},
            {'name': 'Data Access Layer', 'type': 'repository', 'description': 'Data Repository'},
            {'name': 'Database', 'type': 'database', 'description': 'Data Storage'}
        ]
        
        relationships = [
            {'from': 'Presentation Layer', 'to': 'Business Layer', 'type': 'call', 'label': 'Service Call'},
            {'from': 'Business Layer', 'to': 'Data Access Layer', 'type': 'call', 'label': 'Data Request'},
            {'from': 'Data Access Layer', 'to': 'Database', 'type': 'query', 'label': 'SQL Query'}
        ]
        
        return self.mermaid.generate_architecture_diagram(
            components, relationships, "Layered Architecture"
        )
    
    def _generate_event_driven_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate event-driven architecture diagram."""
        
        components = [
            {'name': 'Event Producer', 'type': 'service', 'description': 'Generates Events'},
            {'name': 'Event Bus', 'type': 'queue', 'description': 'Message Broker'},
            {'name': 'Event Consumer 1', 'type': 'service', 'description': 'Processes Events'},
            {'name': 'Event Consumer 2', 'type': 'service', 'description': 'Processes Events'},
            {'name': 'Event Store', 'type': 'database', 'description': 'Event History'}
        ]
        
        relationships = [
            {'from': 'Event Producer', 'to': 'Event Bus', 'type': 'publish', 'label': 'Publish Event'},
            {'from': 'Event Bus', 'to': 'Event Consumer 1', 'type': 'subscribe', 'label': 'Subscribe'},
            {'from': 'Event Bus', 'to': 'Event Consumer 2', 'type': 'subscribe', 'label': 'Subscribe'},
            {'from': 'Event Bus', 'to': 'Event Store', 'type': 'store', 'label': 'Store Event'}
        ]
        
        return self.mermaid.generate_architecture_diagram(
            components, relationships, "Event-Driven Architecture"
        )
    
    def _generate_generic_architecture(self, analysis_data: Dict[str, Any]) -> str:
        """Generate generic system architecture diagram."""
        
        return self.mermaid.generate_github_repo_overview(
            analysis_data, "System Architecture"
        )
