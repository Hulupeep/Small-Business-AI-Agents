"""
Accounting Software Integrations - QuickBooks and Xero API Integration

Provides seamless integration with popular accounting software:
- QuickBooks Online API integration
- Xero API integration
- Automated data synchronization
- Real-time financial data updates
- Error handling and retry mechanisms
"""

import os
import json
import logging
import requests
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import time

try:
    from requests_oauthlib import OAuth2Session
    from oauthlib.oauth2 import WebApplicationClient
except ImportError:
    OAuth2Session = None
    WebApplicationClient = None


@dataclass
class AccountingTransaction:
    """Standardized transaction format for accounting software."""
    id: str
    date: datetime
    description: str
    amount: float
    account_id: str
    category: str
    vendor_id: Optional[str] = None
    invoice_number: Optional[str] = None
    tax_amount: Optional[float] = None
    reference: Optional[str] = None
    memo: Optional[str] = None


@dataclass
class Vendor:
    """Vendor/supplier information."""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_id: Optional[str] = None


@dataclass
class Account:
    """Chart of accounts entry."""
    id: str
    name: str
    account_type: str
    account_subtype: Optional[str] = None
    active: bool = True
    balance: Optional[float] = None


class QuickBooksIntegration:
    """QuickBooks Online API integration for automated accounting."""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = self._get_base_url(config.get('sandbox', True))
        self.access_token = config.get('access_token')
        self.refresh_token = config.get('refresh_token')
        self.company_id = config.get('company_id')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')

        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 1.0  # Minimum seconds between requests

    def _get_base_url(self, sandbox: bool = True) -> str:
        """Get QuickBooks API base URL."""
        if sandbox:
            return "https://sandbox-quickbooks.api.intuit.com"
        return "https://quickbooks.api.intuit.com"

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request with rate limiting."""
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)

        url = f"{self.base_url}/v3/company/{self.company_id}/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            self.last_request_time = time.time()

            if response.status_code == 401:
                # Token expired, try to refresh
                if self._refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    # Retry the request
                    if method.upper() == 'GET':
                        response = requests.get(url, headers=headers, params=params)
                    elif method.upper() == 'POST':
                        response = requests.post(url, headers=headers, json=data)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"QuickBooks API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response: {e.response.text}")
            raise

    def _refresh_access_token(self) -> bool:
        """Refresh expired access token."""
        if not self.refresh_token:
            return False

        try:
            token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

            auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

            headers = {
                'Authorization': f'Basic {auth_header}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }

            response = requests.post(token_url, headers=headers, data=data)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data.get('refresh_token', self.refresh_token)

            self.logger.info("Successfully refreshed QuickBooks access token")
            return True

        except Exception as e:
            self.logger.error(f"Failed to refresh token: {e}")
            return False

    def get_company_info(self) -> Dict[str, Any]:
        """Get company information."""
        return self._make_request('GET', 'companyinfo/1')

    def get_accounts(self) -> List[Account]:
        """Retrieve chart of accounts."""
        response = self._make_request('GET', 'accounts')

        accounts = []
        for account_data in response.get('QueryResponse', {}).get('Account', []):
            account = Account(
                id=account_data['Id'],
                name=account_data['Name'],
                account_type=account_data['AccountType'],
                account_subtype=account_data.get('AccountSubType'),
                active=account_data.get('Active', True),
                balance=account_data.get('CurrentBalance')
            )
            accounts.append(account)

        return accounts

    def get_vendors(self) -> List[Vendor]:
        """Retrieve vendor list."""
        response = self._make_request('GET', 'vendors')

        vendors = []
        for vendor_data in response.get('QueryResponse', {}).get('Vendor', []):
            vendor = Vendor(
                id=vendor_data['Id'],
                name=vendor_data['Name'],
                email=vendor_data.get('PrimaryEmailAddr', {}).get('Address'),
                phone=vendor_data.get('PrimaryPhone', {}).get('FreeFormNumber'),
                address=self._format_address(vendor_data.get('BillAddr', {})),
                tax_id=vendor_data.get('TaxIdentifier')
            )
            vendors.append(vendor)

        return vendors

    def create_vendor(self, vendor_data: Dict[str, Any]) -> Vendor:
        """Create a new vendor."""
        qb_vendor_data = {
            "Vendor": {
                "Name": vendor_data['name'],
                "CompanyName": vendor_data.get('company_name', vendor_data['name'])
            }
        }

        if vendor_data.get('email'):
            qb_vendor_data["Vendor"]["PrimaryEmailAddr"] = {
                "Address": vendor_data['email']
            }

        if vendor_data.get('phone'):
            qb_vendor_data["Vendor"]["PrimaryPhone"] = {
                "FreeFormNumber": vendor_data['phone']
            }

        response = self._make_request('POST', 'vendors', qb_vendor_data)

        vendor_resp = response['QueryResponse']['Vendor'][0]
        return Vendor(
            id=vendor_resp['Id'],
            name=vendor_resp['Name'],
            email=vendor_resp.get('PrimaryEmailAddr', {}).get('Address'),
            phone=vendor_resp.get('PrimaryPhone', {}).get('FreeFormNumber')
        )

    def create_bill(self, transaction: AccountingTransaction) -> Dict[str, Any]:
        """Create a bill (expense) in QuickBooks."""
        bill_data = {
            "Bill": {
                "VendorRef": {
                    "value": transaction.vendor_id
                },
                "TxnDate": transaction.date.strftime('%Y-%m-%d'),
                "DueDate": (transaction.date + timedelta(days=30)).strftime('%Y-%m-%d'),
                "Line": [
                    {
                        "Amount": transaction.amount,
                        "DetailType": "AccountBasedExpenseLineDetail",
                        "AccountBasedExpenseLineDetail": {
                            "AccountRef": {
                                "value": transaction.account_id
                            }
                        },
                        "Description": transaction.description
                    }
                ]
            }
        }

        if transaction.reference:
            bill_data["Bill"]["DocNumber"] = transaction.reference

        if transaction.memo:
            bill_data["Bill"]["PrivateNote"] = transaction.memo

        response = self._make_request('POST', 'bills', bill_data)
        return response

    def create_expense(self, transaction: AccountingTransaction) -> Dict[str, Any]:
        """Create an expense transaction in QuickBooks."""
        expense_data = {
            "Purchase": {
                "PaymentType": "Cash",
                "AccountRef": {
                    "value": transaction.account_id
                },
                "TxnDate": transaction.date.strftime('%Y-%m-%d'),
                "Line": [
                    {
                        "Amount": transaction.amount,
                        "DetailType": "AccountBasedExpenseLineDetail",
                        "AccountBasedExpenseLineDetail": {
                            "AccountRef": {
                                "value": transaction.account_id
                            }
                        },
                        "Description": transaction.description
                    }
                ]
            }
        }

        if transaction.vendor_id:
            expense_data["Purchase"]["EntityRef"] = {
                "value": transaction.vendor_id,
                "type": "Vendor"
            }

        response = self._make_request('POST', 'purchases', expense_data)
        return response

    def _format_address(self, address_data: Dict[str, Any]) -> str:
        """Format QuickBooks address data into string."""
        address_parts = []
        for key in ['Line1', 'Line2', 'City', 'CountrySubDivisionCode', 'PostalCode']:
            if address_data.get(key):
                address_parts.append(address_data[key])
        return ', '.join(address_parts)

    def sync_transactions(self, transactions: List[AccountingTransaction]) -> Dict[str, Any]:
        """Sync multiple transactions to QuickBooks."""
        results = {
            'total': len(transactions),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for transaction in transactions:
            try:
                if transaction.vendor_id:
                    self.create_bill(transaction)
                else:
                    self.create_expense(transaction)

                results['successful'] += 1
                self.logger.info(f"Successfully synced transaction: {transaction.id}")

            except Exception as e:
                results['failed'] += 1
                error_msg = f"Failed to sync transaction {transaction.id}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)

        return results


class XeroIntegration:
    """Xero API integration for automated accounting."""

    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.xero.com/api.xro/2.0"
        self.access_token = config.get('access_token')
        self.tenant_id = config.get('tenant_id')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')

        # Rate limiting
        self.last_request_time = 0
        self.request_interval = 1.0

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make authenticated API request to Xero."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)

        url = f"{self.base_url}/{endpoint}"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'xero-tenant-id': self.tenant_id,
            'Content-Type': 'application/json'
        }

        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data)

            self.last_request_time = time.time()
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Xero API request failed: {e}")
            raise

    def get_accounts(self) -> List[Account]:
        """Retrieve chart of accounts from Xero."""
        response = self._make_request('GET', 'Accounts')

        accounts = []
        for account_data in response.get('Accounts', []):
            account = Account(
                id=account_data['AccountID'],
                name=account_data['Name'],
                account_type=account_data['Type'],
                account_subtype=account_data.get('Class'),
                active=account_data.get('Status') == 'ACTIVE'
            )
            accounts.append(account)

        return accounts

    def get_contacts(self) -> List[Vendor]:
        """Retrieve contacts (vendors/suppliers) from Xero."""
        response = self._make_request('GET', 'Contacts')

        vendors = []
        for contact_data in response.get('Contacts', []):
            if contact_data.get('IsSupplier'):
                vendor = Vendor(
                    id=contact_data['ContactID'],
                    name=contact_data['Name'],
                    email=contact_data.get('EmailAddress'),
                    phone=contact_data.get('Phones', [{}])[0].get('PhoneNumber') if contact_data.get('Phones') else None,
                    tax_id=contact_data.get('TaxNumber')
                )
                vendors.append(vendor)

        return vendors

    def create_contact(self, vendor_data: Dict[str, Any]) -> Vendor:
        """Create a new contact in Xero."""
        contact_data = {
            "Contacts": [
                {
                    "Name": vendor_data['name'],
                    "IsSupplier": True
                }
            ]
        }

        if vendor_data.get('email'):
            contact_data["Contacts"][0]["EmailAddress"] = vendor_data['email']

        if vendor_data.get('phone'):
            contact_data["Contacts"][0]["Phones"] = [
                {
                    "PhoneType": "DEFAULT",
                    "PhoneNumber": vendor_data['phone']
                }
            ]

        response = self._make_request('POST', 'Contacts', contact_data)

        contact_resp = response['Contacts'][0]
        return Vendor(
            id=contact_resp['ContactID'],
            name=contact_resp['Name'],
            email=contact_resp.get('EmailAddress'),
            phone=contact_resp.get('Phones', [{}])[0].get('PhoneNumber') if contact_resp.get('Phones') else None
        )

    def create_bill(self, transaction: AccountingTransaction) -> Dict[str, Any]:
        """Create a bill in Xero."""
        bill_data = {
            "Invoices": [
                {
                    "Type": "ACCPAY",  # Accounts Payable
                    "Contact": {
                        "ContactID": transaction.vendor_id
                    },
                    "Date": transaction.date.strftime('%Y-%m-%d'),
                    "DueDate": (transaction.date + timedelta(days=30)).strftime('%Y-%m-%d'),
                    "LineItems": [
                        {
                            "Description": transaction.description,
                            "UnitAmount": transaction.amount,
                            "AccountCode": transaction.account_id
                        }
                    ]
                }
            ]
        }

        if transaction.reference:
            bill_data["Invoices"][0]["InvoiceNumber"] = transaction.reference

        response = self._make_request('POST', 'Invoices', bill_data)
        return response

    def create_bank_transaction(self, transaction: AccountingTransaction) -> Dict[str, Any]:
        """Create a bank transaction in Xero."""
        transaction_data = {
            "BankTransactions": [
                {
                    "Type": "SPEND",
                    "Contact": {
                        "ContactID": transaction.vendor_id
                    } if transaction.vendor_id else None,
                    "Date": transaction.date.strftime('%Y-%m-%d'),
                    "LineItems": [
                        {
                            "Description": transaction.description,
                            "UnitAmount": transaction.amount,
                            "AccountCode": transaction.account_id
                        }
                    ],
                    "BankAccount": {
                        "AccountID": transaction.account_id
                    }
                }
            ]
        }

        # Remove None contact if no vendor
        if not transaction.vendor_id:
            del transaction_data["BankTransactions"][0]["Contact"]

        response = self._make_request('POST', 'BankTransactions', transaction_data)
        return response

    def sync_transactions(self, transactions: List[AccountingTransaction]) -> Dict[str, Any]:
        """Sync multiple transactions to Xero."""
        results = {
            'total': len(transactions),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        for transaction in transactions:
            try:
                if transaction.vendor_id:
                    self.create_bill(transaction)
                else:
                    self.create_bank_transaction(transaction)

                results['successful'] += 1
                self.logger.info(f"Successfully synced transaction to Xero: {transaction.id}")

            except Exception as e:
                results['failed'] += 1
                error_msg = f"Failed to sync transaction {transaction.id}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)

        return results


class AccountingIntegrationManager:
    """Unified manager for multiple accounting software integrations."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.integrations = {}

        # Initialize enabled integrations
        if config.get('quickbooks', {}).get('enabled'):
            try:
                self.integrations['quickbooks'] = QuickBooksIntegration(config['quickbooks'])
                self.logger.info("QuickBooks integration initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize QuickBooks: {e}")

        if config.get('xero', {}).get('enabled'):
            try:
                self.integrations['xero'] = XeroIntegration(config['xero'])
                self.logger.info("Xero integration initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Xero: {e}")

    def get_available_integrations(self) -> List[str]:
        """Get list of available integrations."""
        return list(self.integrations.keys())

    def sync_transactions(self, transactions: List[AccountingTransaction], target_system: Optional[str] = None) -> Dict[str, Any]:
        """Sync transactions to accounting software."""
        if target_system and target_system in self.integrations:
            # Sync to specific system
            return self.integrations[target_system].sync_transactions(transactions)

        # Sync to all configured systems
        results = {}
        for system_name, integration in self.integrations.items():
            try:
                results[system_name] = integration.sync_transactions(transactions)
            except Exception as e:
                results[system_name] = {
                    'error': str(e),
                    'successful': 0,
                    'failed': len(transactions)
                }

        return results

    def get_chart_of_accounts(self, system: str) -> List[Account]:
        """Get chart of accounts from specified system."""
        if system not in self.integrations:
            raise ValueError(f"Integration not available: {system}")

        return self.integrations[system].get_accounts()

    def get_vendors(self, system: str) -> List[Vendor]:
        """Get vendor list from specified system."""
        if system not in self.integrations:
            raise ValueError(f"Integration not available: {system}")

        if system == 'quickbooks':
            return self.integrations[system].get_vendors()
        elif system == 'xero':
            return self.integrations[system].get_contacts()

    def create_vendor(self, vendor_data: Dict[str, Any], system: str) -> Vendor:
        """Create vendor in specified system."""
        if system not in self.integrations:
            raise ValueError(f"Integration not available: {system}")

        if system == 'quickbooks':
            return self.integrations[system].create_vendor(vendor_data)
        elif system == 'xero':
            return self.integrations[system].create_contact(vendor_data)

    def test_connection(self, system: str) -> Dict[str, Any]:
        """Test connection to accounting software."""
        if system not in self.integrations:
            return {
                'success': False,
                'error': f"Integration not available: {system}"
            }

        try:
            if system == 'quickbooks':
                company_info = self.integrations[system].get_company_info()
                return {
                    'success': True,
                    'system': system,
                    'company_name': company_info.get('QueryResponse', {}).get('CompanyInfo', [{}])[0].get('CompanyName'),
                    'message': 'Connection successful'
                }

            elif system == 'xero':
                accounts = self.integrations[system].get_accounts()
                return {
                    'success': True,
                    'system': system,
                    'account_count': len(accounts),
                    'message': 'Connection successful'
                }

        except Exception as e:
            return {
                'success': False,
                'system': system,
                'error': str(e)
            }

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        status = {
            'total_integrations': len(self.integrations),
            'systems': {}
        }

        for system_name in self.integrations:
            connection_test = self.test_connection(system_name)
            status['systems'][system_name] = {
                'connected': connection_test['success'],
                'last_tested': datetime.now().isoformat(),
                'details': connection_test
            }

        return status


def create_sample_config() -> Dict[str, Any]:
    """Create a sample configuration for accounting integrations."""
    return {
        'quickbooks': {
            'enabled': False,
            'sandbox': True,
            'client_id': 'your_quickbooks_client_id',
            'client_secret': 'your_quickbooks_client_secret',
            'access_token': 'your_access_token',
            'refresh_token': 'your_refresh_token',
            'company_id': 'your_company_id'
        },
        'xero': {
            'enabled': False,
            'client_id': 'your_xero_client_id',
            'client_secret': 'your_xero_client_secret',
            'access_token': 'your_xero_access_token',
            'tenant_id': 'your_xero_tenant_id'
        }
    }


def convert_to_accounting_transaction(transaction_data: Dict[str, Any], system_accounts: List[Account]) -> AccountingTransaction:
    """Convert generic transaction data to AccountingTransaction format."""
    # Map category to account ID
    account_id = None
    for account in system_accounts:
        if account.name.lower() == transaction_data.get('category', '').lower():
            account_id = account.id
            break

    # Fallback to first expense account if no match
    if not account_id:
        expense_accounts = [a for a in system_accounts if 'expense' in a.account_type.lower()]
        if expense_accounts:
            account_id = expense_accounts[0].id

    return AccountingTransaction(
        id=transaction_data.get('id', str(hash(transaction_data.get('description', '')))),
        date=datetime.fromisoformat(transaction_data['date']) if isinstance(transaction_data['date'], str) else transaction_data['date'],
        description=transaction_data['description'],
        amount=float(transaction_data['amount']),
        account_id=account_id or '1',  # Fallback to account 1
        category=transaction_data.get('category', 'Uncategorized'),
        vendor_id=transaction_data.get('vendor_id'),
        invoice_number=transaction_data.get('invoice_number'),
        reference=transaction_data.get('reference'),
        memo=transaction_data.get('memo')
    )