"""
Document parsing module for PDF and DOCX files
Handles text extraction with error handling and optimization
"""

import pdfplumber
import docx2txt
from docx import Document
import streamlit as st
from typing import Optional, Union
import io

class DocumentParser:
    """Handles parsing of PDF and DOCX documents"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'docx', 'txt']
    
    @st.cache_data
    def extract_text(_self, uploaded_file) -> str:
        """Extract text from uploaded file with OCR fallback"""
        if uploaded_file is None:
            return ""
        
        try:
            file_type = uploaded_file.type
            
            if file_type == "application/pdf":
                text = _self._extract_from_pdf(uploaded_file)
                # OCR fallback for scanned PDFs
                if len(text.strip()) < 50:  # Likely scanned PDF
                    text = _self._extract_with_ocr(uploaded_file)
                return text
            elif file_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                return _self._extract_from_docx(uploaded_file)
            elif file_type == "text/plain":
                return _self._extract_from_txt(uploaded_file)
            else:
                st.error(f"Unsupported file type: {file_type}")
                return ""
                
        except Exception as e:
            st.error(f"Error parsing document: {str(e)}")
            return ""
    
    def _extract_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
            return ""
    
    def _extract_from_docx(self, uploaded_file) -> str:
        """Extract text from DOCX file"""
        try:
            # Method 1: Using docx2txt (simpler)
            text = docx2txt.process(uploaded_file)
            if text.strip():
                return text.strip()
            
            # Method 2: Using python-docx (more detailed)
            uploaded_file.seek(0)  # Reset file pointer
            doc = Document(uploaded_file)
            text_parts = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            return "\n".join(text_parts)
            
        except Exception as e:
            st.error(f"Error reading DOCX: {str(e)}")
            return ""
    
    def _extract_from_txt(self, uploaded_file) -> str:
        """Extract text from TXT file"""
        try:
            return str(uploaded_file.read(), "utf-8")
        except Exception as e:
            st.error(f"Error reading TXT: {str(e)}")
            return ""
    
    def _extract_with_ocr(self, uploaded_file) -> str:
        """Extract text using OCR for scanned PDFs"""
        try:
            import pytesseract
            from PIL import Image
            import fitz  # PyMuPDF
            
            # Convert PDF to images and OCR
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                page_text = pytesseract.image_to_string(img)
                text += page_text + "\n"
            
            doc.close()
            return text.strip()
            
        except ImportError:
            st.warning("OCR not available. Install pytesseract and tesseract for scanned PDF support.")
            return ""
        except Exception as e:
            st.warning(f"OCR failed: {str(e)}")
            return ""
    
    def validate_file(self, uploaded_file) -> bool:
        """Validate uploaded file"""
        if uploaded_file is None:
            return False
        
        # Check file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("File size too large. Maximum 10MB allowed.")
            return False
        
        # Check file type
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension not in self.supported_formats:
            st.error(f"Unsupported file format. Supported: {', '.join(self.supported_formats)}")
            return False
        
        return True
    
    def get_file_info(self, uploaded_file) -> dict:
        """Get file information"""
        if uploaded_file is None:
            return {}
        
        return {
            'name': uploaded_file.name,
            'size': uploaded_file.size,
            'type': uploaded_file.type,
            'extension': uploaded_file.name.split('.')[-1].lower()
        }