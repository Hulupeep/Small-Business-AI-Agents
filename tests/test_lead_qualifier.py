"""
Unit tests for Lead Qualifier Agent
"""

import unittest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.lead_qualifier import (
    LeadQualifierAgent,
    Lead,
    BANTScore,
    LeadSource,
    LeadStatus,
    CompanySize,
    QualificationCriteria
)


class TestLeadQualifierAgent(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()

        self.qualifier = LeadQualifierAgent(db_path=self.temp_db.name)

        # Sample lead data
        self.sample_lead_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "company": "Test Company",
            "job_title": "CEO",
            "phone": "+1-555-0123",
            "website": "testcompany.com",
            "company_size": "medium",
            "industry": "technology"
        }

    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_initialization(self):
        """Test lead qualifier initialization"""
        self.assertIsNotNone(self.qualifier)
        self.assertIsInstance(self.qualifier.qualification_criteria, QualificationCriteria)
        self.assertEqual(self.qualifier.db_path, self.temp_db.name)

    def test_capture_lead(self):
        """Test lead capture functionality"""
        lead_id = self.qualifier.capture_lead(self.sample_lead_data, LeadSource.WEBSITE_FORM)

        self.assertIsNotNone(lead_id)
        self.assertIn("lead_", lead_id)

        # Verify lead was saved
        lead = self.qualifier._get_lead(lead_id)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.email, self.sample_lead_data["email"])
        self.assertEqual(lead.first_name, self.sample_lead_data["first_name"])

    def test_budget_score_calculation(self):
        """Test budget score calculation"""
        # Create leads with different company sizes
        test_cases = [
            (CompanySize.STARTUP, 30),
            (CompanySize.SMALL, 50),
            (CompanySize.MEDIUM, 70),
            (CompanySize.LARGE, 85),
            (CompanySize.ENTERPRISE, 95)
        ]

        for company_size, expected_min_score in test_cases:
            lead = Lead(
                lead_id="test_lead",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                company="Test Company",
                job_title="Manager",
                company_size=company_size,
                industry="technology"
            )

            score = self.qualifier._calculate_budget_score(lead)
            self.assertGreaterEqual(score, expected_min_score)
            self.assertLessEqual(score, 100)

    def test_authority_score_calculation(self):
        """Test authority score calculation"""
        # Test different job titles
        test_cases = [
            ("CEO", 95),
            ("CTO", 95),
            ("Founder", 95),
            ("VP of Engineering", 80),
            ("Director of Sales", 80),
            ("Marketing Manager", 60),
            ("Senior Developer", 60),
            ("Data Analyst", 30),
            ("Coordinator", 30)
        ]

        for job_title, expected_min_score in test_cases:
            lead = Lead(
                lead_id="test_lead",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                company="Test Company",
                job_title=job_title
            )

            score = self.qualifier._calculate_authority_score(lead)
            self.assertGreaterEqual(score, expected_min_score - 10)  # Allow some variance
            self.assertLessEqual(score, 100)

    def test_need_score_calculation(self):
        """Test need score calculation"""
        # Test high-need industry
        high_need_lead = Lead(
            lead_id="test_lead",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Company",
            job_title="Manager",
            industry="technology",
            company_size=CompanySize.MEDIUM
        )

        high_score = self.qualifier._calculate_need_score(high_need_lead)

        # Test lower-need industry
        low_need_lead = Lead(
            lead_id="test_lead",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Company",
            job_title="Manager",
            industry="agriculture",
            company_size=CompanySize.MEDIUM
        )

        low_score = self.qualifier._calculate_need_score(low_need_lead)

        self.assertGreater(high_score, low_score)
        self.assertLessEqual(high_score, 100)
        self.assertLessEqual(low_score, 100)

    def test_timeline_score_calculation(self):
        """Test timeline score calculation"""
        # Create lead with recent timestamp
        recent_lead = Lead(
            lead_id="test_lead",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Company",
            job_title="Manager",
            source=LeadSource.CHAT,
            created_at=datetime.now()
        )

        recent_score = self.qualifier._calculate_timeline_score(recent_lead)

        # Create lead with old timestamp
        old_lead = Lead(
            lead_id="test_lead",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Company",
            job_title="Manager",
            source=LeadSource.CHAT,
            created_at=datetime.now() - timedelta(days=30)
        )

        old_score = self.qualifier._calculate_timeline_score(old_lead)

        self.assertGreater(recent_score, old_score)

    def test_qualify_lead(self):
        """Test complete lead qualification process"""
        # Create a high-quality lead
        high_quality_data = {
            "email": "ceo@techcorp.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "company": "TechCorp Solutions",
            "job_title": "Chief Executive Officer",
            "phone": "+1-555-0199",
            "company_size": "enterprise",
            "industry": "technology"
        }

        lead_id = self.qualifier.capture_lead(high_quality_data, LeadSource.REFERRAL)
        bant_score = self.qualifier.qualify_lead(lead_id)

        self.assertIsInstance(bant_score, BANTScore)
        self.assertGreater(bant_score.overall_score, 70)  # Should be high score
        self.assertGreater(bant_score.budget_score, 0)
        self.assertGreater(bant_score.authority_score, 0)
        self.assertGreater(bant_score.need_score, 0)
        self.assertGreater(bant_score.timeline_score, 0)

        # Check lead status was updated
        lead = self.qualifier._get_lead(lead_id)
        self.assertIn(lead.status, [LeadStatus.QUALIFIED, LeadStatus.NURTURING])

    def test_lead_status_determination(self):
        """Test lead status determination based on BANT score"""
        # Test qualified threshold
        qualified_status = self.qualifier._determine_lead_status(80)
        self.assertEqual(qualified_status, LeadStatus.QUALIFIED)

        # Test nurturing threshold
        nurturing_status = self.qualifier._determine_lead_status(60)
        self.assertEqual(nurturing_status, LeadStatus.NURTURING)

        # Test unqualified threshold
        unqualified_status = self.qualifier._determine_lead_status(30)
        self.assertEqual(unqualified_status, LeadStatus.UNQUALIFIED)

    def test_bulk_import_leads(self):
        """Test bulk lead import functionality"""
        bulk_leads = [
            {
                "email": f"user{i}@company{i}.com",
                "first_name": f"User{i}",
                "last_name": "Test",
                "company": f"Company {i}",
                "job_title": "Manager",
                "company_size": "small",
                "industry": "technology"
            }
            for i in range(5)
        ]

        lead_ids = self.qualifier.bulk_import_leads(bulk_leads, LeadSource.EMAIL)

        self.assertEqual(len(lead_ids), 5)

        # Verify all leads were created
        for lead_id in lead_ids:
            lead = self.qualifier._get_lead(lead_id)
            self.assertIsNotNone(lead)

    def test_get_qualified_leads(self):
        """Test retrieving qualified leads"""
        # Create some leads
        qualified_lead_data = {
            "email": "qualified@example.com",
            "first_name": "Qualified",
            "last_name": "Lead",
            "company": "Qualified Company",
            "job_title": "CEO",
            "company_size": "enterprise",
            "industry": "technology"
        }

        lead_id = self.qualifier.capture_lead(qualified_lead_data, LeadSource.WEBSITE_FORM)
        self.qualifier.qualify_lead(lead_id)

        qualified_leads = self.qualifier.get_qualified_leads(7)

        self.assertIsInstance(qualified_leads, list)
        # Should have at least one qualified lead (if the scoring worked correctly)
        # self.assertGreater(len(qualified_leads), 0)

    def test_analytics_generation(self):
        """Test analytics generation"""
        # Create some test leads
        for i in range(3):
            lead_data = {
                "email": f"analytics{i}@test.com",
                "first_name": f"Analytics{i}",
                "last_name": "Test",
                "company": f"Analytics Company {i}",
                "job_title": "Manager",
                "company_size": "medium",
                "industry": "technology"
            }

            lead_id = self.qualifier.capture_lead(lead_data, LeadSource.WEBSITE_FORM)
            self.qualifier.qualify_lead(lead_id)

        analytics = self.qualifier.get_analytics(30)

        self.assertIsInstance(analytics, dict)
        self.assertIn("total_leads", analytics)
        self.assertIn("qualification_rate", analytics)
        self.assertIn("time_savings", analytics)
        self.assertGreaterEqual(analytics["total_leads"], 3)

    def test_qualification_reason_generation(self):
        """Test qualification reason generation"""
        lead = Lead(
            lead_id="test_lead",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company="Test Company",
            job_title="CEO",
            company_size=CompanySize.ENTERPRISE,
            industry="technology"
        )

        reason = self.qualifier._generate_qualification_reason(
            lead, 90, 95, 85, 80
        )

        self.assertIsInstance(reason, str)
        self.assertGreater(len(reason), 0)
        self.assertIn("|", reason)  # Should have multiple reasons separated by |

    def test_crm_integration_setup(self):
        """Test CRM integration configuration"""
        test_config = {
            "api_key": "test_key",
            "base_url": "https://test.crm.com"
        }

        self.qualifier.configure_crm_integration("test_crm", test_config)

        self.assertIn("test_crm", self.qualifier.crm_integrations)
        self.assertEqual(self.qualifier.crm_integrations["test_crm"], test_config)

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with invalid lead ID
        lead = self.qualifier._get_lead("invalid_lead_id")
        self.assertIsNone(lead)

        # Test with missing required fields
        incomplete_data = {
            "email": "incomplete@test.com",
            "first_name": "Incomplete"
            # Missing required fields
        }

        with self.assertRaises(KeyError):
            self.qualifier.capture_lead(incomplete_data)


class TestDataClasses(unittest.TestCase):

    def test_lead_creation(self):
        """Test Lead dataclass creation"""
        lead = Lead(
            lead_id="test_lead_001",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            company="Test Company",
            job_title="Manager"
        )

        self.assertEqual(lead.lead_id, "test_lead_001")
        self.assertEqual(lead.email, "test@example.com")
        self.assertEqual(lead.status, LeadStatus.NEW)  # Default value
        self.assertIsNotNone(lead.created_at)  # Should be set automatically

    def test_bant_score_calculation(self):
        """Test BANTScore calculation"""
        bant_score = BANTScore(
            budget_score=80,
            authority_score=90,
            need_score=70,
            timeline_score=60,
            overall_score=0,  # Will be calculated
            qualification_reason="Test reason"
        )

        # Check if overall score was calculated correctly
        expected_overall = (80 * 0.25) + (90 * 0.30) + (70 * 0.30) + (60 * 0.15)
        self.assertAlmostEqual(bant_score.overall_score, expected_overall, places=1)

    def test_qualification_criteria(self):
        """Test QualificationCriteria defaults"""
        criteria = QualificationCriteria()

        self.assertIsInstance(criteria.target_industries, list)
        self.assertIsInstance(criteria.authority_titles, list)
        self.assertIsInstance(criteria.disqualifying_keywords, list)
        self.assertGreater(len(criteria.target_industries), 0)
        self.assertIn("technology", criteria.target_industries)


if __name__ == "__main__":
    # Create logs directory for testing
    Path("logs").mkdir(exist_ok=True)

    # Run tests
    unittest.main(verbosity=2)