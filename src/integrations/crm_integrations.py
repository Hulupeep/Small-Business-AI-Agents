"""
CRM Integration utilities for lead management
"""

import asyncio
import json
import requests
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CRMIntegration(ABC):
    """Abstract base class for CRM integrations"""

    @abstractmethod
    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create a new lead in the CRM"""
        pass

    @abstractmethod
    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update existing lead in the CRM"""
        pass

    @abstractmethod
    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead data from the CRM"""
        pass


class SupabaseCRM(CRMIntegration):
    """Supabase integration for lead management"""

    def __init__(self, url: str, key: str, table_name: str = "leads"):
        self.url = url.rstrip('/')
        self.key = key
        self.table_name = table_name
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create lead in Supabase"""
        try:
            # Prepare data for Supabase
            supabase_data = {
                "email": lead_data["email"],
                "first_name": lead_data["first_name"],
                "last_name": lead_data["last_name"],
                "company": lead_data["company"],
                "job_title": lead_data["job_title"],
                "phone": lead_data.get("phone"),
                "website": lead_data.get("website"),
                "company_size": lead_data.get("company_size"),
                "industry": lead_data.get("industry"),
                "source": lead_data.get("source", "unknown"),
                "status": lead_data.get("status", "new"),
                "bant_score": lead_data.get("bant_score"),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            url = f"{self.url}/rest/v1/{self.table_name}"

            response = requests.post(url, headers=self.headers, json=supabase_data)
            response.raise_for_status()

            result = response.json()
            lead_id = result[0]["id"] if result else None

            logger.info(f"Created lead in Supabase: {lead_id}")
            return str(lead_id)

        except Exception as e:
            logger.error(f"Failed to create lead in Supabase: {e}")
            raise

    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update lead in Supabase"""
        try:
            updates["updated_at"] = datetime.now().isoformat()

            url = f"{self.url}/rest/v1/{self.table_name}?id=eq.{lead_id}"

            response = requests.patch(url, headers=self.headers, json=updates)
            response.raise_for_status()

            logger.info(f"Updated lead in Supabase: {lead_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update lead in Supabase: {e}")
            return False

    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead from Supabase"""
        try:
            url = f"{self.url}/rest/v1/{self.table_name}?id=eq.{lead_id}"

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            result = response.json()
            return result[0] if result else None

        except Exception as e:
            logger.error(f"Failed to get lead from Supabase: {e}")
            return None


class AirtableCRM(CRMIntegration):
    """Airtable integration for lead management"""

    def __init__(self, api_key: str, base_id: str, table_name: str = "Leads"):
        self.api_key = api_key
        self.base_id = base_id
        self.table_name = table_name
        self.base_url = f"https://api.airtable.com/v0/{base_id}/{table_name}"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create lead in Airtable"""
        try:
            # Prepare data for Airtable
            airtable_data = {
                "records": [{
                    "fields": {
                        "Email": lead_data["email"],
                        "First Name": lead_data["first_name"],
                        "Last Name": lead_data["last_name"],
                        "Company": lead_data["company"],
                        "Job Title": lead_data["job_title"],
                        "Phone": lead_data.get("phone", ""),
                        "Website": lead_data.get("website", ""),
                        "Company Size": lead_data.get("company_size", ""),
                        "Industry": lead_data.get("industry", ""),
                        "Source": lead_data.get("source", "unknown"),
                        "Status": lead_data.get("status", "new"),
                        "BANT Score": lead_data.get("bant_score", 0),
                        "Created": datetime.now().isoformat()
                    }
                }]
            }

            response = requests.post(self.base_url, headers=self.headers, json=airtable_data)
            response.raise_for_status()

            result = response.json()
            record_id = result["records"][0]["id"]

            logger.info(f"Created lead in Airtable: {record_id}")
            return record_id

        except Exception as e:
            logger.error(f"Failed to create lead in Airtable: {e}")
            raise

    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update lead in Airtable"""
        try:
            # Convert field names for Airtable
            airtable_updates = {}
            field_mapping = {
                "status": "Status",
                "bant_score": "BANT Score",
                "phone": "Phone",
                "website": "Website"
            }

            for key, value in updates.items():
                airtable_key = field_mapping.get(key, key.title())
                airtable_updates[airtable_key] = value

            airtable_updates["Updated"] = datetime.now().isoformat()

            data = {
                "records": [{
                    "id": lead_id,
                    "fields": airtable_updates
                }]
            }

            response = requests.patch(self.base_url, headers=self.headers, json=data)
            response.raise_for_status()

            logger.info(f"Updated lead in Airtable: {lead_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update lead in Airtable: {e}")
            return False

    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get lead from Airtable"""
        try:
            url = f"{self.base_url}/{lead_id}"

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            result = response.json()
            return result.get("fields")

        except Exception as e:
            logger.error(f"Failed to get lead from Airtable: {e}")
            return None


class HubSpotCRM(CRMIntegration):
    """HubSpot integration for lead management"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.hubapi.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def create_lead(self, lead_data: Dict[str, Any]) -> str:
        """Create contact in HubSpot"""
        try:
            # Prepare data for HubSpot
            hubspot_data = {
                "properties": {
                    "email": lead_data["email"],
                    "firstname": lead_data["first_name"],
                    "lastname": lead_data["last_name"],
                    "company": lead_data["company"],
                    "jobtitle": lead_data["job_title"],
                    "phone": lead_data.get("phone", ""),
                    "website": lead_data.get("website", ""),
                    "company_size": lead_data.get("company_size", ""),
                    "industry": lead_data.get("industry", ""),
                    "hs_lead_status": lead_data.get("status", "NEW"),
                    "bant_score": str(lead_data.get("bant_score", 0))
                }
            }

            url = f"{self.base_url}/crm/v3/objects/contacts"

            response = requests.post(url, headers=self.headers, json=hubspot_data)
            response.raise_for_status()

            result = response.json()
            contact_id = result["id"]

            logger.info(f"Created contact in HubSpot: {contact_id}")
            return contact_id

        except Exception as e:
            logger.error(f"Failed to create contact in HubSpot: {e}")
            raise

    async def update_lead(self, lead_id: str, updates: Dict[str, Any]) -> bool:
        """Update contact in HubSpot"""
        try:
            # Convert field names for HubSpot
            hubspot_updates = {}
            field_mapping = {
                "status": "hs_lead_status",
                "bant_score": "bant_score",
                "phone": "phone",
                "website": "website"
            }

            for key, value in updates.items():
                hubspot_key = field_mapping.get(key, key)
                hubspot_updates[hubspot_key] = str(value)

            data = {"properties": hubspot_updates}

            url = f"{self.base_url}/crm/v3/objects/contacts/{lead_id}"

            response = requests.patch(url, headers=self.headers, json=data)
            response.raise_for_status()

            logger.info(f"Updated contact in HubSpot: {lead_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update contact in HubSpot: {e}")
            return False

    async def get_lead(self, lead_id: str) -> Optional[Dict[str, Any]]:
        """Get contact from HubSpot"""
        try:
            url = f"{self.base_url}/crm/v3/objects/contacts/{lead_id}"

            response = requests.get(url, headers=self.headers)
            response.raise_for_status()

            result = response.json()
            return result.get("properties")

        except Exception as e:
            logger.error(f"Failed to get contact from HubSpot: {e}")
            return None


class CRMManager:
    """Manager class for handling multiple CRM integrations"""

    def __init__(self):
        self.integrations: Dict[str, CRMIntegration] = {}

    def add_integration(self, name: str, integration: CRMIntegration):
        """Add a CRM integration"""
        self.integrations[name] = integration
        logger.info(f"Added CRM integration: {name}")

    async def sync_lead_to_all(self, lead_data: Dict[str, Any]) -> Dict[str, str]:
        """Sync lead to all configured CRM systems"""
        results = {}

        for name, integration in self.integrations.items():
            try:
                lead_id = await integration.create_lead(lead_data)
                results[name] = lead_id
                logger.info(f"Synced lead to {name}: {lead_id}")
            except Exception as e:
                logger.error(f"Failed to sync lead to {name}: {e}")
                results[name] = f"ERROR: {e}"

        return results

    async def update_lead_in_all(self, lead_ids: Dict[str, str], updates: Dict[str, Any]) -> Dict[str, bool]:
        """Update lead in all CRM systems"""
        results = {}

        for name, lead_id in lead_ids.items():
            if name in self.integrations and not lead_id.startswith("ERROR"):
                try:
                    success = await self.integrations[name].update_lead(lead_id, updates)
                    results[name] = success
                except Exception as e:
                    logger.error(f"Failed to update lead in {name}: {e}")
                    results[name] = False

        return results


def setup_crm_integrations(config: Dict[str, Any]) -> CRMManager:
    """Set up CRM integrations based on configuration"""
    manager = CRMManager()

    # Supabase
    if "supabase" in config:
        supabase_config = config["supabase"]
        if all(key in supabase_config for key in ["url", "key"]):
            integration = SupabaseCRM(
                url=supabase_config["url"],
                key=supabase_config["key"],
                table_name=supabase_config.get("table", "leads")
            )
            manager.add_integration("supabase", integration)

    # Airtable
    if "airtable" in config:
        airtable_config = config["airtable"]
        if all(key in airtable_config for key in ["api_key", "base_id"]):
            integration = AirtableCRM(
                api_key=airtable_config["api_key"],
                base_id=airtable_config["base_id"],
                table_name=airtable_config.get("table", "Leads")
            )
            manager.add_integration("airtable", integration)

    # HubSpot
    if "hubspot" in config:
        hubspot_config = config["hubspot"]
        if "api_key" in hubspot_config:
            integration = HubSpotCRM(api_key=hubspot_config["api_key"])
            manager.add_integration("hubspot", integration)

    return manager