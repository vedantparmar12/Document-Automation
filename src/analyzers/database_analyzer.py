"""
Database schema analysis for various database systems.

This module provides comprehensive analysis of database schemas,
including SQL, NoSQL, and other data storage systems.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import ast

logger = logging.getLogger(__name__)


@dataclass
class DatabaseField:
    """Represents a database field/column."""
    name: str
    data_type: str
    nullable: bool = True
    primary_key: bool = False
    foreign_key: Optional[str] = None
    unique: bool = False
    indexed: bool = False
    default_value: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DatabaseTable:
    """Represents a database table/collection."""
    name: str
    fields: List[DatabaseField]
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def primary_keys(self) -> List[str]:
        """Get primary key field names."""
        return [f.name for f in self.fields if f.primary_key]
    
    @property
    def foreign_keys(self) -> List[Dict[str, str]]:
        """Get foreign key relationships."""
        fks = []
        for field in self.fields:
            if field.foreign_key:
                fks.append({
                    'field': field.name,
                    'references': field.foreign_key
                })
        return fks


@dataclass
class DatabaseSchema:
    """Complete database schema information."""
    name: str
    database_type: str  # sql, mongodb, redis, etc.
    tables: List[DatabaseTable]
    views: List[Dict[str, Any]] = field(default_factory=list)
    procedures: List[Dict[str, Any]] = field(default_factory=list)
    functions: List[Dict[str, Any]] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'database_type': self.database_type,
            'tables': [
                {
                    'name': table.name,
                    'fields': [
                        {
                            'name': field.name,
                            'data_type': field.data_type,
                            'nullable': field.nullable,
                            'primary_key': field.primary_key,
                            'foreign_key': field.foreign_key,
                            'unique': field.unique,
                            'indexed': field.indexed,
                            'default_value': field.default_value,
                            'constraints': field.constraints,
                            'metadata': field.metadata
                        }
                        for field in table.fields
                    ],
                    'indexes': table.indexes,
                    'constraints': table.constraints,
                    'relationships': table.relationships,
                    'metadata': table.metadata
                }
                for table in self.tables
            ],
            'views': self.views,
            'procedures': self.procedures,
            'functions': self.functions,
            'triggers': self.triggers,
            'metadata': self.metadata
        }
    
    def get_table(self, table_name: str) -> Optional[DatabaseTable]:
        """Get table by name."""
        for table in self.tables:
            if table.name.lower() == table_name.lower():
                return table
        return None
    
    def get_relationships(self) -> List[Dict[str, Any]]:
        """Get all foreign key relationships."""
        relationships = []
        for table in self.tables:
            for fk in table.foreign_keys:
                relationships.append({
                    'from_table': table.name,
                    'from_field': fk['field'],
                    'to_table': fk['references'].split('.')[0] if '.' in fk['references'] else 'unknown',
                    'to_field': fk['references'].split('.')[1] if '.' in fk['references'] else fk['references'],
                    'relationship_type': 'many_to_one'  # Simplified
                })
        return relationships


class DatabaseAnalyzer:
    """
    Database schema analyzer supporting multiple database systems.
    
    Analyzes:
    - SQL DDL files
    - ORM model files (Django, SQLAlchemy, etc.)
    - Migration files
    - NoSQL schema definitions
    - Configuration files
    """
    
    def __init__(self):
        self.sql_keywords = self._load_sql_keywords()
        self.type_mappings = self._load_type_mappings()
    
    def _load_sql_keywords(self) -> Set[str]:
        """Load SQL keywords for parsing."""
        return {
            'CREATE', 'TABLE', 'VIEW', 'INDEX', 'PROCEDURE', 'FUNCTION',
            'PRIMARY', 'KEY', 'FOREIGN', 'REFERENCES', 'UNIQUE', 'NOT', 'NULL',
            'DEFAULT', 'AUTO_INCREMENT', 'SERIAL', 'IDENTITY',
            'VARCHAR', 'CHAR', 'TEXT', 'INT', 'INTEGER', 'BIGINT', 'DECIMAL',
            'FLOAT', 'DOUBLE', 'DATE', 'DATETIME', 'TIMESTAMP', 'BOOLEAN', 'BOOL'
        }
    
    def _load_type_mappings(self) -> Dict[str, Dict[str, str]]:
        """Load type mappings for different databases."""
        return {
            'mysql': {
                'VARCHAR': 'string',
                'TEXT': 'text',
                'INT': 'integer',
                'BIGINT': 'bigint',
                'DECIMAL': 'decimal',
                'FLOAT': 'float',
                'DATE': 'date',
                'DATETIME': 'datetime',
                'TIMESTAMP': 'timestamp',
                'BOOLEAN': 'boolean'
            },
            'postgresql': {
                'VARCHAR': 'string',
                'TEXT': 'text',
                'INTEGER': 'integer',
                'BIGINT': 'bigint',
                'NUMERIC': 'decimal',
                'REAL': 'float',
                'DATE': 'date',
                'TIMESTAMP': 'timestamp',
                'BOOLEAN': 'boolean'
            },
            'sqlite': {
                'TEXT': 'text',
                'INTEGER': 'integer',
                'REAL': 'float',
                'BLOB': 'binary',
                'NUMERIC': 'numeric'
            }
        }
    
    def analyze_database_schema(
        self,
        file_contents: Dict[str, str],
        database_type: Optional[str] = None
    ) -> List[DatabaseSchema]:
        """
        Analyze database schema from various sources.
        
        Args:
            file_contents: Dictionary of file_path -> content
            database_type: Optional database type hint
            
        Returns:
            List of detected database schemas
        """
        schemas = []
        
        # Detect database type if not provided
        if not database_type:
            database_type = self._detect_database_type(file_contents)
        
        # Analyze SQL files
        sql_schemas = self._analyze_sql_files(file_contents, database_type)
        schemas.extend(sql_schemas)
        
        # Analyze ORM models
        orm_schemas = self._analyze_orm_models(file_contents)
        schemas.extend(orm_schemas)
        
        # Analyze migration files
        migration_schemas = self._analyze_migrations(file_contents)
        schemas.extend(migration_schemas)
        
        # Analyze NoSQL schema definitions
        nosql_schemas = self._analyze_nosql_schemas(file_contents)
        schemas.extend(nosql_schemas)
        
        return schemas
    
    def _detect_database_type(self, file_contents: Dict[str, str]) -> str:
        """Detect database type from file contents."""
        sql_indicators = {
            'mysql': ['ENGINE=InnoDB', 'AUTO_INCREMENT', 'TINYINT', 'MEDIUMTEXT'],
            'postgresql': ['SERIAL', 'BIGSERIAL', 'UUID', '::'],
            'sqlite': ['AUTOINCREMENT', 'WITHOUT ROWID'],
            'mongodb': ['db.collection', 'ObjectId', 'mongoose'],
            'redis': ['HSET', 'SADD', 'ZADD']
        }
        
        for file_path, content in file_contents.items():
            content_lower = content.lower()
            
            for db_type, indicators in sql_indicators.items():
                if any(indicator.lower() in content_lower for indicator in indicators):
                    return db_type
        
        # Default to generic SQL
        return 'sql'
    
    def _analyze_sql_files(
        self, 
        file_contents: Dict[str, str], 
        database_type: str
    ) -> List[DatabaseSchema]:
        """Analyze SQL DDL files."""
        schemas = []
        
        sql_files = [
            (path, content) for path, content in file_contents.items()
            if Path(path).suffix.lower() in ['.sql', '.ddl']
        ]
        
        if not sql_files:
            return schemas
        
        # Group files by schema/database
        schema_files = defaultdict(list)
        for file_path, content in sql_files:
            # Try to determine schema name from file path
            schema_name = self._extract_schema_name(file_path)
            schema_files[schema_name].append((file_path, content))
        
        for schema_name, files in schema_files.items():
            tables = []
            views = []
            procedures = []
            functions = []
            
            for file_path, content in files:
                # Parse SQL statements
                statements = self._parse_sql_statements(content)
                
                for stmt in statements:
                    if stmt['type'] == 'CREATE_TABLE':
                        table = self._parse_create_table(stmt['content'], database_type)
                        if table:
                            tables.append(table)
                    elif stmt['type'] == 'CREATE_VIEW':
                        view = self._parse_create_view(stmt['content'])
                        if view:
                            views.append(view)
                    elif stmt['type'] == 'CREATE_PROCEDURE':
                        proc = self._parse_create_procedure(stmt['content'])
                        if proc:
                            procedures.append(proc)
                    elif stmt['type'] == 'CREATE_FUNCTION':
                        func = self._parse_create_function(stmt['content'])
                        if func:
                            functions.append(func)
            
            if tables or views or procedures or functions:
                schema = DatabaseSchema(
                    name=schema_name,
                    database_type=database_type,
                    tables=tables,
                    views=views,
                    procedures=procedures,
                    functions=functions
                )
                schemas.append(schema)
        
        return schemas
    
    def _analyze_orm_models(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze ORM model files (Django, SQLAlchemy, etc.)."""
        schemas = []
        
        # Django models
        django_schemas = self._analyze_django_models(file_contents)
        schemas.extend(django_schemas)
        
        # SQLAlchemy models
        sqlalchemy_schemas = self._analyze_sqlalchemy_models(file_contents)
        schemas.extend(sqlalchemy_schemas)
        
        # Sequelize models (JavaScript)
        sequelize_schemas = self._analyze_sequelize_models(file_contents)
        schemas.extend(sequelize_schemas)
        
        return schemas
    
    def _analyze_django_models(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze Django model files."""
        tables = []
        
        for file_path, content in file_contents.items():
            if 'models.py' in file_path or '/models/' in file_path:
                django_tables = self._parse_django_models(content, file_path)
                tables.extend(django_tables)
        
        if tables:
            return [DatabaseSchema(
                name='django',
                database_type='django_orm',
                tables=tables
            )]
        
        return []
    
    def _analyze_sqlalchemy_models(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze SQLAlchemy model files."""
        tables = []
        
        for file_path, content in file_contents.items():
            if ('sqlalchemy' in content.lower() and 
                Path(file_path).suffix == '.py'):
                sqlalchemy_tables = self._parse_sqlalchemy_models(content, file_path)
                tables.extend(sqlalchemy_tables)
        
        if tables:
            return [DatabaseSchema(
                name='sqlalchemy',
                database_type='sqlalchemy_orm',
                tables=tables
            )]
        
        return []
    
    def _analyze_sequelize_models(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze Sequelize model files."""
        tables = []
        
        for file_path, content in file_contents.items():
            if ('sequelize' in content.lower() and 
                Path(file_path).suffix in ['.js', '.ts']):
                sequelize_tables = self._parse_sequelize_models(content, file_path)
                tables.extend(sequelize_tables)
        
        if tables:
            return [DatabaseSchema(
                name='sequelize',
                database_type='sequelize_orm',
                tables=tables
            )]
        
        return []
    
    def _analyze_migrations(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze database migration files."""
        schemas = []
        
        migration_files = [
            (path, content) for path, content in file_contents.items()
            if 'migration' in path.lower() or 'migrate' in path.lower()
        ]
        
        if not migration_files:
            return schemas
        
        tables = []
        for file_path, content in migration_files:
            # Django migrations
            if 'migrations/' in file_path and '.py' in file_path:
                migration_tables = self._parse_django_migration(content)
                tables.extend(migration_tables)
            
            # Rails migrations
            elif 'db/migrate' in file_path and '.rb' in file_path:
                migration_tables = self._parse_rails_migration(content)
                tables.extend(migration_tables)
            
            # Laravel migrations
            elif 'database/migrations' in file_path and '.php' in file_path:
                migration_tables = self._parse_laravel_migration(content)
                tables.extend(migration_tables)
        
        if tables:
            schemas.append(DatabaseSchema(
                name='migrations',
                database_type='migration_based',
                tables=tables
            ))
        
        return schemas
    
    def _analyze_nosql_schemas(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze NoSQL schema definitions."""
        schemas = []
        
        # MongoDB schemas
        mongodb_schemas = self._analyze_mongodb_schemas(file_contents)
        schemas.extend(mongodb_schemas)
        
        # Redis schemas
        redis_schemas = self._analyze_redis_schemas(file_contents)
        schemas.extend(redis_schemas)
        
        return schemas
    
    def _analyze_mongodb_schemas(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze MongoDB schema definitions."""
        collections = []
        
        for file_path, content in file_contents.items():
            if 'mongoose' in content.lower() or 'mongodb' in content.lower():
                mongo_collections = self._parse_mongoose_schemas(content)
                collections.extend(mongo_collections)
        
        if collections:
            return [DatabaseSchema(
                name='mongodb',
                database_type='mongodb',
                tables=collections  # Collections are treated as tables
            )]
        
        return []
    
    def _analyze_redis_schemas(self, file_contents: Dict[str, str]) -> List[DatabaseSchema]:
        """Analyze Redis data structure usage."""
        # Redis doesn't have a fixed schema, but we can analyze usage patterns
        structures = []
        
        for file_path, content in file_contents.items():
            redis_usage = self._parse_redis_usage(content)
            structures.extend(redis_usage)
        
        if structures:
            return [DatabaseSchema(
                name='redis',
                database_type='redis',
                tables=structures,
                metadata={'note': 'Redis structures inferred from usage patterns'}
            )]
        
        return []
    
    # SQL Parsing Methods
    
    def _parse_sql_statements(self, content: str) -> List[Dict[str, Any]]:
        """Parse SQL content into statements."""
        statements = []
        
        # Remove comments
        content = re.sub(r'--.*$', '', content, flags=re.MULTILINE)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Split by semicolons (simplified)
        raw_statements = content.split(';')
        
        for stmt in raw_statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            
            stmt_upper = stmt.upper()
            
            if 'CREATE TABLE' in stmt_upper:
                statements.append({'type': 'CREATE_TABLE', 'content': stmt})
            elif 'CREATE VIEW' in stmt_upper:
                statements.append({'type': 'CREATE_VIEW', 'content': stmt})
            elif 'CREATE PROCEDURE' in stmt_upper or 'CREATE PROC' in stmt_upper:
                statements.append({'type': 'CREATE_PROCEDURE', 'content': stmt})
            elif 'CREATE FUNCTION' in stmt_upper:
                statements.append({'type': 'CREATE_FUNCTION', 'content': stmt})
            else:
                statements.append({'type': 'OTHER', 'content': stmt})
        
        return statements
    
    def _parse_create_table(self, sql: str, database_type: str) -> Optional[DatabaseTable]:
        """Parse CREATE TABLE statement."""
        # Extract table name
        table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([^\s(]+)', sql, re.IGNORECASE)
        if not table_match:
            return None
        
        table_name = table_match.group(1).strip('`"[]')
        
        # Extract column definitions
        # Find the content between first ( and last )
        paren_start = sql.find('(')
        paren_end = sql.rfind(')')
        
        if paren_start == -1 or paren_end == -1:
            return None
        
        columns_section = sql[paren_start + 1:paren_end]
        
        # Parse fields
        fields = self._parse_table_fields(columns_section, database_type)
        
        return DatabaseTable(
            name=table_name,
            fields=fields,
            metadata={'source': 'sql_ddl'}
        )
    
    def _parse_table_fields(self, columns_section: str, database_type: str) -> List[DatabaseField]:
        """Parse table field definitions."""
        fields = []
        
        # Split by commas, but be careful about nested parentheses
        field_definitions = self._split_field_definitions(columns_section)
        
        for field_def in field_definitions:
            field_def = field_def.strip()
            if not field_def or field_def.upper().startswith(('PRIMARY', 'FOREIGN', 'UNIQUE', 'INDEX', 'KEY')):
                continue
            
            field = self._parse_single_field(field_def, database_type)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_single_field(self, field_def: str, database_type: str) -> Optional[DatabaseField]:
        """Parse a single field definition."""
        parts = field_def.split()
        if len(parts) < 2:
            return None
        
        field_name = parts[0].strip('`"[]')
        field_type = parts[1]
        
        # Parse field properties
        field_def_upper = field_def.upper()
        
        nullable = 'NOT NULL' not in field_def_upper
        primary_key = 'PRIMARY KEY' in field_def_upper
        unique = 'UNIQUE' in field_def_upper
        auto_increment = any(keyword in field_def_upper for keyword in ['AUTO_INCREMENT', 'SERIAL', 'IDENTITY'])
        
        # Extract default value
        default_match = re.search(r'DEFAULT\s+([^,\s]+)', field_def, re.IGNORECASE)
        default_value = default_match.group(1) if default_match else None
        
        # Extract foreign key reference
        fk_match = re.search(r'REFERENCES\s+([^\s(]+)', field_def, re.IGNORECASE)
        foreign_key = fk_match.group(1) if fk_match else None
        
        # Normalize data type
        normalized_type = self._normalize_data_type(field_type, database_type)
        
        constraints = []
        if auto_increment:
            constraints.append('AUTO_INCREMENT')
        
        return DatabaseField(
            name=field_name,
            data_type=normalized_type,
            nullable=nullable,
            primary_key=primary_key,
            foreign_key=foreign_key,
            unique=unique,
            default_value=default_value,
            constraints=constraints,
            metadata={'raw_type': field_type}
        )
    
    def _split_field_definitions(self, columns_section: str) -> List[str]:
        """Split field definitions by commas, handling nested parentheses."""
        fields = []
        current_field = ""
        paren_depth = 0
        
        for char in columns_section:
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == ',' and paren_depth == 0:
                fields.append(current_field)
                current_field = ""
                continue
            
            current_field += char
        
        if current_field:
            fields.append(current_field)
        
        return fields
    
    def _normalize_data_type(self, raw_type: str, database_type: str) -> str:
        """Normalize data type to common format."""
        # Remove size specifications
        base_type = re.sub(r'\([^)]*\)', '', raw_type).upper()
        
        # Map to normalized type
        type_map = self.type_mappings.get(database_type, {})
        return type_map.get(base_type, base_type.lower())
    
    # ORM Parsing Methods
    
    def _parse_django_models(self, content: str, file_path: str) -> List[DatabaseTable]:
        """Parse Django model definitions."""
        tables = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if (isinstance(node, ast.ClassDef) and 
                    any(isinstance(base, ast.Attribute) and base.attr == 'Model' 
                        for base in node.bases if isinstance(base, ast.Attribute))):
                    
                    table = self._parse_django_model_class(node)
                    if table:
                        tables.append(table)
        
        except SyntaxError:
            # Fallback to regex parsing
            tables = self._parse_django_models_regex(content)
        
        return tables
    
    def _parse_django_model_class(self, class_node: ast.ClassDef) -> Optional[DatabaseTable]:
        """Parse a Django model class."""
        table_name = class_node.name.lower()
        fields = []
        
        for node in class_node.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    field_name = target.id
                    
                    # Skip Meta class and methods
                    if field_name.startswith('_') or field_name in ['Meta', 'objects']:
                        continue
                    
                    field = self._parse_django_field(field_name, node.value)
                    if field:
                        fields.append(field)
        
        return DatabaseTable(
            name=table_name,
            fields=fields,
            metadata={'source': 'django_model', 'model_class': class_node.name}
        )
    
    def _parse_django_field(self, field_name: str, value_node: ast.AST) -> Optional[DatabaseField]:
        """Parse a Django model field."""
        if not isinstance(value_node, ast.Call):
            return None
        
        # Get field type
        field_type = 'unknown'
        if isinstance(value_node.func, ast.Attribute):
            field_type = value_node.func.attr
        elif isinstance(value_node.func, ast.Name):
            field_type = value_node.func.id
        
        # Parse field arguments
        nullable = True
        primary_key = False
        unique = False
        default_value = None
        
        for keyword in value_node.keywords:
            if keyword.arg == 'null':
                nullable = isinstance(keyword.value, ast.Constant) and keyword.value.value
            elif keyword.arg == 'primary_key':
                primary_key = isinstance(keyword.value, ast.Constant) and keyword.value.value
            elif keyword.arg == 'unique':
                unique = isinstance(keyword.value, ast.Constant) and keyword.value.value
            elif keyword.arg == 'default':
                if isinstance(keyword.value, ast.Constant):
                    default_value = str(keyword.value.value)
        
        # Map Django field types to normalized types
        django_type_map = {
            'CharField': 'string',
            'TextField': 'text',
            'IntegerField': 'integer',
            'BigIntegerField': 'bigint',
            'FloatField': 'float',
            'DecimalField': 'decimal',
            'DateField': 'date',
            'DateTimeField': 'datetime',
            'BooleanField': 'boolean',
            'ForeignKey': 'integer',  # FK reference
            'OneToOneField': 'integer',
            'ManyToManyField': 'relation'
        }
        
        normalized_type = django_type_map.get(field_type, field_type.lower())
        
        return DatabaseField(
            name=field_name,
            data_type=normalized_type,
            nullable=nullable,
            primary_key=primary_key,
            unique=unique,
            default_value=default_value,
            metadata={'django_field_type': field_type}
        )
    
    def _parse_django_models_regex(self, content: str) -> List[DatabaseTable]:
        """Parse Django models using regex (fallback)."""
        tables = []
        
        # Find model classes
        class_pattern = r'class\s+(\w+)\s*\([^)]*Model[^)]*\):'
        
        for match in re.finditer(class_pattern, content):
            model_name = match.group(1)
            class_start = match.end()
            
            # Find class body (simplified)
            lines = content[class_start:].split('\n')
            class_body = []
            indent_level = None
            
            for line in lines:
                if line.strip() == '':
                    continue
                
                current_indent = len(line) - len(line.lstrip())
                
                if indent_level is None:
                    indent_level = current_indent
                elif current_indent <= indent_level and line.strip():
                    break
                
                class_body.append(line)
            
            # Parse fields from class body
            fields = self._parse_django_fields_regex('\n'.join(class_body))
            
            if fields:
                tables.append(DatabaseTable(
                    name=model_name.lower(),
                    fields=fields,
                    metadata={'source': 'django_model_regex', 'model_class': model_name}
                ))
        
        return tables
    
    def _parse_django_fields_regex(self, class_body: str) -> List[DatabaseField]:
        """Parse Django fields using regex."""
        fields = []
        
        field_pattern = r'(\w+)\s*=\s*models\.(\w+)\('
        
        for match in re.finditer(field_pattern, class_body):
            field_name = match.group(1)
            field_type = match.group(2)
            
            if field_name.startswith('_') or field_name in ['Meta', 'objects']:
                continue
            
            # Map field type
            django_type_map = {
                'CharField': 'string',
                'TextField': 'text',
                'IntegerField': 'integer',
                'DateTimeField': 'datetime',
                'BooleanField': 'boolean',
                'ForeignKey': 'integer'
            }
            
            normalized_type = django_type_map.get(field_type, field_type.lower())
            
            fields.append(DatabaseField(
                name=field_name,
                data_type=normalized_type,
                metadata={'django_field_type': field_type}
            ))
        
        return fields
    
    # Helper Methods
    
    def _extract_schema_name(self, file_path: str) -> str:
        """Extract schema name from file path."""
        path = Path(file_path)
        
        # Try to get schema from directory structure
        parts = path.parts
        
        if 'schemas' in parts:
            idx = parts.index('schemas')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        
        if 'database' in parts:
            idx = parts.index('database')
            if idx + 1 < len(parts):
                return parts[idx + 1]
        
        # Default to filename without extension
        return path.stem
    
    def _parse_create_view(self, sql: str) -> Dict[str, Any]:
        """Parse CREATE VIEW statement."""
        view_match = re.search(r'CREATE\s+VIEW\s+([^\s(]+)', sql, re.IGNORECASE)
        if not view_match:
            return {}
        
        return {
            'name': view_match.group(1).strip('`"[]'),
            'definition': sql,
            'type': 'view'
        }
    
    def _parse_create_procedure(self, sql: str) -> Dict[str, Any]:
        """Parse CREATE PROCEDURE statement."""
        proc_match = re.search(r'CREATE\s+PROCEDURE\s+([^\s(]+)', sql, re.IGNORECASE)
        if not proc_match:
            return {}
        
        return {
            'name': proc_match.group(1).strip('`"[]'),
            'definition': sql,
            'type': 'procedure'
        }
    
    def _parse_create_function(self, sql: str) -> Dict[str, Any]:
        """Parse CREATE FUNCTION statement."""
        func_match = re.search(r'CREATE\s+FUNCTION\s+([^\s(]+)', sql, re.IGNORECASE)
        if not func_match:
            return {}
        
        return {
            'name': func_match.group(1).strip('`"[]'),
            'definition': sql,
            'type': 'function'
        }
    
    # Placeholder methods for other ORM and NoSQL parsers
    def _parse_sqlalchemy_models(self, content: str, file_path: str) -> List[DatabaseTable]:
        """Parse SQLAlchemy models (placeholder)."""
        # Implementation would be similar to Django but for SQLAlchemy syntax
        return []
    
    def _parse_sequelize_models(self, content: str, file_path: str) -> List[DatabaseTable]:
        """Parse Sequelize models (placeholder)."""
        # Implementation for JavaScript/TypeScript Sequelize models
        return []
    
    def _parse_django_migration(self, content: str) -> List[DatabaseTable]:
        """Parse Django migration files (placeholder)."""
        return []
    
    def _parse_rails_migration(self, content: str) -> List[DatabaseTable]:
        """Parse Rails migration files (placeholder)."""
        return []
    
    def _parse_laravel_migration(self, content: str) -> List[DatabaseTable]:
        """Parse Laravel migration files (placeholder)."""
        return []
    
    def _parse_mongoose_schemas(self, content: str) -> List[DatabaseTable]:
        """Parse Mongoose schemas (placeholder)."""
        return []
    
    def _parse_redis_usage(self, content: str) -> List[DatabaseTable]:
        """Parse Redis usage patterns (placeholder)."""
        return []
    
    def generate_schema_documentation(self, schema: DatabaseSchema) -> Dict[str, Any]:
        """Generate comprehensive schema documentation."""
        return {
            'overview': {
                'schema_name': schema.name,
                'database_type': schema.database_type,
                'total_tables': len(schema.tables),
                'total_fields': sum(len(table.fields) for table in schema.tables),
                'relationships': len(schema.get_relationships())
            },
            'tables': [
                {
                    'name': table.name,
                    'field_count': len(table.fields),
                    'primary_keys': table.primary_keys,
                    'foreign_keys': table.foreign_keys,
                    'indexes': len(table.indexes),
                    'fields': [
                        {
                            'name': field.name,
                            'type': field.data_type,
                            'nullable': field.nullable,
                            'constraints': field.constraints
                        }
                        for field in table.fields
                    ]
                }
                for table in schema.tables
            ],
            'relationships': schema.get_relationships(),
            'views': len(schema.views),
            'procedures': len(schema.procedures),
            'functions': len(schema.functions),
            'metadata': schema.metadata
        }
