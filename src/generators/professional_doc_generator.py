"""
Professional Documentation Generator

This module creates comprehensive, detailed documentation similar to high-quality
open source projects with rich content, examples, and technical details.
"""

import os
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ProfessionalDocumentationGenerator:
    """Generates professional, comprehensive documentation with rich content."""
    
    def __init__(self):
        self.project_patterns = {
            'tracker': {
                'type': 'Monitoring Tool',
                'description': 'monitors and tracks changes in data over time',
                'features': [
                    'Real-time monitoring capabilities',
                    'Automated notifications and alerts',
                    'Historical data tracking',
                    'Customizable thresholds'
                ]
            },
            'scraper': {
                'type': 'Web Scraping Tool',
                'description': 'extracts and collects data from web sources',
                'features': [
                    'Intelligent data extraction',
                    'Anti-detection mechanisms',
                    'Multiple format support',
                    'Scheduled scraping'
                ]
            },
            'api': {
                'type': 'API Service',
                'description': 'provides programmatic access to functionality',
                'features': [
                    'RESTful API endpoints',
                    'Authentication and authorization',
                    'Rate limiting',
                    'Comprehensive documentation'
                ]
            },
            'bot': {
                'type': 'Automation Bot',
                'description': 'automates repetitive tasks and workflows',
                'features': [
                    'Task automation',
                    'Scheduled operations',
                    'Event-driven actions',
                    'Extensible plugin system'
                ]
            }
        }
    
    def generate_documentation(
        self, 
        analysis_result: Dict[str, Any], 
        project_root: str, 
        output_path: str, 
        repo_url: str
    ) -> str:
        """
        Generates professional documentation from analysis results.
        """
        logger.info(f"Generating professional documentation for: {output_path}")
        
        # Extract project information
        project_name = self._extract_project_name(repo_url, project_root)
        project_info = self._analyze_project_type(project_name, analysis_result)
        
        # Generate all sections
        sections = []
        
        # Title and Description
        sections.append(self._generate_title_section(project_name, project_info))
        
        # Table of Contents
        sections.append(self._generate_toc())
        
        # Overview
        sections.append(self._generate_overview(project_name, project_info, analysis_result))
        
        # Features
        sections.append(self._generate_features(project_name, project_info, analysis_result))
        
        # Architecture
        sections.append(self._generate_architecture(project_name, analysis_result))
        
        # Prerequisites
        sections.append(self._generate_prerequisites(analysis_result))
        
        # Installation
        sections.append(self._generate_installation(project_name, repo_url, analysis_result))
        
        # Configuration
        sections.append(self._generate_configuration(project_name, analysis_result))
        
        # Usage
        sections.append(self._generate_usage(project_name, project_info, analysis_result))
        
        # API Reference (if applicable)
        if self._has_api(analysis_result):
            sections.append(self._generate_api_reference(project_name, analysis_result))
        
        # Project Structure
        sections.append(self._generate_project_structure(analysis_result))
        
        # How It Works
        sections.append(self._generate_how_it_works(project_name, project_info))
        
        # Deployment
        sections.append(self._generate_deployment(project_name, analysis_result))
        
        # Contributing
        sections.append(self._generate_contributing())
        
        # Troubleshooting
        sections.append(self._generate_troubleshooting(project_name, project_info))
        
        # Legal Disclaimer
        sections.append(self._generate_legal_disclaimer(project_info))
        
        # License
        sections.append(self._generate_license())
        
        # Build final document
        doc_content = "\n\n".join(sections)
        
        # Save the document
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            logger.info(f"Professional documentation saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save documentation: {e}")
        
        return doc_content
    
    def _extract_project_name(self, repo_url: str, project_root: str) -> str:
        """Extract a clean project name."""
        if repo_url.startswith('http'):
            name = os.path.basename(repo_url).replace('.git', '')
        else:
            name = os.path.basename(project_root)
        
        return name.replace('-', ' ').replace('_', ' ').title()
    
    def _analyze_project_type(self, project_name: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and determine project type with detailed info."""
        project_name_lower = project_name.lower()
        
        # Check against patterns
        for pattern, info in self.project_patterns.items():
            if pattern in project_name_lower:
                return info
        
        # Check dependencies for type hints
        deps = [d.lower() for d in analysis_result.get('dependencies', [])]
        
        if any(web in deps for web in ['beautifulsoup4', 'scrapy', 'selenium']):
            return self.project_patterns['scraper']
        elif any(api in deps for api in ['flask', 'django', 'fastapi']):
            return self.project_patterns['api']
        
        # Default
        return {
            'type': 'Software Application',
            'description': 'provides comprehensive functionality for various use cases',
            'features': ['Core functionality', 'Modular design', 'Extensible architecture']
        }
    
    def _generate_title_section(self, project_name: str, project_info: Dict[str, Any]) -> str:
        """Generate title and tagline."""
        tagline = f"A powerful Python-based {project_info['type'].lower()} that {project_info['description']}."
        
        return f"# {project_name}\n\n{tagline}"
    
    def _generate_toc(self) -> str:
        """Generate table of contents."""
        return """## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Legal Disclaimer](#legal-disclaimer)
- [License](#license)"""
    
    def _generate_overview(self, project_name: str, project_info: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Generate detailed overview section."""
        language = self._detect_language(analysis_result)
        
        overview = f"""## Overview

{project_name} is an automated {project_info['type'].lower()} designed to help users {project_info['description']}. Built with {language}, this tool leverages modern techniques to provide efficient and reliable functionality.

### Why Use {project_name}?

"""
        
        # Add benefits based on project type
        if 'tracker' in project_name.lower():
            overview += """- **Save Money**: Never miss important changes or opportunities
- **Save Time**: Eliminate the need for manual checking
- **Stay Informed**: Get instant notifications about changes
- **Track Multiple Items**: Monitor unlimited items simultaneously
- **Historical Data**: Keep track of trends over time"""
        elif 'scraper' in project_name.lower():
            overview += """- **Automated Data Collection**: Extract data without manual effort
- **Scalable Solution**: Handle large-scale data extraction
- **Structured Output**: Get clean, organized data
- **Regular Updates**: Keep your data fresh with scheduled runs
- **Multiple Sources**: Support for various websites and formats"""
        else:
            overview += """- **Efficiency**: Automate repetitive tasks
- **Reliability**: Consistent and accurate results
- **Scalability**: Handle growing demands
- **Flexibility**: Customize to your needs
- **Integration**: Works with existing systems"""
        
        return overview
    
    def _generate_features(self, project_name: str, project_info: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Generate comprehensive features section."""
        features = """## Features

### Core Features

"""
        
        # Add project-specific features
        for feature in project_info['features']:
            features += f"- **{feature}**: {self._get_feature_description(feature, project_name)}\n"
        
        # Add standard features
        features += """- **User-friendly Interface**: Simple and intuitive design
- **Flexible Configuration**: Customize settings to your needs
- **Comprehensive Logging**: Detailed logs for debugging
- **Error Handling**: Robust error management

### Advanced Features

"""
        
        # Add advanced features based on dependencies
        deps = analysis_result.get('dependencies', [])
        if any('api' in d.lower() or 'flask' in d.lower() or 'fastapi' in d.lower() for d in deps):
            features += """- **RESTful API**: Full API access for integration
- **Authentication**: Secure access control
- **Rate Limiting**: Prevent abuse
"""
        
        if any('database' in d.lower() or 'sql' in d.lower() for d in deps):
            features += """- **Data Persistence**: Store data reliably
- **Query Optimization**: Fast data retrieval
- **Backup Support**: Data safety features
"""
        
        features += """- **Cross-platform Support**: Works on Windows, macOS, and Linux
- **Extensible Architecture**: Easy to add new features
- **Community Support**: Active development and user community"""
        
        return features
    
    def _generate_architecture(self, project_name: str, analysis_result: Dict[str, Any]) -> str:
        """Generate architecture section with diagram."""
        arch = f"""## Architecture

The application follows a modular architecture with clear separation of concerns:

```
+-----------------+     +-----------------+     +-----------------+
|   User Interface|---->|   Application   |---->|    Data Store   |
|   (CLI/Web)     |     |     Logic       |     |   (Database)    |
+-----------------+     +-----------------+     +-----------------+
                               |
                               v
                        +-----------------+
                        |  Core Services  |
                        |  (Processing)   |
                        +-----------------+
                               |
                               v
                        +-----------------+
                        | External APIs   |
                        |  (Integrations) |
                        +-----------------+
```

### Components

- **User Interface**: Handles user interactions and displays results
- **Application Logic**: Core business logic and workflow management
- **Data Store**: Persistent storage for application data
- **Core Services**: Specialized services for specific tasks
- **External APIs**: Integration with third-party services"""
        
        return arch
    
    def _generate_prerequisites(self, analysis_result: Dict[str, Any]) -> str:
        """Generate prerequisites section."""
        language = self._detect_language(analysis_result)
        
        prereq = """## Prerequisites

Before installation, ensure you have the following:

"""
        
        if language == "Python":
            prereq += """- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)
"""
        elif language == "JavaScript/Node.js":
            prereq += """- Node.js 14.x or higher
- npm or yarn package manager
- Git
"""
        else:
            prereq += """- Appropriate runtime for the programming language
- Package manager
- Git
"""
        
        # Add project-specific prerequisites
        deps = analysis_result.get('dependencies', [])
        if any('email' in d.lower() or 'smtp' in d.lower() for d in deps):
            prereq += "- Valid email credentials for SMTP\n"
        if any('database' in d.lower() or 'sql' in d.lower() for d in deps):
            prereq += "- Database server (PostgreSQL/MySQL/SQLite)\n"
        
        prereq += """- Internet connection

### System Requirements

- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 20.04+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 500MB available space
- **Network**: Stable internet connection"""
        
        return prereq
    
    def _generate_installation(self, project_name: str, repo_url: str, analysis_result: Dict[str, Any]) -> str:
        """Generate detailed installation instructions."""
        language = self._detect_language(analysis_result)
        repo_name = os.path.basename(repo_url).replace('.git', '')
        
        install = f"""## Installation

### Step 1: Clone the Repository

```bash
git clone {repo_url if repo_url.startswith('http') else 'https://github.com/username/' + repo_name}
cd {repo_name}
```

"""
        
        if language == "Python":
            install += """### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\\Scripts\\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```"""
        elif language == "JavaScript/Node.js":
            install += """### Step 2: Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```"""
        
        install += """

### Step 4: Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Application Settings
APP_ENV=development
DEBUG=True
SECRET_KEY=your_secret_key_here

# Database Configuration (if applicable)
DATABASE_URL=sqlite:///app.db

# API Keys (if applicable)
API_KEY=your_api_key_here

# Other Configuration
LOG_LEVEL=INFO
```

### Step 5: Initialize Application

```bash
# Run setup script
python setup.py

# Or initialize database
python manage.py migrate
```"""
        
        return install
    
    def _generate_configuration(self, project_name: str, analysis_result: Dict[str, Any]) -> str:
        """Generate configuration section."""
        config = f"""## Configuration

### Environment Variables

The application uses environment variables for configuration. Create a `.env` file with the following variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `APP_ENV` | Application environment | `development` | Yes |
| `DEBUG` | Debug mode | `False` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///app.db` | Yes |

### Configuration File

You can also use a configuration file (`config.json` or `config.yaml`):

```json
{{
  "app": {{
    "name": "{project_name}",
    "version": "1.0.0",
    "debug": false
  }},
  "database": {{
    "type": "sqlite",
    "path": "./data/app.db"
  }},
  "logging": {{
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }}
}}
```

### Advanced Configuration

For production environments, consider:

- Using environment-specific configuration files
- Storing sensitive data in secure vaults
- Implementing configuration validation
- Using configuration management tools"""
        
        return config
    
    def _generate_usage(self, project_name: str, project_info: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Generate comprehensive usage section."""
        usage = f"""## Usage

### Starting the Application

```bash
# Development mode
python app.py

# Production mode
python app.py --env production

# With specific configuration
python app.py --config /path/to/config.json
```

### Basic Usage

"""
        
        if 'tracker' in project_info['type'].lower():
            usage += """#### Adding Items to Track

```bash
# Add a new item
python tracker.py add --url "https://example.com/item" --target-value 100

# Add with custom interval
python tracker.py add --url "https://example.com/item" --interval 3600
```

#### Checking Status

```bash
# Check all items
python tracker.py check --all

# Check specific item
python tracker.py check --id 123
```"""
        elif 'scraper' in project_info['type'].lower():
            usage += """#### Running a Scrape

```bash
# Scrape a single URL
python scraper.py scrape --url "https://example.com"

# Scrape multiple URLs
python scraper.py scrape --file urls.txt

# Scrape with custom settings
python scraper.py scrape --url "https://example.com" --format json --output data/
```"""
        else:
            usage += """#### Basic Commands

```bash
# Run the application
python app.py run

# Show help
python app.py --help

# Check version
python app.py --version
```"""
        
        usage += """

### Command Line Interface

The application provides a comprehensive CLI with the following commands:

| Command | Description | Example |
|---------|-------------|---------|
| `run` | Start the application | `python app.py run` |
| `config` | Show configuration | `python app.py config` |
| `test` | Run tests | `python app.py test` |
| `help` | Show help message | `python app.py help` |

### Web Interface (if applicable)

Access the web interface at `http://localhost:8000` after starting the application.

### Scheduling and Automation

For continuous operation:

```bash
# Using cron (Linux/macOS)
*/30 * * * * /path/to/venv/bin/python /path/to/app.py run

# Using Task Scheduler (Windows)
# Create a task that runs the script at your desired interval
```"""
        
        return usage
    
    def _generate_api_reference(self, project_name: str, analysis_result: Dict[str, Any]) -> str:
        """Generate API reference section."""
        api_ref = """## API Reference

### Authentication

All API requests require authentication using an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/endpoint
```

### Endpoints

#### GET /api/v1/status
Get application status

**Request:**
```bash
curl -X GET https://api.example.com/api/v1/status \\
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response:**
```json
{
  "status": "active",
  "version": "1.0.0",
  "uptime": 3600
}
```

#### POST /api/v1/items
Create a new item

**Request:**
```bash
curl -X POST https://api.example.com/api/v1/items \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Item Name",
    "url": "https://example.com/item",
    "settings": {
      "interval": 3600,
      "notify": true
    }
  }'
```

**Response:**
```json
{
  "id": "123",
  "name": "Item Name",
  "created_at": "2024-01-19T12:00:00Z",
  "status": "active"
}
```

#### GET /api/v1/items/{id}
Get item details

**Request:**
```bash
curl -X GET https://api.example.com/api/v1/items/123 \\
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### PUT /api/v1/items/{id}
Update an item

**Request:**
```bash
curl -X PUT https://api.example.com/api/v1/items/123 \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "settings": {
      "interval": 7200
    }
  }'
```

#### DELETE /api/v1/items/{id}
Delete an item

**Request:**
```bash
curl -X DELETE https://api.example.com/api/v1/items/123 \\
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Error Responses

The API uses standard HTTP status codes:

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Server Error |

### Rate Limiting

API requests are limited to:
- 100 requests per minute for authenticated users
- 10 requests per minute for unauthenticated users"""
        
        return api_ref
    
    def _generate_project_structure(self, analysis_result: Dict[str, Any]) -> str:
        """Generate detailed project structure."""
        structure = """## Project Structure

```
project_root/
|
|-- app/
|   |-- __init__.py
|   |-- main.py            # Application entry point
|   |-- config.py          # Configuration management
|   |-- models.py          # Data models
|   `-- utils.py           # Utility functions
|
|-- core/
|   |-- __init__.py
|   |-- processor.py       # Core processing logic
|   |-- validator.py       # Input validation
|   `-- exceptions.py      # Custom exceptions
|
|-- services/
|   |-- __init__.py
|   |-- api_service.py     # External API integration
|   |-- db_service.py      # Database operations
|   `-- notification.py    # Notification handling
|
|-- tests/
|   |-- __init__.py
|   |-- test_core.py       # Core functionality tests
|   |-- test_services.py   # Service tests
|   `-- test_integration.py # Integration tests
|
|-- docs/
|   |-- api.md             # API documentation
|   |-- configuration.md   # Configuration guide
|   `-- development.md     # Development guide
|
|-- scripts/
|   |-- setup.py           # Setup script
|   |-- migrate.py         # Database migrations
|   `-- deploy.sh          # Deployment script
|
|-- data/                  # Data directory
|-- logs/                  # Log files
|-- .env.example           # Environment variables example
|-- .gitignore             # Git ignore file
|-- requirements.txt       # Python dependencies
|-- Dockerfile             # Docker configuration
|-- docker-compose.yml     # Docker Compose configuration
`-- README.md              # This file
```

### Key Directories

- **`app/`**: Main application code
- **`core/`**: Core business logic
- **`services/`**: External service integrations
- **`tests/`**: Test suite
- **`docs/`**: Additional documentation
- **`scripts/`**: Utility scripts"""
        
        return structure
    
    def _generate_how_it_works(self, project_name: str, project_info: Dict[str, Any]) -> str:
        """Generate how it works section."""
        how_it_works = f"""## How It Works

### Core Process Flow

"""
        
        if 'tracker' in project_info['type'].lower():
            how_it_works += """1. **URL Validation**: Validates the target URL
2. **Data Fetching**: Retrieves current data from the source
3. **Data Processing**: Extracts and processes relevant information
4. **Comparison**: Compares with previous values and thresholds
5. **Notification**: Sends alerts if conditions are met
6. **Storage**: Updates database with new information

### Tracking Algorithm

```python
def track_item(item):
    # Fetch current data
    current_data = fetch_data(item.url)
    
    # Process and extract value
    current_value = extract_value(current_data)
    
    # Compare with target
    if meets_criteria(current_value, item.target):
        # Send notification
        notify_user(item, current_value)
    
    # Store results
    store_result(item.id, current_value)
```"""
        elif 'scraper' in project_info['type'].lower():
            how_it_works += """1. **URL Processing**: Validates and prepares URLs
2. **Request Handling**: Sends HTTP requests with proper headers
3. **HTML Parsing**: Extracts data using selectors
4. **Data Cleaning**: Processes and validates extracted data
5. **Storage**: Saves data in specified format

### Scraping Process

```python
def scrape_page(url):
    # Set up session with headers
    session = create_session()
    
    # Fetch page content
    response = session.get(url)
    
    # Parse HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract data
    data = extract_data(soup)
    
    # Clean and validate
    cleaned_data = clean_data(data)
    
    return cleaned_data
```"""
        
        how_it_works += """

### Data Flow Diagram

```
Input -> Validation -> Processing -> Analysis -> Output
  |                                            |
  v                                            v
Error Handling <-<-<-<-<-<-<-<-<-<-<-<-<- Storage
```

### Performance Optimization

- **Caching**: Frequently accessed data is cached
- **Connection Pooling**: Reuses network connections
- **Batch Processing**: Handles multiple items efficiently
- **Async Operations**: Non-blocking I/O for better performance"""
        
        return how_it_works
    
    def _generate_deployment(self, project_name: str, analysis_result: Dict[str, Any]) -> str:
        """Generate deployment section."""
        deploy = f"""## Deployment

### Local Deployment

Follow the installation steps above for local deployment.

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t {project_name.lower().replace(' ', '-')} .
   ```

2. Run the container:
   ```bash
   docker run -d \\
     -p 8000:8000 \\
     --env-file .env \\
     --name {project_name.lower().replace(' ', '-')} \\
     {project_name.lower().replace(' ', '-')}
   ```

### Cloud Deployment

#### Heroku

1. Create a Heroku app:
   ```bash
   heroku create your-app-name
   ```

2. Set environment variables:
   ```bash
   heroku config:set KEY=VALUE
   ```

3. Deploy:
   ```bash
   git push heroku main
   ```

#### AWS

1. Create an EC2 instance
2. Install dependencies
3. Clone repository
4. Set up systemd service
5. Configure nginx reverse proxy

#### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
    depends_on:
      - db
      
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Considerations

- Use environment variables for sensitive data
- Set up proper logging and monitoring
- Implement health checks
- Configure automatic restarts
- Set up SSL/TLS certificates
- Implement backup strategies"""
        
        return deploy
    
    def _generate_contributing(self) -> str:
        """Generate contributing section."""
        return """## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Write or update tests
5. Ensure all tests pass:
   ```bash
   python -m pytest
   ```
6. Commit your changes:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```
7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Write descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Ensure backward compatibility

### Code Style

- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused
- Handle errors appropriately

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_core.py
```

### Areas for Contribution

- Bug fixes and issue resolution
- New features and enhancements
- Documentation improvements
- Test coverage expansion
- Performance optimizations
- Security improvements"""
    
    def _generate_troubleshooting(self, project_name: str, project_info: Dict[str, Any]) -> str:
        """Generate troubleshooting section."""
        trouble = f"""## Troubleshooting

### Common Issues

"""
        
        if 'tracker' in project_info['type'].lower() or 'scraper' in project_info['type'].lower():
            trouble += """#### "Access Denied" or "403 Forbidden" Error
- **Cause**: Website blocking automated requests
- **Solution**: 
  - Update User-Agent header
  - Implement request delays
  - Use proxy rotation
  - Check robots.txt compliance

#### "Connection Timeout" Error
- **Cause**: Network issues or server not responding
- **Solution**:
  - Check internet connection
  - Increase timeout values
  - Implement retry logic
  - Verify URL is correct
"""
        
        trouble += """#### "Module Not Found" Error
- **Cause**: Missing dependencies
- **Solution**:
  - Run `pip install -r requirements.txt`
  - Ensure virtual environment is activated
  - Check Python version compatibility

#### "Permission Denied" Error
- **Cause**: Insufficient file permissions
- **Solution**:
  - Check file/directory permissions
  - Run with appropriate user privileges
  - Ensure write access to data directories

### Debug Mode

Enable detailed logging for troubleshooting:

```python
# Set in .env file
LOG_LEVEL=DEBUG

# Or in code
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance Issues

If experiencing slow performance:

1. **Check System Resources**
   ```bash
   # CPU usage
   top
   
   # Memory usage
   free -h
   
   # Disk space
   df -h
   ```

2. **Optimize Configuration**
   - Reduce concurrent operations
   - Increase cache size
   - Optimize database queries

3. **Profile Code**
   ```python
   import cProfile
   cProfile.run('main()')
   ```

### Getting Help

If you encounter issues:

1. Check existing [issues](https://github.com/username/repo/issues)
2. Search [documentation](https://github.com/username/repo/wiki)
3. Ask in [discussions](https://github.com/username/repo/discussions)
4. Create a new issue with:
   - Error message
   - Steps to reproduce
   - System information
   - Configuration details"""
        
        return trouble
    
    def _generate_legal_disclaimer(self, project_info: Dict[str, Any]) -> str:
        """Generate legal disclaimer."""
        disclaimer = """## Legal Disclaimer

"""
        
        if 'scraper' in project_info['type'].lower():
            disclaimer += """This tool is for educational and research purposes only. Users must:

- Comply with website Terms of Service
- Respect robots.txt files
- Implement reasonable rate limiting
- Not use for illegal purposes
- Obtain permission when required

**Important**: Web scraping may be subject to legal restrictions in your jurisdiction. Users are responsible for ensuring compliance with all applicable laws and regulations.

The developers of this tool are not responsible for any misuse or damage caused by using this software.
"""
        else:
            disclaimer += """This software is provided "as is" without warranty of any kind. Users must:

- Use responsibly and ethically
- Comply with all applicable laws
- Not use for illegal purposes
- Respect third-party rights

The developers are not liable for any damages or losses arising from the use of this software.
"""
        
        return disclaimer
    
    def _generate_license(self) -> str:
        """Generate license section."""
        return """## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Acknowledgments

- Open source community for amazing tools and libraries
- Contributors who helped improve this project
- Users who provided valuable feedback

### Contact

- **Issues**: [GitHub Issues](https://github.com/username/repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/repo/discussions)
- **Email**: contact@example.com

### Links

- [Documentation](https://github.com/username/repo/wiki)
- [Changelog](https://github.com/username/repo/releases)
- [Contributing Guide](CONTRIBUTING.md)"""
    
    # Helper methods
    
    def _detect_language(self, analysis_result: Dict[str, Any]) -> str:
        """Detect primary programming language."""
        # Check for specific files
        all_files = []
        
        def get_files(structure):
            if 'files' in structure:
                all_files.extend([f['name'].lower() for f in structure['files']])
            if 'subdirectories' in structure:
                for subdir in structure['subdirectories']:
                    get_files(subdir)
        
        get_files(analysis_result.get('project_structure', {}))
        
        if any(f in all_files for f in ['requirements.txt', 'setup.py', 'pyproject.toml']):
            return 'Python'
        elif any(f in all_files for f in ['package.json', 'yarn.lock']):
            return 'JavaScript/Node.js'
        elif any(f in all_files for f in ['pom.xml', 'build.gradle']):
            return 'Java'
        elif any(f in all_files for f in ['go.mod', 'go.sum']):
            return 'Go'
        
        return 'Python'  # Default
    
    def _has_api(self, analysis_result: Dict[str, Any]) -> bool:
        """Check if project has API."""
        deps = [d.lower() for d in analysis_result.get('dependencies', [])]
        return any(api in deps for api in ['flask', 'django', 'fastapi', 'express'])
    
    def _get_feature_description(self, feature: str, project_name: str) -> str:
        """Get detailed feature description."""
        descriptions = {
            'Real-time monitoring capabilities': f'Continuously monitors targets and provides instant updates',
            'Automated notifications and alerts': 'Sends timely alerts via email, SMS, or webhooks',
            'Historical data tracking': 'Maintains complete history for trend analysis',
            'Customizable thresholds': 'Set your own criteria for notifications',
            'Intelligent data extraction': 'Smart algorithms to extract relevant data accurately',
            'Anti-detection mechanisms': 'Avoids detection with rotating headers and delays',
            'Multiple format support': 'Export data in JSON, CSV, XML, and more',
            'Scheduled scraping': 'Run automated scrapes at specified intervals',
            'RESTful API endpoints': 'Well-designed API following REST principles',
            'Authentication and authorization': 'Secure access control with token-based auth',
            'Rate limiting': 'Prevents API abuse with intelligent rate limiting',
            'Comprehensive documentation': 'Detailed docs with examples and tutorials'
        }
        
        return descriptions.get(feature, f'Enhances {project_name} functionality')
    
    def generate_interactive_documentation(
        self,
        analysis_result: Dict[str, Any],
        title: str = "Interactive Documentation",
        theme: str = "default",
        include_search: bool = True,
        include_navigation: bool = True,
        include_live_diagrams: bool = True,
        output_path: str = "docs/interactive.html"
    ) -> str:
        """Generate interactive HTML documentation with search and navigation."""
        try:
            # Generate enhanced HTML with interactive features
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Enhanced styling for interactive documentation */
        :root {{
            --primary-color: #2563eb;
            --secondary-color: #64748b;
            --background-color: #ffffff;
            --text-color: #1e293b;
            --code-background: #f8fafc;
            --border-color: #e2e8f0;
        }}
        
        [data-theme="dark"] {{
            --background-color: #0f172a;
            --text-color: #f1f5f9;
            --code-background: #1e293b;
            --border-color: #334155;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            background-color: var(--background-color);
            color: var(--text-color);
            transition: background-color 0.3s, color 0.3s;
        }}
        
        .header {{
            background: var(--primary-color);
            color: white;
            padding: 1rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0;
            display: inline-block;
        }}
        
        .header-controls {{
            float: right;
            margin-top: 0.5rem;
        }}
        
        .theme-toggle, .search-toggle {{
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 0.5rem;
        }}
        
        .search-container {{
            background: var(--background-color);
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            display: none;
        }}
        
        .search-container.active {{
            display: block;
        }}
        
        .search-input {{
            width: 100%;
            padding: 0.5rem;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            font-size: 1rem;
        }}
        
        .container {{
            display: flex;
            min-height: calc(100vh - 80px);
        }}
        
        .sidebar {{
            width: 250px;
            background: var(--code-background);
            border-right: 1px solid var(--border-color);
            padding: 1rem;
            overflow-y: auto;
            max-height: calc(100vh - 80px);
        }}
        
        .sidebar.hidden {{
            display: none;
        }}
        
        .sidebar ul {{
            list-style: none;
            padding: 0;
            margin: 0;
        }}
        
        .sidebar li {{
            margin: 0.25rem 0;
        }}
        
        .sidebar a {{
            color: var(--text-color);
            text-decoration: none;
            display: block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}
        
        .sidebar a:hover {{
            background-color: var(--border-color);
        }}
        
        .content {{
            flex: 1;
            padding: 2rem;
            max-width: calc(100vw - 250px);
            overflow-x: auto;
        }}
        
        .content.full-width {{
            max-width: 100vw;
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-color);
            margin-top: 2rem;
            margin-bottom: 1rem;
        }}
        
        h1:first-child {{
            margin-top: 0;
        }}
        
        code {{
            background-color: var(--code-background);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Monaco', 'Consolas', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: var(--code-background);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid var(--primary-color);
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        .mermaid {{
            text-align: center;
            margin: 2rem 0;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }}
        
        th, td {{
            border: 1px solid var(--border-color);
            padding: 0.75rem;
            text-align: left;
        }}
        
        th {{
            background-color: var(--code-background);
            font-weight: 600;
        }}
        
        .highlight {{
            background-color: yellow;
            color: black;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                max-height: none;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }}
            
            .content {{
                max-width: 100vw;
            }}
        }}
    </style>
    {('<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>' if include_live_diagrams else '')}
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="header-controls">
            {('<button class="search-toggle" onclick="toggleSearch()">Search</button>' if include_search else '')}
            <button class="theme-toggle" onclick="toggleTheme()">Dark</button>
            {('<button class="nav-toggle" onclick="toggleSidebar()">Menu</button>' if include_navigation else '')}
        </div>
    </div>
    
    {f'''<div class="search-container" id="searchContainer">
        <input type="text" class="search-input" placeholder="Search documentation..." 
               onkeyup="searchContent()" id="searchInput">
    </div>''' if include_search else ''}
    
    <div class="container">
        {f'''<nav class="sidebar" id="sidebar">
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#architecture">Architecture</a></li>
                <li><a href="#installation">Installation</a></li>
                <li><a href="#usage">Usage</a></li>
                <li><a href="#api">API Reference</a></li>
                <li><a href="#structure">Project Structure</a></li>
                <li><a href="#deployment">Deployment</a></li>
                <li><a href="#contributing">Contributing</a></li>
            </ul>
        </nav>''' if include_navigation else ''}
        
        <main class="content" id="content">
            {self._generate_interactive_content(analysis_result)}
        </main>
    </div>
    
    <script>
        // Theme toggle functionality
        function toggleTheme() {{
            const body = document.body;
            const button = document.querySelector('.theme-toggle');
            
            if (body.hasAttribute('data-theme')) {{
                body.removeAttribute('data-theme');
                button.textContent = 'Dark';
            }} else {{
                body.setAttribute('data-theme', 'dark');
                button.textContent = 'Light';
            }}
        }}
        
        // Sidebar toggle functionality
        function toggleSidebar() {{
            const sidebar = document.getElementById('sidebar');
            const content = document.getElementById('content');
            
            if (sidebar) {{
                sidebar.classList.toggle('hidden');
                content.classList.toggle('full-width');
            }}
        }}
        
        // Search functionality
        {f'''function toggleSearch() {{
            const container = document.getElementById('searchContainer');
            const input = document.getElementById('searchInput');
            
            container.classList.toggle('active');
            if (container.classList.contains('active')) {{
                input.focus();
            }}
        }}
        
        function searchContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const content = document.getElementById('content');
            
            if (!searchTerm) {{
                clearHighlights();
                return;
            }}
            
            clearHighlights();
            highlightText(content, searchTerm);
        }}
        
        function highlightText(element, searchTerm) {{
            if (element.nodeType === Node.TEXT_NODE) {{
                const text = element.textContent;
                const index = text.toLowerCase().indexOf(searchTerm);
                
                if (index >= 0) {{
                    const highlightedText = text.substring(0, index) + 
                        '<span class="highlight">' + 
                        text.substring(index, index + searchTerm.length) + 
                        '</span>' + 
                        text.substring(index + searchTerm.length);
                    
                    const wrapper = document.createElement('span');
                    wrapper.innerHTML = highlightedText;
                    element.parentNode.replaceChild(wrapper, element);
                }}
            }} else {{
                for (let child of element.childNodes) {{
                    highlightText(child, searchTerm);
                }}
            }}
        }}
        
        function clearHighlights() {{
            const highlights = document.querySelectorAll('.highlight');
            highlights.forEach(highlight => {{
                const parent = highlight.parentNode;
                parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
                parent.normalize();
            }});
        }}''' if include_search else ''}
        
        // Initialize Mermaid diagrams
        {f'''document.addEventListener('DOMContentLoaded', function() {{
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        }});''' if include_live_diagrams else ''}
    </script>
</body>
</html>"""
            
            # Save to file
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to generate interactive documentation: {e}")
            return f"Error generating interactive documentation: {str(e)}"
    
    def _generate_interactive_content(self, analysis_result: Dict[str, Any]) -> str:
        """Generate the main content for interactive documentation."""
        content = []
        
        # Generate basic markdown content and convert to HTML
        project_name = "Project"  # You could extract this from analysis_result
        project_info = {
            'type': 'Application', 
            'description': 'provides functionality',
            'features': ['Core functionality', 'Modular design', 'Extensible architecture']
        }
        
        markdown_sections = [
            self._generate_overview(project_name, project_info, analysis_result),
            self._generate_features(project_name, project_info, analysis_result),
            self._generate_architecture(project_name, analysis_result),
            self._generate_installation(project_name, "", analysis_result),
            self._generate_usage(project_name, project_info, analysis_result),
        ]
        
        # Convert markdown to HTML (simplified)
        html_content = ""
        for section in markdown_sections:
            html_content += self._markdown_to_html_basic(section) + "\n\n"
        
        return html_content
    
    def _markdown_to_html_basic(self, markdown: str) -> str:
        """Basic markdown to HTML conversion."""
        html = markdown
        
        # Headers
        html = re.sub(r'^### (.*$)', r'<h3 id="\1">\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*$)', r'<h2 id="\1">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.*$)', r'<h1 id="\1">\1</h1>', html, flags=re.MULTILINE)
        
        # Code blocks
        html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code class="\1">\2</code></pre>', html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        
        # Lists
        lines = html.split('\n')
        result_lines = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        return '\n'.join(result_lines).replace('\n', '<br>\n')
    
    def export_documentation(
        self,
        analysis_result: Dict[str, Any],
        format: str = "html",
        theme: str = "default",
        title: Optional[str] = None,
        include_toc: bool = True,
        include_diagrams: bool = True,
        include_search: bool = True,
        custom_css: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Export documentation in various formats."""
        try:
            if not output_path:
                output_path = f"docs/export.{format}"
            
            if format.lower() in ['html', 'htm']:
                return self.generate_interactive_documentation(
                    analysis_result=analysis_result,
                    title=title or "Documentation",
                    theme=theme,
                    include_search=include_search,
                    include_navigation=include_toc,
                    include_live_diagrams=include_diagrams,
                    output_path=output_path
                )
            elif format.lower() in ['md', 'markdown']:
                # Generate markdown
                project_name = title or "Project"
                project_info = {
                    'type': 'Application', 
                    'description': 'provides functionality',
                    'features': ['Core functionality', 'Modular design', 'Extensible architecture']
                }
                
                markdown_content = self.generate_documentation(
                    analysis_result=analysis_result,
                    project_root="",
                    output_path=output_path,
                    repo_url=""
                )
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                return markdown_content
            else:
                # Default to HTML for unsupported formats
                return self.export_documentation(
                    analysis_result, "html", theme, title, include_toc, 
                    include_diagrams, include_search, custom_css, output_path
                )
                
        except Exception as e:
            logger.error(f"Failed to export documentation: {e}")
            return f"Error exporting documentation: {str(e)}"
