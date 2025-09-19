"""
Test suite for Contract Analyzer Agent
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.agents.contract_analyzer import (
    ContractAnalyzerAgent,
    ContractType,
    RiskLevel,
    ClauseType,
    ContractClause,
    ContractAnalysis,
    PaymentTerm,
    ContractParty
)


@pytest.fixture
def agent():
    """Create ContractAnalyzerAgent instance for testing"""
    return ContractAnalyzerAgent()


@pytest.fixture
def sample_contract():
    """Sample contract text for testing"""
    return """
    SERVICE AGREEMENT

    This Service Agreement is entered into between ABC Corporation ("Client") and XYZ Services LLC ("Provider").

    1. PAYMENT TERMS
    Client shall pay Provider $50,000 for services rendered. Payment is due within 30 days of invoice date.
    Late payments will incur a 2% monthly penalty.

    2. SERVICES
    Provider will deliver consulting services as specified in Exhibit A.

    3. TERMINATION
    Either party may terminate this agreement with 30 days written notice.

    4. LIABILITY
    Provider's total liability shall not exceed the total amount paid under this agreement.

    5. CONFIDENTIALITY
    Both parties agree to maintain confidentiality of proprietary information disclosed during the term of this agreement.

    6. GOVERNING LAW
    This agreement shall be governed by the laws of California.

    Effective Date: January 1, 2024
    Expiration Date: December 31, 2024
    """


@pytest.fixture
def high_risk_contract():
    """High-risk contract for testing"""
    return """
    CONSULTING AGREEMENT

    Consultant agrees to unlimited liability for any and all damages.
    This agreement automatically renews without notice.
    Client has sole discretion to terminate immediately without cause.
    Consultant waives all rights to dispute resolution.
    """


class TestContractAnalyzerAgent:
    """Test cases for ContractAnalyzerAgent"""

    @pytest.mark.asyncio
    async def test_contract_type_identification(self, agent):
        """Test contract type identification"""
        # Service agreement
        service_text = "This is a service agreement for professional services"
        contract_type = await agent._identify_contract_type(service_text)
        assert contract_type == ContractType.SERVICE_AGREEMENT

        # Employment contract
        employment_text = "Employment agreement for full-time employee with salary"
        contract_type = await agent._identify_contract_type(employment_text)
        assert contract_type == ContractType.EMPLOYMENT

        # NDA
        nda_text = "Non-disclosure agreement for confidential information"
        contract_type = await agent._identify_contract_type(nda_text)
        assert contract_type == ContractType.NDA

        # Unknown type defaults to service agreement
        unknown_text = "Some random text without contract keywords"
        contract_type = await agent._identify_contract_type(unknown_text)
        assert contract_type == ContractType.SERVICE_AGREEMENT

    def test_title_extraction(self, agent, sample_contract):
        """Test contract title extraction"""
        title = agent._extract_title(sample_contract)
        assert "SERVICE AGREEMENT" in title

    @pytest.mark.asyncio
    async def test_entity_extraction(self, agent, sample_contract):
        """Test entity extraction from contract"""
        entities = await agent._extract_entities(sample_contract)

        assert isinstance(entities, list)
        assert len(entities) > 0

        # Should extract monetary amounts
        money_entities = [e for e in entities if e.entity_type == "MONEY"]
        assert len(money_entities) > 0
        assert any("50,000" in e.text or "50000" in e.text for e in money_entities)

        # Should extract dates
        date_entities = [e for e in entities if e.entity_type == "DATES"]
        assert len(date_entities) > 0

        # Should extract organizations
        org_entities = [e for e in entities if e.entity_type == "ORG"]
        # May find organizations if spaCy is available

    def test_party_identification(self, agent, sample_contract):
        """Test contract party identification"""
        entities = []  # Mock entities for testing
        parties = agent._identify_parties(sample_contract, entities)

        assert isinstance(parties, list)
        # Should identify at least some parties based on text patterns

    def test_clause_type_identification(self, agent):
        """Test clause type identification"""
        # Payment clause
        payment_text = "Payment shall be due within 30 days of invoice"
        clause_type = agent._identify_clause_type(payment_text)
        assert clause_type == ClauseType.PAYMENT_TERMS

        # Termination clause
        termination_text = "Either party may terminate this agreement"
        clause_type = agent._identify_clause_type(termination_text)
        assert clause_type == ClauseType.TERMINATION

        # Liability clause
        liability_text = "Total liability shall not exceed the amount paid"
        clause_type = agent._identify_clause_type(liability_text)
        assert clause_type == ClauseType.LIABILITY

        # Confidentiality clause
        confidentiality_text = "Both parties agree to maintain confidentiality"
        clause_type = agent._identify_clause_type(confidentiality_text)
        assert clause_type == ClauseType.CONFIDENTIALITY

        # Unknown clause
        unknown_text = "This is some random text"
        clause_type = agent._identify_clause_type(unknown_text)
        assert clause_type is None

    def test_risk_assessment(self, agent):
        """Test clause risk assessment"""
        # High risk: unlimited liability
        high_risk_text = "Contractor has unlimited liability for all damages"
        risk = agent._assess_clause_risk(high_risk_text, ClauseType.LIABILITY)
        assert risk == RiskLevel.CRITICAL

        # Low risk: limited liability
        low_risk_text = "Liability is limited to the amount paid under this agreement"
        risk = agent._assess_clause_risk(low_risk_text, ClauseType.LIABILITY)
        assert risk == RiskLevel.LOW

        # Medium risk: general liability
        medium_risk_text = "Contractor shall be liable for damages"
        risk = agent._assess_clause_risk(medium_risk_text, ClauseType.LIABILITY)
        assert risk == RiskLevel.MEDIUM

    def test_keyword_extraction(self, agent):
        """Test keyword extraction from clauses"""
        text = "Payment of $50,000 shall be due within 30 days"
        keywords = agent._extract_clause_key_terms(text)

        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        # Should contain monetary amounts and important terms
        assert any("50,000" in k or "payment" in k.lower() for k in keywords)

    def test_concern_identification(self, agent):
        """Test concern identification in clauses"""
        # Problematic terms
        problematic_text = "Contractor has unlimited liability and waives all rights"
        concerns = agent._identify_clause_concerns(problematic_text, ClauseType.LIABILITY)

        assert isinstance(concerns, list)
        assert len(concerns) > 0
        assert any("unlimited" in concern.lower() for concern in concerns)

        # No concerns
        good_text = "Liability is reasonably limited"
        concerns = agent._identify_clause_concerns(good_text, ClauseType.LIABILITY)
        # May or may not have concerns depending on implementation

    def test_suggestion_generation(self, agent):
        """Test suggestion generation for clauses"""
        concerns = ["Contains potentially problematic term: 'unlimited'"]
        suggestions = agent._generate_clause_suggestions(
            "unlimited liability text",
            ClauseType.LIABILITY,
            concerns
        )

        assert isinstance(suggestions, list)
        if concerns:
            assert len(suggestions) > 0

    def test_payment_terms_extraction(self, agent, sample_contract):
        """Test payment terms extraction"""
        entities = []  # Mock entities
        payment_terms = agent._extract_payment_terms(sample_contract, entities)

        assert isinstance(payment_terms, list)
        # Should extract payment information from the contract

    def test_key_dates_extraction(self, agent, sample_contract):
        """Test key dates extraction"""
        entities = []  # Mock entities
        key_dates = agent._extract_key_dates(sample_contract, entities)

        assert isinstance(key_dates, dict)
        # Should extract effective and expiration dates

    def test_compliance_scoring(self, agent):
        """Test compliance score calculation"""
        # Mock clauses
        clauses = [
            Mock(clause_type=ClauseType.PAYMENT_TERMS, risk_level=RiskLevel.LOW),
            Mock(clause_type=ClauseType.TERMINATION, risk_level=RiskLevel.LOW),
            Mock(clause_type=ClauseType.LIABILITY, risk_level=RiskLevel.MEDIUM)
        ]

        score = agent._calculate_compliance_score(clauses, ContractType.SERVICE_AGREEMENT)

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_missing_clauses_identification(self, agent):
        """Test missing clause identification"""
        # Minimal clauses
        clauses = [
            Mock(clause_type=ClauseType.PAYMENT_TERMS)
        ]

        missing = agent._identify_missing_clauses(clauses, ContractType.SERVICE_AGREEMENT)

        assert isinstance(missing, list)
        # Should identify missing standard clauses

    def test_recommendation_generation(self, agent):
        """Test recommendation generation"""
        clauses = []
        missing_clauses = [ClauseType.LIABILITY, ClauseType.TERMINATION]
        risk_assessment = {RiskLevel.CRITICAL: 1, RiskLevel.HIGH: 0, RiskLevel.MEDIUM: 1, RiskLevel.LOW: 2}

        recommendations = agent._generate_recommendations(clauses, missing_clauses, risk_assessment)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        # Should include recommendations for missing clauses and risks

    def test_redflag_identification(self, agent, high_risk_contract):
        """Test red flag identification"""
        clauses = []  # Mock clauses
        redflags = agent._identify_redflags(high_risk_contract, clauses)

        assert isinstance(redflags, list)
        assert len(redflags) > 0
        # Should identify multiple red flags in the high-risk contract

    def test_financial_summary_creation(self, agent):
        """Test financial summary creation"""
        # Mock payment terms and entities
        payment_terms = [
            Mock(amount=50000, currency="USD", due_date=datetime.now())
        ]
        entities = [
            Mock(entity_type="MONEY", text="$50,000")
        ]

        summary = agent._create_financial_summary(payment_terms, entities)

        assert isinstance(summary, dict)
        assert "total_value" in summary
        assert "currency" in summary
        assert "payment_schedule" in summary

    @pytest.mark.asyncio
    async def test_full_contract_analysis(self, agent, sample_contract):
        """Test complete contract analysis workflow"""
        analysis = await agent.analyze_contract(sample_contract)

        assert isinstance(analysis, ContractAnalysis)
        assert analysis.contract_id is not None
        assert analysis.contract_type == ContractType.SERVICE_AGREEMENT
        assert analysis.title is not None
        assert isinstance(analysis.clauses, list)
        assert isinstance(analysis.entities, list)
        assert isinstance(analysis.risk_assessment, dict)
        assert isinstance(analysis.compliance_score, float)
        assert 0 <= analysis.compliance_score <= 100
        assert isinstance(analysis.recommendations, list)

    @pytest.mark.asyncio
    async def test_high_risk_contract_analysis(self, agent, high_risk_contract):
        """Test analysis of high-risk contract"""
        analysis = await agent.analyze_contract(high_risk_contract)

        assert isinstance(analysis, ContractAnalysis)
        # Should identify high risks
        assert analysis.risk_assessment[RiskLevel.CRITICAL] > 0 or analysis.risk_assessment[RiskLevel.HIGH] > 0
        # Should have lower compliance score
        assert analysis.compliance_score < 80
        # Should have red flags
        assert len(analysis.redflags) > 0

    @pytest.mark.asyncio
    async def test_template_comparison(self, agent, sample_contract):
        """Test contract comparison against template"""
        analysis = await agent.analyze_contract(sample_contract)
        comparison = await agent.compare_with_template(analysis, ContractType.SERVICE_AGREEMENT)

        assert isinstance(comparison, dict)
        assert "template_type" in comparison
        assert "coverage_score" in comparison
        assert "deviations" in comparison
        assert "improvements" in comparison
        assert 0 <= comparison["coverage_score"] <= 100

    @pytest.mark.asyncio
    async def test_risk_report_generation(self, agent, sample_contract):
        """Test risk report generation"""
        analysis = await agent.analyze_contract(sample_contract)
        risk_report = await agent.generate_risk_report(analysis)

        assert isinstance(risk_report, dict)
        assert "contract_id" in risk_report
        assert "overall_risk_level" in risk_report
        assert "risk_breakdown" in risk_report
        assert "compliance_status" in risk_report
        assert "financial_exposure" in risk_report
        assert "action_items" in risk_report

        # Overall risk level should be valid
        assert risk_report["overall_risk_level"] in [level for level in RiskLevel]

    def test_section_splitting(self, agent, sample_contract):
        """Test contract section splitting"""
        sections = agent._split_into_sections(sample_contract)

        assert isinstance(sections, list)
        assert len(sections) > 0
        # Should split contract into logical sections

    def test_overall_risk_calculation(self, agent):
        """Test overall risk level calculation"""
        # Critical risk
        analysis_critical = Mock()
        analysis_critical.risk_assessment = {
            RiskLevel.CRITICAL: 1,
            RiskLevel.HIGH: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.LOW: 2,
            RiskLevel.MINIMAL: 0
        }

        risk = agent._calculate_overall_risk(analysis_critical)
        assert risk == RiskLevel.CRITICAL

        # High risk
        analysis_high = Mock()
        analysis_high.risk_assessment = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 1,
            RiskLevel.LOW: 1,
            RiskLevel.MINIMAL: 0
        }

        risk = agent._calculate_overall_risk(analysis_high)
        assert risk == RiskLevel.HIGH

        # Low risk
        analysis_low = Mock()
        analysis_low.risk_assessment = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 0,
            RiskLevel.MEDIUM: 0,
            RiskLevel.LOW: 5,
            RiskLevel.MINIMAL: 0
        }

        risk = agent._calculate_overall_risk(analysis_low)
        assert risk == RiskLevel.LOW

    def test_financial_exposure_calculation(self, agent):
        """Test financial exposure calculation"""
        # Mock analysis with liability clause
        analysis = Mock()
        analysis.financial_summary = {"total_value": 100000}
        analysis.clauses = [
            Mock(
                clause_type=ClauseType.LIABILITY,
                content="Liability shall not exceed $50,000"
            )
        ]

        exposure = agent._calculate_financial_exposure(analysis)

        assert isinstance(exposure, dict)
        assert "contract_value" in exposure
        assert "liability_cap" in exposure
        assert "unlimited_liability" in exposure
        assert exposure["contract_value"] == 100000

    def test_standard_clauses_loading(self, agent):
        """Test that standard clauses are properly loaded"""
        standard_clauses = agent.standard_clauses

        assert isinstance(standard_clauses, dict)
        assert len(standard_clauses) > 0

        # Should have clauses for major contract types
        assert ContractType.SERVICE_AGREEMENT in standard_clauses
        assert ContractType.EMPLOYMENT in standard_clauses
        assert ContractType.NDA in standard_clauses

    def test_risk_patterns_loading(self, agent):
        """Test that risk patterns are properly loaded"""
        risk_patterns = agent.risk_patterns

        assert isinstance(risk_patterns, dict)
        assert len(risk_patterns) > 0

        # Should have patterns for major risks
        assert "unlimited_liability" in risk_patterns
        assert "automatic_renewal" in risk_patterns

        # Each pattern should have required fields
        for pattern_name, pattern_info in risk_patterns.items():
            assert "patterns" in pattern_info
            assert "risk_level" in pattern_info
            assert "description" in pattern_info

    def test_legal_terms_loading(self, agent):
        """Test that legal terms dictionary is loaded"""
        legal_terms = agent.legal_terms_dict

        assert isinstance(legal_terms, dict)
        assert len(legal_terms) > 0

        # Should have common legal terms
        assert "force majeure" in legal_terms
        assert "indemnification" in legal_terms

    @pytest.mark.asyncio
    async def test_contract_with_custom_id(self, agent, sample_contract):
        """Test contract analysis with custom ID"""
        custom_id = "CONTRACT_2024_001"
        analysis = await agent.analyze_contract(sample_contract, custom_id)

        assert analysis.contract_id == custom_id

    @pytest.mark.asyncio
    async def test_empty_contract(self, agent):
        """Test analysis of empty or minimal contract"""
        empty_contract = "This is not really a contract."
        analysis = await agent.analyze_contract(empty_contract)

        assert isinstance(analysis, ContractAnalysis)
        # Should handle gracefully with minimal content

    def test_pattern_matching(self, agent):
        """Test regex pattern matching for entities"""
        text = "Payment of $50,000.00 due on January 15, 2024"

        # Test money patterns
        money_matches = []
        for pattern in agent.patterns["money"]:
            money_matches.extend(re.findall(pattern, text))

        assert len(money_matches) > 0
        assert any("50,000" in match for match in money_matches)

        # Test date patterns
        date_matches = []
        for pattern in agent.patterns["dates"]:
            date_matches.extend(re.findall(pattern, text))

        assert len(date_matches) > 0


@pytest.mark.asyncio
async def test_integration_workflow():
    """Test complete workflow integration"""
    agent = ContractAnalyzerAgent()

    # Comprehensive contract for testing
    comprehensive_contract = """
    PROFESSIONAL SERVICES AGREEMENT

    This Agreement is between Tech Corp Inc. ("Client") and Consultant LLC ("Provider").

    1. SERVICES
    Provider will deliver software development services.

    2. PAYMENT
    Total fee: $75,000 USD. Payment due Net 30.
    Late payment fee: 1.5% per month.

    3. TERM
    Effective: March 1, 2024
    Expires: February 28, 2025

    4. TERMINATION
    Either party may terminate with 60 days written notice.

    5. LIABILITY
    Provider's liability limited to fees paid in the 12 months preceding the claim.

    6. INTELLECTUAL PROPERTY
    All work product owned by Client upon payment.

    7. CONFIDENTIALITY
    5-year confidentiality obligation for both parties.

    8. DISPUTE RESOLUTION
    Disputes resolved through binding arbitration in California.

    9. GOVERNING LAW
    Governed by California state law.
    """

    # Full analysis
    analysis = await agent.analyze_contract(comprehensive_contract)

    # Verify analysis quality
    assert analysis.compliance_score > 70  # Should be well-structured
    assert len(analysis.clauses) >= 5  # Should identify multiple clauses
    assert analysis.contract_type == ContractType.SERVICE_AGREEMENT

    # Template comparison
    comparison = await agent.compare_with_template(analysis, ContractType.SERVICE_AGREEMENT)
    assert comparison["coverage_score"] > 60  # Should have good coverage

    # Risk report
    risk_report = await agent.generate_risk_report(analysis)
    assert risk_report["overall_risk_level"] in [RiskLevel.LOW, RiskLevel.MEDIUM]  # Well-structured contract


if __name__ == "__main__":
    pytest.main([__file__, "-v"])