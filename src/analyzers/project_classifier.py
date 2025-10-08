"""
Project Classifier

Semantic classification of projects based on code analysis, not just dependencies.
Replaces pattern-based classification with intelligent understanding.
"""

import logging
import re
from typing import Dict, List, Any, Set, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ProjectClassification:
    """Result of project classification."""
    primary_type: str  # mcp_server, rest_api, web_scraper, cli_tool, library, etc.
    secondary_types: List[str]  # Additional classifications
    confidence: float  # 0.0 to 1.0
    frameworks: List[str]  # Detected frameworks
    protocols: List[str]  # HTTP, WebSocket, MCP, gRPC, etc.
    domain: Optional[str]  # Business domain if detectable
    purpose: str  # High-level purpose description
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'primary_type': self.primary_type,
            'secondary_types': self.secondary_types,
            'confidence': self.confidence,
            'frameworks': self.frameworks,
            'protocols': self.protocols,
            'domain': self.domain,
            'purpose': self.purpose
        }


class ProjectClassifier:
    """Intelligent project classifier using semantic analysis."""
    
    def __init__(self):
        self.project_types = {
            'mcp_server': {
                'indicators': [
                    'from mcp.server import Server',
                    'from mcp import Server',
                    '@app.list_tools',
                    '@server.list_tools',
                    'stdio_server',
                    'sse_server'
                ],
                'weight': 10,
                'description': 'Model Context Protocol (MCP) Server'
            },
            'rest_api': {
                'indicators': [
                    '@app.route',
                    '@router.get',
                    '@router.post',
                    'FastAPI(',
                    'Flask(__name__)',
                    'APIRouter()',
                    'create_app()'
                ],
                'weight': 8,
                'description': 'REST API Server'
            },
            'graphql_api': {
                'indicators': [
                    'graphene',
                    'strawberry.field',
                    '@strawberry.type',
                    'GraphQLSchema',
                    'Query(',
                    'Mutation('
                ],
                'weight': 9,
                'description': 'GraphQL API Server'
            },
            'web_scraper': {
                'indicators': [
                    'BeautifulSoup',
                    'scrapy.Spider',
                    'selenium.webdriver',
                    'playwright',
                    'requests.get',
                    'aiohttp.ClientSession'
                ],
                'weight': 7,
                'description': 'Web Scraping Tool'
            },
            'cli_tool': {
                'indicators': [
                    'argparse.ArgumentParser',
                    'click.command',
                    'typer.Typer',
                    'if __name__ == "__main__"',
                    'sys.argv'
                ],
                'weight': 6,
                'description': 'Command-Line Interface Tool'
            },
            'data_pipeline': {
                'indicators': [
                    'airflow.DAG',
                    'prefect.flow',
                    'luigi.Task',
                    'dask.dataframe',
                    'spark.SparkContext'
                ],
                'weight': 8,
                'description': 'Data Pipeline/ETL Tool'
            },
            'ml_model': {
                'indicators': [
                    'tensorflow.keras',
                    'torch.nn',
                    'sklearn.model',
                    'model.fit',
                    'model.predict',
                    'train_test_split'
                ],
                'weight': 8,
                'description': 'Machine Learning Model'
            },
            'bot': {
                'indicators': [
                    'discord.Client',
                    'telebot.TeleBot',
                    'slack_sdk',
                    'on_message',
                    'send_message'
                ],
                'weight': 8,
                'description': 'Bot/Chatbot Application'
            },
            'library': {
                'indicators': [
                    'setup.py',
                    '__init__.py',
                    'from .', 
                    'import .'
                ],
                'weight': 5,
                'description': 'Python Library/Package'
            }
        }
        
        self.framework_patterns = {
            'FastAPI': r'from fastapi import|FastAPI\(',
            'Flask': r'from flask import|Flask\(__name__\)',
            'Django': r'from django|django.conf',
            'Scrapy': r'import scrapy|scrapy\.Spider',
            'Selenium': r'from selenium|selenium\.webdriver',
            'BeautifulSoup': r'from bs4|BeautifulSoup',
            'MCP': r'from mcp|mcp\.server',
            'SQLAlchemy': r'from sqlalchemy|sqlalchemy\.orm',
            'Pydantic': r'from pydantic|BaseModel',
            'Typer': r'import typer|typer\.Typer',
            'Click': r'import click|@click\.command',
        }
        
        self.protocol_patterns = {
            'HTTP/REST': [r'requests\.', r'@app\.route', r'@router\.(get|post|put|delete)'],
            'WebSocket': [r'websocket', r'ws://', r'wss://'],
            'MCP': [r'from mcp', r'stdio_server', r'sse_server'],
            'gRPC': [r'import grpc', r'grpc\.server'],
            'GraphQL': [r'graphene', r'strawberry', r'GraphQLSchema'],
        }
    
    def classify(
        self,
        file_contents: Dict[str, str],
        dependencies: List[Dict[str, Any]],
        project_structure: Dict[str, Any]
    ) -> ProjectClassification:
        """
        Classify a project based on code analysis.
        
        Args:
            file_contents: Dictionary of file_path: content
            dependencies: List of project dependencies
            project_structure: Project directory structure
            
        Returns:
            ProjectClassification with detailed classification
        """
        logger.info("Classifying project...")
        
        # Combine all code for analysis
        all_code = self._get_primary_code(file_contents)
        
        # Score each project type
        type_scores = self._score_project_types(all_code, file_contents)
        
        # Detect frameworks
        frameworks = self._detect_frameworks(all_code)
        
        # Detect protocols
        protocols = self._detect_protocols(all_code)
        
        # Detect domain
        domain = self._detect_domain(file_contents, dependencies)
        
        # Get top classifications
        primary_type, confidence = self._get_primary_type(type_scores)
        secondary_types = self._get_secondary_types(type_scores, primary_type)
        
        # Generate purpose description
        purpose = self._generate_purpose(primary_type, frameworks, domain)
        
        return ProjectClassification(
            primary_type=primary_type,
            secondary_types=secondary_types,
            confidence=confidence,
            frameworks=frameworks,
            protocols=protocols,
            domain=domain,
            purpose=purpose
        )
    
    def _get_primary_code(self, file_contents: Dict[str, str]) -> str:
        """Get the most relevant code files for classification."""
        # Prioritize main entry points
        priority_files = []
        
        for file_path, content in file_contents.items():
            if not file_path.endswith('.py'):
                continue
            
            filename = Path(file_path).name.lower()
            
            # High priority files
            if filename in ['server.py', 'main.py', 'app.py', '__main__.py']:
                priority_files.insert(0, content)
            # Medium priority
            elif filename in ['__init__.py', 'cli.py', 'api.py']:
                priority_files.append(content)
        
        # If we have priority files, use them
        if priority_files:
            return '\n'.join(priority_files)
        
        # Otherwise, combine all Python files
        return '\n'.join(
            content for path, content in file_contents.items()
            if path.endswith('.py')
        )
    
    def _score_project_types(
        self,
        code: str,
        file_contents: Dict[str, str]
    ) -> Dict[str, float]:
        """Score each project type based on indicators."""
        scores = {}
        
        for type_name, type_info in self.project_types.items():
            score = 0.0
            indicators_found = 0
            
            for indicator in type_info['indicators']:
                if indicator in code:
                    score += type_info['weight']
                    indicators_found += 1
            
            # Boost score based on number of indicators
            if indicators_found > 1:
                score *= (1 + indicators_found * 0.1)
            
            scores[type_name] = score
        
        return scores
    
    def _get_primary_type(self, scores: Dict[str, float]) -> Tuple[str, float]:
        """Get the primary project type and confidence."""
        if not scores or max(scores.values()) == 0:
            return 'unknown', 0.0
        
        # Get type with highest score
        primary_type = max(scores, key=scores.get)
        max_score = scores[primary_type]
        
        # Calculate confidence (normalize to 0-1)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        return primary_type, confidence
    
    def _get_secondary_types(
        self,
        scores: Dict[str, float],
        primary_type: str
    ) -> List[str]:
        """Get secondary project types."""
        threshold = scores.get(primary_type, 0) * 0.3  # 30% of primary score
        
        secondary = [
            type_name for type_name, score in scores.items()
            if score >= threshold and type_name != primary_type and score > 0
        ]
        
        # Sort by score
        secondary.sort(key=lambda x: scores[x], reverse=True)
        
        return secondary[:3]  # Return top 3
    
    def _detect_frameworks(self, code: str) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = []
        
        for framework, pattern in self.framework_patterns.items():
            if re.search(pattern, code):
                frameworks.append(framework)
        
        return frameworks
    
    def _detect_protocols(self, code: str) -> List[str]:
        """Detect communication protocols used."""
        protocols = []
        
        for protocol, patterns in self.protocol_patterns.items():
            if any(re.search(pattern, code) for pattern in patterns):
                protocols.append(protocol)
        
        return protocols
    
    def _detect_domain(
        self,
        file_contents: Dict[str, str],
        dependencies: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Try to detect the business/application domain."""
        # Look for domain-specific keywords in filenames and code
        domain_keywords = {
            'airbnb': 'Travel & Accommodation',
            'hotel': 'Travel & Accommodation',
            'booking': 'Reservation Systems',
            'payment': 'Financial Services',
            'stripe': 'Payment Processing',
            'ecommerce': 'E-Commerce',
            'shop': 'E-Commerce',
            'social': 'Social Media',
            'chat': 'Communication',
            'email': 'Communication',
            'weather': 'Weather Services',
            'news': 'News & Media',
            'finance': 'Financial Services',
            'stock': 'Financial Markets',
            'analytics': 'Data Analytics',
            'monitoring': 'System Monitoring',
            'healthcare': 'Healthcare',
            'education': 'Education',
        }
        
        # Check file paths and content
        all_text = ' '.join(file_contents.keys()) + ' '.join(file_contents.values())
        all_text = all_text.lower()
        
        for keyword, domain in domain_keywords.items():
            if keyword in all_text:
                return domain
        
        return None
    
    def _generate_purpose(
        self,
        primary_type: str,
        frameworks: List[str],
        domain: Optional[str]
    ) -> str:
        """Generate a purpose description."""
        type_descriptions = {
            'mcp_server': 'provides AI assistants with structured tools and resources through the Model Context Protocol',
            'rest_api': 'provides HTTP-based API endpoints for client applications',
            'graphql_api': 'provides a GraphQL interface for flexible data querying',
            'web_scraper': 'extracts and collects data from web sources',
            'cli_tool': 'provides command-line interface for user interactions',
            'data_pipeline': 'processes and transforms data through automated workflows',
            'ml_model': 'performs machine learning predictions and analysis',
            'bot': 'provides automated interactions through messaging platforms',
            'library': 'provides reusable functionality for other applications',
            'unknown': 'provides software functionality'
        }
        
        base_purpose = type_descriptions.get(primary_type, type_descriptions['unknown'])
        
        # Add domain context if available
        if domain:
            base_purpose = f"in the {domain} domain, {base_purpose}"
        
        # Add framework info
        if frameworks:
            framework_str = ', '.join(frameworks[:2])  # Top 2 frameworks
            base_purpose = f"built with {framework_str}, {base_purpose}"
        
        return base_purpose


def classify_project(
    file_contents: Dict[str, str],
    dependencies: List[Dict[str, Any]],
    project_structure: Dict[str, Any]
) -> ProjectClassification:
    """
    Convenience function to classify a project.
    
    Args:
        file_contents: Dictionary mapping file paths to contents
        dependencies: List of project dependencies
        project_structure: Project directory structure
        
    Returns:
        ProjectClassification with detailed classification
    """
    classifier = ProjectClassifier()
    return classifier.classify(file_contents, dependencies, project_structure)
