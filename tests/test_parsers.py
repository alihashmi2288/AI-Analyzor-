"""
Unit tests for document parsers
"""

import pytest
import io
from src.parsers import DocumentParser

class TestDocumentParser:
    
    def setup_method(self):
        """Setup test fixtures"""
        self.parser = DocumentParser()
    
    def test_parser_initialization(self):
        """Test parser initialization"""
        assert self.parser.supported_formats == ['pdf', 'docx', 'txt']
    
    def test_validate_file_none(self):
        """Test file validation with None input"""
        assert not self.parser.validate_file(None)
    
    def test_get_file_info_none(self):
        """Test file info with None input"""
        assert self.parser.get_file_info(None) == {}
    
    def test_extract_text_none(self):
        """Test text extraction with None input"""
        assert self.parser.extract_text(None) == ""
    
    def test_extract_from_txt(self):
        """Test text extraction from TXT content"""
        # Create mock file object
        txt_content = "This is a test resume content."
        mock_file = io.BytesIO(txt_content.encode('utf-8'))
        mock_file.type = "text/plain"
        mock_file.name = "test.txt"
        mock_file.size = len(txt_content)
        
        result = self.parser._extract_from_txt(mock_file)
        assert result == txt_content
    
    def test_supported_formats(self):
        """Test supported file formats"""
        expected_formats = ['pdf', 'docx', 'txt']
        assert self.parser.supported_formats == expected_formats
    
    @pytest.mark.parametrize("file_extension,expected", [
        ("pdf", True),
        ("docx", True), 
        ("txt", True),
        ("doc", False),
        ("xlsx", False)
    ])
    def test_file_format_validation(self, file_extension, expected):
        """Test file format validation"""
        # This would require mocking file objects with different extensions
        # Implementation depends on how validate_file method works
        pass