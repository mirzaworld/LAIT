import pdfplumber
import re
import logging
from datetime import datetime

class PDFParserService:
    def __init__(self):
        self.patterns = {
            'invoice_number': r'Invoice[:\s#]+([A-Z0-9\-]+)',
            'date': r'Date[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            'total_amount': r'Total[:\s]*\$?([\d,]+\.?\d*)',
            'vendor_name': r'(.*?)\n',  # Usually at the top of invoice
            'matter_number': r'Matter[:\s#]+([A-Z0-9\-]+)'
        }
    
    def parse_invoice(self, pdf_file):
        """Parse an invoice PDF file and extract structured data."""
        try:
            with pdfplumber.open(pdf_file) as pdf:
                text = ""
                line_items = []
                
                # Extract text from all pages
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                    
                    # Try to find tables on each page (for line items)
                    tables = page.extract_tables()
                    for table in tables:
                        line_items.extend(self._process_table(table))
                
                # Extract invoice metadata using regex patterns
                invoice_data = self._extract_metadata(text)
                
                # Add processed line items
                invoice_data['line_items'] = line_items
                
                return invoice_data
                
        except Exception as e:
            logging.error(f"Error parsing PDF: {str(e)}")
            raise

    # Backwards compatible method name used elsewhere
    def parse_pdf(self, pdf_file):
        return self.parse_invoice(pdf_file)

    def _extract_metadata(self, text):
        """Extract invoice metadata using regex patterns."""
        data = {}
        
        for field, pattern in self.patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Convert date to standard format if found
                if field == 'date':
                    try:
                        # Try different date formats
                        for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y']:
                            try:
                                value = datetime.strptime(value, fmt).strftime('%Y-%m-%d')
                                break
                            except ValueError:
                                continue
                    except ValueError:
                        logging.warning(f"Could not parse date: {value}")
                
                # Clean up amount
                if field == 'total_amount':
                    try:
                        value = float(value.replace(',', ''))
                    except ValueError:
                        value = 0.0
                
                data[field] = value
        
        return data
    
    def _process_table(self, table):
        """Process a table extracted from the PDF to find line items."""
        line_items = []
        
        if not table or len(table) < 2:  # Need at least header and one row
            return line_items
        
        # Try to identify columns based on headers
        headers = [str(h).lower() if h else '' for h in table[0]]
        
        # Find important column indices
        desc_col = next((i for i, h in enumerate(headers) if 'description' in h), None)
        hours_col = next((i for i, h in enumerate(headers) if 'hours' in h), None)
        rate_col = next((i for i, h in enumerate(headers) if 'rate' in h), None)
        amount_col = next((i for i, h in enumerate(headers) if 'amount' in h or 'total' in h), None)
        
        # Process each row
        for row in table[1:]:
            if not row or all(cell is None or str(cell).strip() == '' for cell in row):
                continue
                
            line_item = {}
            
            if desc_col is not None and len(row) > desc_col:
                line_item['description'] = str(row[desc_col]).strip()
            
            if hours_col is not None and len(row) > hours_col:
                try:
                    line_item['hours'] = float(str(row[hours_col]).replace(',', ''))
                except (ValueError, TypeError):
                    line_item['hours'] = 0
            
            if rate_col is not None and len(row) > rate_col:
                try:
                    line_item['rate'] = float(str(row[rate_col]).replace('$', '').replace(',', ''))
                except (ValueError, TypeError):
                    line_item['rate'] = 0
            
            if amount_col is not None and len(row) > amount_col:
                try:
                    line_item['amount'] = float(str(row[amount_col]).replace('$', '').replace(',', ''))
                except (ValueError, TypeError):
                    line_item['amount'] = 0
            
            if line_item:
                line_items.append(line_item)
        
        return line_items
