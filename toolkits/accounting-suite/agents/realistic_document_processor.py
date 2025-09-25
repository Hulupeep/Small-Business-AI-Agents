"""
Document Processor Agent
Realistic document processing using OCR and AI categorization
"""

import re
import json
import datetime
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import pytesseract
import openai
from pathlib import Path
import logging

class DocumentType(Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    BANK_STATEMENT = "bank_statement"
    BILL = "bill"
    OTHER = "other"

class ExpenseCategory(Enum):
    OFFICE_SUPPLIES = "office_supplies"
    TRAVEL = "travel"
    MEALS = "meals"
    UTILITIES = "utilities"
    RENT = "rent"
    PROFESSIONAL_SERVICES = "professional_services"
    MARKETING = "marketing"
    INSURANCE = "insurance"
    EQUIPMENT = "equipment"
    SOFTWARE = "software"
    UNCATEGORIZED = "uncategorized"

@dataclass
class ProcessedDocument:
    document_id: str
    document_type: DocumentType
    extracted_data: Dict
    confidence_score: float
    validation_errors: List[str]
    category: Optional[ExpenseCategory]
    processing_timestamp: datetime.datetime
    file_path: str

@dataclass
class InvoiceData:
    invoice_number: str
    date: datetime.date
    due_date: datetime.date
    client_name: str
    client_email: str
    line_items: List[Dict]
    subtotal: float
    tax_amount: float
    total: float

class DocumentProcessor:
    """
    Document Processor for small accounting practices
    Uses OCR and OpenAI for document processing and expense categorization
    """

    def __init__(self, openai_api_key: str = None):
        # Initialize OpenAI client
        self.openai_client = None
        if openai_api_key:
            openai.api_key = openai_api_key
            self.openai_client = openai

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Common expense categories and keywords
        self.expense_keywords = {
            ExpenseCategory.OFFICE_SUPPLIES: [
                'stationery', 'paper', 'printer', 'pens', 'supplies', 'office depot', 'staples'
            ],
            ExpenseCategory.TRAVEL: [
                'hotel', 'flight', 'train', 'taxi', 'uber', 'lyft', 'gas', 'fuel', 'mileage'
            ],
            ExpenseCategory.MEALS: [
                'restaurant', 'food', 'coffee', 'lunch', 'dinner', 'catering', 'starbucks'
            ],
            ExpenseCategory.UTILITIES: [
                'electricity', 'gas', 'water', 'internet', 'phone', 'mobile', 'broadband'
            ],
            ExpenseCategory.RENT: [
                'rent', 'lease', 'rental', 'property', 'office space'
            ],
            ExpenseCategory.PROFESSIONAL_SERVICES: [
                'consultant', 'lawyer', 'accountant', 'legal', 'audit', 'advisory'
            ],
            ExpenseCategory.MARKETING: [
                'advertising', 'marketing', 'promotion', 'social media', 'google ads'
            ],
            ExpenseCategory.SOFTWARE: [
                'software', 'saas', 'subscription', 'license', 'microsoft', 'adobe'
            ],
            ExpenseCategory.EQUIPMENT: [
                'computer', 'laptop', 'monitor', 'hardware', 'equipment', 'machinery'
            ]
        }

    def process_document(self, file_path: str, document_type: str = "auto") -> ProcessedDocument:
        """Main document processing function"""

        try:
            # Determine document type if auto
            if document_type == "auto":
                doc_type = self._detect_document_type(file_path)
            else:
                doc_type = DocumentType(document_type)

            # Extract text using OCR
            extracted_text = self._extract_text_ocr(file_path)

            # Parse document based on type
            if doc_type == DocumentType.RECEIPT:
                extracted_data = self._parse_receipt(extracted_text)
            elif doc_type == DocumentType.INVOICE:
                extracted_data = self._parse_invoice(extracted_text)
            else:
                extracted_data = self._parse_generic_document(extracted_text)

            # Categorize expense using AI
            category = self._categorize_expense_ai(
                extracted_data.get('description', ''),
                extracted_data.get('vendor', '')
            )

            # Validate extracted data
            validation_errors = self._validate_document(extracted_data, doc_type)

            # Calculate confidence score
            confidence = self._calculate_confidence(extracted_data, validation_errors)

            # Create processed document
            document_id = f"DOC_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"

            return ProcessedDocument(
                document_id=document_id,
                document_type=doc_type,
                extracted_data=extracted_data,
                confidence_score=confidence,
                validation_errors=validation_errors,
                category=category,
                processing_timestamp=datetime.datetime.now(),
                file_path=file_path
            )

        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
            raise

    def _extract_text_ocr(self, file_path: str) -> str:
        """Extract text from image using Tesseract OCR"""

        try:
            # Load and preprocess image
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not load image: {file_path}")

            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 5)

            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Extract text
            text = pytesseract.image_to_string(thresh, config='--psm 6')

            return text.strip()

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""

    def _detect_document_type(self, file_path: str) -> DocumentType:
        """Auto-detect document type from filename and content"""

        filename = Path(file_path).name.lower()

        if any(word in filename for word in ['receipt', 'rcpt']):
            return DocumentType.RECEIPT
        elif any(word in filename for word in ['invoice', 'inv']):
            return DocumentType.INVOICE
        elif any(word in filename for word in ['statement', 'bank']):
            return DocumentType.BANK_STATEMENT
        else:
            return DocumentType.OTHER

    def _parse_receipt(self, text: str) -> Dict:
        """Parse receipt text and extract key information"""

        receipt_data = {
            'vendor': '',
            'date': None,
            'total_amount': 0.0,
            'tax_amount': 0.0,
            'description': '',
            'raw_text': text
        }

        lines = text.split('\n')

        # Extract vendor (usually first non-empty line)
        for line in lines:
            if line.strip():
                receipt_data['vendor'] = line.strip()
                break

        # Extract total amount
        amount_patterns = [
            r'total[:\s]*\$?(\d+\.?\d*)',
            r'amount[:\s]*\$?(\d+\.?\d*)',
            r'\$(\d+\.?\d*)\s*total'
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    receipt_data['total_amount'] = float(match.group(1))
                    break
                except ValueError:
                    continue

        # Extract date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(\w+ \d{1,2}, \d{4})'
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group(1)
                    receipt_data['date'] = self._parse_date(date_str)
                    break
                except:
                    continue

        # Create description from vendor and key items
        receipt_data['description'] = f"{receipt_data['vendor']} - Receipt"

        return receipt_data

    def _parse_invoice(self, text: str) -> Dict:
        """Parse invoice text and extract key information"""

        invoice_data = {
            'invoice_number': '',
            'vendor': '',
            'date': None,
            'due_date': None,
            'total_amount': 0.0,
            'description': '',
            'raw_text': text
        }

        # Extract invoice number
        inv_patterns = [
            r'invoice[#:\s]*(\w+)',
            r'inv[#:\s]*(\w+)',
            r'#(\w+)'
        ]

        for pattern in inv_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_data['invoice_number'] = match.group(1)
                break

        # Extract vendor name (first substantial line)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 3 and not line.strip().isdigit():
                invoice_data['vendor'] = line.strip()
                break

        # Extract amounts (similar to receipt)
        amount_match = re.search(r'total[:\s]*\$?(\d+\.?\d*)', text, re.IGNORECASE)
        if amount_match:
            try:
                invoice_data['total_amount'] = float(amount_match.group(1))
            except ValueError:
                pass

        invoice_data['description'] = f"Invoice from {invoice_data['vendor']}"

        return invoice_data

    def _parse_generic_document(self, text: str) -> Dict:
        """Parse generic document"""

        return {
            'description': text[:100] + "..." if len(text) > 100 else text,
            'raw_text': text,
            'total_amount': 0.0
        }

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse various date formats"""

        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%Y-%m-%d',
            '%B %d, %Y', '%b %d, %Y'
        ]

        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        # Return today's date as fallback
        return datetime.date.today()

    def _categorize_expense_ai(self, description: str, vendor: str = '') -> Optional[ExpenseCategory]:
        """Categorize expense using AI if available, fallback to keyword matching"""

        if self.openai_client and (description or vendor):
            try:
                return self._ai_categorize_expense(description, vendor)
            except Exception as e:
                self.logger.warning(f"AI categorization failed: {e}")

        # Fallback to keyword matching
        return self._categorize_expense_keywords(description + " " + vendor)

    def _ai_categorize_expense(self, description: str, vendor: str = '') -> Optional[ExpenseCategory]:
        """Use OpenAI to categorize expense"""

        categories = [cat.value for cat in ExpenseCategory]
        prompt = f"""
        Categorize this business expense into one of these categories:
        {', '.join(categories)}

        Vendor: {vendor}
        Description: {description}

        Respond with only the category name exactly as listed above.
        """

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an accounting assistant that categorizes business expenses. Respond only with the exact category name from the provided list."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )

            category_name = response.choices[0].message.content.strip().lower()

            # Match to ExpenseCategory enum
            for category in ExpenseCategory:
                if category.value == category_name:
                    return category

        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")

        return ExpenseCategory.UNCATEGORIZED

    def _categorize_expense_keywords(self, text: str) -> ExpenseCategory:
        """Categorize expense based on keywords"""

        text_lower = text.lower()

        for category, keywords in self.expense_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category

        return ExpenseCategory.UNCATEGORIZED

    def _validate_document(self, data: Dict, doc_type: DocumentType) -> List[str]:
        """Validate extracted document data"""

        errors = []

        # Check for required fields based on document type
        if doc_type == DocumentType.RECEIPT:
            if not data.get('vendor'):
                errors.append("Missing vendor information")
            if not data.get('total_amount'):
                errors.append("Missing total amount")
            if not data.get('date'):
                errors.append("Missing transaction date")

        elif doc_type == DocumentType.INVOICE:
            if not data.get('vendor'):
                errors.append("Missing vendor information")
            if not data.get('total_amount'):
                errors.append("Missing total amount")

        # Validate amounts are reasonable
        amount = data.get('total_amount', 0)
        if amount > 10000:
            errors.append("Unusually high amount - please verify")
        elif amount < 0:
            errors.append("Negative amount detected")

        return errors

    def _calculate_confidence(self, data: Dict, errors: List[str]) -> float:
        """Calculate confidence score for extracted data"""

        score = 100.0

        # Reduce score for missing data
        required_fields = ['vendor', 'total_amount', 'date']
        for field in required_fields:
            if not data.get(field):
                score -= 25

        # Reduce score for validation errors
        score -= len(errors) * 15

        # Boost score for having detailed information
        if data.get('description') and len(data['description']) > 10:
            score += 10

        return max(0, min(100, score))

    def create_invoice_template(self, client_data: Dict, line_items: List[Dict]) -> InvoiceData:
        """Generate invoice from template"""

        subtotal = sum(item.get('amount', 0) for item in line_items)
        tax_rate = 0.0875  # Example tax rate
        tax_amount = subtotal * tax_rate if client_data.get('tax_exempt', False) is False else 0
        total = subtotal + tax_amount

        invoice = InvoiceData(
            invoice_number=f"INV-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}",
            date=datetime.date.today(),
            due_date=datetime.date.today() + datetime.timedelta(days=30),
            client_name=client_data['name'],
            client_email=client_data['email'],
            line_items=line_items,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total
        )

        return invoice

    def generate_expense_report(self, expenses: List[ProcessedDocument],
                              start_date: datetime.date, end_date: datetime.date) -> Dict:
        """Generate expense report summary"""

        # Filter expenses by date
        period_expenses = [
            exp for exp in expenses
            if start_date <= exp.processing_timestamp.date() <= end_date
        ]

        # Group by category
        category_totals = {}
        total_amount = 0

        for expense in period_expenses:
            category = expense.category.value if expense.category else 'uncategorized'
            amount = expense.extracted_data.get('total_amount', 0)

            if category not in category_totals:
                category_totals[category] = {'count': 0, 'amount': 0, 'expenses': []}

            category_totals[category]['count'] += 1
            category_totals[category]['amount'] += amount
            category_totals[category]['expenses'].append(expense.document_id)
            total_amount += amount

        report = {
            'period': f"{start_date} to {end_date}",
            'total_expenses': len(period_expenses),
            'total_amount': round(total_amount, 2),
            'category_breakdown': category_totals,
            'average_expense': round(total_amount / len(period_expenses), 2) if period_expenses else 0,
            'generated_at': datetime.datetime.now().isoformat()
        }

        return report

    def get_monthly_dashboard_data(self, expenses: List[ProcessedDocument]) -> Dict:
        """Generate monthly dashboard data"""

        today = datetime.date.today()
        first_day = today.replace(day=1)

        # Current month expenses
        current_month = [
            exp for exp in expenses
            if exp.processing_timestamp.date() >= first_day
        ]

        # Previous month for comparison
        if first_day.month == 1:
            prev_month_start = datetime.date(first_day.year - 1, 12, 1)
            prev_month_end = datetime.date(first_day.year, first_day.month, 1) - datetime.timedelta(days=1)
        else:
            prev_month_start = datetime.date(first_day.year, first_day.month - 1, 1)
            prev_month_end = first_day - datetime.timedelta(days=1)

        previous_month = [
            exp for exp in expenses
            if prev_month_start <= exp.processing_timestamp.date() <= prev_month_end
        ]

        current_total = sum(exp.extracted_data.get('total_amount', 0) for exp in current_month)
        previous_total = sum(exp.extracted_data.get('total_amount', 0) for exp in previous_month)

        # Calculate change
        change_percent = 0
        if previous_total > 0:
            change_percent = ((current_total - previous_total) / previous_total) * 100

        # Top categories this month
        category_totals = {}
        for expense in current_month:
            category = expense.category.value if expense.category else 'uncategorized'
            amount = expense.extracted_data.get('total_amount', 0)
            category_totals[category] = category_totals.get(category, 0) + amount

        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]

        dashboard = {
            'current_month_total': round(current_total, 2),
            'previous_month_total': round(previous_total, 2),
            'change_percent': round(change_percent, 1),
            'expense_count': len(current_month),
            'average_expense': round(current_total / len(current_month), 2) if current_month else 0,
            'top_categories': top_categories,
            'last_updated': datetime.datetime.now().isoformat()
        }

        return dashboard

# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    api_key = os.getenv('OPENAI_API_KEY')
    processor = DocumentProcessor(openai_api_key=api_key)

    # Test with a sample document (would need actual image file)
    # processed_doc = processor.process_document('sample_receipt.jpg', 'receipt')
    # print(f"Processed document: {processed_doc.document_id}")
    # print(f"Category: {processed_doc.category}")
    # print(f"Confidence: {processed_doc.confidence_score}%")

    print("Document processor initialized successfully")