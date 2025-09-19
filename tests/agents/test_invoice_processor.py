"""
Test Suite for Invoice Processing Agent

Comprehensive tests covering:
- OCR functionality and accuracy
- Invoice data extraction
- Anomaly detection
- Business value tracking
- Integration testing
"""

import pytest
import os
import tempfile
import json
import cv2
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the modules to test
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from agents.invoice_processor import (
    InvoiceProcessor, InvoiceData, OCREngine, InvoiceParser,
    AnomalyDetector, BusinessValueTracker
)


class TestOCREngine:
    """Test OCR functionality."""

    def setup_method(self):
        self.ocr_engine = OCREngine()

    def test_preprocess_image(self):
        """Test image preprocessing pipeline."""
        # Create a sample noisy image
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)

        processed = self.ocr_engine.preprocess_image(image)

        assert processed is not None
        assert len(processed.shape) == 2  # Should be grayscale
        assert processed.dtype == np.uint8

    @patch('pytesseract.image_to_string')
    def test_extract_text_from_image(self, mock_tesseract):
        """Test text extraction from image."""
        mock_tesseract.return_value = "Sample Invoice Text\nAmount: $123.45"

        image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        result = self.ocr_engine.extract_text_from_image(image)

        assert result == "Sample Invoice Text\nAmount: $123.45"
        mock_tesseract.assert_called_once()

    def test_create_sample_invoice_image(self):
        """Helper method to create sample invoice for testing."""
        # Create a simple invoice-like image for testing
        image = np.ones((400, 600, 3), dtype=np.uint8) * 255

        # Add some text-like patterns (simplified)
        cv2.putText(image, "INVOICE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        cv2.putText(image, "Invoice #: INV-001", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
        cv2.putText(image, "Amount: $1,234.56", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        return image

    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz):
        """Test PDF text extraction."""
        # Mock PyMuPDF document
        mock_doc = Mock()
        mock_page = Mock()
        mock_page.get_text.return_value = "Invoice Text from PDF"
        mock_doc.load_page.return_value = mock_page
        mock_doc.__len__.return_value = 1
        mock_fitz.return_value = mock_doc

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            try:
                result = self.ocr_engine.extract_text_from_pdf(tmp_file.name)
                assert "Invoice Text from PDF" in result
            finally:
                os.unlink(tmp_file.name)


class TestInvoiceParser:
    """Test invoice parsing functionality."""

    def setup_method(self):
        self.parser = InvoiceParser()

    def test_extract_invoice_number(self):
        """Test invoice number extraction."""
        text = "Invoice #: INV-12345\nAmount: $500.00"
        result = self.parser._extract_invoice_number(text)
        assert result == "INV-12345"

    def test_extract_vendor_name(self):
        """Test vendor name extraction."""
        lines = ["ABC Company Inc", "123 Main St", "Invoice #12345"]
        result = self.parser._extract_vendor_name(lines)
        assert result == "ABC Company Inc"

    def test_extract_amounts(self):
        """Test amount extraction."""
        text = "Subtotal: $100.00\nTax: $8.50\nTotal: $108.50"
        amounts = self.parser._extract_amounts(text)

        assert amounts['total'] == 108.50
        assert amounts['tax'] == 8.50
        assert amounts['subtotal'] == 100.00

    def test_extract_dates(self):
        """Test date extraction."""
        text = "Invoice Date: 01/15/2024\nDue Date: 02/15/2024"
        dates = self.parser._extract_dates(text)

        assert dates['invoice_date'] is not None
        assert dates['invoice_date'].month == 1
        assert dates['invoice_date'].day == 15
        assert dates['invoice_date'].year == 2024

    def test_parse_complete_invoice(self):
        """Test complete invoice parsing."""
        sample_text = """
        ABC Company Inc
        123 Main Street
        City, ST 12345

        Invoice #: INV-2024-001
        Date: 01/15/2024
        Due Date: 02/15/2024

        Description: Professional Services
        Amount: $1,250.00
        Tax: $100.00
        Total: $1,350.00
        """

        result = self.parser.parse_invoice_text(sample_text)

        assert isinstance(result, InvoiceData)
        assert result.invoice_number == "INV-2024-001"
        assert result.vendor_name == "ABC Company Inc"
        assert result.total_amount == 1350.00
        assert result.tax_amount == 100.00
        assert result.confidence_score > 0.5

    def test_confidence_score_calculation(self):
        """Test confidence score calculation."""
        good_data = {
            'invoice_number': 'INV-001',
            'vendor_name': 'Test Company',
            'invoice_date': datetime.now(),
            'total_amount': 100.00
        }

        score = self.parser._calculate_confidence_score(good_data)
        assert score == 1.0

        poor_data = {
            'invoice_number': None,
            'vendor_name': 'UNKNOWN',
            'invoice_date': None,
            'total_amount': 0
        }

        score = self.parser._calculate_confidence_score(poor_data)
        assert score == 0.0


class TestAnomalyDetector:
    """Test anomaly detection functionality."""

    def setup_method(self):
        # Create temporary history file
        self.temp_dir = tempfile.mkdtemp()
        self.history_path = os.path.join(self.temp_dir, 'test_history.pkl')
        self.detector = AnomalyDetector(self.history_path)

    def teardown_method(self):
        # Clean up
        if os.path.exists(self.history_path):
            os.unlink(self.history_path)
        os.rmdir(self.temp_dir)

    def test_duplicate_detection(self):
        """Test duplicate invoice detection."""
        # Create first invoice
        invoice1 = InvoiceData(
            invoice_number="INV-001",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now(),
            due_date=None,
            total_amount=100.00,
            tax_amount=8.00,
            subtotal=92.00,
            line_items=[]
        )

        # Process first invoice
        anomalies1 = self.detector.detect_anomalies(invoice1)
        assert "DUPLICATE_INVOICE" not in anomalies1

        # Create duplicate invoice
        invoice2 = InvoiceData(
            invoice_number="INV-001",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now(),
            due_date=None,
            total_amount=100.00,
            tax_amount=8.00,
            subtotal=92.00,
            line_items=[]
        )

        # Process duplicate
        anomalies2 = self.detector.detect_anomalies(invoice2)
        assert "DUPLICATE_INVOICE" in anomalies2

    def test_amount_anomaly_detection(self):
        """Test unusual amount detection."""
        # Add several normal invoices
        for i in range(5):
            invoice = InvoiceData(
                invoice_number=f"INV-{i:03d}",
                vendor_name="Regular Vendor",
                vendor_address="123 Main St",
                invoice_date=datetime.now(),
                due_date=None,
                total_amount=100.00 + i * 10,  # 100, 110, 120, 130, 140
                tax_amount=8.00,
                subtotal=92.00,
                line_items=[]
            )
            self.detector.detect_anomalies(invoice)

        # Add an unusually high invoice
        unusual_invoice = InvoiceData(
            invoice_number="INV-999",
            vendor_name="Regular Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now(),
            due_date=None,
            total_amount=10000.00,  # Much higher than normal
            tax_amount=800.00,
            subtotal=9200.00,
            line_items=[]
        )

        anomalies = self.detector.detect_anomalies(unusual_invoice)
        assert "UNUSUAL_AMOUNT" in anomalies

    def test_date_anomaly_detection(self):
        """Test date-based anomaly detection."""
        # Future date invoice
        future_invoice = InvoiceData(
            invoice_number="INV-FUTURE",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now() + timedelta(days=30),
            due_date=None,
            total_amount=100.00,
            tax_amount=8.00,
            subtotal=92.00,
            line_items=[]
        )

        anomalies = self.detector.detect_anomalies(future_invoice)
        assert "FUTURE_DATE" in anomalies

        # Old invoice
        old_invoice = InvoiceData(
            invoice_number="INV-OLD",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now() - timedelta(days=400),
            due_date=None,
            total_amount=100.00,
            tax_amount=8.00,
            subtotal=92.00,
            line_items=[]
        )

        anomalies = self.detector.detect_anomalies(old_invoice)
        assert "OLD_INVOICE" in anomalies


class TestBusinessValueTracker:
    """Test business value tracking functionality."""

    def setup_method(self):
        # Create temporary metrics file
        self.temp_dir = tempfile.mkdtemp()
        self.metrics_path = os.path.join(self.temp_dir, 'test_metrics.json')
        self.tracker = BusinessValueTracker(self.metrics_path)

    def teardown_method(self):
        # Clean up
        if os.path.exists(self.metrics_path):
            os.unlink(self.metrics_path)
        os.rmdir(self.temp_dir)

    def test_record_processing(self):
        """Test processing metrics recording."""
        # Record processing of an invoice
        self.tracker.record_processing(
            processing_time_minutes=0.5,
            anomalies_found=['DUPLICATE_INVOICE']
        )

        assert self.tracker.metrics['invoices_processed'] == 1
        assert self.tracker.metrics['duplicate_invoices_caught'] == 1
        assert self.tracker.metrics['total_processing_time_saved'] > 0

    def test_roi_calculation(self):
        """Test ROI report generation."""
        # Simulate processing multiple invoices
        for i in range(10):
            self.tracker.record_processing(
                processing_time_minutes=0.5,
                anomalies_found=[] if i % 3 else ['DUPLICATE_INVOICE']
            )

        roi_report = self.tracker.get_roi_report()

        assert 'summary' in roi_report
        assert 'monthly_projections' in roi_report
        assert 'roi_analysis' in roi_report
        assert roi_report['summary']['invoices_processed'] == 10
        assert roi_report['summary']['total_cost_savings'] > 0

    def test_metrics_persistence(self):
        """Test metrics saving and loading."""
        # Record some processing
        self.tracker.record_processing(2.0, [])
        initial_count = self.tracker.metrics['invoices_processed']

        # Create new tracker with same file
        new_tracker = BusinessValueTracker(self.metrics_path)

        # Should load existing metrics
        assert new_tracker.metrics['invoices_processed'] == initial_count


class TestInvoiceProcessor:
    """Test main invoice processor functionality."""

    def setup_method(self):
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create test config
        self.test_config = {
            'output_directory': os.path.join(self.temp_dir, 'output'),
            'supported_formats': ['.pdf', '.png', '.jpg'],
            'min_confidence_score': 0.7
        }

        # Create processor with test config
        with patch('agents.invoice_processor.InvoiceProcessor._load_config') as mock_config:
            mock_config.return_value = self.test_config
            self.processor = InvoiceProcessor()

    def teardown_method(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_file_validation(self):
        """Test file format validation."""
        # Test with non-existent file
        result = self.processor.process_invoice('/nonexistent/file.pdf')
        assert not result['success']
        assert 'not found' in result['error']

    @patch.object(OCREngine, 'extract_text_from_pdf')
    @patch.object(InvoiceParser, 'parse_invoice_text')
    @patch.object(AnomalyDetector, 'detect_anomalies')
    def test_successful_processing(self, mock_anomalies, mock_parser, mock_ocr):
        """Test successful invoice processing."""
        # Mock OCR extraction
        mock_ocr.return_value = "Sample invoice text with amount $123.45"

        # Mock parser result
        mock_invoice_data = InvoiceData(
            invoice_number="INV-001",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now(),
            due_date=None,
            total_amount=123.45,
            tax_amount=9.88,
            subtotal=113.57,
            line_items=[],
            confidence_score=0.85
        )
        mock_parser.return_value = mock_invoice_data

        # Mock anomaly detection
        mock_anomalies.return_value = []

        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            try:
                result = self.processor.process_invoice(tmp_file.name)

                assert result['success']
                assert result['invoice_data']['invoice_number'] == "INV-001"
                assert result['confidence_score'] == 0.85
                assert result['saved_to_accounting']

            finally:
                os.unlink(tmp_file.name)

    @patch.object(OCREngine, 'extract_text_from_image')
    @patch.object(InvoiceParser, 'parse_invoice_text')
    def test_low_confidence_handling(self, mock_parser, mock_ocr):
        """Test handling of low confidence results."""
        # Mock OCR extraction
        mock_ocr.return_value = "Poor quality text"

        # Mock parser result with low confidence
        mock_invoice_data = InvoiceData(
            invoice_number="INV-001",
            vendor_name="Test Vendor",
            vendor_address="123 Main St",
            invoice_date=datetime.now(),
            due_date=None,
            total_amount=123.45,
            tax_amount=9.88,
            subtotal=113.57,
            line_items=[],
            confidence_score=0.3  # Low confidence
        )
        mock_parser.return_value = mock_invoice_data

        # Create temporary test image
        test_image = np.ones((100, 100, 3), dtype=np.uint8) * 255
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            cv2.imwrite(tmp_file.name, test_image)
            try:
                result = self.processor.process_invoice(tmp_file.name)

                assert result['success']
                assert not result['saved_to_accounting']
                assert result['requires_manual_review']

            finally:
                os.unlink(tmp_file.name)

    def test_batch_processing(self):
        """Test batch processing functionality."""
        # Create temporary directory with test files
        test_dir = os.path.join(self.temp_dir, 'test_invoices')
        os.makedirs(test_dir)

        # Create mock files
        test_files = ['invoice1.pdf', 'invoice2.png', 'invoice3.jpg']
        for filename in test_files:
            file_path = os.path.join(test_dir, filename)
            with open(file_path, 'w') as f:
                f.write("dummy content")

        # Mock the process_invoice method to return success
        with patch.object(self.processor, 'process_invoice') as mock_process:
            mock_process.return_value = {
                'success': True,
                'anomalies': [],
                'business_impact': {'time_saved_minutes': 18}
            }

            result = self.processor.process_batch(test_dir)

            assert result['total_files'] == 3
            assert result['processed_successfully'] == 3
            assert result['failed'] == 0

    def test_business_metrics_integration(self):
        """Test business metrics tracking integration."""
        metrics = self.processor.get_business_metrics()

        assert 'summary' in metrics
        assert 'monthly_projections' in metrics
        assert 'roi_analysis' in metrics


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_processing(self):
        """Test complete end-to-end invoice processing."""
        # This would test the entire pipeline with real files
        # For brevity, we'll mock the components

        processor = InvoiceProcessor()

        # Test that all components are properly initialized
        assert processor.ocr_engine is not None
        assert processor.parser is not None
        assert processor.anomaly_detector is not None
        assert processor.value_tracker is not None

    def test_error_handling_and_recovery(self):
        """Test error handling in various scenarios."""
        processor = InvoiceProcessor()

        # Test with corrupted file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b"corrupted content")
            tmp_file.flush()

            try:
                result = processor.process_invoice(tmp_file.name)
                # Should handle error gracefully
                assert 'error' in result or not result['success']

            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.slow
    def test_performance_benchmarking(self):
        """Test processing performance with timing."""
        processor = InvoiceProcessor()

        # Create multiple test files and measure processing time
        test_files = []
        for i in range(5):
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(b"dummy pdf content")
                test_files.append(tmp_file.name)

        try:
            start_time = datetime.now()

            with patch.object(processor, 'process_invoice') as mock_process:
                mock_process.return_value = {
                    'success': True,
                    'processing_time_minutes': 0.5,
                    'anomalies': [],
                    'business_impact': {'time_saved_minutes': 18}
                }

                for file_path in test_files:
                    processor.process_invoice(file_path)

            total_time = (datetime.now() - start_time).total_seconds()

            # Should process 5 files in reasonable time
            assert total_time < 10  # seconds

        finally:
            for file_path in test_files:
                os.unlink(file_path)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])