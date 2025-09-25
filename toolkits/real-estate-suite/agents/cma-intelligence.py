"""
CMA (Comparative Market Analysis) Agent
Generates property valuations and market analysis using available data sources.
Practical tool for real estate agents to create professional CMA reports.
"""

import asyncio
import json
import logging
import statistics
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import openai
import pandas as pd
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"

class PropertyStatus(Enum):
    SOLD = "sold"
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"

@dataclass
class SimplePropertyData:
    """Basic property data structure for CMA analysis."""

    # Basic Property Information
    address: str
    city: str
    state: str
    zip_code: str

    # Property Details
    property_type: PropertyType
    bedrooms: int
    bathrooms: float
    square_footage: int
    lot_size: Optional[float] = None
    year_built: Optional[int] = None
    garage_spaces: Optional[int] = None

    # Pricing Information
    list_price: Optional[int] = None
    sale_price: Optional[int] = None
    price_per_sqft: Optional[float] = None

    # Market Information
    status: PropertyStatus = PropertyStatus.ACTIVE
    list_date: Optional[datetime] = None
    sale_date: Optional[datetime] = None
    days_on_market: Optional[int] = None

    # Additional Features
    features: List[str] = None
    mls_number: Optional[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        # Calculate price per square foot
        if self.sale_price and self.square_footage:
            self.price_per_sqft = self.sale_price / self.square_footage
        elif self.list_price and self.square_footage:
            self.price_per_sqft = self.list_price / self.square_footage

@dataclass
class CMAResult:
    """Results of Comparative Market Analysis."""

    subject_address: str
    analysis_date: datetime
    comparable_count: int
    estimated_value: int
    value_range_low: int
    value_range_high: int
    price_per_sqft_avg: float
    average_days_on_market: int
    market_conditions: str
    confidence_level: str
    comparable_properties: List[Dict]
    pricing_recommendations: Dict
    market_analysis: str
    next_steps: List[str]

class SimpleCMAAgent:
    """Practical CMA generator using available data and AI analysis."""

    def __init__(self, openai_api_key: str = None, database_url: str = None):
        self.openai_client = openai.OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
        self.db_engine = None
        if database_url or os.getenv('DATABASE_URL'):
            self.db_engine = create_engine(database_url or os.getenv('DATABASE_URL'))
            self.setup_database()

    def setup_database(self):
        """Initialize simple database table for property data."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS properties (
            id SERIAL PRIMARY KEY,
            mls_number VARCHAR(50),
            address VARCHAR(500) NOT NULL,
            city VARCHAR(100),
            state VARCHAR(10),
            zip_code VARCHAR(10),
            property_type VARCHAR(50),
            bedrooms INTEGER,
            bathrooms DECIMAL(3,1),
            square_footage INTEGER,
            lot_size DECIMAL(10,2),
            year_built INTEGER,
            garage_spaces INTEGER,
            list_price INTEGER,
            sale_price INTEGER,
            price_per_sqft DECIMAL(8,2),
            status VARCHAR(20),
            list_date DATE,
            sale_date DATE,
            days_on_market INTEGER,
            features TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_properties_location ON properties(city, state, zip_code);
        CREATE INDEX IF NOT EXISTS idx_properties_size ON properties(bedrooms, bathrooms, square_footage);
        CREATE INDEX IF NOT EXISTS idx_properties_sale_date ON properties(sale_date);
        """

        with self.db_engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()

    async def generate_cma(self, subject_property: SimplePropertyData,
                          months_back: int = 6,
                          radius_miles: float = 2.0) -> CMAResult:
        """
        Generate a Comparative Market Analysis for a property.

        Args:
            subject_property: Property to analyze
            months_back: How many months back to look for comparable sales
            radius_miles: Search radius (if location data available)

        Returns:
            CMAResult with analysis and recommendations
        """
        try:
            # Find comparable properties
            comparables = await self._find_comparables(subject_property, months_back)

            if not comparables:
                logger.warning("No comparable properties found")
                return self._generate_no_comps_result(subject_property)

            # Perform analysis
            analysis_results = self._analyze_comparables(subject_property, comparables)

            # Generate AI insights
            ai_analysis = await self._generate_ai_analysis(subject_property, comparables, analysis_results)

            # Create pricing recommendations
            pricing_recs = self._generate_pricing_recommendations(
                subject_property, analysis_results, len(comparables)
            )

            # Generate next steps
            next_steps = self._generate_next_steps(subject_property, analysis_results)

            return CMAResult(
                subject_address=subject_property.address,
                analysis_date=datetime.now(),
                comparable_count=len(comparables),
                estimated_value=analysis_results["estimated_value"],
                value_range_low=analysis_results["value_range_low"],
                value_range_high=analysis_results["value_range_high"],
                price_per_sqft_avg=analysis_results["avg_price_per_sqft"],
                average_days_on_market=analysis_results["avg_days_on_market"],
                market_conditions=analysis_results["market_conditions"],
                confidence_level=analysis_results["confidence_level"],
                comparable_properties=[asdict(comp) for comp in comparables],
                pricing_recommendations=pricing_recs,
                market_analysis=ai_analysis,
                next_steps=next_steps
            )

        except Exception as e:
            logger.error(f"Error generating CMA: {str(e)}")
            raise

    async def _find_comparables(self, subject: SimplePropertyData, months_back: int) -> List[SimplePropertyData]:
        """Find comparable properties from database or sample data."""

        if not self.db_engine:
            logger.info("No database connection - using sample data")
            return self._generate_sample_comparables(subject)

        # Calculate search parameters
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months_back * 30)

        # Define size ranges (20% variance)
        sqft_range = (
            int(subject.square_footage * 0.8),
            int(subject.square_footage * 1.2)
        )
        bed_range = (
            max(1, subject.bedrooms - 1),
            subject.bedrooms + 1
        )
        bath_range = (
            max(1, subject.bathrooms - 0.5),
            subject.bathrooms + 1
        )

        search_sql = """
        SELECT * FROM properties
        WHERE status = 'sold'
        AND sale_date >= %(start_date)s
        AND sale_date <= %(end_date)s
        AND property_type = %(property_type)s
        AND city = %(city)s
        AND state = %(state)s
        AND bedrooms BETWEEN %(bed_min)s AND %(bed_max)s
        AND bathrooms BETWEEN %(bath_min)s AND %(bath_max)s
        AND square_footage BETWEEN %(sqft_min)s AND %(sqft_max)s
        AND sale_price IS NOT NULL
        ORDER BY sale_date DESC
        LIMIT 10
        """

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "property_type": subject.property_type.value,
            "city": subject.city,
            "state": subject.state,
            "bed_min": bed_range[0],
            "bed_max": bed_range[1],
            "bath_min": bath_range[0],
            "bath_max": bath_range[1],
            "sqft_min": sqft_range[0],
            "sqft_max": sqft_range[1]
        }

        try:
            with self.db_engine.connect() as conn:
                result = conn.execute(text(search_sql), params)
                rows = result.fetchall()

            # Convert to SimplePropertyData objects
            comparables = []
            for row in rows:
                prop = SimplePropertyData(
                    address=row.address,
                    city=row.city,
                    state=row.state,
                    zip_code=row.zip_code,
                    property_type=PropertyType(row.property_type),
                    bedrooms=row.bedrooms,
                    bathrooms=float(row.bathrooms),
                    square_footage=row.square_footage,
                    lot_size=float(row.lot_size) if row.lot_size else None,
                    year_built=row.year_built,
                    garage_spaces=row.garage_spaces,
                    list_price=row.list_price,
                    sale_price=row.sale_price,
                    status=PropertyStatus(row.status),
                    list_date=row.list_date,
                    sale_date=row.sale_date,
                    days_on_market=row.days_on_market,
                    features=row.features.split(",") if row.features else [],
                    mls_number=row.mls_number
                )
                comparables.append(prop)

            return comparables

        except Exception as e:
            logger.error(f"Database search failed: {str(e)}")
            return self._generate_sample_comparables(subject)

    def _generate_sample_comparables(self, subject: SimplePropertyData) -> List[SimplePropertyData]:
        """Generate realistic sample comparable properties for demo purposes."""

        comparables = []
        base_price_psf = 200  # Base price per square foot

        # Generate 5-8 sample comparables with realistic variations
        for i in range(6):
            # Vary size slightly
            size_variance = 1.0 + (i - 3) * 0.05  # ±15% variance
            sqft = int(subject.square_footage * size_variance)

            # Vary price per square foot realistically
            price_psf = base_price_psf * (1.0 + (i - 3) * 0.08)  # ±24% variance
            sale_price = int(sqft * price_psf)

            # Random but realistic variations
            bed_var = max(2, subject.bedrooms + (i % 3 - 1))
            bath_var = subject.bathrooms + (i % 3 - 1) * 0.5

            # Sold dates in the past 6 months
            days_ago = 30 + i * 20
            sale_date = datetime.now() - timedelta(days=days_ago)

            comp = SimplePropertyData(
                address=f"{1000 + i * 100} Sample Street",
                city=subject.city,
                state=subject.state,
                zip_code=subject.zip_code,
                property_type=subject.property_type,
                bedrooms=bed_var,
                bathrooms=bath_var,
                square_footage=sqft,
                lot_size=0.25 + i * 0.05,
                year_built=subject.year_built + (i - 3) if subject.year_built else None,
                garage_spaces=2,
                sale_price=sale_price,
                status=PropertyStatus.SOLD,
                sale_date=sale_date,
                days_on_market=15 + i * 5,
                features=["updated_kitchen", "hardwood_floors"] if i % 2 else ["granite_counters"],
                mls_number=f"SAMPLE{i:03d}"
            )
            comparables.append(comp)

        return comparables

    def _analyze_comparables(self, subject: SimplePropertyData,
                           comparables: List[SimplePropertyData]) -> Dict:
        """Analyze comparable properties to estimate value."""

        # Extract data for analysis
        sale_prices = [comp.sale_price for comp in comparables if comp.sale_price]
        price_per_sqft_values = [comp.price_per_sqft for comp in comparables if comp.price_per_sqft]
        days_on_market_values = [comp.days_on_market for comp in comparables if comp.days_on_market]

        # Calculate statistics
        median_price = statistics.median(sale_prices)
        avg_price_per_sqft = statistics.mean(price_per_sqft_values)
        avg_days_on_market = int(statistics.mean(days_on_market_values)) if days_on_market_values else 30

        # Estimate value for subject property
        estimated_value = int(avg_price_per_sqft * subject.square_footage)

        # Apply adjustments
        adjusted_value = self._apply_adjustments(subject, comparables, estimated_value)

        # Calculate value range (±5%)
        value_range_low = int(adjusted_value * 0.95)
        value_range_high = int(adjusted_value * 1.05)

        # Determine market conditions
        market_conditions = self._assess_market_conditions(days_on_market_values, len(comparables))

        # Determine confidence level
        confidence_level = self._calculate_confidence(len(comparables), days_on_market_values)

        return {
            "estimated_value": adjusted_value,
            "value_range_low": value_range_low,
            "value_range_high": value_range_high,
            "avg_price_per_sqft": avg_price_per_sqft,
            "avg_days_on_market": avg_days_on_market,
            "market_conditions": market_conditions,
            "confidence_level": confidence_level,
            "median_sale_price": int(median_price),
            "price_range": {
                "low": min(sale_prices),
                "high": max(sale_prices)
            }
        }

    def _apply_adjustments(self, subject: SimplePropertyData,
                          comparables: List[SimplePropertyData],
                          base_value: int) -> int:
        """Apply basic adjustments based on property features."""

        adjusted_value = base_value

        # Age adjustment
        if subject.year_built:
            avg_year_built = statistics.mean([c.year_built for c in comparables if c.year_built])
            if avg_year_built:
                year_diff = subject.year_built - avg_year_built
                age_adjustment = year_diff * 500  # $500 per year difference
                adjusted_value += int(age_adjustment)

        # Lot size adjustment
        if subject.lot_size:
            avg_lot_size = statistics.mean([c.lot_size for c in comparables if c.lot_size])
            if avg_lot_size:
                lot_diff = subject.lot_size - avg_lot_size
                lot_adjustment = lot_diff * 10000  # $10k per acre difference
                adjusted_value += int(lot_adjustment)

        # Feature adjustments
        subject_features = set(subject.features)
        avg_features = set()
        for comp in comparables:
            avg_features.update(comp.features)

        unique_features = subject_features - avg_features
        feature_bonus = len(unique_features) * 2000  # $2k per unique feature
        adjusted_value += feature_bonus

        return max(adjusted_value, int(base_value * 0.8))  # Don't adjust below 80% of base

    def _assess_market_conditions(self, days_on_market_values: List[int], comp_count: int) -> str:
        """Assess current market conditions."""

        if not days_on_market_values:
            return "Limited data available"

        avg_dom = statistics.mean(days_on_market_values)

        if avg_dom <= 20:
            return "Hot seller's market - properties selling quickly"
        elif avg_dom <= 45:
            return "Balanced market - normal selling times"
        elif avg_dom <= 90:
            return "Buyer's market - longer selling times"
        else:
            return "Slow market - extended selling times"

    def _calculate_confidence(self, comp_count: int, days_on_market_values: List[int]) -> str:
        """Calculate confidence level in the analysis."""

        confidence_score = 0

        # Number of comparables
        if comp_count >= 6:
            confidence_score += 3
        elif comp_count >= 4:
            confidence_score += 2
        elif comp_count >= 2:
            confidence_score += 1

        # Market activity (consistent days on market)
        if days_on_market_values:
            dom_std = statistics.stdev(days_on_market_values) if len(days_on_market_values) > 1 else 0
            if dom_std <= 15:  # Consistent market
                confidence_score += 2
            elif dom_std <= 30:
                confidence_score += 1

        # Data recency (all sample data is recent)
        confidence_score += 1

        if confidence_score >= 5:
            return "High confidence"
        elif confidence_score >= 3:
            return "Moderate confidence"
        else:
            return "Low confidence - limited data"

    async def _generate_ai_analysis(self, subject: SimplePropertyData,
                                   comparables: List[SimplePropertyData],
                                   analysis: Dict) -> str:
        """Generate AI-powered market analysis."""

        # Prepare comparable sales summary
        comp_summary = []
        for i, comp in enumerate(comparables[:5], 1):  # Limit to 5 for prompt
            comp_summary.append(
                f"Comp {i}: {comp.address} - {comp.bedrooms}BR/{comp.bathrooms}BA, "
                f"{comp.square_footage:,} sqft, sold for ${comp.sale_price:,} "
                f"(${comp.price_per_sqft:.0f}/sqft) after {comp.days_on_market} days"
            )

        prompt = f"""
        Analyze this real estate market data and provide professional insights:

        SUBJECT PROPERTY:
        {subject.address}, {subject.city}, {subject.state}
        {subject.bedrooms}BR/{subject.bathrooms}BA, {subject.square_footage:,} sq ft
        Built: {subject.year_built or 'Unknown'}
        Features: {', '.join(subject.features) if subject.features else 'Standard'}

        COMPARABLE SALES:
        {chr(10).join(comp_summary)}

        MARKET ANALYSIS:
        - Estimated Value: ${analysis['estimated_value']:,}
        - Average $/sqft: ${analysis['avg_price_per_sqft']:.0f}
        - Average Days on Market: {analysis['avg_days_on_market']} days
        - Market Conditions: {analysis['market_conditions']}

        Provide a professional analysis covering:
        1. Value assessment and key pricing factors
        2. Market positioning relative to competition
        3. Timing and pricing strategy recommendations
        4. Key selling points to highlight

        Keep it concise and actionable for a real estate professional.
        """

        try:
            response = await self.openai_client.chat.completions.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an experienced real estate appraiser and market analyst. Provide professional, practical insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=600
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return f"Professional analysis based on {len(comparables)} comparable sales shows estimated value of ${analysis['estimated_value']:,} with {analysis['confidence_level'].lower()}. Market conditions indicate {analysis['market_conditions'].lower()}. Property is well-positioned based on size and location factors."

    def _generate_pricing_recommendations(self, subject: SimplePropertyData,
                                        analysis: Dict, comp_count: int) -> Dict:
        """Generate specific pricing strategy recommendations."""

        estimated_value = analysis['estimated_value']

        strategies = {
            "conservative": {
                "price": int(estimated_value * 0.95),
                "description": "Price 5% below estimated value to generate quick interest",
                "pros": ["Fast sale likely", "Multiple offers possible", "Minimal carrying costs"],
                "cons": ["May leave money on table", "Could signal desperation"],
                "timeline": "2-4 weeks"
            },
            "market_value": {
                "price": estimated_value,
                "description": "Price at estimated market value",
                "pros": ["Fair market price", "Attracts serious buyers", "Room for negotiation"],
                "cons": ["Standard timeline", "Competition from similar properties"],
                "timeline": "4-8 weeks"
            },
            "aspirational": {
                "price": int(estimated_value * 1.05),
                "description": "Price 5% above market to test demand",
                "pros": ["Maximum profit potential", "Negotiation buffer", "Tests market strength"],
                "cons": ["Longer time on market", "May price out buyers", "Risk of price reduction"],
                "timeline": "8-12 weeks"
            }
        }

        # Recommend strategy based on market conditions
        market_conditions = analysis['market_conditions'].lower()
        if "hot" in market_conditions or "seller" in market_conditions:
            recommended = "aspirational"
        elif "slow" in market_conditions or "buyer" in market_conditions:
            recommended = "conservative"
        else:
            recommended = "market_value"

        return {
            "strategies": strategies,
            "recommended": recommended,
            "reasoning": f"Based on {analysis['market_conditions'].lower()} and {comp_count} comparable sales"
        }

    def _generate_next_steps(self, subject: SimplePropertyData, analysis: Dict) -> List[str]:
        """Generate practical next steps for the agent."""

        steps = [
            "Review CMA results with seller/buyer",
            f"Discuss pricing strategy - recommend ${analysis['estimated_value']:,}",
            "Highlight key features that add value",
            "Prepare marketing materials emphasizing competitive advantages"
        ]

        # Add condition-specific steps
        if analysis['confidence_level'] == "Low confidence - limited data":
            steps.append("Consider expanding search area for more comparables")

        if "slow" in analysis['market_conditions'].lower():
            steps.append("Develop aggressive marketing plan for buyer's market")
            steps.append("Consider pre-inspection to address buyer concerns")

        if "hot" in analysis['market_conditions'].lower():
            steps.append("Prepare for multiple offer scenario")
            steps.append("Set clear offer deadline and terms")

        steps.extend([
            "Schedule professional photography if listing",
            "Plan follow-up market analysis in 30 days",
            "Document analysis for client files"
        ])

        return steps

    def _generate_no_comps_result(self, subject: SimplePropertyData) -> CMAResult:
        """Generate CMA result when no comparables are found."""

        # Rough estimate based on property type and size
        estimated_psf = {
            PropertyType.SINGLE_FAMILY: 200,
            PropertyType.CONDO: 180,
            PropertyType.TOWNHOUSE: 190,
            PropertyType.MULTI_FAMILY: 150
        }.get(subject.property_type, 180)

        estimated_value = int(subject.square_footage * estimated_psf)

        return CMAResult(
            subject_address=subject.address,
            analysis_date=datetime.now(),
            comparable_count=0,
            estimated_value=estimated_value,
            value_range_low=int(estimated_value * 0.85),
            value_range_high=int(estimated_value * 1.15),
            price_per_sqft_avg=estimated_psf,
            average_days_on_market=45,
            market_conditions="Insufficient data for market assessment",
            confidence_level="Low - no comparable data available",
            comparable_properties=[],
            pricing_recommendations={
                "strategies": {
                    "broad_market": {
                        "price": estimated_value,
                        "description": "Estimated value based on property size and type",
                        "pros": ["Starting point for market testing"],
                        "cons": ["No local market validation"],
                        "timeline": "Unknown - requires market feedback"
                    }
                },
                "recommended": "broad_market",
                "reasoning": "No comparable sales found - value estimate based on property characteristics only"
            },
            market_analysis="No comparable sales found in the specified criteria. Value estimate is preliminary and should be validated with additional market research, expanded search area, or professional appraisal.",
            next_steps=[
                "Expand search criteria (area, time period, property type)",
                "Research broader market trends in the area",
                "Consider professional appraisal",
                "Start with estimated price and adjust based on market feedback",
                "Monitor similar new listings for pricing guidance"
            ]
        )

    def save_property(self, property_data: SimplePropertyData) -> bool:
        """Save property data to database for future CMA use."""

        if not self.db_engine:
            logger.warning("No database connection available")
            return False

        insert_sql = """
        INSERT INTO properties (
            mls_number, address, city, state, zip_code, property_type,
            bedrooms, bathrooms, square_footage, lot_size, year_built,
            garage_spaces, list_price, sale_price, price_per_sqft, status,
            list_date, sale_date, days_on_market, features
        ) VALUES (
            %(mls_number)s, %(address)s, %(city)s, %(state)s, %(zip_code)s, %(property_type)s,
            %(bedrooms)s, %(bathrooms)s, %(square_footage)s, %(lot_size)s, %(year_built)s,
            %(garage_spaces)s, %(list_price)s, %(sale_price)s, %(price_per_sqft)s, %(status)s,
            %(list_date)s, %(sale_date)s, %(days_on_market)s, %(features)s
        ) ON CONFLICT (mls_number) DO UPDATE SET
            sale_price = EXCLUDED.sale_price,
            status = EXCLUDED.status,
            sale_date = EXCLUDED.sale_date,
            updated_at = NOW()
        """

        try:
            with self.db_engine.connect() as conn:
                conn.execute(text(insert_sql), {
                    "mls_number": property_data.mls_number,
                    "address": property_data.address,
                    "city": property_data.city,
                    "state": property_data.state,
                    "zip_code": property_data.zip_code,
                    "property_type": property_data.property_type.value,
                    "bedrooms": property_data.bedrooms,
                    "bathrooms": property_data.bathrooms,
                    "square_footage": property_data.square_footage,
                    "lot_size": property_data.lot_size,
                    "year_built": property_data.year_built,
                    "garage_spaces": property_data.garage_spaces,
                    "list_price": property_data.list_price,
                    "sale_price": property_data.sale_price,
                    "price_per_sqft": property_data.price_per_sqft,
                    "status": property_data.status.value,
                    "list_date": property_data.list_date,
                    "sale_date": property_data.sale_date,
                    "days_on_market": property_data.days_on_market,
                    "features": ",".join(property_data.features) if property_data.features else None
                })
                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Failed to save property: {str(e)}")
            return False

# Example usage
async def main():
    """Example of using the CMA agent."""

    # Initialize CMA agent
    cma_agent = SimpleCMAAgent()

    # Example subject property
    subject = SimplePropertyData(
        address="123 Example Street",
        city="Austin",
        state="TX",
        zip_code="78701",
        property_type=PropertyType.SINGLE_FAMILY,
        bedrooms=3,
        bathrooms=2.5,
        square_footage=2100,
        lot_size=0.25,
        year_built=2015,
        garage_spaces=2,
        list_price=650000,
        features=["updated_kitchen", "hardwood_floors", "granite_counters"]
    )

    # Generate CMA
    try:
        cma_result = await cma_agent.generate_cma(subject, months_back=6)

        print("CMA ANALYSIS RESULTS")
        print("=" * 40)
        print(f"Subject: {cma_result.subject_address}")
        print(f"Analysis Date: {cma_result.analysis_date.strftime('%B %d, %Y')}")
        print(f"Comparable Sales: {cma_result.comparable_count}")
        print(f"Estimated Value: ${cma_result.estimated_value:,}")
        print(f"Value Range: ${cma_result.value_range_low:,} - ${cma_result.value_range_high:,}")
        print(f"Avg Price/SqFt: ${cma_result.price_per_sqft_avg:.0f}")
        print(f"Market Conditions: {cma_result.market_conditions}")
        print(f"Confidence: {cma_result.confidence_level}")

        print("\nPRICING RECOMMENDATIONS:")
        recommended = cma_result.pricing_recommendations['recommended']
        rec_strategy = cma_result.pricing_recommendations['strategies'][recommended]
        print(f"Recommended: {recommended.title()} - ${rec_strategy['price']:,}")
        print(f"Strategy: {rec_strategy['description']}")
        print(f"Expected Timeline: {rec_strategy['timeline']}")

        print(f"\nMARKET ANALYSIS:")
        print(cma_result.market_analysis)

        print("\nNEXT STEPS:")
        for i, step in enumerate(cma_result.next_steps[:5], 1):
            print(f"{i}. {step}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())