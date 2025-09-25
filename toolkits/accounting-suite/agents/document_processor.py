"""
Client Document Processor Agent
Intelligent processing of Irish receipts, bank statements, and financial documents
"""

import re
import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from PIL import Image
import pytesseract

class DocumentType(Enum):
    RECEIPT = "receipt"
    BANK_STATEMENT = "bank_statement"
    INVOICE = "invoice"
    PAYROLL = "payroll"
    DIRECTORS_LOAN = "directors_loan"

class ExpenseCategory(Enum):
    MOTOR_EXPENSES = "motor_expenses"
    OFFICE_EXPENSES = "office_expenses"
    TRAVEL = "travel"
    PROFESSIONAL_FEES = "professional_fees"
    ADVERTISING = "advertising"
    UTILITIES = "utilities"
    RENT = "rent"
    ENTERTAINMENT = "entertainment"

@dataclass
class ProcessedDocument:
    document_id: str
    document_type: DocumentType
    extracted_data: Dict
    confidence_score: float
    validation_errors: List[str]
    vat_claimable: bool
    category: Optional[ExpenseCategory]
    processing_timestamp: datetime.datetime

@dataclass
class BankTransaction:
    transaction_id: str
    date: datetime.date
    description: str
    amount: float
    balance: float
    bank_code: str
    account_number: str
    category: Optional[str]
    duplicate_probability: float

class IrishDocumentProcessor:
    """
    Irish Document Processor for accounting practices
    Handles receipt processing, bank reconciliation, and document categorization
    """

    def __init__(self):
        self.vat_rates = {
            0.23: 'standard',
            0.135: 'reduced',
            0.09: 'super_reduced',
            0.0: 'zero'
        }

        # Irish bank codes and formats
        self.irish_banks = {
            'AIB': {'sort_code_pattern': r'^93\d{4}$', 'account_pattern': r'^\d{8}$'},
            'BOI': {'sort_code_pattern': r'^90\d{4}$', 'account_pattern': r'^\d{8}$'},
            'Ulster': {'sort_code_pattern': r'^98\d{4}$', 'account_pattern': r'^\d{8}$'},
            'PTSB': {'sort_code_pattern': r'^99\d{4}$', 'account_pattern': r'^\d{8}$'}
        }

        # Common Irish expense categories and keywords
        self.expense_keywords = {
            ExpenseCategory.MOTOR_EXPENSES: [
                'petrol', 'diesel', 'fuel', 'parking', 'motor tax', 'insurance',
                'garage', 'service', 'tyres', 'breakdown', 'nct', 'toll'
            ],
            ExpenseCategory.OFFICE_EXPENSES: [
                'stationery', 'paper', 'printer', 'computer', 'software',
                'telephone', 'broadband', 'office supplies'
            ],
            ExpenseCategory.TRAVEL: [
                'hotel', 'accommodation', 'train', 'bus', 'taxi', 'flights',
                'meals', 'subsistence', 'conference'
            ],
            ExpenseCategory.PROFESSIONAL_FEES: [
                'solicitor', 'accountant', 'consultant', 'advisor', 'legal',
                'audit', 'tax advice', 'professional services'
            ],
            ExpenseCategory.UTILITIES: [
                'electricity', 'gas', 'water', 'waste', 'heating', 'lighting'
            ]
        }

        # VAT number validation patterns
        self.vat_patterns = {
            'ireland': r'^IE\d{7}[A-Z]{1,2}$',
            'uk': r'^GB\d{9}$|^GB\d{12}$',
            'eu': r'^[A-Z]{2}[\w\d]{8,12}$'
        }

    def process_receipt(self, image_path: str) -> ProcessedDocument:
        """Process Irish VAT receipt using OCR and pattern recognition"""

        # Load and preprocess image
        image = cv2.imread(image_path)
        processed_image = self._preprocess_image(image)

        # Extract text using OCR
        text = pytesseract.image_to_string(processed_image)

        # Parse receipt data
        receipt_data = self._parse_receipt_text(text)

        # Validate Irish VAT compliance
        validation_errors = self._validate_irish_receipt(receipt_data)

        # Determine expense category
        category = self._categorize_expense(receipt_data.get('description', ''))

        # Calculate confidence score
        confidence = self._calculate_confidence(receipt_data, validation_errors)

        return ProcessedDocument(
            document_id=f"RCP_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            document_type=DocumentType.RECEIPT,
            extracted_data=receipt_data,
            confidence_score=confidence,
            validation_errors=validation_errors,
            vat_claimable=self._is_vat_claimable(receipt_data),
            category=category,
            processing_timestamp=datetime.datetime.now()
        )

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply threshold to get black and white image
        _, threshold = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Deskew image if needed
        deskewed = self._deskew_image(threshold)

        return deskewed

    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct image skew for better OCR"""

        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def _parse_receipt_text(self, text: str) -> Dict:
        """Extract structured data from receipt text"""

        receipt_data = {
            'business_name': '',
            'address': '',
            'vat_number': '',
            'date': None,
            'total_amount': 0.0,
            'vat_amount': 0.0,
            'net_amount': 0.0,
            'vat_rate': 0.0,
            'items': [],
            'raw_text': text
        }

        lines = text.split('\n')

        # Extract business name (usually first line)
        if lines:
            receipt_data['business_name'] = lines[0].strip()

        # Extract VAT number
        vat_match = re.search(r'VAT[:\s]*([A-Z]{2}\d+[A-Z]*\d*)', text, re.IGNORECASE)
        if vat_match:
            receipt_data['vat_number'] = vat_match.group(1)

        # Extract date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+\w+\s+\d{2,4})',
            r'(\w+\s+\d{1,2},?\s+\d{2,4})'
        ]

        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                try:
                    date_str = date_match.group(1)
                    # Parse various date formats
                    receipt_data['date'] = self._parse_date(date_str)
                    break
                except:
                    continue

        # Extract total amount
        total_patterns = [
            r'TOTAL[:\s]*€?(\d+\.?\d*)',
            r'AMOUNT[:\s]*€?(\d+\.?\d*)',
            r'€(\d+\.?\d*)\s*TOTAL'
        ]

        for pattern in total_patterns:
            total_match = re.search(pattern, text, re.IGNORECASE)
            if total_match:
                receipt_data['total_amount'] = float(total_match.group(1))
                break

        # Extract VAT information
        vat_patterns = [
            r'VAT[:\s]*€?(\d+\.?\d*)',
            r'(\d+\.?\d*)%?\s*VAT',
            r'VAT\s*@\s*(\d+\.?\d*)%'
        ]

        for pattern in vat_patterns:
            vat_match = re.search(pattern, text, re.IGNORECASE)
            if vat_match:
                vat_value = float(vat_match.group(1))
                if vat_value > 1:  # Likely VAT amount
                    receipt_data['vat_amount'] = vat_value
                else:  # Likely VAT rate
                    receipt_data['vat_rate'] = vat_value / 100

        # Calculate net amount if not provided
        if receipt_data['total_amount'] and receipt_data['vat_amount']:
            receipt_data['net_amount'] = receipt_data['total_amount'] - receipt_data['vat_amount']

        return receipt_data

    def _parse_date(self, date_str: str) -> datetime.date:
        """Parse various date formats"""

        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y',
            '%d %B %Y', '%d %b %Y', '%B %d, %Y', '%b %d, %Y'
        ]

        for fmt in date_formats:
            try:
                return datetime.datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        # If no format matches, return today's date as fallback
        return datetime.date.today()

    def _validate_irish_receipt(self, receipt_data: Dict) -> List[str]:
        """Validate receipt compliance with Irish VAT requirements"""

        errors = []

        # Check required fields
        if not receipt_data.get('business_name'):
            errors.append("Missing business name")

        if not receipt_data.get('date'):
            errors.append("Missing transaction date")

        if not receipt_data.get('total_amount'):
            errors.append("Missing total amount")

        # Validate VAT number format if present
        vat_number = receipt_data.get('vat_number')
        if vat_number and not re.match(self.vat_patterns['ireland'], vat_number):
            errors.append("Invalid Irish VAT number format")

        # Check VAT rate validity
        vat_rate = receipt_data.get('vat_rate', 0)
        if vat_rate and vat_rate not in [0.0, 0.09, 0.135, 0.23]:
            errors.append(f"Invalid VAT rate: {vat_rate}%")

        # Check if receipt is too old for VAT claim
        receipt_date = receipt_data.get('date')
        if receipt_date:
            age_limit = datetime.date.today() - datetime.timedelta(days=1460)  # 4 years
            if receipt_date < age_limit:
                errors.append("Receipt too old for VAT claim (>4 years)")

        return errors

    def _categorize_expense(self, description: str) -> Optional[ExpenseCategory]:
        """Categorize expense based on description"""

        description_lower = description.lower()

        for category, keywords in self.expense_keywords.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category

        return None

    def _is_vat_claimable(self, receipt_data: Dict) -> bool:
        """Determine if VAT can be claimed on this expense"""

        # Must have valid VAT number
        vat_number = receipt_data.get('vat_number')
        if not vat_number or not re.match(self.vat_patterns['ireland'], vat_number):
            return False

        # Must have VAT amount or rate
        vat_amount = receipt_data.get('vat_amount', 0)
        vat_rate = receipt_data.get('vat_rate', 0)
        if not vat_amount and not vat_rate:
            return False

        # Check for non-claimable categories
        category = self._categorize_expense(receipt_data.get('business_name', ''))
        non_claimable = [ExpenseCategory.ENTERTAINMENT]
        if category in non_claimable:
            return False

        return True

    def _calculate_confidence(self, receipt_data: Dict, validation_errors: List[str]) -> float:
        """Calculate confidence score for extracted data"""

        score = 100.0

        # Reduce score for missing required fields
        required_fields = ['business_name', 'date', 'total_amount']
        for field in required_fields:
            if not receipt_data.get(field):
                score -= 20

        # Reduce score for validation errors
        score -= len(validation_errors) * 10

        # Boost score for having VAT information
        if receipt_data.get('vat_number') and receipt_data.get('vat_amount'):
            score += 10

        return max(0, min(100, score))

    def process_bank_statement(self, file_path: str, bank_code: str) -> List[BankTransaction]:
        """Process bank statement and extract transactions"""

        transactions = []

        # Parse based on bank format
        if bank_code in self.irish_banks:
            if file_path.endswith('.csv'):
                transactions = self._parse_csv_bank_statement(file_path, bank_code)
            elif file_path.endswith('.pdf'):
                transactions = self._parse_pdf_bank_statement(file_path, bank_code)

        # Detect duplicates
        transactions = self._detect_duplicate_transactions(transactions)

        # Categorize transactions
        for transaction in transactions:
            transaction.category = self._categorize_bank_transaction(transaction.description)

        return transactions

    def _parse_csv_bank_statement(self, file_path: str, bank_code: str) -> List[BankTransaction]:
        """Parse CSV format bank statement"""

        transactions = []

        # Bank-specific CSV formats
        csv_formats = {
            'AIB': {'date_col': 0, 'desc_col': 1, 'amount_col': 2, 'balance_col': 3},
            'BOI': {'date_col': 0, 'desc_col': 2, 'amount_col': 3, 'balance_col': 4},
            'Ulster': {'date_col': 0, 'desc_col': 1, 'amount_col': 3, 'balance_col': 4},
            'PTSB': {'date_col': 0, 'desc_col': 1, 'amount_col': 2, 'balance_col': 3}
        }

        # This would parse actual CSV files
        # For demo purposes, returning sample data

        sample_transactions = [
            BankTransaction(
                transaction_id="TXN_001",
                date=datetime.date.today(),
                description="VISA PURCHASE - OFFICE SUPPLIES LTD",
                amount=-125.50,
                balance=2500.00,
                bank_code=bank_code,
                account_number="12345678",
                category="office_expenses",
                duplicate_probability=0.0
            )
        ]

        return sample_transactions

    def _detect_duplicate_transactions(self, transactions: List[BankTransaction]) -> List[BankTransaction]:
        """Detect potential duplicate transactions"""

        for i, trans1 in enumerate(transactions):
            for j, trans2 in enumerate(transactions):
                if i != j:
                    # Check for similar amounts, dates, and descriptions
                    amount_similar = abs(trans1.amount - trans2.amount) < 0.01
                    date_similar = abs((trans1.date - trans2.date).days) <= 1
                    desc_similar = self._similarity_score(trans1.description, trans2.description) > 0.8

                    if amount_similar and date_similar and desc_similar:
                        transactions[j].duplicate_probability = 0.9

        return transactions

    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate string similarity score"""

        # Simple Jaccard similarity
        set1 = set(str1.lower().split())
        set2 = set(str2.lower().split())

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0

    def _categorize_bank_transaction(self, description: str) -> str:
        """Categorize bank transaction based on description"""

        description_lower = description.lower()

        # Common transaction patterns
        patterns = {
            'salary': ['salary', 'wages', 'payroll'],
            'utilities': ['electricity', 'gas', 'water', 'phone'],
            'rent': ['rent', 'lease'],
            'loan': ['loan', 'mortgage', 'credit'],
            'transfer': ['transfer', 'tfr'],
            'fee': ['fee', 'charge', 'commission']
        }

        for category, keywords in patterns.items():
            for keyword in keywords:
                if keyword in description_lower:
                    return category

        return 'general'

    def reconcile_accounts(self, bank_transactions: List[BankTransaction],
                          book_transactions: List[Dict]) -> Dict:
        """Perform bank reconciliation"""

        reconciliation = {
            'bank_balance': 0,
            'book_balance': 0,
            'reconciled_items': [],
            'outstanding_deposits': [],
            'outstanding_checks': [],
            'adjustments_needed': [],
            'reconciliation_difference': 0
        }

        # Get latest bank balance
        if bank_transactions:
            reconciliation['bank_balance'] = bank_transactions[-1].balance

        # Calculate book balance
        book_balance = sum(tx.get('amount', 0) for tx in book_transactions)
        reconciliation['book_balance'] = book_balance

        # Match transactions
        for bank_tx in bank_transactions:
            matched = False
            for book_tx in book_transactions:
                if (abs(bank_tx.amount - book_tx.get('amount', 0)) < 0.01 and
                    abs((bank_tx.date - book_tx.get('date', datetime.date.today())).days) <= 2):

                    reconciliation['reconciled_items'].append({
                        'bank_transaction': bank_tx.transaction_id,
                        'book_transaction': book_tx.get('id'),
                        'amount': bank_tx.amount
                    })
                    matched = True
                    break

            if not matched:
                if bank_tx.amount > 0:
                    reconciliation['outstanding_deposits'].append(bank_tx)
                else:
                    reconciliation['outstanding_checks'].append(bank_tx)

        # Calculate difference
        reconciliation['reconciliation_difference'] = (
            reconciliation['bank_balance'] - reconciliation['book_balance']
        )

        return reconciliation

# Example usage
if __name__ == "__main__":
    processor = IrishDocumentProcessor()

    # Test receipt processing
    print("Testing receipt processing...")

    # Test bank reconciliation
    print("Testing bank reconciliation...")

    sample_bank_txns = [
        BankTransaction(
            transaction_id="B001",
            date=datetime.date.today(),
            description="Office Supplies Purchase",
            amount=-250.00,
            balance=1750.00,
            bank_code="AIB",
            account_number="12345678",
            category="office_expenses",
            duplicate_probability=0.0
        )
    ]

    sample_book_txns = [
        {
            'id': 'BK001',
            'date': datetime.date.today(),
            'amount': -250.00,
            'description': 'Office supplies'
        }
    ]

    reconciliation = processor.reconcile_accounts(sample_bank_txns, sample_book_txns)
    print(f"Reconciliation difference: €{reconciliation['reconciliation_difference']:.2f}")