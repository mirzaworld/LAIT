"""
Enhanced PDF parsing service with PII redaction and comprehensive error handling
"""
import pdfplumber
import re
from typing import Dict, List, Any, Tuple
import logging
from datetime import datetime
import pandas as pd
import spacy
from services.s3_service import S3Service
from services.audit_service import AuditLogger

logger = logging.getLogger(__name__)

class PDFParser:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
        
        self.s3_service = S3Service()
        
    def extract_invoice_data(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Extract and process invoice data from PDF with error handling and PII redaction
        """
        try:
            with pdfplumber.open(file_path) as pdf:
                raw_text = ""
                tables = []
                
                # Extract text and tables from all pages
                for page in pdf.pages:
                    raw_text += page.extract_text() + "\n"
                    tables.extend(page.extract_tables())
                
                # Redact PII from text
                redacted_text = self._redact_pii(raw_text)
                
                # Extract structured data
                invoice_data = {
                    'metadata': self._extract_metadata(pdf),
                    'vendor_info': self._extract_vendor_info(redacted_text),
                    'invoice_details': self._extract_invoice_details(redacted_text),
                    'line_items': self._process_tables(tables),
                }
                
                # Validate extracted data
                self._validate_invoice_data(invoice_data)
                
                # Store original file in S3
                s3_path = self.s3_service.upload_file(
                    open(file_path, 'rb'),
                    f"invoices/{datetime.now().strftime('%Y/%m/%d')}/{original_filename}",
                    'application/pdf'
                )
                
                invoice_data['file_location'] = s3_path
                
                # Log successful extraction
                AuditLogger.log_event(
                    'invoice_parse',
                    {'filename': original_filename, 'status': 'success'},
                    resource_type='invoice'
                )
                
                return invoice_data
                
        except Exception as e:
            logger.error(f"Error processing PDF {original_filename}: {str(e)}")
            AuditLogger.log_event(
                'invoice_parse',
                {'filename': original_filename, 'error': str(e)},
                status='error',
                resource_type='invoice'
            )
            raise
    
    def _redact_pii(self, text: str) -> str:
        """
        Redact PII from text using spaCy NER
        """
        doc = self.nlp(text)
        redacted_text = text
        
        # Collect all entities to redact
        entities_to_redact = []
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'EMAIL', 'PHONE', 'SSN']:
                entities_to_redact.append((ent.start_char, ent.end_char))
        
        # Additional pattern matching for sensitive data
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'
        }
        
        for pattern_type, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities_to_redact.append(match.span())
        
        # Sort and merge overlapping ranges
        entities_to_redact.sort(key=lambda x: x[0])
        merged = []
        for start, end in entities_to_redact:
            if not merged or merged[-1][1] < start:
                merged.append((start, end))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        
        # Redact text from end to start to preserve indices
        for start, end in reversed(merged):
            redacted_text = redacted_text[:start] + '[REDACTED]' + redacted_text[end:]
        
        return redacted_text
    
    def _extract_metadata(self, pdf) -> Dict[str, Any]:
        """Extract PDF metadata"""
        return {
            'pages': len(pdf.pages),
            'metadata': pdf.metadata
        }
    
    def _extract_vendor_info(self, text: str) -> Dict[str, str]:
        """Extract vendor information using regex patterns"""
        patterns = {
            'company_name': r'(?i)(?:Company|Vendor|From):\s*([^\n]+)',
            'address': r'(?i)Address:\s*([^\n]+)',
            'tax_id': r'(?i)(?:Tax ID|EIN):\s*([^\n]+)',
            'contact': r'(?i)Contact:\s*([^\n]+)'
        }
        
        vendor_info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                vendor_info[key] = match.group(1).strip()
        
        return vendor_info
    
    def _extract_invoice_details(self, text: str) -> Dict[str, Any]:
        """Extract invoice details using regex patterns"""
        patterns = {
            'invoice_number': r'(?i)Invoice\s*#?:\s*([^\n]+)',
            'date': r'(?i)Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'due_date': r'(?i)Due\s*Date:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'total_amount': r'(?i)Total:\s*\$?([\d,]+\.?\d*)',
            'matter_number': r'(?i)Matter\s*#?:\s*([^\n]+)'
        }
        
        invoice_details = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                if key in ['date', 'due_date']:
                    try:
                        value = pd.to_datetime(value).strftime('%Y-%m-%d')
                    except:
                        logger.warning(f"Could not parse date: {value}")
                elif key == 'total_amount':
                    value = float(value.replace(',', ''))
                invoice_details[key] = value
        
        return invoice_details
    
    def _process_tables(self, tables: List[List[str]]) -> List[Dict[str, Any]]:
        """Process and structure tabular data from the invoice"""
        line_items = []
        
        for table in tables:
            if not table or not table[0]:  # Skip empty tables
                continue
                
            # Try to identify header row
            header_row = self._identify_header_row(table)
            if header_row is None:
                continue
                
            # Convert table to pandas DataFrame
            df = pd.DataFrame(table[header_row + 1:], columns=table[header_row])
            
            # Clean column names
            df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
            
            # Process each row
            for _, row in df.iterrows():
                line_item = {}
                
                # Extract relevant fields
                for col in df.columns:
                    value = row[col]
                    if pd.isna(value) or value == '':
                        continue
                        
                    # Convert amounts to float
                    if any(x in col for x in ['amount', 'rate', 'total']):
                        try:
                            value = float(str(value).replace('$', '').replace(',', ''))
                        except:
                            continue
                            
                    # Convert hours to float
                    if 'hours' in col:
                        try:
                            value = float(value)
                        except:
                            continue
                            
                    line_item[col] = value
                
                if line_item:  # Only add non-empty line items
                    line_items.append(line_item)
        
        return line_items
    
    def _identify_header_row(self, table: List[List[str]]) -> int:
        """Identify the header row in a table"""
        header_keywords = ['description', 'amount', 'hours', 'rate', 'total', 'date']
        
        for i, row in enumerate(table):
            row_text = ' '.join(str(cell).lower() for cell in row)
            if any(keyword in row_text for keyword in header_keywords):
                return i
        
        return None
    
    def _validate_invoice_data(self, data: Dict[str, Any]) -> None:
        """Validate extracted invoice data"""
        required_fields = {
            'invoice_details': ['invoice_number', 'date', 'total_amount'],
            'vendor_info': ['company_name']
        }
        
        for section, fields in required_fields.items():
            if section not in data:
                raise ValueError(f"Missing required section: {section}")
            
            for field in fields:
                if field not in data[section]:
                    raise ValueError(f"Missing required field: {field} in {section}")
                
        # Validate line items
        if 'line_items' not in data or not data['line_items']:
            raise ValueError("No line items found in invoice")
