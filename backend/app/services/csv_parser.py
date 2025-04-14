import csv
import logging
import os
from typing import Dict, Any, List, Optional

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class CSVParser(FileParserInterface):
    """
    Parser for CSV (Comma-Separated Values) files.
    """
    
    def __init__(self):
        """Initialize the CSV parser."""
        pass
        
    def parse(self, file_path: str) -> ParserResult:
        """
        Parse a CSV file and return its structured content.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            A ParserResult object containing the parsed content
        """
        logger.info(f"Parsing CSV file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            text = self.get_full_text(file_path)
            metadata = self._extract_metadata(file_path)
            sections = self.get_sections(file_path)
            
            return ParserResult(
                text=text,
                sections=sections,
                metadata=metadata,
                file_path=file_path
            )
            
        except Exception as e:
            logger.error(f"Error parsing CSV file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            The extracted text content as a formatted string
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                return file.read()
                
        except UnicodeDecodeError:
            # Try different encodings if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading CSV file with alternate encoding {file_path}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error extracting text from CSV file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a CSV file, where each section represents a logical
        part of the data (e.g., header row, data rows).
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            A list of sections, each containing title and content
        """
        try:
            # Try to parse CSV data
            data = self._parse_csv_data(file_path)
            
            sections = []
            
            # Create a section for headers
            if data and data[0]:
                headers = data[0]
                header_section = {
                    "title": "Headers",
                    "content": ", ".join(headers)
                }
                sections.append(header_section)
            
            # Create sections for data overview
            if len(data) > 1:
                data_rows = data[1:]
                
                # Data summary section
                rows_count = len(data_rows)
                summary_section = {
                    "title": "Data Summary",
                    "content": f"Total rows: {rows_count}\nColumns: {len(data[0]) if data[0] else 0}"
                }
                sections.append(summary_section)
                
                # Sample data section (first 10 rows)
                sample_rows = data_rows[:10]
                sample_content = "\n".join([", ".join(row) for row in sample_rows])
                if sample_content:
                    sample_section = {
                        "title": "Sample Data",
                        "content": sample_content
                    }
                    sections.append(sample_section)
                
            # If no sections were found, create a single section with raw content
            if not sections:
                full_text = self.get_full_text(file_path)
                sections = [{"title": "Content", "content": full_text}]
                
            return sections
            
        except Exception as e:
            logger.warning(f"Error extracting sections from CSV file {file_path}: {str(e)}")
            # Fallback to raw text
            full_text = self.get_full_text(file_path)
            return [{"title": "Content", "content": full_text}]
    
    def _parse_csv_data(self, file_path: str) -> List[List[str]]:
        """
        Parse CSV data into a list of rows.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            A list of rows, where each row is a list of string values
        """
        data = []
        
        # Try different delimiters and encodings
        delimiters = [',', ';', '\t', '|']
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            for delimiter in delimiters:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                        reader = csv.reader(file, delimiter=delimiter)
                        data = list(reader)
                        
                    # If we successfully parsed and got multiple rows and columns, return the data
                    if len(data) > 1 and any(len(row) > 1 for row in data):
                        logger.info(f"Successfully parsed CSV with delimiter '{delimiter}' and encoding '{encoding}'")
                        return data
                        
                except Exception as e:
                    logger.debug(f"Failed parsing CSV with delimiter '{delimiter}' and encoding '{encoding}': {str(e)}")
                    continue
        
        # If we reach here, we either have minimal data or none
        # Return whatever we have as a last resort
        if data:
            return data
            
        # Last attempt - just read lines
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                lines = file.readlines()
                return [line.strip().split(',') for line in lines if line.strip()]
        except Exception as e:
            logger.error(f"Failed to parse CSV file {file_path} with any method: {str(e)}")
            return []
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            A dictionary containing metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            # Parse the CSV to get additional metadata
            data = self._parse_csv_data(file_path)
            
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
            }
            
            # Add CSV-specific metadata
            if data:
                metadata.update({
                    "row_count": len(data),
                    "column_count": len(data[0]) if data and data[0] else 0,
                    "has_header": True if data and len(data) > 1 else False
                })
                
                # Try to detect column types
                if len(data) > 1 and data[0]:
                    column_names = data[0]
                    metadata["columns"] = column_names
                
            return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from CSV file {file_path}: {str(e)}")
            # Return basic file metadata if extraction fails
            return {
                "file_size": os.path.getsize(file_path)
            } 