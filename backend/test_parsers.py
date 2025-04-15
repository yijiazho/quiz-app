import os
import sys
import logging
import time

# Configure logging first
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG level
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.debug("Starting script execution")
logger.debug(f"Current working directory: {os.getcwd()}")

# Add the current directory to the Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
logger.debug(f"Added to Python path: {backend_dir}")

logger.debug("Attempting to import ParserFactory")
from app.services.parser import ParserFactory
logger.debug("Successfully imported ParserFactory")

from typing import Dict, Any, Union, List

def format_section_content(content: str, max_length: int = 200) -> str:
    """Format section content for display"""
    if not content:
        return ""
    content = str(content).strip()
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content

def test_parser(filepath: str) -> None:
    """
    Test a parser with the given file
    
    Args:
        filepath: Path to the file to test
    """
    try:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing parser for: {filepath}")
        logger.info(f"{'='*50}")
        
        # Get the appropriate parser
        ext = os.path.splitext(filepath)[1]
        logger.info(f"Getting parser for file extension: {ext}")
        parser = ParserFactory.get_parser(filepath)
        
        if parser is None:
            logger.error(f"No parser available for {filepath}")
            return
            
        logger.info(f"Using parser: {parser.__class__.__name__}")
        
        # Special logging for CSV files
        if ext == '.csv':
            logger.info("Testing CSV file...")
            logger.info(f"File exists: {os.path.exists(filepath)}")
            logger.info(f"File size: {os.path.getsize(filepath)}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"File content preview: {content[:100]}")
            except Exception as e:
                logger.error(f"Error reading CSV file: {str(e)}")
        
        # Parse the file
        try:
            logger.info("Starting file parsing...")
            result = parser.parse(filepath)
            logger.info("Successfully parsed file")
        except Exception as e:
            logger.error(f"Error during parsing: {str(e)}", exc_info=True)
            return
        
        # Log the results
        try:
            logger.info("\nTitle:")
            logger.info("-" * 50)
            logger.info(result.title)
            
            logger.info("\nContent (first 200 chars):")
            logger.info("-" * 50)
            logger.info(format_section_content(result.content))
            
            logger.info("\nSections:")
            logger.info("-" * 50)
            logger.info(f"Found {len(result.sections)} sections")
            
            # Handle both Dict[str, str] and List[Dict[str, Any]] section types
            if isinstance(result.sections, dict):
                # Handle Dict[str, str] sections
                for section_name, section_content in result.sections.items():
                    logger.info(f"\n{section_name}:")
                    logger.info("-" * 30)
                    formatted_content = format_section_content(section_content)
                    if formatted_content:
                        logger.info(formatted_content)
                    else:
                        logger.info("(empty section)")
            else:
                # Handle List[Dict[str, Any]] sections
                for section in result.sections:
                    title = section.get('title', 'Untitled Section')
                    content = section.get('content', '')
                    level = section.get('level', 1)
                    
                    logger.info(f"\n{'  ' * (level-1)}{title}:")
                    logger.info("-" * 30)
                    formatted_content = format_section_content(content)
                    if formatted_content:
                        logger.info(formatted_content)
                    else:
                        logger.info("(empty section)")
                
            logger.info("\nMetadata:")
            logger.info("-" * 50)
            for key, value in result.metadata.items():
                logger.info(f"{key}: {value}")
                
            logger.info(f"\nCompleted testing {filepath}")
                
        except Exception as e:
            logger.error(f"Error displaying results: {str(e)}", exc_info=True)
            
    except Exception as e:
        logger.error(f"Error testing parser for {filepath}: {str(e)}", exc_info=True)

def main():
    """Main test function"""
    try:
        # Test files directory
        test_dir = "test_files"
        
        # Create test directory if it doesn't exist
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            logger.info(f"Created test directory: {test_dir}")
            
        # Create sample test files
        test_files = {
            "sample.txt": """This is a sample text file.
It has multiple lines.
And some content.
This is a new paragraph.

This is another paragraph with some interesting content.
It contains various words and sentences.""",
            
            "sample.csv": """header1,header2,header3
value1,value2,value3
value4,value5,value6
value7,value8,value9""",
            
            "sample.json": """{
    "key": "value",
    "array": [1, 2, 3],
    "nested": {
        "field": "data",
        "numbers": [4, 5, 6]
    }
}"""
        }
        
        # Create test files
        for filename, content in test_files.items():
            filepath = os.path.join(test_dir, filename)
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"Created test file: {filepath}")
            except Exception as e:
                logger.error(f"Error creating test file {filepath}: {str(e)}")
                continue
            
        # Test files in a specific order
        test_order = ["sample.txt", "sample.csv", "sample.json"]
        
        for filename in test_order:
            filepath = os.path.join(test_dir, filename)
            logger.info(f"\n{'='*50}")
            logger.info(f"Starting test for {filename}")
            logger.info(f"{'='*50}")
            
            if not os.path.exists(filepath):
                logger.error(f"Test file not found: {filepath}")
                continue
                
            try:
                # Verify file content
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    logger.info(f"File content verified, size: {len(content)} bytes")
                
                # Run the test
                test_parser(filepath)
                
                # Add a small delay between tests
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to test {filepath}: {str(e)}", exc_info=True)
                continue
                
        logger.info("\nAll tests completed.")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main() 