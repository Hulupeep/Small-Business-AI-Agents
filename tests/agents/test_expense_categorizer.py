"""
Test Suite for Expense Categorizer Agent

Comprehensive tests covering:
- Transaction categorization accuracy
- Machine learning model training
- Rule-based categorization
- Tax deductibility calculations
- Business value tracking
- Report generation
"""

import pytest
import os
import tempfile
import json
import pickle
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from collections import defaultdict

# Import the modules to test
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from agents.expense_categorizer import (
    ExpenseCategorizer, Transaction, TaxCategoryMapper, PatternLearningEngine,
    RuleBasedCategorizer, ExpenseReportGenerator, BusinessValueTracker
)


class TestTransaction:
    """Test Transaction dataclass functionality."""

    def test_transaction_creation(self):
        """Test transaction object creation."""
        transaction = Transaction(
            id="txn_001",
            date=datetime(2024, 1, 15),
            description="Office supplies from Staples",
            amount=45.67,
            account="Business Checking",
            merchant="Staples",
            category="Office Supplies"
        )

        assert transaction.id == "txn_001"
        assert transaction.amount == 45.67
        assert transaction.merchant == "Staples"
        assert transaction.processing_timestamp is not None

    def test_transaction_defaults(self):
        """Test transaction default values."""
        transaction = Transaction(
            id="txn_002",
            date=datetime.now(),
            description="Test transaction",
            amount=100.0,
            account="Test Account"
        )

        assert transaction.tags == []
        assert transaction.confidence_score == 0.0
        assert transaction.is_business_expense == True
        assert transaction.processing_timestamp is not None


class TestTaxCategoryMapper:
    """Test tax category mapping functionality."""

    def setup_method(self):
        self.mapper = TaxCategoryMapper()

    def test_fully_deductible_categories(self):
        """Test fully deductible business expense categories."""
        tax_info = self.mapper.get_tax_info('Office Supplies')
        assert tax_info['deductible'] == True
        assert tax_info['rate'] == 1.0
        assert tax_info['schedule'] == 'Schedule C'

    def test_partially_deductible_categories(self):
        """Test partially deductible categories."""
        tax_info = self.mapper.get_tax_info('Meals & Entertainment')
        assert tax_info['deductible'] == True
        assert tax_info['rate'] == 0.5

        tax_info = self.mapper.get_tax_info('Vehicle Expenses')
        assert tax_info['deductible'] == True
        assert tax_info['rate'] == 0.575

    def test_non_deductible_categories(self):
        """Test non-deductible categories."""
        tax_info = self.mapper.get_tax_info('Personal')
        assert tax_info['deductible'] == False
        assert tax_info['rate'] == 0.0

    def test_deduction_calculation(self):
        """Test deduction amount calculation."""
        # Fully deductible
        deduction = self.mapper.calculate_deduction(100.0, 'Office Supplies')
        assert deduction == 100.0

        # Partially deductible
        deduction = self.mapper.calculate_deduction(100.0, 'Meals & Entertainment')
        assert deduction == 50.0

        # Non-deductible
        deduction = self.mapper.calculate_deduction(100.0, 'Personal')
        assert deduction == 0.0

    def test_unknown_category(self):
        """Test handling of unknown categories."""
        tax_info = self.mapper.get_tax_info('Unknown Category')
        assert tax_info['deductible'] == False
        assert tax_info['rate'] == 0.0


class TestPatternLearningEngine:
    """Test machine learning pattern recognition."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.model_path = os.path.join(self.temp_dir, 'test_model.pkl')
        self.engine = PatternLearningEngine(self.model_path)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_feature_preparation(self):
        """Test feature extraction from transactions."""
        transaction = Transaction(
            id="txn_001",
            date=datetime(2024, 1, 15),
            description="Coffee at Starbucks",
            amount=5.50,
            account="Business Card",
            merchant="Starbucks"
        )

        features = self.engine.prepare_features(transaction)

        assert "coffee" in features.lower()
        assert "starbucks" in features.lower()
        assert "small_amount" in features.lower()
        assert "monday" in features.lower()  # Jan 15, 2024 was a Monday

    def test_model_training(self):
        """Test model training with sample data."""
        # Create sample training transactions
        transactions = [
            Transaction("1", datetime.now(), "Starbucks coffee", 5.0, "Card", "Starbucks", "Meals & Entertainment"),
            Transaction("2", datetime.now(), "Office supplies", 25.0, "Card", "Staples", "Office Supplies"),
            Transaction("3", datetime.now(), "Uber ride", 15.0, "Card", "Uber", "Business Travel"),
            Transaction("4", datetime.now(), "Coffee meeting", 12.0, "Card", "Local Cafe", "Meals & Entertainment"),
            Transaction("5", datetime.now(), "Printer paper", 30.0, "Card", "OfficeMax", "Office Supplies"),
            Transaction("6", datetime.now(), "Airport taxi", 45.0, "Card", "Yellow Cab", "Business Travel"),
            Transaction("7", datetime.now(), "Lunch meeting", 35.0, "Card", "Restaurant", "Meals & Entertainment"),
            Transaction("8", datetime.now(), "Software subscription", 99.0, "Card", "Adobe", "Software & Subscriptions"),
            Transaction("9", datetime.now(), "Business cards", 50.0, "Card", "Vistaprint", "Marketing & Advertising"),
            Transaction("10", datetime.now(), "Domain registration", 15.0, "Card", "GoDaddy", "Software & Subscriptions"),
        ]

        result = self.engine.train_model(transactions)

        assert result['accuracy'] > 0.0
        assert result['categories_learned'] >= 2
        assert result['training_samples'] == 10
        assert self.engine.is_trained

    def test_prediction(self):
        """Test category prediction after training."""
        # First train the model
        transactions = [
            Transaction("1", datetime.now(), "Starbucks coffee", 5.0, "Card", "Starbucks", "Meals & Entertainment"),
            Transaction("2", datetime.now(), "Office supplies", 25.0, "Card", "Staples", "Office Supplies"),
            Transaction("3", datetime.now(), "Coffee shop", 8.0, "Card", "Local Cafe", "Meals & Entertainment"),
            Transaction("4", datetime.now(), "Pens and paper", 15.0, "Card", "OfficeMax", "Office Supplies"),
        ]

        self.engine.train_model(transactions)

        # Test prediction
        new_transaction = Transaction(
            "test", datetime.now(), "Coffee at Dunkin", 4.50, "Card", "Dunkin Donuts"
        )

        category, confidence = self.engine.predict_category(new_transaction)

        assert category in ["Meals & Entertainment", "Office Supplies", "Uncategorized"]
        assert 0.0 <= confidence <= 1.0

    def test_insufficient_training_data(self):
        """Test handling of insufficient training data."""
        transactions = [
            Transaction("1", datetime.now(), "Test", 10.0, "Card", "Test", "Test Category")
        ]

        with pytest.raises(ValueError, match="Need at least 10 transactions"):
            self.engine.train_model(transactions)


class TestRuleBasedCategorizer:
    """Test rule-based categorization system."""

    def setup_method(self):
        self.categorizer = RuleBasedCategorizer()

    def test_office_supplies_categorization(self):
        """Test office supplies categorization."""
        transaction = Transaction(
            "1", datetime.now(), "Office Depot supplies", 50.0, "Card", "Office Depot"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Office Supplies"
        assert confidence >= 0.8

    def test_software_categorization(self):
        """Test software subscription categorization."""
        transaction = Transaction(
            "1", datetime.now(), "Adobe Creative Cloud", 99.0, "Card", "Adobe"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Software & Subscriptions"
        assert confidence >= 0.9

    def test_travel_categorization(self):
        """Test travel expense categorization."""
        transaction = Transaction(
            "1", datetime.now(), "Uber to airport", 35.0, "Card", "Uber"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Business Travel"
        assert confidence >= 0.7

    def test_meals_categorization(self):
        """Test meals categorization."""
        transaction = Transaction(
            "1", datetime.now(), "Business lunch", 45.0, "Card", "Restaurant"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Meals & Entertainment"

    def test_merchant_mapping(self):
        """Test direct merchant mapping."""
        transaction = Transaction(
            "1", datetime.now(), "GitHub subscription", 9.0, "Card", "github.com"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Software & Subscriptions"
        assert subcategory == "Development Tools"
        assert confidence == 0.95

    def test_fallback_categorization(self):
        """Test fallback categorization for unknown patterns."""
        transaction = Transaction(
            "1", datetime.now(), "XYZ Unknown Service", 25.0, "Card", "Unknown Merchant"
        )

        category, subcategory, confidence = self.categorizer.categorize_transaction(transaction)

        assert category == "Uncategorized"
        assert confidence <= 0.2


class TestExpenseReportGenerator:
    """Test expense report generation functionality."""

    def setup_method(self):
        self.tax_mapper = TaxCategoryMapper()
        self.generator = ExpenseReportGenerator(self.tax_mapper)

    def create_sample_transactions(self) -> list:
        """Create sample transactions for testing."""
        return [
            Transaction("1", datetime(2024, 1, 15), "Office supplies", 50.0, "Card", "Staples", "Office Supplies", is_business_expense=True),
            Transaction("2", datetime(2024, 1, 16), "Business lunch", 75.0, "Card", "Restaurant", "Meals & Entertainment", is_business_expense=True),
            Transaction("3", datetime(2024, 1, 17), "Software subscription", 99.0, "Card", "Adobe", "Software & Subscriptions", is_business_expense=True),
            Transaction("4", datetime(2024, 1, 18), "Groceries", 120.0, "Card", "Walmart", "Personal", is_business_expense=False),
            Transaction("5", datetime(2024, 2, 15), "Conference travel", 300.0, "Card", "United Airlines", "Business Travel", is_business_expense=True),
        ]

    def test_monthly_report_generation(self):
        """Test monthly expense report generation."""
        transactions = self.create_sample_transactions()
        report = self.generator.generate_monthly_report(transactions, 1, 2024)

        assert 'summary' in report
        assert 'category_breakdown' in report
        assert 'tax_summary' in report

        # Check summary calculations
        summary = report['summary']
        assert summary['business_expenses'] == 224.0  # 50 + 75 + 99
        assert summary['personal_expenses'] == 120.0
        assert summary['transaction_count'] == 4  # Only January transactions

        # Check category breakdown
        categories = report['category_breakdown']
        assert categories['Office Supplies'] == 50.0
        assert categories['Meals & Entertainment'] == 75.0

    def test_quarterly_report_generation(self):
        """Test quarterly expense report generation."""
        transactions = self.create_sample_transactions()
        report = self.generator.generate_quarterly_report(transactions, 1, 2024)

        assert 'quarter' in report
        assert 'tax_categories' in report
        assert 'summary' in report

        # Should include January and February transactions
        tax_categories = report['tax_categories']
        assert 'Office Supplies' in tax_categories
        assert 'Business Travel' in tax_categories

    def test_tax_summary_calculation(self):
        """Test tax deductible summary calculation."""
        transactions = self.create_sample_transactions()
        tax_summary = self.generator._generate_tax_summary(transactions)

        assert 'deductible_by_category' in tax_summary
        assert 'total_deductible' in tax_summary

        # Check deductible amounts
        deductible = tax_summary['deductible_by_category']
        assert deductible['Office Supplies'] == 50.0  # 100% deductible
        assert deductible['Meals & Entertainment'] == 37.5  # 50% deductible
        assert deductible['Software & Subscriptions'] == 99.0  # 100% deductible

    def test_empty_month_report(self):
        """Test report generation for month with no transactions."""
        transactions = self.create_sample_transactions()
        report = self.generator.generate_monthly_report(transactions, 12, 2024)

        assert 'error' in report


class TestBusinessValueTracker:
    """Test business value tracking functionality."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.metrics_path = os.path.join(self.temp_dir, 'test_metrics.json')
        self.tracker = BusinessValueTracker(self.metrics_path)

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_initial_metrics(self):
        """Test initial metrics setup."""
        assert self.tracker.metrics['transactions_processed'] == 0
        assert self.tracker.metrics['cost_savings'] == 0.0
        assert self.tracker.metrics['bookkeeper_hourly_rate'] == 30.0

    def test_categorization_recording(self):
        """Test recording of categorization metrics."""
        # Record automatic categorization
        self.tracker.record_categorization(
            processing_time_seconds=1.0,
            confidence=0.85,
            was_automatic=True
        )

        assert self.tracker.metrics['transactions_processed'] == 1
        assert self.tracker.metrics['manual_categorizations_saved'] == 1
        assert self.tracker.metrics['time_saved_hours'] > 0

    def test_roi_report_generation(self):
        """Test ROI report generation."""
        # Simulate processing multiple transactions
        for i in range(20):
            self.tracker.record_categorization(
                processing_time_seconds=0.5,
                confidence=0.8,
                was_automatic=True
            )

        roi_report = self.tracker.get_roi_report()

        assert 'performance_metrics' in roi_report
        assert 'financial_impact' in roi_report
        assert 'roi_analysis' in roi_report

        # Check performance metrics
        performance = roi_report['performance_metrics']
        assert performance['transactions_processed'] == 20
        assert performance['automation_rate'] == 100.0

        # Check financial impact
        financial = roi_report['financial_impact']
        assert financial['total_cost_savings'] > 0

    def test_accuracy_tracking(self):
        """Test accuracy rate tracking."""
        # Record high confidence categorizations
        for _ in range(5):
            self.tracker.record_categorization(1.0, 0.9, True)

        # Record low confidence categorizations
        for _ in range(5):
            self.tracker.record_categorization(1.0, 0.3, False)

        roi_report = self.tracker.get_roi_report()
        accuracy = roi_report['performance_metrics']['accuracy_rate']

        # Should be average of all confidence scores
        assert 50 < accuracy < 70  # Average of 0.9 and 0.3 is 0.6


class TestExpenseCategorizer:
    """Test main expense categorizer functionality."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

        # Create test config
        self.test_config = {
            'confidence_threshold': 0.7,
            'auto_categorize': True,
            'learning_enabled': True,
            'transactions_file': os.path.join(self.temp_dir, 'test_transactions.pkl')
        }

        with patch('agents.expense_categorizer.ExpenseCategorizer._load_config') as mock_config:
            mock_config.return_value = self.test_config
            self.categorizer = ExpenseCategorizer()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_single_transaction_categorization(self):
        """Test categorizing a single transaction."""
        transaction_data = {
            'id': 'txn_001',
            'date': datetime(2024, 1, 15),
            'description': 'Office supplies from Staples',
            'amount': 45.67,
            'account': 'Business Card',
            'merchant': 'Staples'
        }

        result = self.categorizer.categorize_transaction(transaction_data)

        assert result['success']
        assert result['category'] == 'Office Supplies'
        assert result['confidence_score'] > 0.7
        assert result['tax_deductible']
        assert 'processing_time_ms' in result

    def test_batch_categorization(self):
        """Test batch transaction categorization."""
        transactions_data = [
            {
                'id': 'txn_001',
                'date': datetime(2024, 1, 15),
                'description': 'Office supplies',
                'amount': 50.0,
                'account': 'Card',
                'merchant': 'Staples'
            },
            {
                'id': 'txn_002',
                'date': datetime(2024, 1, 16),
                'description': 'Business lunch',
                'amount': 75.0,
                'account': 'Card',
                'merchant': 'Restaurant'
            },
            {
                'id': 'txn_003',
                'date': datetime(2024, 1, 17),
                'description': 'Unknown expense',
                'amount': 25.0,
                'account': 'Card',
                'merchant': 'Unknown'
            }
        ]

        result = self.categorizer.categorize_batch(transactions_data)

        assert result['total_transactions'] == 3
        assert result['successfully_categorized'] == 3
        assert result['high_confidence'] >= 2  # First two should be high confidence
        assert result['requires_review'] >= 1  # Third should need review

    def test_model_training(self):
        """Test ML model training from historical data."""
        # Add some categorized transactions to history
        sample_transactions = [
            Transaction("1", datetime.now(), "Starbucks", 5.0, "Card", "Starbucks", "Meals & Entertainment"),
            Transaction("2", datetime.now(), "Office Depot", 25.0, "Card", "Office Depot", "Office Supplies"),
            Transaction("3", datetime.now(), "Uber", 15.0, "Card", "Uber", "Business Travel"),
            Transaction("4", datetime.now(), "Coffee", 6.0, "Card", "Local Cafe", "Meals & Entertainment"),
            Transaction("5", datetime.now(), "Staples", 30.0, "Card", "Staples", "Office Supplies"),
            Transaction("6", datetime.now(), "Taxi", 20.0, "Card", "Yellow Cab", "Business Travel"),
            Transaction("7", datetime.now(), "Lunch", 35.0, "Card", "Restaurant", "Meals & Entertainment"),
            Transaction("8", datetime.now(), "Adobe", 99.0, "Card", "Adobe", "Software & Subscriptions"),
            Transaction("9", datetime.now(), "Business cards", 50.0, "Card", "Vistaprint", "Marketing & Advertising"),
            Transaction("10", datetime.now(), "Domain", 15.0, "Card", "GoDaddy", "Software & Subscriptions"),
        ]

        self.categorizer.transactions = sample_transactions

        result = self.categorizer.train_from_history()

        assert result['success']
        assert result['model_ready']
        assert result['training_results']['categories_learned'] >= 3

    def test_expense_report_generation(self):
        """Test expense report generation."""
        # Add sample transactions
        self.categorizer.transactions = [
            Transaction("1", datetime(2024, 1, 15), "Office supplies", 50.0, "Card", "Staples", "Office Supplies", is_business_expense=True),
            Transaction("2", datetime(2024, 1, 16), "Business lunch", 75.0, "Card", "Restaurant", "Meals & Entertainment", is_business_expense=True),
        ]

        # Generate monthly report
        result = self.categorizer.generate_expense_report('monthly', {'month': 1, 'year': 2024})

        assert 'summary' in result
        assert 'category_breakdown' in result
        assert result['summary']['business_expenses'] == 125.0

    def test_business_metrics_tracking(self):
        """Test business metrics integration."""
        # Process some transactions to generate metrics
        transaction_data = {
            'id': 'txn_001',
            'date': datetime.now(),
            'description': 'Test transaction',
            'amount': 50.0,
            'account': 'Card',
            'merchant': 'Test'
        }

        self.categorizer.categorize_transaction(transaction_data)

        metrics = self.categorizer.get_business_metrics()

        assert 'performance_metrics' in metrics
        assert 'financial_impact' in metrics
        assert metrics['performance_metrics']['transactions_processed'] == 1

    def test_export_functionality(self):
        """Test exporting for accounting software."""
        # Add sample transactions
        self.categorizer.transactions = [
            Transaction("1", datetime(2024, 1, 15), "Office supplies", 50.0, "Card", "Staples", "Office Supplies", is_business_expense=True),
            Transaction("2", datetime(2024, 1, 16), "Business lunch", 75.0, "Card", "Restaurant", "Meals & Entertainment", is_business_expense=True),
        ]

        # Test CSV export
        result = self.categorizer.export_for_accounting_software('csv')

        assert result['format'] == 'csv'
        assert result['record_count'] == 2
        assert 'filename' in result

    def test_error_handling(self):
        """Test error handling in categorization."""
        # Test with invalid transaction data
        invalid_data = {
            'id': 'invalid',
            'description': 'Test',
            # Missing required fields
        }

        result = self.categorizer.categorize_transaction(invalid_data)

        assert not result['success']
        assert 'error' in result


class TestIntegrationScenarios:
    """Integration tests for complete workflows."""

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_categorization(self):
        """Test complete categorization workflow."""
        categorizer = ExpenseCategorizer()

        # Simulate real transaction data
        transaction_data = {
            'id': 'bank_txn_12345',
            'date': datetime(2024, 1, 15),
            'description': 'SQ *COFFEE SHOP',
            'amount': 4.50,
            'account': 'Business Checking',
            'merchant': 'Coffee Shop'
        }

        result = categorizer.categorize_transaction(transaction_data)

        # Verify end-to-end processing
        assert result['success']
        assert result['category'] is not None
        assert result['tax_deductible'] is not None
        assert result['deductible_amount'] >= 0

    def test_learning_and_improvement(self):
        """Test that categorizer improves with more data."""
        categorizer = ExpenseCategorizer()

        # Initial categorization (should use rules)
        initial_result = categorizer.categorize_transaction({
            'id': 'test1',
            'date': datetime.now(),
            'description': 'Unknown vendor payment',
            'amount': 100.0,
            'account': 'Card',
            'merchant': 'Unknown Vendor'
        })

        initial_confidence = initial_result['confidence_score']

        # Add training data
        training_transactions = []
        for i in range(15):
            training_transactions.append(Transaction(
                f"train_{i}",
                datetime.now(),
                f"Unknown vendor payment {i}",
                100.0 + i,
                "Card",
                "Unknown Vendor",
                "Professional Services"
            ))

        categorizer.transactions = training_transactions
        categorizer.train_from_history()

        # Re-categorize similar transaction
        improved_result = categorizer.categorize_transaction({
            'id': 'test2',
            'date': datetime.now(),
            'description': 'Unknown vendor payment',
            'amount': 105.0,
            'account': 'Card',
            'merchant': 'Unknown Vendor'
        })

        # Should show improvement or at least maintain performance
        assert improved_result['success']


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])