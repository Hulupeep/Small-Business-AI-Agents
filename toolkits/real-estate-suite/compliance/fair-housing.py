"""
Fair Housing Compliance Checker
Basic compliance checking for real estate marketing content.
Helps identify potentially problematic language that may violate Fair Housing laws.
"""

import re
import logging
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ViolationType(Enum):
    """Types of potential Fair Housing violations."""
    FAMILIAL_STATUS = "familial_status"
    RELIGION = "religion"
    RACE_ETHNICITY = "race_ethnicity"
    DISABILITY = "disability"
    NATIONAL_ORIGIN = "national_origin"
    SOURCE_OF_INCOME = "source_of_income"

@dataclass
class ComplianceIssue:
    """Represents a potential compliance issue found in text."""
    violation_type: ViolationType
    original_phrase: str
    explanation: str
    suggested_replacement: str
    severity: str  # high, medium, low

@dataclass
class ComplianceResult:
    """Results of compliance check."""
    is_compliant: bool
    issues: List[ComplianceIssue]
    corrected_text: str
    suggestions: List[str]

class BasicFairHousingChecker:
    """Basic Fair Housing compliance checker for real estate marketing text."""

    def __init__(self, openai_api_key: str = None):
        self.openai_client = None
        if openai_api_key or os.getenv('OPENAI_API_KEY'):
            self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))

        # Load basic compliance rules
        self.prohibited_terms = self._load_prohibited_terms()
        self.replacements = self._load_safe_replacements()

    def _load_prohibited_terms(self) -> Dict[ViolationType, List[str]]:
        """Load basic prohibited terms organized by violation type."""
        return {
            ViolationType.FAMILIAL_STATUS: [
                'family', 'families', 'children', 'kids', 'child-friendly',
                'family-oriented', 'singles', 'couples only', 'no children',
                'adult community', 'mature', 'empty nesters', 'retirees',
                'adults only', 'seniors only'
            ],
            ViolationType.RELIGION: [
                'christian', 'jewish', 'muslim', 'church', 'temple', 'mosque',
                'synagogue', 'religious', 'kosher', 'blessed', 'cathedral'
            ],
            ViolationType.RACE_ETHNICITY: [
                'white', 'black', 'asian', 'hispanic', 'latino', 'african american',
                'caucasian', 'minority', 'ethnic', 'diverse', 'integrated'
            ],
            ViolationType.DISABILITY: [
                'disabled', 'handicapped', 'wheelchair accessible', 'special needs',
                'mobility impaired', 'handicap accessible'
            ],
            ViolationType.NATIONAL_ORIGIN: [
                'american only', 'english only', 'foreign', 'immigrant',
                'no foreigners', 'citizens only', 'documented'
            ],
            ViolationType.SOURCE_OF_INCOME: [
                'no section 8', 'no vouchers', 'no housing assistance',
                'no government assistance', 'income restrictions'
            ]
        }

    def _load_safe_replacements(self) -> Dict[str, str]:
        """Load safe replacement phrases for problematic terms."""
        return {
            # Familial status replacements
            'family-friendly': 'spacious layout',
            'great for families': 'versatile living space',
            'perfect for children': 'flexible floor plan',
            'no children': 'adult building (where legally permitted)',
            'adults only': 'age-restricted community (55+)',
            'mature residents': 'age-qualified community',
            'singles preferred': 'efficient layout',
            'couples only': 'intimate setting',

            # Religious replacements
            'near church': 'near places of worship',
            'christian community': 'faith-friendly area',
            'kosher kitchen': 'specialty kitchen',
            'blessed home': 'special property',

            # General descriptive replacements
            'quiet building': 'well-maintained building',
            'peaceful community': 'tranquil neighborhood',
            'sophisticated residents': 'quality community',
            'upscale clientele': 'professional community',

            # Accessibility replacements
            'wheelchair accessible': 'accessibility features available',
            'handicap accessible': 'accessible design',
            'disabled friendly': 'universal design features',

            # Economic/source replacements
            'no section 8': 'traditional rental terms',
            'no vouchers': 'standard lease terms',
            'income requirements': 'qualification criteria',
            'credit check required': 'standard application process'
        }

    def check_compliance(self, text: str) -> ComplianceResult:
        """
        Check text for basic Fair Housing compliance issues.

        Args:
            text: Marketing text to check

        Returns:
            ComplianceResult with issues and suggestions
        """
        issues = []
        corrected_text = text

        # Check for prohibited terms
        for violation_type, terms in self.prohibited_terms.items():
            for term in terms:
                if self._contains_term(text, term):
                    issue = ComplianceIssue(
                        violation_type=violation_type,
                        original_phrase=term,
                        explanation=self._get_explanation(violation_type, term),
                        suggested_replacement=self._get_replacement(term),
                        severity=self._get_severity(violation_type, term)
                    )
                    issues.append(issue)

                    # Apply correction to text
                    corrected_text = self._apply_correction(corrected_text, term, issue.suggested_replacement)

        # Generate suggestions
        suggestions = self._generate_suggestions(issues)

        return ComplianceResult(
            is_compliant=len(issues) == 0,
            issues=issues,
            corrected_text=corrected_text,
            suggestions=suggestions
        )

    async def enhanced_check(self, text: str) -> ComplianceResult:
        """
        Enhanced compliance check using AI analysis.

        Args:
            text: Marketing text to analyze

        Returns:
            Enhanced ComplianceResult
        """
        # First run basic check
        basic_result = self.check_compliance(text)

        if not self.openai_client:
            logger.info("OpenAI client not available, using basic checking only")
            return basic_result

        # AI-enhanced analysis
        try:
            ai_prompt = f"""
            Review this real estate marketing text for Fair Housing Act compliance:

            TEXT: "{text}"

            Check for violations of these protected classes:
            - Race, Color, National Origin
            - Religion
            - Sex/Gender
            - Familial Status (families with children)
            - Disability

            Identify any language that might:
            1. Express preference for certain groups
            2. Exclude or discourage protected classes
            3. Use coded language that could be discriminatory

            Provide specific recommendations for improvement.
            Keep response concise and practical.
            """

            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Fair Housing compliance expert. Identify potential issues and suggest improvements."},
                    {"role": "user", "content": ai_prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )

            ai_feedback = response.choices[0].message.content.strip()
            basic_result.suggestions.append(f"AI Analysis: {ai_feedback}")

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")

        return basic_result

    def _contains_term(self, text: str, term: str) -> bool:
        """Check if text contains potentially problematic term."""
        # Case insensitive, whole word matching
        pattern = r'\b' + re.escape(term.lower()) + r'\b'
        return bool(re.search(pattern, text.lower()))

    def _get_explanation(self, violation_type: ViolationType, term: str) -> str:
        """Get explanation for why term is problematic."""
        explanations = {
            ViolationType.FAMILIAL_STATUS: f"'{term}' may indicate preference for or against families with children",
            ViolationType.RELIGION: f"'{term}' references religion, which is a protected class",
            ViolationType.RACE_ETHNICITY: f"'{term}' references race or ethnicity, which is protected",
            ViolationType.DISABILITY: f"'{term}' may discourage people with disabilities",
            ViolationType.NATIONAL_ORIGIN: f"'{term}' may discriminate based on national origin",
            ViolationType.SOURCE_OF_INCOME: f"'{term}' may discriminate against housing assistance recipients"
        }
        return explanations.get(violation_type, f"'{term}' may be discriminatory")

    def _get_replacement(self, term: str) -> str:
        """Get safe replacement for problematic term."""
        return self.replacements.get(term.lower(), "property available to qualified applicants")

    def _get_severity(self, violation_type: ViolationType, term: str) -> str:
        """Determine severity of potential violation."""
        high_severity_terms = [
            'no children', 'adults only', 'no section 8', 'no vouchers',
            'english only', 'citizens only'
        ]

        if term.lower() in high_severity_terms:
            return "high"
        elif violation_type in [ViolationType.FAMILIAL_STATUS, ViolationType.RACE_ETHNICITY]:
            return "medium"
        else:
            return "low"

    def _apply_correction(self, text: str, original_term: str, replacement: str) -> str:
        """Apply correction to text."""
        # Case insensitive replacement
        pattern = re.compile(re.escape(original_term), re.IGNORECASE)
        return pattern.sub(replacement, text)

    def _generate_suggestions(self, issues: List[ComplianceIssue]) -> List[str]:
        """Generate practical suggestions based on found issues."""
        suggestions = []

        if not issues:
            suggestions.append("Text appears compliant with basic Fair Housing requirements")
            return suggestions

        # Group issues by type
        issue_types = set(issue.violation_type for issue in issues)

        if ViolationType.FAMILIAL_STATUS in issue_types:
            suggestions.append("Focus on property features rather than target demographics")
            suggestions.append("Avoid language that suggests preference for certain family types")

        if ViolationType.RELIGION in issue_types:
            suggestions.append("Use 'places of worship' instead of specific religious references")

        if ViolationType.RACE_ETHNICITY in issue_types:
            suggestions.append("Describe neighborhood amenities without referencing demographics")

        if ViolationType.DISABILITY in issue_types:
            suggestions.append("Describe accessibility features factually without assumptions")

        # General suggestions
        high_severity_count = len([i for i in issues if i.severity == "high"])
        if high_severity_count > 0:
            suggestions.append("Consider legal review - high-severity issues found")

        suggestions.extend([
            "Use objective, descriptive language about property and location",
            "Focus on amenities, features, and benefits rather than target audience",
            "Consider Fair Housing training for marketing team"
        ])

        return suggestions

    def generate_safe_description(self, property_details: Dict) -> str:
        """
        Generate a Fair Housing compliant property description.

        Args:
            property_details: Dict with property information

        Returns:
            Compliant property description
        """
        bedrooms = property_details.get('bedrooms', 0)
        bathrooms = property_details.get('bathrooms', 0)
        sqft = property_details.get('square_footage', 0)
        features = property_details.get('features', [])
        location = property_details.get('city', 'desirable location')

        description_parts = [
            f"Attractive {bedrooms}-bedroom, {bathrooms}-bathroom property",
            f"featuring {sqft:,} square feet of living space" if sqft else "with generous living space",
            f"Located in {location} with convenient access to amenities"
        ]

        # Add features safely
        safe_features = []
        for feature in features:
            # Convert potentially problematic features to safe descriptions
            if 'family' in feature.lower():
                safe_features.append('spacious layout')
            elif 'updated' in feature.lower():
                safe_features.append(feature)  # Updates are safe
            elif 'kitchen' in feature.lower():
                safe_features.append(feature)  # Kitchen features are safe
            else:
                safe_features.append(feature)

        if safe_features:
            description_parts.append(f"Notable features include: {', '.join(safe_features[:3])}")

        description_parts.extend([
            "Property offers excellent value and modern conveniences",
            "Perfect opportunity for qualified buyers"
        ])

        return ". ".join(description_parts) + "."

# Example usage and testing
def main():
    """Example usage of Fair Housing checker."""

    checker = BasicFairHousingChecker()

    # Test cases
    test_cases = [
        "Beautiful family home with great schools nearby! Perfect for young professionals with children.",
        "Spacious 3-bedroom home in established neighborhood. Close to parks, shopping, and transportation.",
        "No children allowed. Adults only building. No Section 8 accepted.",
        "Luxury condo near church and community center. Great for executives and professionals.",
        "Quiet, mature community. English-speaking tenants preferred."
    ]

    print("FAIR HOUSING COMPLIANCE CHECK")
    print("=" * 50)

    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTEST CASE {i}:")
        print(f"Original: {test_text}")

        # Check compliance
        result = checker.check_compliance(test_text)

        if result.is_compliant:
            print("✅ COMPLIANT")
        else:
            print(f"❌ ISSUES FOUND ({len(result.issues)})")

            for issue in result.issues:
                print(f"  • Issue: '{issue.original_phrase}' ({issue.severity} severity)")
                print(f"    Problem: {issue.explanation}")
                print(f"    Suggestion: '{issue.suggested_replacement}'")

            print(f"\nCorrected text: {result.corrected_text}")

        if result.suggestions:
            print(f"\nSuggestions:")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")

        print("-" * 50)

    # Example of generating safe description
    print("\nSAFE DESCRIPTION GENERATION:")
    property_details = {
        'bedrooms': 3,
        'bathrooms': 2,
        'square_footage': 1800,
        'features': ['updated kitchen', 'hardwood floors', 'family room'],
        'city': 'Austin'
    }

    safe_description = checker.generate_safe_description(property_details)
    print(f"Generated: {safe_description}")

if __name__ == "__main__":
    main()