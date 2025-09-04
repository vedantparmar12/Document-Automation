"""
Database diagram generator for creating database schema and relationship diagrams.

This module provides specialized diagram generation for database schemas,
entity relationships, and data flow diagrams.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass

from .mermaid_generator import MermaidGenerator

logger = logging.getLogger(__name__)


@dataclass
class TableRelationship:
    """Represents a relationship between database tables."""
    from_table: str
    to_table: str
    from_field: str
    to_field: str
    relationship_type: str  # one_to_one, one_to_many, many_to_many
    constraint_name: Optional[str] = None


class DatabaseDiagramGenerator:
    """
    Generates database-related diagrams including ER diagrams,
    schema diagrams, and data flow diagrams.
    """
    
    def __init__(self):
        self.mermaid = MermaidGenerator()
    
    def generate_comprehensive_database_diagram(
        self,
        database_schema: Dict[str, Any],
        title: str = "Database Schema"
    ) -> str:
        """
        Generate a comprehensive database diagram showing tables,
        relationships, indexes, and constraints.
        
        Args:
            database_schema: Complete database schema information
            title: Diagram title
            
        Returns:
            Mermaid ER diagram code
        """
        tables = database_schema.get('tables', [])
        relationships = database_schema.get('relationships', [])
        
        if not tables:
            return self._generate_empty_database_diagram(title)
        
        lines = [
            "erDiagram",
            f"    title {title}",
            ""
        ]
        
        # Add tables with detailed field information
        for table in tables:
            table_name = table.get('name', 'unknown').upper()
            fields = table.get('fields', [])
            indexes = table.get('indexes', [])
            
            lines.append(f"    {table_name} {{")
            
            # Add fields with detailed information
            for field in fields:
                field_name = field.get('name', 'unknown')
                field_type = field.get('data_type', 'string').upper()
                
                # Build constraint information
                constraints = []
                if field.get('primary_key'):
                    constraints.append('PK')
                if field.get('foreign_key'):
                    constraints.append('FK')
                if field.get('unique'):
                    constraints.append('UK')
                if not field.get('nullable', True):
                    constraints.append('NOT NULL')
                if field.get('indexed'):
                    constraints.append('IDX')
                
                # Add default value if present
                default_value = field.get('default_value')
                if default_value:
                    constraints.append(f"DEFAULT {default_value}")
                
                constraint_str = f" \"{', '.join(constraints)}\"" if constraints else ""
                lines.append(f"        {field_type} {field_name}{constraint_str}")
            
            lines.append("    }")
            lines.append("")
        
        # Add relationships with detailed information
        for rel in relationships:
            from_table = rel.get('from_table', '').upper()
            to_table = rel.get('to_table', '').upper()
            rel_type = rel.get('relationship_type', 'one_to_many')
            from_field = rel.get('from_field', '')
            to_field = rel.get('to_field', '')
            
            # Create relationship label
            rel_label = f"{from_field}-{to_field}" if from_field and to_field else "relates"
            
            if rel_type == 'one_to_one':
                lines.append(f"    {from_table} ||--|| {to_table} : {rel_label}")
            elif rel_type == 'one_to_many':
                lines.append(f"    {from_table} ||--o{{ {to_table} : {rel_label}")
            elif rel_type == 'many_to_many':
                lines.append(f"    {from_table} }}o--o{{ {to_table} : {rel_label}")
            elif rel_type == 'many_to_one':
                lines.append(f"    {from_table} }}o--|| {to_table} : {rel_label}")
            else:
                lines.append(f"    {from_table} ||--|| {to_table} : {rel_label}")
        
        return "\n".join(lines)
    
    def generate_database_architecture_diagram(
        self,
        database_info: Dict[str, Any],
        title: str = "Database Architecture"
    ) -> str:
        """
        Generate database architecture diagram showing database systems,
        connections, replication, and infrastructure.
        
        Args:
            database_info: Database architecture information
            title: Diagram title
            
        Returns:
            Mermaid flowchart showing database architecture
        """
        lines = [
            "flowchart TB",
            f"    title[\"{title}\"]",
            ""
        ]
        
        # Application layer
        applications = database_info.get('applications', [])
        if applications:
            lines.append("    subgraph \"Application Layer\"")
            for app in applications:
                app_id = self.mermaid._sanitize_id(app.get('name', 'app'))
                app_name = app.get('name', 'Application')
                app_type = app.get('type', 'web')
                
                if app_type == 'web':
                    lines.append(f"        {app_id}[🌐 {app_name}]:::webapp")
                elif app_type == 'api':
                    lines.append(f"        {app_id}[🔌 {app_name}]:::api")
                else:
                    lines.append(f"        {app_id}[📱 {app_name}]:::app")
            
            lines.extend(["    end", ""])
        
        # Database layer
        databases = database_info.get('databases', [])
        if databases:
            lines.append("    subgraph \"Database Layer\"")
            
            for db in databases:
                db_id = self.mermaid._sanitize_id(db.get('name', 'db'))
                db_name = db.get('name', 'Database')
                db_type = db.get('type', 'SQL')
                db_role = db.get('role', 'primary')
                
                if db_role == 'primary':
                    lines.append(f"        {db_id}[(🗄️ {db_name}<br/>{db_type} - Primary)]:::primary_db")
                elif db_role == 'replica':
                    lines.append(f"        {db_id}[(📋 {db_name}<br/>{db_type} - Replica)]:::replica_db")
                elif db_role == 'cache':
                    lines.append(f"        {db_id}[(⚡ {db_name}<br/>Cache)]:::cache_db")
                else:
                    lines.append(f"        {db_id}[(🗃️ {db_name}<br/>{db_type})]:::database")
            
            lines.extend(["    end", ""])
        
        # Infrastructure layer
        infrastructure = database_info.get('infrastructure', [])
        if infrastructure:
            lines.append("    subgraph \"Infrastructure\"")
            
            for infra in infrastructure:
                infra_id = self.mermaid._sanitize_id(infra.get('name', 'infra'))
                infra_name = infra.get('name', 'Infrastructure')
                infra_type = infra.get('type', 'server')
                
                if infra_type == 'load_balancer':
                    lines.append(f"        {infra_id}[⚖️ {infra_name}]:::load_balancer")
                elif infra_type == 'proxy':
                    lines.append(f"        {infra_id}[🔄 {infra_name}]:::proxy")
                else:
                    lines.append(f"        {infra_id}[🖥️ {infra_name}]:::server")
            
            lines.extend(["    end", ""])
        
        # Add connections
        connections = database_info.get('connections', [])
        for conn in connections:
            from_comp = self.mermaid._sanitize_id(conn.get('from', 'unknown'))
            to_comp = self.mermaid._sanitize_id(conn.get('to', 'unknown'))
            conn_type = conn.get('type', 'query')
            
            if conn_type == 'replication':
                lines.append(f"    {from_comp} -.->|Replication| {to_comp}")
            elif conn_type == 'backup':
                lines.append(f"    {from_comp} -.->|Backup| {to_comp}")
            elif conn_type == 'cache':
                lines.append(f"    {from_comp} -->|Cache| {to_comp}")
            else:
                lines.append(f"    {from_comp} -->|Query| {to_comp}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef webapp fill:#e3f2fd,stroke:#1976d2,stroke-width:2px",
            "    classDef api fill:#e8f5e8,stroke:#388e3c,stroke-width:2px",
            "    classDef app fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px",
            "    classDef primary_db fill:#fff3e0,stroke:#f57c00,stroke-width:3px",
            "    classDef replica_db fill:#fff3e0,stroke:#ff9800,stroke-width:2px,stroke-dasharray: 5 5",
            "    classDef cache_db fill:#ffebee,stroke:#e91e63,stroke-width:2px",
            "    classDef database fill:#f1f8e9,stroke:#689f38,stroke-width:2px",
            "    classDef load_balancer fill:#fce4ec,stroke:#c2185b,stroke-width:2px",
            "    classDef proxy fill:#e1f5fe,stroke:#0277bd,stroke-width:2px",
            "    classDef server fill:#f9fbe7,stroke:#827717,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def generate_data_flow_diagram(
        self,
        data_flows: List[Dict[str, Any]],
        title: str = "Database Data Flow"
    ) -> str:
        """
        Generate data flow diagram showing how data moves through
        the database system.
        
        Args:
            data_flows: List of data flow information
            title: Diagram title
            
        Returns:
            Mermaid flowchart showing data flows
        """
        lines = [
            "flowchart LR",
            f"    title[\"{title}\"]"
        ]
        
        # Collect all nodes
        nodes = set()
        flows_by_type = {'read': [], 'write': [], 'sync': [], 'backup': []}
        
        for flow in data_flows:
            source = flow.get('source', 'Unknown')
            target = flow.get('target', 'Unknown')
            flow_type = flow.get('flow_type', 'read')
            
            source_id = self.mermaid._sanitize_id(source)
            target_id = self.mermaid._sanitize_id(target)
            
            nodes.add((source_id, source, flow.get('source_type', 'component')))
            nodes.add((target_id, target, flow.get('target_type', 'component')))
            
            if flow_type in flows_by_type:
                flows_by_type[flow_type].append(flow)
            else:
                flows_by_type['read'].append(flow)
        
        # Add node definitions
        for node_id, node_name, node_type in sorted(nodes):
            if node_type == 'database':
                lines.append(f"    {node_id}[(🗄️ {node_name})]:::database")
            elif node_type == 'application':
                lines.append(f"    {node_id}[📱 {node_name}]:::application")
            elif node_type == 'cache':
                lines.append(f"    {node_id}[⚡ {node_name}]:::cache")
            elif node_type == 'queue':
                lines.append(f"    {node_id}[📫 {node_name}]:::queue")
            else:
                lines.append(f"    {node_id}[📦 {node_name}]:::component")
        
        lines.append("")
        
        # Add flows by type
        for flow_type, flows in flows_by_type.items():
            if not flows:
                continue
                
            for flow in flows:
                source_id = self.mermaid._sanitize_id(flow.get('source', 'Unknown'))
                target_id = self.mermaid._sanitize_id(flow.get('target', 'Unknown'))
                data_type = flow.get('data_type', 'data')
                
                if flow_type == 'write':
                    lines.append(f"    {source_id} -->|Write {data_type}| {target_id}")
                elif flow_type == 'sync':
                    lines.append(f"    {source_id} <-->|Sync {data_type}| {target_id}")
                elif flow_type == 'backup':
                    lines.append(f"    {source_id} -.->|Backup {data_type}| {target_id}")
                else:  # read
                    lines.append(f"    {source_id} -->|Read {data_type}| {target_id}")
        
        # Add styling
        lines.extend([
            "",
            "    classDef database fill:#fff3e0,stroke:#f57c00,stroke-width:2px",
            "    classDef application fill:#e3f2fd,stroke:#1976d2,stroke-width:2px",
            "    classDef cache fill:#ffebee,stroke:#e91e63,stroke-width:2px",
            "    classDef queue fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px",
            "    classDef component fill:#e8f5e8,stroke:#388e3c,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def generate_migration_timeline(
        self,
        migrations: List[Dict[str, Any]],
        title: str = "Database Migration Timeline"
    ) -> str:
        """
        Generate timeline diagram showing database migrations.
        
        Args:
            migrations: List of migration information
            title: Diagram title
            
        Returns:
            Mermaid timeline/gantt diagram
        """
        if not migrations:
            return self._generate_empty_migration_diagram(title)
        
        lines = [
            "gantt",
            f"    title {title}",
            "    dateFormat  YYYY-MM-DD",
            "    section Database Schema"
        ]
        
        for i, migration in enumerate(migrations):
            migration_name = migration.get('name', f'Migration {i+1}')
            migration_type = migration.get('type', 'schema_change')
            created_date = migration.get('created_date', '2024-01-01')
            
            # Clean migration name for gantt chart
            clean_name = migration_name.replace(':', '').replace(',', '')
            
            if migration_type == 'create_table':
                lines.append(f"    Create {clean_name}    :create, {created_date}, 1d")
            elif migration_type == 'alter_table':
                lines.append(f"    Alter {clean_name}     :alter, {created_date}, 1d")
            elif migration_type == 'drop_table':
                lines.append(f"    Drop {clean_name}      :drop, {created_date}, 1d")
            else:
                lines.append(f"    {clean_name}           :change, {created_date}, 1d")
        
        return "\n".join(lines)
    
    def generate_database_performance_diagram(
        self,
        performance_data: Dict[str, Any],
        title: str = "Database Performance"
    ) -> str:
        """
        Generate diagram showing database performance characteristics.
        
        Args:
            performance_data: Performance metrics and information
            title: Diagram title
            
        Returns:
            Mermaid flowchart showing performance aspects
        """
        lines = [
            "flowchart TD",
            f"    title[\"{title}\"]",
            ""
        ]
        
        # Performance metrics
        metrics = performance_data.get('metrics', {})
        
        lines.append("    subgraph \"Performance Metrics\"")
        
        if 'query_performance' in metrics:
            qp = metrics['query_performance']
            avg_time = qp.get('average_time', 'N/A')
            slow_queries = qp.get('slow_queries', 0)
            lines.append(f"        QP[📊 Query Performance<br/>Avg: {avg_time}ms<br/>Slow: {slow_queries}]:::metric")
        
        if 'connection_pool' in metrics:
            cp = metrics['connection_pool']
            active = cp.get('active_connections', 0)
            max_conn = cp.get('max_connections', 0)
            lines.append(f"        CP[🔗 Connections<br/>Active: {active}/{max_conn}]:::metric")
        
        if 'storage' in metrics:
            storage = metrics['storage']
            used = storage.get('used_space', 'N/A')
            total = storage.get('total_space', 'N/A')
            lines.append(f"        ST[💾 Storage<br/>Used: {used}/{total}]:::metric")
        
        lines.extend(["    end", ""])
        
        # Bottlenecks
        bottlenecks = performance_data.get('bottlenecks', [])
        if bottlenecks:
            lines.append("    subgraph \"Identified Bottlenecks\"")
            
            for i, bottleneck in enumerate(bottlenecks):
                bottleneck_id = f"BN{i+1}"
                bottleneck_name = bottleneck.get('name', 'Bottleneck')
                severity = bottleneck.get('severity', 'medium')
                
                if severity == 'high':
                    lines.append(f"        {bottleneck_id}[🔴 {bottleneck_name}]:::high_severity")
                elif severity == 'medium':
                    lines.append(f"        {bottleneck_id}[🟡 {bottleneck_name}]:::medium_severity")
                else:
                    lines.append(f"        {bottleneck_id}[🟢 {bottleneck_name}]:::low_severity")
            
            lines.extend(["    end", ""])
        
        # Optimization suggestions
        optimizations = performance_data.get('optimizations', [])
        if optimizations:
            lines.append("    subgraph \"Optimization Suggestions\"")
            
            for i, opt in enumerate(optimizations):
                opt_id = f"OPT{i+1}"
                opt_name = opt.get('name', 'Optimization')
                impact = opt.get('impact', 'medium')
                
                lines.append(f"        {opt_id}[💡 {opt_name}]:::optimization")
            
            lines.extend(["    end", ""])
        
        # Add styling
        lines.extend([
            "",
            "    classDef metric fill:#e1f5fe,stroke:#0277bd,stroke-width:2px",
            "    classDef high_severity fill:#ffebee,stroke:#d32f2f,stroke-width:3px",
            "    classDef medium_severity fill:#fff8e1,stroke:#f57c00,stroke-width:2px",
            "    classDef low_severity fill:#e8f5e8,stroke:#388e3c,stroke-width:2px",
            "    classDef optimization fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def _generate_empty_database_diagram(self, title: str) -> str:
        """Generate placeholder diagram when no database schema is available."""
        return f"""erDiagram
    title {title}
    
    NO_SCHEMA {{
        string message "No database schema detected"
        string suggestion "Add database models or DDL files"
    }}"""
    
    def _generate_empty_migration_diagram(self, title: str) -> str:
        """Generate placeholder diagram when no migrations are available."""
        return f"""gantt
    title {title}
    dateFormat  YYYY-MM-DD
    
    section Status
    No migrations found    :milestone, 2024-01-01, 0d"""
