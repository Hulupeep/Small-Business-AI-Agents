"""
MLS Integration Connector
Provides standardized connection to Multiple Listing Services (MLS) using RETS and WebAPI.
"""

import asyncio
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import re

import aiohttp
import requests
from requests.auth import HTTPDigestAuth
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MLSCredentials:
    """MLS connection credentials."""
    login_url: str
    username: str
    password: str
    user_agent: str
    user_agent_password: Optional[str] = None
    rets_version: str = "RETS/1.7.2"
    mls_id: str = ""

@dataclass
class PropertySearchCriteria:
    """Property search criteria for MLS queries."""
    property_type: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_codes: Optional[List[str]] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_bathrooms: Optional[float] = None
    max_bathrooms: Optional[float] = None
    min_sqft: Optional[int] = None
    max_sqft: Optional[int] = None
    min_lot_size: Optional[float] = None
    max_lot_size: Optional[float] = None
    min_year_built: Optional[int] = None
    max_year_built: Optional[int] = None
    status: Optional[str] = None  # Active, Sold, Pending, etc.
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    max_results: int = 100

class MLSConnector:
    """
    Universal MLS connector supporting RETS and modern WebAPI connections.
    Handles authentication, querying, and data standardization across different MLS systems.
    """

    def __init__(self, credentials: MLSCredentials):
        self.credentials = credentials
        self.session = requests.Session()
        self.login_url = None
        self.search_url = None
        self.metadata_url = None
        self.is_authenticated = False
        self.field_mappings = {}
        self.supported_property_types = []

    async def authenticate(self) -> bool:
        """
        Authenticate with the MLS system using RETS protocol.

        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Setup authentication
            auth = HTTPDigestAuth(self.credentials.username, self.credentials.password)

            # Prepare login headers
            headers = {
                'User-Agent': self.credentials.user_agent,
                'RETS-Version': self.credentials.rets_version,
                'Accept': '*/*'
            }

            # Add User-Agent password if required
            if self.credentials.user_agent_password:
                headers['RETS-UA-Authorization'] = f'Digest {self._calculate_ua_digest()}'

            # Perform login
            response = self.session.get(
                self.credentials.login_url,
                auth=auth,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                # Parse login response to get URLs
                self._parse_login_response(response.text)
                self.is_authenticated = True

                # Get metadata and field mappings
                await self._load_metadata()

                logger.info(f"Successfully authenticated with MLS: {self.credentials.mls_id}")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    def _parse_login_response(self, response_text: str):
        """Parse RETS login response to extract service URLs."""
        try:
            # Parse XML response
            root = ET.fromstring(response_text)

            # Extract URLs from RETS-RESPONSE
            rets_response = root.find('.//RETS-RESPONSE')
            if rets_response is not None:
                for child in rets_response:
                    if child.tag == 'Search':
                        self.search_url = child.text
                    elif child.tag == 'GetMetadata':
                        self.metadata_url = child.text
                    elif child.tag == 'Login':
                        self.login_url = child.text

        except ET.ParseError:
            # Handle non-XML response (some MLS systems return plain text)
            lines = response_text.split('\n')
            for line in lines:
                if 'Search=' in line:
                    self.search_url = line.split('=')[1].strip()
                elif 'GetMetadata=' in line:
                    self.metadata_url = line.split('=')[1].strip()

    async def _load_metadata(self):
        """Load MLS metadata to understand field mappings and available resources."""
        if not self.metadata_url:
            logger.warning("No metadata URL available, using default field mappings")
            self._set_default_field_mappings()
            return

        try:
            # Get resource metadata
            metadata_params = {
                'Type': 'METADATA-RESOURCE',
                'ID': '0'
            }

            response = self.session.get(
                self.metadata_url,
                params=metadata_params,
                timeout=30
            )

            if response.status_code == 200:
                self._parse_metadata(response.text)
            else:
                logger.warning("Failed to load metadata, using defaults")
                self._set_default_field_mappings()

        except Exception as e:
            logger.error(f"Error loading metadata: {str(e)}")
            self._set_default_field_mappings()

    def _parse_metadata(self, metadata_xml: str):
        """Parse MLS metadata to extract field mappings."""
        try:
            root = ET.fromstring(metadata_xml)

            # Extract field mappings from metadata
            # This is simplified - real implementation would parse full metadata structure
            self.field_mappings = {
                'list_price': 'ListPrice',
                'sale_price': 'SalePrice',
                'address': 'StreetNumber,StreetName',
                'city': 'City',
                'state': 'StateOrProvince',
                'zip_code': 'PostalCode',
                'bedrooms': 'BedroomsTotal',
                'bathrooms': 'BathroomsTotal',
                'square_footage': 'LivingArea',
                'lot_size': 'LotSizeAcres',
                'year_built': 'YearBuilt',
                'property_type': 'PropertyType',
                'status': 'StandardStatus',
                'list_date': 'ListingContractDate',
                'sale_date': 'CloseDate',
                'days_on_market': 'DaysOnMarket',
                'mls_number': 'ListingId',
                'latitude': 'Latitude',
                'longitude': 'Longitude'
            }

        except Exception as e:
            logger.error(f"Error parsing metadata: {str(e)}")
            self._set_default_field_mappings()

    def _set_default_field_mappings(self):
        """Set default field mappings for common MLS systems."""
        self.field_mappings = {
            'list_price': 'LP',
            'sale_price': 'SP',
            'address': 'AD',
            'city': 'CIT',
            'state': 'ST',
            'zip_code': 'ZIP',
            'bedrooms': 'BR',
            'bathrooms': 'BTH',
            'square_footage': 'ASF',
            'lot_size': 'LSF',
            'year_built': 'YR',
            'property_type': 'PT',
            'status': 'ST',
            'list_date': 'LD',
            'sale_date': 'SD',
            'days_on_market': 'DOM',
            'mls_number': 'MLS',
            'latitude': 'LAT',
            'longitude': 'LON'
        }

    async def search_properties(self, criteria: PropertySearchCriteria) -> List[Dict]:
        """
        Search for properties based on criteria.

        Args:
            criteria: PropertySearchCriteria object with search parameters

        Returns:
            List of property dictionaries
        """
        if not self.is_authenticated:
            if not await self.authenticate():
                raise Exception("Failed to authenticate with MLS")

        try:
            # Build DMQL query
            dmql_query = self._build_dmql_query(criteria)

            # Prepare search parameters
            search_params = {
                'SearchType': 'Property',
                'Class': 'Residential',
                'Query': dmql_query,
                'Format': 'COMPACT-DECODED',
                'Count': '1',
                'StandardNames': '0',
                'Limit': str(criteria.max_results)
            }

            # Execute search
            response = self.session.get(
                self.search_url,
                params=search_params,
                timeout=60
            )

            if response.status_code == 200:
                return self._parse_search_results(response.text)
            else:
                logger.error(f"Search failed: {response.status_code} - {response.text}")
                return []

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []

    def _build_dmql_query(self, criteria: PropertySearchCriteria) -> str:
        """
        Build DMQL (Data Model Query Language) query from search criteria.

        Args:
            criteria: PropertySearchCriteria object

        Returns:
            DMQL query string
        """
        conditions = []

        # Property type
        if criteria.property_type:
            pt_field = self.field_mappings.get('property_type', 'PT')
            conditions.append(f"({pt_field}={criteria.property_type})")

        # Location filters
        if criteria.city:
            city_field = self.field_mappings.get('city', 'CIT')
            conditions.append(f"({city_field}={criteria.city})")

        if criteria.state:
            state_field = self.field_mappings.get('state', 'ST')
            conditions.append(f"({state_field}={criteria.state})")

        if criteria.zip_codes:
            zip_field = self.field_mappings.get('zip_code', 'ZIP')
            zip_conditions = '|'.join(criteria.zip_codes)
            conditions.append(f"({zip_field}={zip_conditions})")

        # Price range
        if criteria.min_price or criteria.max_price:
            price_field = self.field_mappings.get('list_price', 'LP')
            if criteria.min_price and criteria.max_price:
                conditions.append(f"({price_field}={criteria.min_price}-{criteria.max_price})")
            elif criteria.min_price:
                conditions.append(f"({price_field}={criteria.min_price}+)")
            elif criteria.max_price:
                conditions.append(f"({price_field}=0-{criteria.max_price})")

        # Bedroom range
        if criteria.min_bedrooms or criteria.max_bedrooms:
            br_field = self.field_mappings.get('bedrooms', 'BR')
            if criteria.min_bedrooms and criteria.max_bedrooms:
                conditions.append(f"({br_field}={criteria.min_bedrooms}-{criteria.max_bedrooms})")
            elif criteria.min_bedrooms:
                conditions.append(f"({br_field}={criteria.min_bedrooms}+)")

        # Bathroom range
        if criteria.min_bathrooms or criteria.max_bathrooms:
            bath_field = self.field_mappings.get('bathrooms', 'BTH')
            if criteria.min_bathrooms and criteria.max_bathrooms:
                conditions.append(f"({bath_field}={criteria.min_bathrooms}-{criteria.max_bathrooms})")
            elif criteria.min_bathrooms:
                conditions.append(f"({bath_field}={criteria.min_bathrooms}+)")

        # Square footage range
        if criteria.min_sqft or criteria.max_sqft:
            sqft_field = self.field_mappings.get('square_footage', 'ASF')
            if criteria.min_sqft and criteria.max_sqft:
                conditions.append(f"({sqft_field}={criteria.min_sqft}-{criteria.max_sqft})")
            elif criteria.min_sqft:
                conditions.append(f"({sqft_field}={criteria.min_sqft}+)")

        # Status filter
        if criteria.status:
            status_field = self.field_mappings.get('status', 'ST')
            conditions.append(f"({status_field}={criteria.status})")

        # Date range
        if criteria.date_from or criteria.date_to:
            date_field = self.field_mappings.get('list_date', 'LD')
            if criteria.date_from and criteria.date_to:
                date_from_str = criteria.date_from.strftime('%Y-%m-%d')
                date_to_str = criteria.date_to.strftime('%Y-%m-%d')
                conditions.append(f"({date_field}={date_from_str}-{date_to_str})")

        # Combine all conditions with AND
        if conditions:
            return ','.join(conditions)
        else:
            return '(LP=1+)'  # Default query to get all active listings

    def _parse_search_results(self, response_text: str) -> List[Dict]:
        """
        Parse RETS search results into standardized property dictionaries.

        Args:
            response_text: Raw RETS response text

        Returns:
            List of property dictionaries
        """
        properties = []

        try:
            # Parse the RETS response
            lines = response_text.strip().split('\n')
            if len(lines) < 2:
                return properties

            # First line contains column headers
            headers = lines[0].split('\t')

            # Parse each property record
            for line in lines[1:]:
                if line.strip():
                    values = line.split('\t')
                    if len(values) == len(headers):
                        property_data = dict(zip(headers, values))
                        standardized_property = self._standardize_property_data(property_data)
                        properties.append(standardized_property)

        except Exception as e:
            logger.error(f"Error parsing search results: {str(e)}")

        return properties

    def _standardize_property_data(self, raw_data: Dict) -> Dict:
        """
        Convert raw MLS data to standardized property format.

        Args:
            raw_data: Raw property data from MLS

        Returns:
            Standardized property dictionary
        """
        standardized = {}

        # Map fields using field mappings
        field_map = {
            'mls_number': self._get_field_value(raw_data, 'mls_number'),
            'address': self._build_address(raw_data),
            'city': self._get_field_value(raw_data, 'city'),
            'state': self._get_field_value(raw_data, 'state'),
            'zip_code': self._get_field_value(raw_data, 'zip_code'),
            'latitude': self._parse_float(self._get_field_value(raw_data, 'latitude')),
            'longitude': self._parse_float(self._get_field_value(raw_data, 'longitude')),
            'property_type': self._get_field_value(raw_data, 'property_type'),
            'bedrooms': self._parse_int(self._get_field_value(raw_data, 'bedrooms')),
            'bathrooms': self._parse_float(self._get_field_value(raw_data, 'bathrooms')),
            'square_footage': self._parse_int(self._get_field_value(raw_data, 'square_footage')),
            'lot_size': self._parse_float(self._get_field_value(raw_data, 'lot_size')),
            'year_built': self._parse_int(self._get_field_value(raw_data, 'year_built')),
            'list_price': self._parse_int(self._get_field_value(raw_data, 'list_price')),
            'sale_price': self._parse_int(self._get_field_value(raw_data, 'sale_price')),
            'status': self._get_field_value(raw_data, 'status'),
            'list_date': self._parse_date(self._get_field_value(raw_data, 'list_date')),
            'sale_date': self._parse_date(self._get_field_value(raw_data, 'sale_date')),
            'days_on_market': self._parse_int(self._get_field_value(raw_data, 'days_on_market'))
        }

        # Remove None values
        standardized = {k: v for k, v in field_map.items() if v is not None}

        # Calculate price per square foot
        if standardized.get('list_price') and standardized.get('square_footage'):
            standardized['price_per_sqft'] = standardized['list_price'] / standardized['square_footage']
        elif standardized.get('sale_price') and standardized.get('square_footage'):
            standardized['price_per_sqft'] = standardized['sale_price'] / standardized['square_footage']

        return standardized

    def _get_field_value(self, data: Dict, field_name: str) -> Optional[str]:
        """Get field value using field mappings."""
        mls_field = self.field_mappings.get(field_name)
        if mls_field and mls_field in data:
            return data[mls_field]
        return None

    def _build_address(self, data: Dict) -> Optional[str]:
        """Build full address from MLS components."""
        address_components = []

        # Try to get street number and name
        for field in ['StreetNumber', 'StreetName', 'AD', 'ADDRESS']:
            if field in data and data[field]:
                address_components.append(data[field])
                break

        if address_components:
            return ' '.join(address_components)
        return None

    def _parse_int(self, value: Optional[str]) -> Optional[int]:
        """Safely parse integer value."""
        if value and str(value).strip():
            try:
                return int(float(str(value).strip().replace(',', '')))
            except (ValueError, TypeError):
                return None
        return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        """Safely parse float value."""
        if value and str(value).strip():
            try:
                return float(str(value).strip().replace(',', ''))
            except (ValueError, TypeError):
                return None
        return None

    def _parse_date(self, value: Optional[str]) -> Optional[datetime]:
        """Safely parse date value."""
        if not value or not str(value).strip():
            return None

        date_str = str(value).strip()

        # Try different date formats
        date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S'
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _calculate_ua_digest(self) -> str:
        """Calculate User-Agent digest for authentication."""
        # Simplified digest calculation - real implementation would follow RETS spec
        import hashlib
        digest_string = f"{self.credentials.user_agent}:{self.credentials.user_agent_password}"
        return hashlib.md5(digest_string.encode()).hexdigest()

    async def get_property_photos(self, mls_number: str) -> List[str]:
        """
        Get photo URLs for a specific property.

        Args:
            mls_number: MLS listing number

        Returns:
            List of photo URLs
        """
        # This would implement RETS GetObject operation for photos
        # Simplified implementation
        try:
            if not self.is_authenticated:
                await self.authenticate()

            # Get photos using RETS GetObject
            photo_params = {
                'Type': 'Photo',
                'Resource': 'Property',
                'ID': f"{mls_number}:*"
            }

            # This would be the actual GetObject URL from login response
            get_object_url = self.search_url.replace('Search', 'GetObject')

            response = self.session.get(
                get_object_url,
                params=photo_params,
                timeout=30
            )

            if response.status_code == 200:
                # Parse multipart response to extract photo URLs
                # Simplified - real implementation would parse multipart MIME
                return []
            else:
                return []

        except Exception as e:
            logger.error(f"Error getting property photos: {str(e)}")
            return []

    async def get_market_statistics(self, area: str, property_type: str = None) -> Dict:
        """
        Get market statistics for a specific area.

        Args:
            area: Geographic area (city, zip code, etc.)
            property_type: Optional property type filter

        Returns:
            Dictionary with market statistics
        """
        try:
            # Search for recent sales in the area
            criteria = PropertySearchCriteria(
                city=area,
                status='Sold',
                date_from=datetime.now() - timedelta(days=90),
                max_results=500
            )

            if property_type:
                criteria.property_type = property_type

            recent_sales = await self.search_properties(criteria)

            if not recent_sales:
                return {}

            # Calculate statistics
            prices = [prop['sale_price'] for prop in recent_sales if prop.get('sale_price')]
            psf_values = [prop['price_per_sqft'] for prop in recent_sales if prop.get('price_per_sqft')]
            dom_values = [prop['days_on_market'] for prop in recent_sales if prop.get('days_on_market')]

            stats = {
                'total_sales': len(recent_sales),
                'median_price': int(pd.Series(prices).median()) if prices else 0,
                'average_price': int(pd.Series(prices).mean()) if prices else 0,
                'median_price_per_sqft': pd.Series(psf_values).median() if psf_values else 0,
                'average_days_on_market': int(pd.Series(dom_values).mean()) if dom_values else 0,
                'analysis_period': '90 days',
                'area': area
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting market statistics: {str(e)}")
            return {}

    async def logout(self):
        """Logout from MLS session."""
        try:
            if self.is_authenticated and self.login_url:
                logout_url = self.login_url.replace('Login', 'Logout')
                self.session.get(logout_url, timeout=10)

            self.session.close()
            self.is_authenticated = False
            logger.info("Logged out from MLS")

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")

# Example usage and testing
async def main():
    """Example usage of the MLS connector."""

    # Setup MLS credentials (example for a generic MLS)
    credentials = MLSCredentials(
        login_url="https://rets.example-mls.com/login.asmx/Login",
        username="your_username",
        password="your_password",
        user_agent="YourCompany/1.0",
        user_agent_password="your_ua_password",
        mls_id="EXAMPLEMLS"
    )

    # Initialize connector
    mls = MLSConnector(credentials)

    try:
        # Authenticate
        if await mls.authenticate():
            print("✅ Successfully authenticated with MLS")

            # Search for properties
            search_criteria = PropertySearchCriteria(
                city="Austin",
                state="TX",
                min_price=400000,
                max_price=600000,
                min_bedrooms=3,
                status="Active",
                max_results=10
            )

            properties = await mls.search_properties(search_criteria)
            print(f"📊 Found {len(properties)} properties matching criteria")

            # Display sample property
            if properties:
                sample_prop = properties[0]
                print(f"\nSample Property:")
                print(f"  Address: {sample_prop.get('address')}")
                print(f"  Price: ${sample_prop.get('list_price', 0):,}")
                print(f"  Size: {sample_prop.get('bedrooms')}BR/{sample_prop.get('bathrooms')}BA")
                print(f"  Sq Ft: {sample_prop.get('square_footage', 0):,}")

            # Get market statistics
            market_stats = await mls.get_market_statistics("Austin", "Residential")
            if market_stats:
                print(f"\n📈 Market Statistics for Austin:")
                print(f"  Total Sales (90 days): {market_stats.get('total_sales', 0)}")
                print(f"  Median Price: ${market_stats.get('median_price', 0):,}")
                print(f"  Average Days on Market: {market_stats.get('average_days_on_market', 0)}")

        else:
            print("❌ Failed to authenticate with MLS")

    finally:
        # Always logout
        await mls.logout()

if __name__ == "__main__":
    asyncio.run(main())