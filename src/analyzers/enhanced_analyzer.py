"""
Enhanced Analyzer Integration

Integrates all specialized analyzers (MCP, project classification, etc.)
into the main analysis workflow.
"""

import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..parsers.mcp_analyzer import MCPServerAnalyzer, MCPServerInfo
from .project_classifier import ProjectClassifier, ProjectClassification

logger = logging.getLogger(__name__)


class EnhancedAnalyzer:
    """
    Enhanced analyzer that uses specialized analyzers based on project type.
    """
    
    def __init__(self):
        self.mcp_analyzer = MCPServerAnalyzer()
        self.project_classifier = ProjectClassifier()
    
    def analyze(
        self,
        codebase_path: str,
        file_contents: Dict[str, str],
        dependencies: List[Dict[str, Any]],
        project_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform enhanced analysis with specialized analyzers.
        
        Args:
            codebase_path: Root path of the codebase
            file_contents: Dictionary mapping file paths to contents
            dependencies: List of project dependencies
            project_structure: Project directory structure
            
        Returns:
            Enhanced analysis results including classification and specialized analysis
        """
        logger.info("Starting enhanced analysis...")
        
        results = {
            'codebase_path': codebase_path,
            'classification': None,
            'mcp_server_info': None,
            'specialized_analysis': {}
        }
        
        # Step 1: Classify the project
        classification = self.project_classifier.classify(
            file_contents=file_contents,
            dependencies=dependencies,
            project_structure=project_structure
        )
        results['classification'] = classification.to_dict()
        
        logger.info(
            f"Project classified as: {classification.primary_type} "
            f"(confidence: {classification.confidence:.2f})"
        )
        
        # Step 2: Run specialized analyzers based on classification
        if classification.primary_type == 'mcp_server':
            logger.info("Running MCP server analysis...")
            mcp_info = self.mcp_analyzer.analyze(codebase_path, file_contents)
            if mcp_info:
                results['mcp_server_info'] = mcp_info.to_dict()
                logger.info(f"Found {len(mcp_info.tools)} MCP tools")
        
        # Step 3: Additional specialized analysis for other types
        elif classification.primary_type == 'rest_api':
            # Future: Add REST API analyzer
            results['specialized_analysis']['rest_api'] = self._analyze_rest_api(
                file_contents
            )
        
        elif classification.primary_type == 'web_scraper':
            # Future: Add scraper analyzer
            results['specialized_analysis']['scraper'] = self._analyze_scraper(
                file_contents
            )
        
        return results
    
    def _analyze_rest_api(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Placeholder for REST API analysis."""
        # TODO: Implement endpoint extraction
        return {
            'endpoints': [],
            'authentication': None
        }
    
    def _analyze_scraper(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """Placeholder for scraper analysis."""
        # TODO: Implement scraper pattern analysis
        return {
            'target_sites': [],
            'extraction_methods': []
        }


def perform_enhanced_analysis(
    codebase_path: str,
    file_contents: Dict[str, str],
    dependencies: List[Dict[str, Any]],
    project_structure: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function for enhanced analysis.
    
    Args:
        codebase_path: Root path of the codebase
        file_contents: Dictionary mapping file paths to contents
        dependencies: List of project dependencies
        project_structure: Project directory structure
        
    Returns:
        Enhanced analysis results
    """
    analyzer = EnhancedAnalyzer()
    return analyzer.analyze(codebase_path, file_contents, dependencies, project_structure)
