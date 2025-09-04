"""
Parser factory for selecting appropriate parsers based on file type.

This module provides a factory for creating and selecting the appropriate
parser for different file types and programming languages.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Type, Union

from .base_parser import BaseParser
from .python_parser import PythonParser
from .javascript_parser import JavaScriptParser

logger = logging.getLogger(__name__)


class ParserFactory:
    """
    Factory class for creating and managing language parsers.
    
    Automatically selects the appropriate parser based on file extensions
    and provides fallback mechanisms for unknown file types.
    """
    
    def __init__(self):
        self._parsers: Dict[str, Type[BaseParser]] = {}
        self._parser_instances: Dict[str, BaseParser] = {}
        self._extension_map: Dict[str, str] = {}
        
        # Register default parsers
        self.register_parser("python", PythonParser)
        self.register_parser("javascript", JavaScriptParser)
        self.register_parser("typescript", JavaScriptParser)
    
    def register_parser(self, language: str, parser_class: Type[BaseParser]) -> None:
        """
        Register a parser for a specific language.
        
        Args:
            language: Language identifier
            parser_class: Parser class to register
        """
        self._parsers[language] = parser_class
        
        # Create instance to get supported extensions
        if language not in self._parser_instances:
            instance = parser_class()
            self._parser_instances[language] = instance
            
            # Map extensions to language
            for ext in instance.get_supported_extensions():
                self._extension_map[ext] = language
        
        logger.info(f"Registered parser for {language}")
    
    def get_parser(self, language: str) -> Optional[BaseParser]:
        """
        Get parser instance for a specific language.
        
        Args:
            language: Language identifier
            
        Returns:
            Parser instance or None if not found
        """
        if language in self._parser_instances:
            return self._parser_instances[language]
        
        if language in self._parsers:
            instance = self._parsers[language]()
            self._parser_instances[language] = instance
            return instance
        
        return None
    
    def get_parser_for_file(self, file_path: str) -> Optional[BaseParser]:
        """
        Get appropriate parser for a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Parser instance or None if no suitable parser found
        """
        extension = Path(file_path).suffix.lower()
        
        if extension in self._extension_map:
            language = self._extension_map[extension]
            return self.get_parser(language)
        
        logger.warning(f"No parser found for extension: {extension}")
        return None
    
    def get_supported_extensions(self) -> Set[str]:
        """Get all supported file extensions."""
        return set(self._extension_map.keys())
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._parsers.keys())
    
    def supports_file(self, file_path: str) -> bool:
        """Check if a file type is supported."""
        extension = Path(file_path).suffix.lower()
        return extension in self._extension_map
    
    def parse_file(self, file_path: str, content: str) -> Optional['ParseResult']:
        """
        Parse a file using the appropriate parser.
        
        Args:
            file_path: Path to the file
            content: File content
            
        Returns:
            ParseResult or None if no parser available
        """
        parser = self.get_parser_for_file(file_path)
        if parser:
            return parser.parse_file(file_path, content)
        
        logger.warning(f"Cannot parse file {file_path}: no suitable parser")
        return None
    
    def get_parser_info(self) -> Dict[str, Dict[str, any]]:
        """Get information about all registered parsers."""
        info = {}
        
        for language, parser_class in self._parsers.items():
            instance = self.get_parser(language)
            if instance:
                info[language] = {
                    'class': parser_class.__name__,
                    'supported_extensions': list(instance.get_supported_extensions()),
                    'language': instance.get_language()
                }
        
        return info


# Global factory instance
_parser_factory: Optional[ParserFactory] = None


def get_parser_factory() -> ParserFactory:
    """Get global parser factory instance."""
    global _parser_factory
    if _parser_factory is None:
        _parser_factory = ParserFactory()
    return _parser_factory


def get_parser_for_file(file_path: str) -> Optional[BaseParser]:
    """Convenience function to get parser for file."""
    return get_parser_factory().get_parser_for_file(file_path)


def parse_file(file_path: str, content: str) -> Optional['ParseResult']:
    """Convenience function to parse file."""
    return get_parser_factory().parse_file(file_path, content)


def supports_file(file_path: str) -> bool:
    """Convenience function to check if file is supported."""
    return get_parser_factory().supports_file(file_path)
