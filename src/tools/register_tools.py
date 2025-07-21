import os
import logging
from typing import Dict, Any

from src.analyzers.codebase_analyzer import CodebaseAnalyzer
from src.generators.professional_doc_generator import ProfessionalDocumentationGenerator

logger = logging.getLogger(__name__)

async def register_all_tools(path: str, source_type: str) -> Dict[str, Any]:
    """
    Register and execute all analysis tools for a given path.
    
    Args:
        path: The path to analyze (local directory or GitHub URL).
        source_type: Type of source ('local' or 'github').
        
    Returns:
        A dictionary with analysis results and the path to the generated documentation.
    """
    try:
        logger.info(f"Registering tools for {source_type}: {path}")
        
        # Create analyzer
        analyzer = CodebaseAnalyzer(path, source_type)
        
        # Perform analysis
        analysis_result = await analyzer.analyze()
        
        if analysis_result.success:
            # --- SAVING LOGIC START ---
            
            # Define the output directory and create a unique filename.
            output_dir = "docs"
            file_name = f"documentation_{analyzer.analysis_id}.md"
            output_path = os.path.join(output_dir, file_name)

            # Get the correct path of the analyzed project
            project_root = analyzer.working_path

            # Use the professional generator to create comprehensive documentation
            doc_generator = ProfessionalDocumentationGenerator()
            doc_generator.generate_documentation(
                analysis_result.data, 
                project_root, 
                output_path,
                path  # Pass the original path/URL
            )
            
            # --- SAVING LOGIC END ---

            return {
                "success": True,
                "analysis_id": analyzer.analysis_id,
                "analysis_result": analysis_result.data,
                "documentation_path": output_path,  # Return the path to the saved file.
                "duration": analysis_result.duration
            }
        else:
            return {
                "success": False,
                "error": analysis_result.error,
                "duration": analysis_result.duration
            }
    
    except Exception as e:
        logger.error(f"Error in register_all_tools: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }
