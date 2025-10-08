"""
Types and schemas for Document Automation MCP Server

Following the design patterns from the original TypeScript MCP server.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

# User context passed through OAuth (similar to original Props)
class UserProps(BaseModel):
    login: str
    name: str
    email: str
    access_token: str

# Extended environment with OAuth provider
class ExtendedEnv(BaseModel):
    OAUTH_PROVIDER: Optional[Any] = None
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    COOKIE_ENCRYPTION_KEY: str
    SENTRY_DSN: Optional[str] = None
    NODE_ENV: str = "development"

# Analysis source types
class SourceType(str, Enum):
    LOCAL = "local"
    GITHUB = "github"

# Documentation formats
class DocumentationFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML = "html"
    RST = "rst"
    PDF = "pdf"

# MCP tool schemas using Pydantic
class AnalyzeCodebaseSchema(BaseModel):
    path: str = Field(..., description="Local folder path or GitHub repository URL")
    source_type: SourceType = Field(..., description="Type of source to analyze")
    include_dependencies: bool = Field(default=True, description="Whether to analyze dependencies")

class GenerateDocumentationSchema(BaseModel):
    analysis_id: str = Field(..., description="ID of the previously analyzed codebase")
    format: DocumentationFormat = Field(default=DocumentationFormat.MARKDOWN, description="Output format for documentation")
    include_api_docs: bool = Field(default=True, description="Whether to include API documentation")
    include_examples: bool = Field(default=True, description="Whether to include code examples")
    include_architecture: bool = Field(default=True, description="Whether to include architecture diagrams")

class ListProjectStructureSchema(BaseModel):
    path: str = Field(..., description="Local folder path or GitHub repository URL")
    source_type: SourceType = Field(..., description="Type of source to analyze")
    max_depth: int = Field(default=5, description="Maximum depth to traverse")

class ExtractApiEndpointsSchema(BaseModel):
    path: str = Field(..., description="Local folder path or GitHub repository URL")
    source_type: SourceType = Field(..., description="Type of source to analyze")
    framework: str = Field(default="auto", description="Web framework to analyze")

class AnalyzeDependenciesSchema(BaseModel):
    path: str = Field(..., description="Local folder path or GitHub repository URL")
    source_type: SourceType = Field(..., description="Type of source to analyze")
    include_dev_dependencies: bool = Field(default=False, description="Whether to include development dependencies")

# MCP response types
class McpTextContent(BaseModel):
    type: str = "text"
    text: str
    is_error: bool = False

class McpResponse(BaseModel):
    content: List[McpTextContent]

# Standard response creators
def create_success_response(message: str, data: Any = None) -> McpResponse:
    text = f"**Success**\n\n{message}"
    if data is not None:
        import json
        text += f"\n\n**Result:**\n```json\n{json.dumps(data, indent=2, default=str)}\n```"
    return McpResponse(
        content=[McpTextContent(text=text)]
    )

def create_error_response(message: str, details: Any = None) -> McpResponse:
    text = f"**Error**\n\n{message}"
    if details is not None:
        import json
        text += f"\n\n**Details:**\n```json\n{json.dumps(details, indent=2, default=str)}\n```"
    return McpResponse(
        content=[McpTextContent(text=text, is_error=True)]
    )

# Analysis operation result type
class AnalysisOperationResult(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: Optional[float] = None

# Security validation result
class SecurityValidationResult(BaseModel):
    is_valid: bool
    error: Optional[str] = None

# OAuth URL construction parameters
class UpstreamAuthorizeParams(BaseModel):
    upstream_url: str
    client_id: str
    scope: str
    redirect_uri: str
    state: Optional[str] = None

# OAuth token exchange parameters
class UpstreamTokenParams(BaseModel):
    code: Optional[str]
    upstream_url: str
    client_secret: str
    redirect_uri: str
    client_id: str

# Project structure representation
class FileInfo(BaseModel):
    name: str
    path: str
    size: int
    type: str
    last_modified: Optional[str] = None

class DirectoryInfo(BaseModel):
    name: str
    path: str
    files: List[FileInfo]
    subdirectories: List['DirectoryInfo']

# Code analysis results
class CodeAnalysisResult(BaseModel):
    project_structure: DirectoryInfo
    dependencies: List[Dict[str, Any]]  # Changed from List[str] to support detailed dependency info
    api_endpoints: List[Dict[str, Any]]
    architecture_info: Dict[str, Any]
    metrics: Dict[str, Any]
    
# Documentation generation result
class DocumentationResult(BaseModel):
    content: str
    format: DocumentationFormat
    metadata: Dict[str, Any]
    generated_at: str

