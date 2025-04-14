from abc import ABC, abstractmethod
from typing import List, Dict, Any


class FileParserInterface(ABC):
    """
    Interface for file parsers that extract structured text from different file types.
    """

    @abstractmethod
    def parse(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a file and extract its content as structured text.

        Args:
            file_path: Path to the file to parse

        Returns:
            A dictionary containing:
            - title: The document title (if available)
            - content: The full text content
            - sections: A list of sections with their titles and content
            - metadata: Any additional metadata extracted from the file
        """
        pass

    @abstractmethod
    def get_full_text(self, file_path: str) -> str:
        """
        Extract the full text content from a file without any structure.

        Args:
            file_path: Path to the file to parse

        Returns:
            The full text content as a string
        """
        pass

    @abstractmethod
    def get_sections(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract sections from a file.

        Args:
            file_path: Path to the file to parse

        Returns:
            A list of sections, each containing:
            - title: The section title
            - content: The section content
            - level: The section level/depth (e.g., 1 for chapter, 2 for subchapter)
        """
        pass


class ParserResult:
    """
    Standard result structure for parsed documents.
    """
    def __init__(
        self,
        title: str = "",
        content: str = "",
        sections: List[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ):
        self.title = title
        self.content = content
        self.sections = sections or []
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert the parser result to a dictionary."""
        return {
            "title": self.title,
            "content": self.content,
            "sections": self.sections,
            "metadata": self.metadata,
        } 