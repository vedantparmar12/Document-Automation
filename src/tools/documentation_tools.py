"""
Documentation tools for MCP server

This module implements the main tool functionality for the Document Automation MCP server,
providing methods for analyzing codebases and generating documentation.
"""

import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.types import TextContent

from src.analyzers.codebase_analyzer import CodebaseAnalyzer
from src.generators.documentation_generator import DocumentationGenerator
from src.generators.professional_doc_generator import ProfessionalDocumentationGenerator as EnhancedDocumentationGenerator
from src.types import (
    CodeAnalysisResult, 
    DocumentationFormat,
    create_success_response,
    create_error_response
)
from src.security.validation import validate_analysis_request, log_security_event

logger = logging.getLogger(__name__)

class DocumentationTools:
    """
    Main documentation tools class that implements MCP tool functionality.
    
    This class provides the core functionality for analyzing codebases and generating
    comprehensive documentation from the analysis results.
    """
    
    def __init__(self):
        """Initialize the documentation tools."""
        self.analysis_cache = {}  # In-memory cache for analysis results
        self.doc_generator = DocumentationGenerator()
        self.enhanced_doc_generator = EnhancedDocumentationGenerator()
    
    async def analyze_codebase(
        self,
        path: str,
        source_type: str,
        include_dependencies: bool = True
    ) -> List[TextContent]:
        """
        Analyze a codebase and extract its structure, dependencies, and components.
        
        Args:
            path: Local folder path or GitHub repository URL
            source_type: Type of source to analyze ('local' or 'github')
            include_dependencies: Whether to analyze dependencies
            
        Returns:
            List of TextContent with analysis results
        """
        try:
            logger.info(f"Starting codebase analysis for {source_type}: {path}")
            
            # Validate the request
            validation_result = validate_analysis_request(path, source_type)
            if not validation_result.is_valid:
                log_security_event("VALIDATION_FAILED", f"Path: {path}, Type: {source_type}")
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Validation failed: {validation_result.error}"
                    ).content[0].text
                )]
            
            # Create analyzer
            analyzer = CodebaseAnalyzer(
                path=path,
                source_type=source_type,
                config={
                    'include_dependencies': include_dependencies
                }
            )
            
            # Perform analysis
            analysis_result = await analyzer.analyze()
            
            if analysis_result.success:
                # Cache the analysis result
                self.analysis_cache[analyzer.analysis_id] = analysis_result.data
                # Also cache the project root and URL for enhanced documentation
                self.analysis_cache[f"{analyzer.analysis_id}_root"] = analyzer.working_path
                self.analysis_cache[f"{analyzer.analysis_id}_url"] = path
                
                # Create response
                response_data = {
                    'analysis_id': analyzer.analysis_id,
                    'summary': analyzer.get_analysis_summary(),
                    'result': analysis_result.data,
                    'duration': analysis_result.duration
                }
                
                return [TextContent(
                    type="text",
                    text=create_success_response(
                        f"Codebase analysis completed successfully",
                        response_data
                    ).content[0].text
                )]
            else:
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Analysis failed: {analysis_result.error}"
                    ).content[0].text
                )]
        
        except Exception as e:
            logger.error(f"Error in analyze_codebase: {str(e)}")
            return [TextContent(
                type="text",
                text=create_error_response(
                    f"Analysis failed: {str(e)}"
                ).content[0].text
            )]
    
    async def generate_documentation(
        self,
        analysis_id: str,
        format: str = "markdown",
        include_api_docs: bool = True,
        include_examples: bool = True,
        include_architecture: bool = True
    ) -> List[TextContent]:
        """
        Generate comprehensive documentation from analyzed codebase structure.
        
        Args:
            analysis_id: ID of the previously analyzed codebase
            format: Output format for documentation ('markdown', 'html', 'rst', 'pdf')
            include_api_docs: Whether to include API documentation
            include_examples: Whether to include code examples
            include_architecture: Whether to include architecture diagrams
            
        Returns:
            List of TextContent with generated documentation
        """
        try:
            logger.info(f"Generating {format} documentation for analysis {analysis_id}")
            
            # Check if analysis exists in cache
            if analysis_id not in self.analysis_cache:
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Analysis ID {analysis_id} not found. Please run analyze_codebase first."
                    ).content[0].text
                )]
            
            # Get analysis result
            analysis_data = self.analysis_cache[analysis_id]
            
            # Convert to CodeAnalysisResult object
            analysis_result = CodeAnalysisResult(**analysis_data)
            
            # Check if enhanced format is requested (we'll use a special format value)
            if format == "enhanced_markdown":
                # Use enhanced generator for better formatting
                output_path = f"docs/documentation_{analysis_id}_enhanced.md"
                os.makedirs("docs", exist_ok=True)
                
                doc_content = self.enhanced_doc_generator.generate_documentation(
                    analysis_result=analysis_data,
                    project_root=self.analysis_cache.get(f"{analysis_id}_root", ""),
                    output_path=output_path,
                    repo_url=self.analysis_cache.get(f"{analysis_id}_url", ""),
                    include_api_docs=include_api_docs,
                    include_architecture=include_architecture
                )
                
                doc_result = type('DocumentationResult', (), {
                    'content': doc_content,
                    'metadata': {
                        'format': 'enhanced_markdown',
                        'file_path': output_path
                    }
                })()
            else:
                # Use standard generator
                doc_result = await self.doc_generator.generate_documentation(
                    analysis_result=analysis_result,
                    format=DocumentationFormat(format),
                    include_api_docs=include_api_docs,
                    include_examples=include_examples,
                    include_architecture=include_architecture
                )
            
            # Create response
            response_data = {
                'analysis_id': analysis_id,
                'format': format,
                'content': doc_result.content,
                'metadata': doc_result.metadata
            }
            
            return [TextContent(
                type="text",
                text=create_success_response(
                    f"Documentation generated successfully in {format} format",
                    response_data
                ).content[0].text
            )]
        
        except Exception as e:
            logger.error(f"Error in generate_documentation: {str(e)}")
            return [TextContent(
                type="text",
                text=create_error_response(
                    f"Documentation generation failed: {str(e)}"
                ).content[0].text
            )]
    
    async def list_project_structure(
        self,
        path: str,
        source_type: str,
        max_depth: int = 5
    ) -> List[TextContent]:
        """
        Get a detailed project structure with file types and sizes.
        
        Args:
            path: Local folder path or GitHub repository URL
            source_type: Type of source to analyze ('local' or 'github')
            max_depth: Maximum depth to traverse
            
        Returns:
            List of TextContent with project structure
        """
        try:
            logger.info(f"Listing project structure for {source_type}: {path}")
            
            # Validate the request
            validation_result = validate_analysis_request(path, source_type)
            if not validation_result.is_valid:
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Validation failed: {validation_result.error}"
                    ).content[0].text
                )]
            
            # Create analyzer
            analyzer = CodebaseAnalyzer(
                path=path,
                source_type=source_type,
                config={'max_depth': max_depth}
            )
            
            # Prepare codebase and analyze structure
            await analyzer._prepare_codebase()
            project_structure = await analyzer._analyze_structure()
            
            # Format structure for display
            structure_text = self._format_structure_for_display(project_structure)
            
            response_data = {
                'path': path,
                'source_type': source_type,
                'max_depth': max_depth,
                'structure': structure_text
            }
            
            return [TextContent(
                type="text",
                text=create_success_response(
                    f"Project structure retrieved successfully",
                    response_data
                ).content[0].text
            )]
        
        except Exception as e:
            logger.error(f"Error in list_project_structure: {str(e)}")
            return [TextContent(
                type="text",
                text=create_error_response(
                    f"Failed to list project structure: {str(e)}"
                ).content[0].text
            )]
    
    async def extract_api_endpoints(
        self,
        path: str,
        source_type: str,
        framework: str = "auto"
    ) -> List[TextContent]:
        """
        Extract and document API endpoints from web frameworks.
        
        Args:
            path: Local folder path or GitHub repository URL
            source_type: Type of source to analyze ('local' or 'github')
            framework: Web framework to analyze ('auto', 'fastapi', 'flask', 'django', 'express', 'spring')
            
        Returns:
            List of TextContent with API endpoints
        """
        try:
            logger.info(f"Extracting API endpoints for {source_type}: {path} (framework: {framework})")
            
            # Validate the request
            validation_result = validate_analysis_request(path, source_type)
            if not validation_result.is_valid:
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Validation failed: {validation_result.error}"
                    ).content[0].text
                )]
            
            # Create analyzer
            analyzer = CodebaseAnalyzer(
                path=path,
                source_type=source_type,
                config={'framework': framework}
            )
            
            # Prepare codebase and extract endpoints
            await analyzer._prepare_codebase()
            api_endpoints = await analyzer._extract_api_endpoints()
            
            response_data = {
                'path': path,
                'source_type': source_type,
                'framework': framework,
                'endpoints': api_endpoints,
                'total_endpoints': len(api_endpoints)
            }
            
            return [TextContent(
                type="text",
                text=create_success_response(
                    f"Found {len(api_endpoints)} API endpoints",
                    response_data
                ).content[0].text
            )]
        
        except Exception as e:
            logger.error(f"Error in extract_api_endpoints: {str(e)}")
            return [TextContent(
                type="text",
                text=create_error_response(
                    f"Failed to extract API endpoints: {str(e)}"
                ).content[0].text
            )]
    
    async def analyze_dependencies(
        self,
        path: str,
        source_type: str,
        include_dev_dependencies: bool = False
    ) -> List[TextContent]:
        """
        Analyze project dependencies and generate dependency documentation.
        
        Args:
            path: Local folder path or GitHub repository URL
            source_type: Type of source to analyze ('local' or 'github')
            include_dev_dependencies: Whether to include development dependencies
            
        Returns:
            List of TextContent with dependency analysis
        """
        try:
            logger.info(f"Analyzing dependencies for {source_type}: {path}")
            
            # Validate the request
            validation_result = validate_analysis_request(path, source_type)
            if not validation_result.is_valid:
                return [TextContent(
                    type="text",
                    text=create_error_response(
                        f"Validation failed: {validation_result.error}"
                    ).content[0].text
                )]
            
            # Create analyzer
            analyzer = CodebaseAnalyzer(
                path=path,
                source_type=source_type,
                config={'include_dev_dependencies': include_dev_dependencies}
            )
            
            # Prepare codebase and analyze dependencies
            await analyzer._prepare_codebase()
            dependencies = await analyzer._analyze_dependencies()
            
            response_data = {
                'path': path,
                'source_type': source_type,
                'include_dev_dependencies': include_dev_dependencies,
                'dependencies': dependencies,
                'total_dependencies': len(dependencies)
            }
            
            return [TextContent(
                type="text",
                text=create_success_response(
                    f"Found {len(dependencies)} dependencies",
                    response_data
                ).content[0].text
            )]
        
        except Exception as e:
            logger.error(f"Error in analyze_dependencies: {str(e)}")
            return [TextContent(
                type="text",
                text=create_error_response(
                    f"Failed to analyze dependencies: {str(e)}"
                ).content[0].text
            )]
    
    def _format_structure_for_display(self, directory_info) -> str:
        """Format directory structure for display."""
        def format_directory(dir_info, level=0):
            indent = "  " * level
            result = [f"{indent}📁 {dir_info.name}/"]
            
            # Add files
            for file_info in dir_info.files:
                file_indent = "  " * (level + 1)
                file_icon = self._get_file_icon(file_info.type)
                size_kb = file_info.size / 1024
                result.append(f"{file_indent}{file_icon} {file_info.name} ({size_kb:.1f} KB)")
            
            # Add subdirectories
            for subdir in dir_info.subdirectories:
                result.extend(format_directory(subdir, level + 1))
            
            return result
        
        return "\n".join(format_directory(directory_info))
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get appropriate emoji icon for file type."""
        icons = {
            'python': '🐍',
            'javascript': '📜',
            'typescript': '📘',
            'java': '☕',
            'cpp': '⚙️',
            'c': '⚙️',
            'go': '🏃',
            'rust': '🦀',
            'ruby': '💎',
            'php': '🐘',
            'html': '🌐',
            'css': '🎨',
            'json': '📋',
            'yaml': '📋',
            'markdown': '📝',
            'text': '📄',
            'sql': '🗃️',
            'dockerfile': '🐳',
            'shell': '🐚',
            'unknown': '📄'
        }
        return icons.get(file_type, '📄')
    
    def get_cached_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis result by ID."""
        return self.analysis_cache.get(analysis_id)
    
    def clear_cache(self):
        """Clear analysis cache."""
        self.analysis_cache.clear()
        logger.info("Analysis cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'total_analyses': len(self.analysis_cache),
            'analysis_ids': list(self.analysis_cache.keys())
        }
