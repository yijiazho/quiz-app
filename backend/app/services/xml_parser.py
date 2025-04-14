import logging
import os
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from xml.dom import minidom

from app.core.parser_interface import FileParserInterface, ParserResult

logger = logging.getLogger(__name__)


class XMLParser(FileParserInterface):
    """
    Parser for XML (eXtensible Markup Language) files.
    """
    
    def __init__(self):
        """Initialize the XML parser."""
        pass
        
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse an XML file and return its structured content.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            A dictionary containing the parsed content
        """
        logger.info(f"Parsing XML file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            # Extract title from filename if no explicit title is found
            filename = os.path.basename(file_path)
            title = os.path.splitext(filename)[0]
            
            # Get full text content
            text = self.get_full_text(file_path)
            
            # Get metadata
            metadata = self._extract_metadata(file_path)
            
            # Get sections
            sections = self.get_sections(file_path)
            
            # Create result
            result = ParserResult(
                title=title,
                content=text,
                sections=sections,
                metadata=metadata
            )
            
            return result.to_dict()
            
        except Exception as e:
            logger.error(f"Error parsing XML file {file_path}: {str(e)}")
            raise
    
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from an XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            The extracted text content
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
                logger.error(f"Error reading XML file with alternate encoding {file_path}: {str(e)}")
                raise
        except Exception as e:
            logger.error(f"Error extracting text from XML file {file_path}: {str(e)}")
            raise
    
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from an XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            A list of sections, each containing title and content
        """
        try:
            # Parse XML data
            root = self._parse_xml_data(file_path)
            sections = []
            
            # Add root element as a section
            sections.append({
                "title": "Root Element",
                "content": f"<{root.tag}> (with {len(root)} direct children)",
                "level": 1
            })
            
            # Add structure section
            structure_content = self._get_xml_structure(root)
            sections.append({
                "title": "Structure",
                "content": structure_content,
                "level": 1
            })
            
            # Add sections for each main child element
            for child in root:
                # For each direct child of root, create a section
                section_title = child.tag
                
                # If the child has a 'name' or 'id' attribute, include it in the title
                for attr_name in ['name', 'id', 'title', 'type']:
                    if attr_name in child.attrib:
                        section_title = f"{child.tag} - {child.attrib[attr_name]}"
                        break
                        
                # Format the child as pretty XML
                try:
                    child_xml = ET.tostring(child, encoding='unicode')
                    # Try to pretty-print if possible, but keep original if it fails
                    try:
                        xml_dom = minidom.parseString(child_xml)
                        section_content = xml_dom.toprettyxml(indent="  ")
                    except:
                        section_content = child_xml
                except:
                    # Fallback if conversion fails
                    section_content = f"<{child.tag}> with {len(child)} children and {len(child.attrib)} attributes"
                    
                    if child.attrib:
                        section_content += "\n\nAttributes: " + ", ".join([f"{k}='{v}'" for k, v in child.attrib.items()])
                        
                sections.append({
                    "title": section_title,
                    "content": section_content,
                    "level": 2
                })
                
            # If the XML has too many root children, limit them
            if len(root) > 10:
                # Keep the first sections we've already added
                truncated_sections = sections[:12]  # Root + Structure + First 10 children
                truncated_sections.append({
                    "title": "Note",
                    "content": f"Showing only the first 10 of {len(root)} child elements.",
                    "level": 1
                })
                sections = truncated_sections
                
            # If no sections were created or if there's an error, add a fallback section with the raw XML
            if not sections:
                full_text = self.get_full_text(file_path)
                sections = [{"title": "XML Content", "content": full_text, "level": 1}]
                
            return sections
            
        except Exception as e:
            logger.warning(f"Error extracting sections from XML file {file_path}: {str(e)}")
            # Fallback to raw text
            full_text = self.get_full_text(file_path)
            return [{"title": "XML Content", "content": full_text, "level": 1}]
    
    def _parse_xml_data(self, file_path: str) -> ET.Element:
        """
        Parse XML data from a file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            The root element of the XML document
        """
        try:
            tree = ET.parse(file_path)
            return tree.getroot()
        except ET.ParseError as e:
            logger.warning(f"XML parse error in {file_path}: {str(e)}")
            # Try to fix common XML issues
            content = self.get_full_text(file_path)
            
            # Try with lxml if available (more lenient parser)
            try:
                import lxml.etree as lxml_et
                tree = lxml_et.fromstring(content.encode('utf-8'))
                # Convert lxml Element to standard ElementTree Element
                return ET.fromstring(lxml_et.tostring(tree))
            except ImportError:
                # lxml not available, try alternative approach
                pass
            except Exception as lxml_error:
                logger.debug(f"lxml parsing failed: {str(lxml_error)}")
                
            # Last resort: try to fix common issues manually
            try:
                # Remove XML declaration if malformed
                if '<?xml' in content and '?>' not in content[:100]:
                    content = content.replace('<?xml', '')
                    
                # Try parsing again
                return ET.fromstring(content)
            except ET.ParseError:
                raise ValueError(f"Unable to parse XML file: {file_path}")
    
    def _get_xml_structure(self, element: ET.Element, level: int = 0, max_depth: int = 3) -> str:
        """
        Generate a text representation of the XML structure.
        
        Args:
            element: The XML element to analyze
            level: Current indentation level
            max_depth: Maximum depth to traverse
            
        Returns:
            Text representation of the structure
        """
        if level > max_depth:
            return "  " * level + "..."
            
        indent = "  " * level
        result = f"{indent}<{element.tag}"
        
        # Add attributes
        if element.attrib:
            attrs = [f"{k}='{v}'" for k, v in list(element.attrib.items())[:3]]
            if len(element.attrib) > 3:
                attrs.append("...")
            result += " " + " ".join(attrs)
            
        if len(element) == 0 and not element.text:
            result += "/>"
            return result
            
        result += ">"
        
        # If element has text content
        if element.text and element.text.strip():
            text = element.text.strip()
            if len(text) > 30:
                text = text[:30] + "..."
            result += f" {text} "
            
        # Process child elements
        if len(element) > 0:
            result += "\n"
            
            # Limit the number of children shown
            child_count = len(element)
            max_children = 5
            
            for i, child in enumerate(element):
                if i < max_children:
                    result += self._get_xml_structure(child, level + 1, max_depth) + "\n"
                else:
                    result += f"{indent}  ... ({child_count - max_children} more elements)\n"
                    break
                    
            result += f"{indent}</{element.tag}>"
        else:
            result += f"</{element.tag}>"
            
        return result
    
    def _extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from an XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            A dictionary containing metadata
        """
        try:
            file_stats = os.stat(file_path)
            
            # Basic file metadata
            metadata = {
                "file_size": file_stats.st_size,
                "created": file_stats.st_ctime,
                "modified": file_stats.st_mtime,
                "file_type": "application/xml",
                "file_name": os.path.basename(file_path)
            }
            
            # Parse XML to get structure information
            try:
                root = self._parse_xml_data(file_path)
                
                # XML-specific metadata
                metadata.update({
                    "root_element": root.tag,
                    "root_attributes": dict(root.attrib),
                    "child_elements_count": len(root),
                })
                
                # Get unique child tags
                child_tags = {}
                for child in root.iter():
                    if child != root:  # Skip the root element
                        tag = child.tag
                        child_tags[tag] = child_tags.get(tag, 0) + 1
                        
                metadata["element_counts"] = child_tags
                
                # Get namespaces if any
                namespaces = {}
                for prefix, uri in root.nsmap.items() if hasattr(root, 'nsmap') else []:
                    namespaces[prefix or 'default'] = uri
                
                if namespaces:
                    metadata["namespaces"] = namespaces
                    
            except Exception as e:
                logger.debug(f"Error extracting XML structure metadata: {str(e)}")
                
            return metadata
                
        except Exception as e:
            logger.warning(f"Error extracting metadata from XML file {file_path}: {str(e)}")
            # Return basic file metadata if extraction fails
            return {
                "file_size": os.path.getsize(file_path),
                "file_type": "application/xml",
                "file_name": os.path.basename(file_path)
            } 