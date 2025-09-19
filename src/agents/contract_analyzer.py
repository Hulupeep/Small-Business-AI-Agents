"""
Contract Analyzer Agent - Intelligent Legal Document Analysis

This agent analyzes contracts, extracts key terms, identifies risks, and compares
against standard templates, saving $2000+/month in legal review costs.
"""

import asyncio
import logging
import re
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any, Set
from enum import Enum
import hashlib

import spacy
import nltk
from textblob import TextBlob
import dateutil.parser as date_parser
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Load spaCy model (download with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Please install spaCy English model: python -m spacy download en_core_web_sm")
    nlp = None


class ContractType(Enum):
    """Types of contracts"""
    SERVICE_AGREEMENT = "service_agreement"
    EMPLOYMENT = "employment"
    NDA = "nda"
    PURCHASE_ORDER = "purchase_order"
    LEASE = "lease"
    VENDOR = "vendor"
    LICENSING = "licensing"
    PARTNERSHIP = "partnership"
    CONSULTING = "consulting"
    SOFTWARE_LICENSE = "software_license"


class RiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class ClauseType(Enum):
    """Types of contract clauses"""
    PAYMENT_TERMS = "payment_terms"
    TERMINATION = "termination"
    LIABILITY = "liability"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    CONFIDENTIALITY = "confidentiality"
    INDEMNIFICATION = "indemnification"
    DISPUTE_RESOLUTION = "dispute_resolution"
    FORCE_MAJEURE = "force_majeure"
    GOVERNING_LAW = "governing_law"
    AMENDMENT = "amendment"
    ASSIGNMENT = "assignment"
    COMPLIANCE = "compliance"


@dataclass
class ContractClause:
    """Contract clause structure"""
    clause_type: ClauseType
    content: str
    start_position: int
    end_position: int
    risk_level: RiskLevel
    key_terms: List[str]
    concerns: List[str]
    suggestions: List[str]


@dataclass
class ContractEntity:
    """Contract entity (names, dates, amounts, etc.)"""
    entity_type: str  # PERSON, ORG, MONEY, DATE, etc.
    text: str
    start_position: int
    end_position: int
    confidence: float


@dataclass
class PaymentTerm:
    """Payment terms structure"""
    amount: Optional[float]
    currency: str
    due_date: Optional[datetime]
    payment_method: Optional[str]
    late_fee: Optional[float]
    discount_terms: Optional[str]


@dataclass
class ContractParty:
    """Contract party information"""
    name: str
    role: str  # client, vendor, contractor, etc.
    address: Optional[str]
    contact_info: Optional[str]
    legal_entity_type: Optional[str]


@dataclass
class ContractAnalysis:
    """Complete contract analysis result"""
    contract_id: str
    contract_type: ContractType
    title: str
    parties: List[ContractParty]
    clauses: List[ContractClause]
    entities: List[ContractEntity]
    payment_terms: List[PaymentTerm]
    key_dates: Dict[str, datetime]
    risk_assessment: Dict[RiskLevel, int]
    compliance_score: float
    missing_clauses: List[ClauseType]
    recommendations: List[str]
    redflags: List[str]
    financial_summary: Dict[str, Any]


class ContractAnalyzerAgent:
    """
    Intelligent contract analysis agent for legal document review.

    Features:
    - Automated clause identification and extraction
    - Risk assessment and compliance checking
    - Key terms and obligations extraction
    - Financial terms analysis
    - Missing clause detection
    - Comparison against standard templates
    - Legal language processing
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize NLP models
        self.nlp = nlp

        # Initialize NER model for legal entities
        try:
            self.ner_model = pipeline(
                "ner",
                model="nlpaueb/legal-bert-base-uncased",
                aggregation_strategy="simple"
            )
        except:
            # Fallback to standard model
            self.ner_model = pipeline("ner", aggregation_strategy="simple")

        # Contract templates and standards
        self.standard_clauses = self._load_standard_clauses()
        self.risk_patterns = self._load_risk_patterns()
        self.legal_terms_dict = self._load_legal_terms()

        # Regex patterns for common contract elements
        self.patterns = {
            "dates": [
                r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
            ],
            "money": [
                r'\$[\d,]+(?:\.\d{2})?',
                r'USD\s*[\d,]+(?:\.\d{2})?',
                r'(?:dollars?)\s*[\d,]+(?:\.\d{2})?',
                r'[\d,]+(?:\.\d{2})?\s*(?:USD|dollars?)'
            ],
            "percentages": [r'\d+(?:\.\d+)?%'],
            "email": [r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'],
            "phone": [r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'],
            "addresses": [r'\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln)']
        }

    def _load_standard_clauses(self) -> Dict[ContractType, Dict[ClauseType, str]]:
        """Load standard clause templates for different contract types"""
        return {
            ContractType.SERVICE_AGREEMENT: {
                ClauseType.PAYMENT_TERMS: "Payment shall be due within thirty (30) days of invoice date.",
                ClauseType.TERMINATION: "Either party may terminate this agreement with thirty (30) days written notice.",
                ClauseType.LIABILITY: "Total liability shall not exceed the total amount paid under this agreement.",
                ClauseType.INTELLECTUAL_PROPERTY: "All work product shall be owned by the client upon full payment.",
                ClauseType.CONFIDENTIALITY: "Both parties agree to maintain confidentiality of proprietary information."
            },
            ContractType.EMPLOYMENT: {
                ClauseType.TERMINATION: "Employment may be terminated by either party with two weeks notice.",
                ClauseType.CONFIDENTIALITY: "Employee agrees to maintain confidentiality of company information.",
                ClauseType.INTELLECTUAL_PROPERTY: "All work product created during employment belongs to the company."
            },
            ContractType.NDA: {
                ClauseType.CONFIDENTIALITY: "Recipient agrees to maintain strict confidentiality of disclosed information.",
                ClauseType.TERMINATION: "This agreement shall remain in effect for five (5) years."
            }
        }

    def _load_risk_patterns(self) -> Dict[str, Dict]:
        """Load risk identification patterns"""
        return {
            "unlimited_liability": {
                "patterns": [
                    r"unlimited\s+liability",
                    r"without\s+limit",
                    r"no\s+cap\s+on\s+liability",
                    r"liability\s+shall\s+not\s+be\s+limited"
                ],
                "risk_level": RiskLevel.CRITICAL,
                "description": "Unlimited liability exposure"
            },
            "automatic_renewal": {
                "patterns": [
                    r"automatically\s+renew",
                    r"auto-renewal",
                    r"shall\s+renew\s+automatically"
                ],
                "risk_level": RiskLevel.MEDIUM,
                "description": "Automatic contract renewal without notice"
            },
            "no_termination_clause": {
                "patterns": [
                    r"cannot\s+be\s+terminated",
                    r"no\s+termination",
                    r"irrevocable"
                ],
                "risk_level": RiskLevel.HIGH,
                "description": "Difficult or impossible to terminate contract"
            },
            "indemnification_broad": {
                "patterns": [
                    r"indemnify.*against\s+all",
                    r"hold\s+harmless\s+from\s+any",
                    r"defend.*against\s+any\s+and\s+all"
                ],
                "risk_level": RiskLevel.HIGH,
                "description": "Broad indemnification requirements"
            },
            "penalty_clauses": {
                "patterns": [
                    r"penalty\s+of",
                    r"liquidated\s+damages",
                    r"fine\s+of"
                ],
                "risk_level": RiskLevel.MEDIUM,
                "description": "Financial penalties for non-compliance"
            }
        }

    def _load_legal_terms(self) -> Dict[str, str]:
        """Load legal terms dictionary for interpretation"""
        return {
            "force majeure": "Unforeseeable circumstances that prevent a party from fulfilling a contract",
            "indemnification": "Compensation for harm or loss",
            "liquidated damages": "Pre-agreed amount of damages for breach of contract",
            "severability": "If one clause is invalid, the rest of the contract remains valid",
            "governing law": "Which jurisdiction's laws apply to the contract",
            "assignment": "Transfer of rights and obligations to another party",
            "waiver": "Voluntary relinquishment of a right or claim",
            "merger clause": "The written contract represents the entire agreement"
        }

    async def analyze_contract(self, contract_text: str, contract_id: str = None) -> ContractAnalysis:
        """Perform comprehensive contract analysis"""
        if not contract_id:
            contract_id = hashlib.md5(contract_text.encode()).hexdigest()[:8]

        self.logger.info(f"Starting analysis of contract {contract_id}")

        # Basic document analysis
        contract_type = await self._identify_contract_type(contract_text)
        title = self._extract_title(contract_text)

        # Extract entities and parties
        entities = await self._extract_entities(contract_text)
        parties = self._identify_parties(contract_text, entities)

        # Extract and analyze clauses
        clauses = await self._extract_clauses(contract_text, contract_type)

        # Extract payment terms
        payment_terms = self._extract_payment_terms(contract_text, entities)

        # Extract key dates
        key_dates = self._extract_key_dates(contract_text, entities)

        # Risk assessment
        risk_assessment = self._assess_risks(clauses, contract_text)

        # Compliance scoring
        compliance_score = self._calculate_compliance_score(clauses, contract_type)

        # Identify missing clauses
        missing_clauses = self._identify_missing_clauses(clauses, contract_type)

        # Generate recommendations
        recommendations = self._generate_recommendations(clauses, missing_clauses, risk_assessment)

        # Identify red flags
        redflags = self._identify_redflags(contract_text, clauses)

        # Financial summary
        financial_summary = self._create_financial_summary(payment_terms, entities)

        return ContractAnalysis(
            contract_id=contract_id,
            contract_type=contract_type,
            title=title,
            parties=parties,
            clauses=clauses,
            entities=entities,
            payment_terms=payment_terms,
            key_dates=key_dates,
            risk_assessment=risk_assessment,
            compliance_score=compliance_score,
            missing_clauses=missing_clauses,
            recommendations=recommendations,
            redflags=redflags,
            financial_summary=financial_summary
        )

    async def _identify_contract_type(self, text: str) -> ContractType:
        """Identify the type of contract"""
        text_lower = text.lower()

        # Keywords for each contract type
        type_keywords = {
            ContractType.SERVICE_AGREEMENT: ["service agreement", "services", "professional services"],
            ContractType.EMPLOYMENT: ["employment", "employee", "job description", "salary"],
            ContractType.NDA: ["non-disclosure", "confidentiality agreement", "nda"],
            ContractType.PURCHASE_ORDER: ["purchase order", "po", "goods", "purchase"],
            ContractType.LEASE: ["lease", "rental", "tenant", "landlord"],
            ContractType.VENDOR: ["vendor", "supplier", "supply agreement"],
            ContractType.LICENSING: ["license", "licensing", "intellectual property"],
            ContractType.PARTNERSHIP: ["partnership", "joint venture", "collaboration"],
            ContractType.CONSULTING: ["consulting", "consultant", "advisory"],
            ContractType.SOFTWARE_LICENSE: ["software license", "software", "end user"]
        }

        scores = {}
        for contract_type, keywords in type_keywords.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            scores[contract_type] = score

        # Return the type with the highest score
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return ContractType.SERVICE_AGREEMENT  # Default

    def _extract_title(self, text: str) -> str:
        """Extract contract title"""
        lines = text.split('\n')

        # Look for title in first few lines
        for line in lines[:10]:
            line = line.strip()
            if line and len(line) < 100 and not line.startswith('Page'):
                # Check if it looks like a title
                if any(word in line.lower() for word in ['agreement', 'contract', 'terms']):
                    return line

        return "Contract Agreement"

    async def _extract_entities(self, text: str) -> List[ContractEntity]:
        """Extract named entities from contract text"""
        entities = []

        # Use spaCy for NER if available
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                entities.append(ContractEntity(
                    entity_type=ent.label_,
                    text=ent.text,
                    start_position=ent.start_char,
                    end_position=ent.end_char,
                    confidence=1.0
                ))

        # Use regex patterns for specific entities
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append(ContractEntity(
                        entity_type=entity_type.upper(),
                        text=match.group(),
                        start_position=match.start(),
                        end_position=match.end(),
                        confidence=0.8
                    ))

        return entities

    def _identify_parties(self, text: str, entities: List[ContractEntity]) -> List[ContractParty]:
        """Identify contract parties"""
        parties = []

        # Look for organizations and persons
        orgs = [e for e in entities if e.entity_type in ['ORG', 'PERSON']]

        # Common party indicators
        party_patterns = [
            r'(?:Client|Customer|Buyer):\s*([^\n]+)',
            r'(?:Vendor|Supplier|Seller|Contractor):\s*([^\n]+)',
            r'(?:Company|Corporation|LLC|Inc\.?):\s*([^\n]+)',
            r'Party\s+A:\s*([^\n]+)',
            r'Party\s+B:\s*([^\n]+)'
        ]

        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                party_name = match.group(1).strip()
                role = match.group().split(':')[0].lower()

                parties.append(ContractParty(
                    name=party_name,
                    role=role,
                    address=None,
                    contact_info=None,
                    legal_entity_type=None
                ))

        # If no specific parties found, use organizations from entities
        if not parties and orgs:
            for i, org in enumerate(orgs[:2]):  # Take first two organizations
                role = "party_a" if i == 0 else "party_b"
                parties.append(ContractParty(
                    name=org.text,
                    role=role,
                    address=None,
                    contact_info=None,
                    legal_entity_type=None
                ))

        return parties

    async def _extract_clauses(self, text: str, contract_type: ContractType) -> List[ContractClause]:
        """Extract and analyze contract clauses"""
        clauses = []

        # Split text into sections
        sections = self._split_into_sections(text)

        for section in sections:
            clause_type = self._identify_clause_type(section)
            if clause_type:
                risk_level = self._assess_clause_risk(section, clause_type)
                key_terms = self._extract_clause_key_terms(section)
                concerns = self._identify_clause_concerns(section, clause_type)
                suggestions = self._generate_clause_suggestions(section, clause_type, concerns)

                clauses.append(ContractClause(
                    clause_type=clause_type,
                    content=section,
                    start_position=text.find(section),
                    end_position=text.find(section) + len(section),
                    risk_level=risk_level,
                    key_terms=key_terms,
                    concerns=concerns,
                    suggestions=suggestions
                ))

        return clauses

    def _split_into_sections(self, text: str) -> List[str]:
        """Split contract text into logical sections"""
        # Simple section splitting based on numbering and headers
        sections = []

        # Split by numbered sections
        numbered_sections = re.split(r'\n\s*\d+\.\s+', text)
        if len(numbered_sections) > 1:
            sections.extend([s.strip() for s in numbered_sections[1:] if s.strip()])
        else:
            # Split by paragraphs
            paragraphs = text.split('\n\n')
            sections.extend([p.strip() for p in paragraphs if len(p.strip()) > 50])

        return sections

    def _identify_clause_type(self, section: str) -> Optional[ClauseType]:
        """Identify the type of clause"""
        section_lower = section.lower()

        clause_keywords = {
            ClauseType.PAYMENT_TERMS: ["payment", "invoice", "billing", "fees", "compensation"],
            ClauseType.TERMINATION: ["termination", "terminate", "end", "expiry", "cancellation"],
            ClauseType.LIABILITY: ["liability", "damages", "loss", "harm", "responsible"],
            ClauseType.INTELLECTUAL_PROPERTY: ["intellectual property", "copyright", "trademark", "patent"],
            ClauseType.CONFIDENTIALITY: ["confidential", "non-disclosure", "proprietary", "secret"],
            ClauseType.INDEMNIFICATION: ["indemnify", "indemnification", "hold harmless", "defend"],
            ClauseType.DISPUTE_RESOLUTION: ["dispute", "arbitration", "mediation", "court", "jurisdiction"],
            ClauseType.FORCE_MAJEURE: ["force majeure", "act of god", "unforeseeable", "beyond control"],
            ClauseType.GOVERNING_LAW: ["governing law", "jurisdiction", "applicable law"],
            ClauseType.AMENDMENT: ["amendment", "modification", "change", "alter"],
            ClauseType.ASSIGNMENT: ["assignment", "transfer", "assign", "delegate"],
            ClauseType.COMPLIANCE: ["compliance", "regulatory", "legal requirements", "laws"]
        }

        scores = {}
        for clause_type, keywords in clause_keywords.items():
            score = sum(section_lower.count(keyword) for keyword in keywords)
            scores[clause_type] = score

        if max(scores.values()) > 0:
            return max(scores, key=scores.get)

        return None

    def _assess_clause_risk(self, section: str, clause_type: ClauseType) -> RiskLevel:
        """Assess risk level of a specific clause"""
        section_lower = section.lower()

        # Check for risk patterns
        for risk_name, risk_info in self.risk_patterns.items():
            for pattern in risk_info["patterns"]:
                if re.search(pattern, section_lower):
                    return risk_info["risk_level"]

        # Clause-specific risk assessment
        if clause_type == ClauseType.LIABILITY:
            if any(word in section_lower for word in ["unlimited", "without limit", "no cap"]):
                return RiskLevel.CRITICAL
            elif any(word in section_lower for word in ["limited to", "not exceed", "maximum"]):
                return RiskLevel.LOW
            else:
                return RiskLevel.MEDIUM

        elif clause_type == ClauseType.TERMINATION:
            if any(word in section_lower for word in ["immediate", "without notice", "cause"]):
                return RiskLevel.HIGH
            elif any(word in section_lower for word in ["30 days", "notice", "written"]):
                return RiskLevel.LOW
            else:
                return RiskLevel.MEDIUM

        elif clause_type == ClauseType.PAYMENT_TERMS:
            if any(word in section_lower for word in ["penalty", "interest", "late fee"]):
                return RiskLevel.MEDIUM
            else:
                return RiskLevel.LOW

        return RiskLevel.LOW

    def _extract_clause_key_terms(self, section: str) -> List[str]:
        """Extract key terms from a clause"""
        # Use TextBlob for noun phrase extraction
        blob = TextBlob(section)
        noun_phrases = [phrase for phrase in blob.noun_phrases if len(phrase.split()) <= 4]

        # Extract monetary amounts
        money_amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', section)

        # Extract dates
        dates = []
        for pattern in self.patterns["dates"]:
            dates.extend(re.findall(pattern, section))

        # Extract percentages
        percentages = re.findall(r'\d+(?:\.\d+)?%', section)

        key_terms = noun_phrases + money_amounts + dates + percentages
        return list(set(key_terms))[:10]  # Limit to top 10

    def _identify_clause_concerns(self, section: str, clause_type: ClauseType) -> List[str]:
        """Identify potential concerns in a clause"""
        concerns = []
        section_lower = section.lower()

        # General red flag words
        red_flags = [
            "unlimited", "without limit", "sole discretion", "irrevocable",
            "perpetual", "unconditional", "absolute", "waive", "forfeit"
        ]

        for flag in red_flags:
            if flag in section_lower:
                concerns.append(f"Contains potentially problematic term: '{flag}'")

        # Clause-specific concerns
        if clause_type == ClauseType.TERMINATION:
            if "without cause" in section_lower and "immediate" in section_lower:
                concerns.append("Allows immediate termination without cause")

        elif clause_type == ClauseType.LIABILITY:
            if "consequential damages" in section_lower:
                concerns.append("May include liability for consequential damages")

        elif clause_type == ClauseType.PAYMENT_TERMS:
            if re.search(r'\d+%.*late', section_lower):
                concerns.append("High late payment penalties")

        return concerns

    def _generate_clause_suggestions(self, section: str, clause_type: ClauseType, concerns: List[str]) -> List[str]:
        """Generate improvement suggestions for a clause"""
        suggestions = []

        if concerns:
            if clause_type == ClauseType.LIABILITY:
                suggestions.append("Consider adding liability caps to limit exposure")
                suggestions.append("Exclude consequential damages from liability")

            elif clause_type == ClauseType.TERMINATION:
                suggestions.append("Add reasonable notice period for termination")
                suggestions.append("Specify acceptable reasons for immediate termination")

            elif clause_type == ClauseType.PAYMENT_TERMS:
                suggestions.append("Negotiate more reasonable payment terms")
                suggestions.append("Consider adding early payment discounts")

        # Standard suggestions by clause type
        if clause_type == ClauseType.INTELLECTUAL_PROPERTY:
            suggestions.append("Ensure work product ownership is clearly defined")
            suggestions.append("Consider retaining rights to pre-existing IP")

        elif clause_type == ClauseType.CONFIDENTIALITY:
            suggestions.append("Define what constitutes confidential information")
            suggestions.append("Set reasonable confidentiality period")

        return suggestions

    def _extract_payment_terms(self, text: str, entities: List[ContractEntity]) -> List[PaymentTerm]:
        """Extract payment terms from contract"""
        payment_terms = []

        # Extract monetary amounts
        money_entities = [e for e in entities if e.entity_type == "MONEY"]

        # Look for payment-related sections
        payment_sections = re.findall(
            r'payment.*?(?=\n\n|\Z)',
            text,
            re.IGNORECASE | re.DOTALL
        )

        for section in payment_sections:
            # Extract amount
            amount = None
            if money_entities:
                amount_text = money_entities[0].text
                amount = float(re.sub(r'[^\d.]', '', amount_text))

            # Extract currency
            currency = "USD"  # Default
            if any(curr in section.upper() for curr in ["EUR", "GBP", "CAD"]):
                currency = next(curr for curr in ["EUR", "GBP", "CAD"] if curr in section.upper())

            # Extract due date info
            due_date = None
            due_patterns = [
                r'due\s+(?:within\s+)?(\d+)\s+days',
                r'payment\s+due\s+(\d+)\s+days',
                r'net\s+(\d+)'
            ]

            for pattern in due_patterns:
                match = re.search(pattern, section, re.IGNORECASE)
                if match:
                    days = int(match.group(1))
                    due_date = datetime.now() + timedelta(days=days)
                    break

            payment_terms.append(PaymentTerm(
                amount=amount,
                currency=currency,
                due_date=due_date,
                payment_method=None,
                late_fee=None,
                discount_terms=None
            ))

        return payment_terms

    def _extract_key_dates(self, text: str, entities: List[ContractEntity]) -> Dict[str, datetime]:
        """Extract important dates from contract"""
        key_dates = {}

        # Get date entities
        date_entities = [e for e in entities if e.entity_type == "DATES"]

        # Look for specific date types
        date_patterns = {
            "effective_date": [r'effective\s+date:?\s*([^\n]+)', r'commencing\s+on\s+([^\n]+)'],
            "expiration_date": [r'expir(?:es|ation)\s+(?:date:?)?\s*([^\n]+)', r'term\s+ends?\s+([^\n]+)'],
            "renewal_date": [r'renewal\s+date:?\s*([^\n]+)', r'renew(?:s|al)\s+on\s+([^\n]+)'],
            "termination_date": [r'terminat(?:es|ion)\s+(?:date:?)?\s*([^\n]+)'],
            "signature_date": [r'signed?\s+(?:on\s+)?([^\n]+)', r'date\s+of\s+signature:?\s*([^\n]+)']
        }

        for date_type, patterns in date_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    try:
                        parsed_date = date_parser.parse(date_str)
                        key_dates[date_type] = parsed_date
                        break
                    except:
                        continue

        return key_dates

    def _assess_risks(self, clauses: List[ContractClause], text: str) -> Dict[RiskLevel, int]:
        """Assess overall contract risks"""
        risk_counts = {level: 0 for level in RiskLevel}

        # Count risks from clauses
        for clause in clauses:
            risk_counts[clause.risk_level] += 1

        # Check for global risk patterns
        text_lower = text.lower()

        # Additional risk checks
        if "unlimited liability" in text_lower:
            risk_counts[RiskLevel.CRITICAL] += 1

        if "automatic renewal" in text_lower and "notice" not in text_lower:
            risk_counts[RiskLevel.HIGH] += 1

        if "indemnify" in text_lower and ("all" in text_lower or "any" in text_lower):
            risk_counts[RiskLevel.HIGH] += 1

        return risk_counts

    def _calculate_compliance_score(self, clauses: List[ContractClause], contract_type: ContractType) -> float:
        """Calculate compliance score based on standard requirements"""
        standard_clauses = self.standard_clauses.get(contract_type, {})

        if not standard_clauses:
            return 80.0  # Default score for unknown types

        present_clause_types = {clause.clause_type for clause in clauses}
        required_clause_types = set(standard_clauses.keys())

        # Base score for having required clauses
        coverage = len(present_clause_types.intersection(required_clause_types)) / len(required_clause_types)
        base_score = coverage * 70  # 70% for having required clauses

        # Penalty for high-risk clauses
        high_risk_clauses = [c for c in clauses if c.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        risk_penalty = min(len(high_risk_clauses) * 5, 30)  # Max 30% penalty

        # Bonus for comprehensive coverage
        extra_clauses = len(present_clause_types) - len(required_clause_types)
        coverage_bonus = min(extra_clauses * 2, 20)  # Max 20% bonus

        final_score = min(base_score + coverage_bonus - risk_penalty, 100)
        return max(final_score, 0)

    def _identify_missing_clauses(self, clauses: List[ContractClause], contract_type: ContractType) -> List[ClauseType]:
        """Identify missing standard clauses"""
        standard_clauses = self.standard_clauses.get(contract_type, {})
        present_clause_types = {clause.clause_type for clause in clauses}
        required_clause_types = set(standard_clauses.keys())

        return list(required_clause_types - present_clause_types)

    def _generate_recommendations(self, clauses: List[ContractClause], missing_clauses: List[ClauseType], risk_assessment: Dict[RiskLevel, int]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Missing clause recommendations
        for missing_clause in missing_clauses:
            if missing_clause == ClauseType.LIABILITY:
                recommendations.append("Add liability limitation clause to cap financial exposure")
            elif missing_clause == ClauseType.TERMINATION:
                recommendations.append("Include clear termination procedures and notice requirements")
            elif missing_clause == ClauseType.DISPUTE_RESOLUTION:
                recommendations.append("Add dispute resolution clause to avoid costly litigation")
            elif missing_clause == ClauseType.FORCE_MAJEURE:
                recommendations.append("Include force majeure clause for unforeseeable circumstances")

        # Risk-based recommendations
        if risk_assessment[RiskLevel.CRITICAL] > 0:
            recommendations.append("CRITICAL: Address unlimited liability and high-risk clauses immediately")

        if risk_assessment[RiskLevel.HIGH] > 2:
            recommendations.append("Consider legal review due to multiple high-risk clauses")

        # Clause-specific recommendations
        for clause in clauses:
            if clause.suggestions:
                recommendations.extend(clause.suggestions[:2])  # Limit to top 2 per clause

        return list(set(recommendations))  # Remove duplicates

    def _identify_redflags(self, text: str, clauses: List[ContractClause]) -> List[str]:
        """Identify major red flags in the contract"""
        redflags = []
        text_lower = text.lower()

        # Critical red flags
        critical_flags = [
            ("unlimited liability", "Unlimited financial liability exposure"),
            ("waive all rights", "Waiver of all legal rights"),
            ("sole discretion", "Gives one party complete control"),
            ("irrevocable", "Cannot be cancelled or changed"),
            ("penalty", "Financial penalties for non-compliance"),
            ("liquidated damages", "Pre-set damage amounts"),
            ("no warranty", "Complete warranty disclaimer"),
            ("as is", "No guarantees on quality or performance")
        ]

        for flag_text, description in critical_flags:
            if flag_text in text_lower:
                redflags.append(description)

        # Missing essential clauses
        essential_clauses = [ClauseType.LIABILITY, ClauseType.TERMINATION]
        present_clause_types = {clause.clause_type for clause in clauses}

        for essential in essential_clauses:
            if essential not in present_clause_types:
                redflags.append(f"Missing essential {essential.value.replace('_', ' ')} clause")

        # High-risk clause concentrations
        critical_clauses = [c for c in clauses if c.risk_level == RiskLevel.CRITICAL]
        if len(critical_clauses) > 1:
            redflags.append("Multiple critical risk clauses present")

        return redflags

    def _create_financial_summary(self, payment_terms: List[PaymentTerm], entities: List[ContractEntity]) -> Dict[str, Any]:
        """Create financial summary of the contract"""
        summary = {
            "total_value": 0,
            "currency": "USD",
            "payment_schedule": [],
            "penalties": [],
            "discounts": []
        }

        # Calculate total value
        money_entities = [e for e in entities if e.entity_type == "MONEY"]
        if money_entities:
            amounts = []
            for entity in money_entities:
                try:
                    amount = float(re.sub(r'[^\d.]', '', entity.text))
                    amounts.append(amount)
                except:
                    continue

            if amounts:
                summary["total_value"] = max(amounts)  # Use largest amount as total value

        # Payment terms summary
        for term in payment_terms:
            if term.amount:
                summary["payment_schedule"].append({
                    "amount": term.amount,
                    "due_date": term.due_date.isoformat() if term.due_date else None,
                    "currency": term.currency
                })

        return summary

    async def compare_with_template(self, analysis: ContractAnalysis, template_type: ContractType) -> Dict[str, Any]:
        """Compare contract against standard template"""
        standard_clauses = self.standard_clauses.get(template_type, {})

        comparison = {
            "template_type": template_type.value,
            "coverage_score": 0,
            "deviations": [],
            "improvements": [],
            "compliance_issues": []
        }

        present_clause_types = {clause.clause_type for clause in analysis.clauses}
        required_clause_types = set(standard_clauses.keys())

        # Calculate coverage
        coverage = len(present_clause_types.intersection(required_clause_types)) / len(required_clause_types) if required_clause_types else 1
        comparison["coverage_score"] = coverage * 100

        # Identify deviations
        for clause in analysis.clauses:
            if clause.clause_type in standard_clauses:
                standard_text = standard_clauses[clause.clause_type]
                if clause.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    comparison["deviations"].append({
                        "clause_type": clause.clause_type.value,
                        "risk_level": clause.risk_level.value,
                        "concerns": clause.concerns
                    })

        # Suggest improvements
        for missing_clause in analysis.missing_clauses:
            if missing_clause in standard_clauses:
                comparison["improvements"].append({
                    "add_clause": missing_clause.value,
                    "suggested_text": standard_clauses[missing_clause]
                })

        return comparison

    async def generate_risk_report(self, analysis: ContractAnalysis) -> Dict[str, Any]:
        """Generate comprehensive risk report"""
        report = {
            "contract_id": analysis.contract_id,
            "overall_risk_level": self._calculate_overall_risk(analysis),
            "risk_breakdown": analysis.risk_assessment,
            "critical_issues": [],
            "recommendations": analysis.recommendations,
            "financial_exposure": self._calculate_financial_exposure(analysis),
            "compliance_status": {
                "score": analysis.compliance_score,
                "status": "Compliant" if analysis.compliance_score >= 80 else "Needs Review"
            },
            "action_items": []
        }

        # Identify critical issues
        for clause in analysis.clauses:
            if clause.risk_level == RiskLevel.CRITICAL:
                report["critical_issues"].append({
                    "clause_type": clause.clause_type.value,
                    "concerns": clause.concerns,
                    "impact": "High financial or legal risk"
                })

        # Generate action items
        if report["critical_issues"]:
            report["action_items"].append("URGENT: Address critical risk clauses before signing")

        if analysis.compliance_score < 70:
            report["action_items"].append("Legal review recommended due to low compliance score")

        if analysis.redflags:
            report["action_items"].append("Review red flags and consider renegotiation")

        return report

    def _calculate_overall_risk(self, analysis: ContractAnalysis) -> RiskLevel:
        """Calculate overall contract risk level"""
        risk_counts = analysis.risk_assessment

        if risk_counts[RiskLevel.CRITICAL] > 0:
            return RiskLevel.CRITICAL
        elif risk_counts[RiskLevel.HIGH] > 2:
            return RiskLevel.HIGH
        elif risk_counts[RiskLevel.HIGH] > 0 or risk_counts[RiskLevel.MEDIUM] > 3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_financial_exposure(self, analysis: ContractAnalysis) -> Dict[str, Any]:
        """Calculate potential financial exposure"""
        exposure = {
            "contract_value": analysis.financial_summary.get("total_value", 0),
            "liability_cap": None,
            "penalty_exposure": 0,
            "unlimited_liability": False
        }

        # Check for liability limitations
        liability_clauses = [c for c in analysis.clauses if c.clause_type == ClauseType.LIABILITY]
        for clause in liability_clauses:
            if "unlimited" in clause.content.lower():
                exposure["unlimited_liability"] = True
            else:
                # Look for liability cap amounts
                amounts = re.findall(r'\$[\d,]+(?:\.\d{2})?', clause.content)
                if amounts:
                    try:
                        cap_amount = float(re.sub(r'[^\d.]', '', amounts[0]))
                        exposure["liability_cap"] = cap_amount
                    except:
                        pass

        return exposure


# Usage example and testing
async def main():
    """Example usage of the Contract Analyzer Agent"""
    agent = ContractAnalyzerAgent()

    # Sample contract text
    sample_contract = """
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

    print("🔍 Analyzing contract...")
    analysis = await agent.analyze_contract(sample_contract)

    print(f"\n📄 Contract Analysis Report")
    print(f"Contract ID: {analysis.contract_id}")
    print(f"Type: {analysis.contract_type.value}")
    print(f"Title: {analysis.title}")
    print(f"Compliance Score: {analysis.compliance_score:.1f}%")

    print(f"\n🏢 Parties:")
    for party in analysis.parties:
        print(f"  • {party.name} ({party.role})")

    print(f"\n📋 Clauses Found:")
    for clause in analysis.clauses:
        print(f"  • {clause.clause_type.value}: {clause.risk_level.value} risk")
        if clause.concerns:
            print(f"    Concerns: {', '.join(clause.concerns)}")

    print(f"\n💰 Financial Summary:")
    print(f"  • Total Value: ${analysis.financial_summary['total_value']:,.2f}")
    print(f"  • Currency: {analysis.financial_summary['currency']}")

    print(f"\n📅 Key Dates:")
    for date_type, date_value in analysis.key_dates.items():
        print(f"  • {date_type.replace('_', ' ').title()}: {date_value.strftime('%Y-%m-%d')}")

    print(f"\n⚠️ Risk Assessment:")
    for risk_level, count in analysis.risk_assessment.items():
        if count > 0:
            print(f"  • {risk_level.value.title()}: {count} clauses")

    if analysis.missing_clauses:
        print(f"\n❌ Missing Clauses:")
        for clause_type in analysis.missing_clauses:
            print(f"  • {clause_type.value.replace('_', ' ').title()}")

    if analysis.redflags:
        print(f"\n🚨 Red Flags:")
        for flag in analysis.redflags:
            print(f"  • {flag}")

    print(f"\n💡 Recommendations:")
    for recommendation in analysis.recommendations[:5]:
        print(f"  • {recommendation}")

    # Generate risk report
    print("\n📊 Generating risk report...")
    risk_report = await agent.generate_risk_report(analysis)

    print(f"\nOverall Risk Level: {risk_report['overall_risk_level'].value.upper()}")
    print(f"Compliance Status: {risk_report['compliance_status']['status']}")

    if risk_report["action_items"]:
        print(f"\n✅ Action Items:")
        for item in risk_report["action_items"]:
            print(f"  • {item}")

    # Compare with template
    print("\n📋 Comparing with standard template...")
    comparison = await agent.compare_with_template(analysis, ContractType.SERVICE_AGREEMENT)

    print(f"Template Coverage: {comparison['coverage_score']:.1f}%")

    if comparison["improvements"]:
        print(f"\nSuggested Improvements:")
        for improvement in comparison["improvements"][:3]:
            print(f"  • Add {improvement['add_clause'].replace('_', ' ')}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the example
    asyncio.run(main())