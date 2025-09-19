# CRM Integration Guide 🗂️

*Connect HubSpot, Salesforce, Google Sheets, Airtable, and more to your LangChain system*

## What You'll Need
- Admin access to your CRM system
- API credentials (we'll show you how to get them)
- 30-45 minutes per integration
- Basic understanding of your CRM structure

---

## HubSpot Integration

### Step 1: Get HubSpot API Key
1. **Log into HubSpot** at app.hubspot.com
2. **Click the settings icon** (gear icon, top right)
3. **Go to "Integrations" → "API key"**
4. **Click "Create key"** (or copy existing key)
5. **Copy the API key** (keep it secure!)

### Step 2: Test HubSpot Connection
```javascript
// Test HubSpot API connection
const hubspotApiKey = 'your-api-key-here';
const hubspotBaseUrl = 'https://api.hubapi.com';

async function testHubSpotConnection() {
    try {
        const response = await fetch(`${hubspotBaseUrl}/contacts/v1/lists/all/contacts/all?hapikey=${hubspotApiKey}&count=1`);
        const data = await response.json();

        if (response.ok) {
            console.log('✅ HubSpot connection successful!');
            console.log('Total contacts:', data.total);
            return true;
        } else {
            console.error('❌ HubSpot connection failed:', data.message);
            return false;
        }
    } catch (error) {
        console.error('❌ Connection error:', error.message);
        return false;
    }
}

// Run test
testHubSpotConnection();
```

### Step 3: HubSpot CRUD Operations
```javascript
class HubSpotCRM {
    constructor(apiKey) {
        this.apiKey = apiKey;
        this.baseUrl = 'https://api.hubapi.com';
    }

    // Create a new contact
    async createContact(contactData) {
        const properties = Object.keys(contactData).map(key => ({
            property: key,
            value: contactData[key]
        }));

        const response = await fetch(`${this.baseUrl}/contacts/v1/contact?hapikey=${this.apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ properties })
        });

        return response.json();
    }

    // Get contact by email
    async getContactByEmail(email) {
        const response = await fetch(
            `${this.baseUrl}/contacts/v1/contact/email/${email}/profile?hapikey=${this.apiKey}`
        );
        return response.json();
    }

    // Update contact
    async updateContact(contactId, updateData) {
        const properties = Object.keys(updateData).map(key => ({
            property: key,
            value: updateData[key]
        }));

        const response = await fetch(`${this.baseUrl}/contacts/v1/contact/vid/${contactId}/profile?hapikey=${this.apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ properties })
        });

        return response.json();
    }

    // Create a deal
    async createDeal(dealData) {
        const properties = Object.keys(dealData).map(key => ({
            name: key,
            value: dealData[key]
        }));

        const response = await fetch(`${this.baseUrl}/deals/v1/deal?hapikey=${this.apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                properties: properties
            })
        });

        return response.json();
    }

    // Log activity/note
    async logActivity(contactId, activityData) {
        const engagement = {
            engagement: {
                active: true,
                type: 'NOTE',
                timestamp: Date.now()
            },
            associations: {
                contactIds: [contactId]
            },
            metadata: {
                body: activityData.notes
            }
        };

        const response = await fetch(`${this.baseUrl}/engagements/v1/engagements?hapikey=${this.apiKey}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(engagement)
        });

        return response.json();
    }
}

// Usage example
const hubspot = new HubSpotCRM('your-api-key');

// Create new contact
hubspot.createContact({
    email: 'john.doe@example.com',
    firstname: 'John',
    lastname: 'Doe',
    phone: '+1234567890',
    company: 'Example Corp'
}).then(result => {
    console.log('Contact created:', result);
});
```

### HubSpot Webhooks Setup
1. **In HubSpot**, go to **Settings → Integrations → Webhooks**
2. **Click "Create webhook"**
3. **Set the target URL** (your server endpoint)
4. **Select events** to monitor:
   - Contact creation
   - Contact property changes
   - Deal stage changes
5. **Save the webhook**

```javascript
// Express.js webhook handler for HubSpot
app.post('/hubspot-webhook', express.json(), (req, res) => {
    const events = req.body;

    events.forEach(event => {
        console.log('HubSpot event:', event.subscriptionType, event.objectId);

        switch(event.subscriptionType) {
            case 'contact.creation':
                handleNewContact(event);
                break;
            case 'contact.propertyChange':
                handleContactUpdate(event);
                break;
            case 'deal.creation':
                handleNewDeal(event);
                break;
        }
    });

    res.sendStatus(200);
});

function handleNewContact(event) {
    console.log('New contact created:', event.objectId);
    // Process with LangChain
    // Send welcome email
    // Add to email sequence
}
```

### HubSpot Troubleshooting
**"Authentication failed"**
- **Solution**: Check API key is correct and account has API access

**"Property does not exist"**
- **Solution**: Create custom properties in HubSpot settings first

**"Rate limit exceeded"**
- **Solution**: HubSpot has limits, implement exponential backoff

---

## Salesforce Integration

### Step 1: Create Connected App
1. **Log into Salesforce** as an admin
2. **Go to Setup** (gear icon → Setup)
3. **Search for "App Manager"** in Quick Find
4. **Click "New Connected App"**
5. **Fill in basic information:**
   - **Connected App Name**: "LangChain Integration"
   - **API Name**: "LangChain_Integration"
   - **Contact Email**: Your email
6. **Enable OAuth Settings:**
   - **Callback URL**: `https://your-domain.com/oauth/callback`
   - **Selected OAuth Scopes**: Add "Full access (full)" and "Perform requests on your behalf at any time (refresh_token, offline_access)"
7. **Save**

### Step 2: Get Salesforce Credentials
1. **After saving**, copy:
   - **Consumer Key** (Client ID)
   - **Consumer Secret** (Client Secret)
2. **Go to "Manage Connected Apps"**
3. **Edit your app**
4. **Set "Permitted Users"** to "Admin approved users are pre-authorized"

### Step 3: Salesforce Authentication
```javascript
// Salesforce OAuth flow
const salesforceAuth = {
    clientId: 'your-consumer-key',
    clientSecret: 'your-consumer-secret',
    redirectUri: 'https://your-domain.com/oauth/callback',
    loginUrl: 'https://login.salesforce.com'
};

// Step 1: Get authorization code
function getSalesforceAuthUrl() {
    const params = new URLSearchParams({
        response_type: 'code',
        client_id: salesforceAuth.clientId,
        redirect_uri: salesforceAuth.redirectUri,
        scope: 'full refresh_token'
    });

    return `${salesforceAuth.loginUrl}/services/oauth2/authorize?${params.toString()}`;
}

// Step 2: Exchange code for tokens
async function getAccessToken(authorizationCode) {
    const response = await fetch(`${salesforceAuth.loginUrl}/services/oauth2/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            grant_type: 'authorization_code',
            client_id: salesforceAuth.clientId,
            client_secret: salesforceAuth.clientSecret,
            redirect_uri: salesforceAuth.redirectUri,
            code: authorizationCode
        })
    });

    return response.json();
}
```

### Step 4: Salesforce CRUD Operations
```javascript
class SalesforceCRM {
    constructor(accessToken, instanceUrl) {
        this.accessToken = accessToken;
        this.instanceUrl = instanceUrl;
        this.apiVersion = 'v58.0';
    }

    async makeRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.instanceUrl}/services/data/${this.apiVersion}${endpoint}`;

        const options = {
            method,
            headers: {
                'Authorization': `Bearer ${this.accessToken}`,
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return response.json();
    }

    // Create record
    async createRecord(objectType, data) {
        return this.makeRequest(`/sobjects/${objectType}/`, 'POST', data);
    }

    // Get record
    async getRecord(objectType, id, fields = []) {
        const fieldsParam = fields.length > 0 ? `?fields=${fields.join(',')}` : '';
        return this.makeRequest(`/sobjects/${objectType}/${id}${fieldsParam}`);
    }

    // Update record
    async updateRecord(objectType, id, data) {
        return this.makeRequest(`/sobjects/${objectType}/${id}`, 'PATCH', data);
    }

    // Search records
    async searchRecords(soqlQuery) {
        const encodedQuery = encodeURIComponent(soqlQuery);
        return this.makeRequest(`/query/?q=${encodedQuery}`);
    }

    // Create lead
    async createLead(leadData) {
        return this.createRecord('Lead', leadData);
    }

    // Create opportunity
    async createOpportunity(opportunityData) {
        return this.createRecord('Opportunity', opportunityData);
    }

    // Get contact by email
    async getContactByEmail(email) {
        const query = `SELECT Id, Name, Email, Phone FROM Contact WHERE Email = '${email}' LIMIT 1`;
        const result = await this.searchRecords(query);
        return result.records[0] || null;
    }
}

// Usage example
const salesforce = new SalesforceCRM('access-token', 'https://your-instance.salesforce.com');

// Create a new lead
salesforce.createLead({
    FirstName: 'Jane',
    LastName: 'Smith',
    Email: 'jane.smith@example.com',
    Company: 'Smith Industries',
    Status: 'Open - Not Contacted'
}).then(result => {
    console.log('Lead created:', result);
});
```

### Salesforce Troubleshooting
**"Invalid session ID"**
- **Solution**: Refresh your access token using the refresh token

**"Insufficient privileges"**
- **Solution**: Check user permissions for the objects you're accessing

**"Required field missing"**
- **Solution**: Include all required fields for the Salesforce object

---

## Google Sheets Integration

### Step 1: Set Up Google Sheets API
1. **Go to** https://console.developers.google.com
2. **Create a new project** or select existing one
3. **Enable Google Sheets API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. **Create credentials:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Fill in service account details
   - Download the JSON key file

### Step 2: Share Your Spreadsheet
1. **Open your Google Sheet**
2. **Click "Share"**
3. **Add the service account email** (from the JSON file)
4. **Give "Editor" permissions**

### Step 3: Google Sheets Integration
```javascript
// Google Sheets integration with googleapis
const { GoogleSpreadsheet } = require('google-spreadsheet');
const credentials = require('./path-to-your-credentials.json');

class GoogleSheetsCRM {
    constructor(spreadsheetId) {
        this.spreadsheetId = spreadsheetId;
        this.doc = new GoogleSpreadsheet(spreadsheetId);
    }

    async initialize() {
        await this.doc.useServiceAccountAuth(credentials);
        await this.doc.loadInfo();
    }

    // Add new row (contact/lead)
    async addContact(contactData) {
        const sheet = this.doc.sheetsByIndex[0]; // First sheet
        const row = await sheet.addRow(contactData);
        return row;
    }

    // Get all contacts
    async getAllContacts() {
        const sheet = this.doc.sheetsByIndex[0];
        const rows = await sheet.getRows();
        return rows.map(row => row._rawData);
    }

    // Find contact by email
    async findContactByEmail(email) {
        const sheet = this.doc.sheetsByIndex[0];
        const rows = await sheet.getRows();
        return rows.find(row => row.Email === email);
    }

    // Update contact
    async updateContact(email, updateData) {
        const contact = await this.findContactByEmail(email);
        if (contact) {
            Object.keys(updateData).forEach(key => {
                contact[key] = updateData[key];
            });
            await contact.save();
            return contact;
        }
        return null;
    }

    // Create new sheet for specific data
    async createSheet(title, headers) {
        const sheet = await this.doc.addSheet({
            title,
            headerValues: headers
        });
        return sheet;
    }
}

// Usage example
async function useGoogleSheets() {
    const sheets = new GoogleSheetsCRM('your-spreadsheet-id');
    await sheets.initialize();

    // Add new contact
    await sheets.addContact({
        Name: 'John Doe',
        Email: 'john@example.com',
        Phone: '+1234567890',
        Company: 'Example Corp',
        Status: 'New Lead',
        'Date Added': new Date().toISOString().split('T')[0]
    });

    console.log('Contact added to Google Sheets!');
}
```

### Google Sheets Formulas for CRM
```javascript
// Add helpful formulas to your sheets
const crmFormulas = {
    // Auto-calculate days since last contact
    daysSinceContact: '=TODAY()-E2',

    // Lead score based on multiple factors
    leadScore: '=IF(F2="Hot",10,IF(F2="Warm",7,IF(F2="Cold",3,0)))+IF(G2>50000,5,0)',

    // Auto-assign sales rep based on region
    assignedRep: '=IF(H2="North","Alice",IF(H2="South","Bob","Charlie"))',

    // Progress bar for deal stage
    dealProgress: '=IF(I2="Prospecting",25,IF(I2="Qualified",50,IF(I2="Proposal",75,IF(I2="Closed Won",100,0))))',
};

// Function to add formulas to sheet
async function addFormulasToSheet(sheet) {
    // Add headers if they don't exist
    const headers = await sheet.headerValues;
    if (!headers.includes('Days Since Contact')) {
        await sheet.resize({ columnCount: headers.length + 1 });
        await sheet.setHeaderRow([...headers, 'Days Since Contact', 'Lead Score', 'Assigned Rep']);
    }
}
```

### Google Sheets Troubleshooting
**"The caller does not have permission"**
- **Solution**: Make sure service account has access to the spreadsheet

**"Sheets API not enabled"**
- **Solution**: Enable Google Sheets API in Google Cloud Console

**"Invalid credentials"**
- **Solution**: Download new credentials JSON file

---

## Airtable Integration

### Step 1: Get Airtable API Key
1. **Go to** https://airtable.com/api
2. **Log into your account**
3. **Go to Account settings**
4. **Generate API key** (or copy existing one)
5. **Note your Base ID** (from the URL when viewing your base)

### Step 2: Airtable Integration
```javascript
// Airtable integration
class AirtableCRM {
    constructor(apiKey, baseId) {
        this.apiKey = apiKey;
        this.baseId = baseId;
        this.baseUrl = 'https://api.airtable.com/v0';
    }

    async makeRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}/${this.baseId}${endpoint}`;

        const options = {
            method,
            headers: {
                'Authorization': `Bearer ${this.apiKey}`,
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url, options);
        return response.json();
    }

    // Create record
    async createRecord(tableName, fields) {
        return this.makeRequest(`/${tableName}`, 'POST', {
            fields: fields
        });
    }

    // Get records
    async getRecords(tableName, options = {}) {
        let endpoint = `/${tableName}`;

        if (Object.keys(options).length > 0) {
            const params = new URLSearchParams(options);
            endpoint += `?${params.toString()}`;
        }

        return this.makeRequest(endpoint);
    }

    // Update record
    async updateRecord(tableName, recordId, fields) {
        return this.makeRequest(`/${tableName}/${recordId}`, 'PATCH', {
            fields: fields
        });
    }

    // Delete record
    async deleteRecord(tableName, recordId) {
        return this.makeRequest(`/${tableName}/${recordId}`, 'DELETE');
    }

    // Find record by field
    async findRecordByField(tableName, fieldName, value) {
        const formula = `{${fieldName}} = "${value}"`;
        const result = await this.getRecords(tableName, {
            filterByFormula: formula,
            maxRecords: 1
        });

        return result.records[0] || null;
    }
}

// Usage example
const airtable = new AirtableCRM('your-api-key', 'your-base-id');

// Create new contact
airtable.createRecord('Contacts', {
    'Name': 'Sarah Johnson',
    'Email': 'sarah@example.com',
    'Phone': '+1234567890',
    'Company': 'Johnson Corp',
    'Status': 'Lead',
    'Notes': 'Interested in our premium package'
}).then(result => {
    console.log('Contact created in Airtable:', result);
});

// Find contact by email
airtable.findRecordByField('Contacts', 'Email', 'sarah@example.com')
    .then(contact => {
        if (contact) {
            console.log('Found contact:', contact.fields);
        }
    });
```

### Airtable Views and Filters
```javascript
// Get records with specific view
async function getContactsByStatus(status) {
    return airtable.getRecords('Contacts', {
        filterByFormula: `{Status} = "${status}"`,
        sort: [{ field: 'Created Time', direction: 'desc' }],
        maxRecords: 100
    });
}

// Get high-value deals
async function getHighValueDeals() {
    return airtable.getRecords('Deals', {
        filterByFormula: '{Deal Value} > 10000',
        view: 'High Priority',
        fields: ['Deal Name', 'Contact', 'Deal Value', 'Stage']
    });
}

// Bulk update records
async function bulkUpdateContacts(updates) {
    const records = updates.map(update => ({
        id: update.recordId,
        fields: update.fields
    }));

    // Airtable allows max 10 records per batch
    const batches = [];
    for (let i = 0; i < records.length; i += 10) {
        batches.push(records.slice(i, i + 10));
    }

    const results = [];
    for (const batch of batches) {
        const result = await airtable.makeRequest('/Contacts', 'PATCH', {
            records: batch
        });
        results.push(result);
    }

    return results;
}
```

---

## Pipedrive Integration

### Step 1: Get Pipedrive API Token
1. **Log into Pipedrive**
2. **Go to Settings → Personal Preferences**
3. **Click "API" tab**
4. **Copy your API token**

### Step 2: Pipedrive Integration
```javascript
class PipedriveCRM {
    constructor(apiToken, companyDomain) {
        this.apiToken = apiToken;
        this.baseUrl = `https://${companyDomain}.pipedrive.com/api/v1`;
    }

    async makeRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const params = new URLSearchParams({ api_token: this.apiToken });

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (method === 'GET') {
            const fullUrl = `${url}?${params.toString()}`;
            const response = await fetch(fullUrl, options);
            return response.json();
        } else {
            if (data) {
                data.api_token = this.apiToken;
                options.body = JSON.stringify(data);
            }
            const response = await fetch(url, options);
            return response.json();
        }
    }

    // Create person (contact)
    async createPerson(personData) {
        return this.makeRequest('/persons', 'POST', personData);
    }

    // Create deal
    async createDeal(dealData) {
        return this.makeRequest('/deals', 'POST', dealData);
    }

    // Get persons
    async getPersons(searchTerm = null) {
        const endpoint = searchTerm
            ? `/persons/search?term=${encodeURIComponent(searchTerm)}`
            : '/persons';
        return this.makeRequest(endpoint);
    }

    // Update person
    async updatePerson(personId, updateData) {
        return this.makeRequest(`/persons/${personId}`, 'PUT', updateData);
    }

    // Add note to person
    async addNote(personId, content) {
        return this.makeRequest('/notes', 'POST', {
            content: content,
            person_id: personId
        });
    }
}
```

---

## Universal CRM Manager

### Multi-CRM Integration Class
```javascript
class UniversalCRM {
    constructor() {
        this.connectors = {
            hubspot: null,
            salesforce: null,
            googlesheets: null,
            airtable: null,
            pipedrive: null
        };
    }

    addConnector(type, connector) {
        this.connectors[type] = connector;
    }

    async syncContact(contactData) {
        const results = {};

        for (const [type, connector] of Object.entries(this.connectors)) {
            if (connector) {
                try {
                    results[type] = await this.createContactInCRM(type, connector, contactData);
                } catch (error) {
                    results[type] = { error: error.message };
                }
            }
        }

        return results;
    }

    async createContactInCRM(type, connector, contactData) {
        switch (type) {
            case 'hubspot':
                return connector.createContact(contactData);
            case 'salesforce':
                return connector.createRecord('Contact', contactData);
            case 'googlesheets':
                return connector.addContact(contactData);
            case 'airtable':
                return connector.createRecord('Contacts', contactData);
            case 'pipedrive':
                return connector.createPerson(contactData);
            default:
                throw new Error(`Unknown CRM type: ${type}`);
        }
    }

    // Standardize contact data format
    standardizeContactData(rawData, sourceFormat) {
        const standardized = {};

        const fieldMappings = {
            hubspot: {
                'email': 'email',
                'firstname': 'firstName',
                'lastname': 'lastName',
                'phone': 'phone',
                'company': 'company'
            },
            salesforce: {
                'Email': 'email',
                'FirstName': 'firstName',
                'LastName': 'lastName',
                'Phone': 'phone',
                'Account.Name': 'company'
            },
            // Add mappings for other CRMs
        };

        const mapping = fieldMappings[sourceFormat];
        if (mapping) {
            Object.keys(rawData).forEach(key => {
                const standardKey = Object.keys(mapping).find(k => mapping[k] === key);
                if (standardKey) {
                    standardized[standardKey] = rawData[key];
                }
            });
        }

        return standardized;
    }
}

// Usage example
const universalCRM = new UniversalCRM();

// Add multiple CRM connectors
universalCRM.addConnector('hubspot', new HubSpotCRM('hubspot-api-key'));
universalCRM.addConnector('airtable', new AirtableCRM('airtable-api-key', 'base-id'));

// Sync contact to all connected CRMs
const contactData = {
    email: 'multi@example.com',
    firstName: 'Multi',
    lastName: 'Platform',
    phone: '+1234567890',
    company: 'Universal Corp'
};

universalCRM.syncContact(contactData).then(results => {
    console.log('Sync results:', results);
});
```

---

## Automation & Workflows

### CRM Automation System
```javascript
class CRMAutomation {
    constructor(crmManager) {
        this.crm = crmManager;
        this.workflows = [];
    }

    addWorkflow(trigger, actions) {
        this.workflows.push({ trigger, actions });
    }

    async processEvent(eventType, eventData) {
        const matchingWorkflows = this.workflows.filter(
            workflow => workflow.trigger.type === eventType
        );

        for (const workflow of matchingWorkflows) {
            if (this.evaluateConditions(workflow.trigger.conditions, eventData)) {
                await this.executeActions(workflow.actions, eventData);
            }
        }
    }

    evaluateConditions(conditions, data) {
        return conditions.every(condition => {
            const value = data[condition.field];
            switch (condition.operator) {
                case 'equals':
                    return value === condition.value;
                case 'contains':
                    return value && value.includes(condition.value);
                case 'greater_than':
                    return value > condition.value;
                default:
                    return false;
            }
        });
    }

    async executeActions(actions, eventData) {
        for (const action of actions) {
            try {
                await this.executeAction(action, eventData);
            } catch (error) {
                console.error('Action execution failed:', error);
            }
        }
    }

    async executeAction(action, eventData) {
        switch (action.type) {
            case 'send_email':
                await this.sendEmail(action.template, eventData);
                break;
            case 'create_task':
                await this.createTask(action.task, eventData);
                break;
            case 'update_contact':
                await this.updateContact(action.updates, eventData);
                break;
            case 'assign_to_user':
                await this.assignToUser(action.userId, eventData);
                break;
        }
    }
}

// Example workflow setup
const automation = new CRMAutomation(universalCRM);

// Workflow: Send welcome email to new contacts
automation.addWorkflow(
    {
        type: 'contact_created',
        conditions: [
            { field: 'status', operator: 'equals', value: 'New Lead' }
        ]
    },
    [
        {
            type: 'send_email',
            template: 'welcome_sequence',
            delay: 0
        },
        {
            type: 'create_task',
            task: {
                title: 'Follow up with new lead',
                assignee: 'sales_team',
                dueDate: '+2 days'
            }
        }
    ]
);

// Workflow: Alert for high-value deals
automation.addWorkflow(
    {
        type: 'deal_created',
        conditions: [
            { field: 'value', operator: 'greater_than', value: 50000 }
        ]
    },
    [
        {
            type: 'assign_to_user',
            userId: 'senior_sales_manager'
        },
        {
            type: 'send_notification',
            message: 'High-value deal created: {{deal_name}}'
        }
    ]
);
```

---

## Common Problems & Solutions

### Authentication Issues
**Problem**: "Invalid API key" or "Access denied"
**Solutions:**
- Verify API key is copied correctly (no extra spaces)
- Check if API access is enabled for your account
- Ensure you have the right permissions
- Try regenerating the API key

### Rate Limiting
**Problem**: "Too many requests" or "Rate limit exceeded"
**Solutions:**
- Implement exponential backoff
- Reduce request frequency
- Use bulk operations when available
- Cache frequently accessed data

### Data Sync Issues
**Problem**: Data not appearing or appearing incorrectly
**Solutions:**
- Check field mappings between systems
- Verify required fields are included
- Test with simple data first
- Check for character encoding issues

### Webhook Failures
**Problem**: Real-time updates not working
**Solutions:**
- Verify webhook URL is publicly accessible
- Check webhook endpoint returns proper status codes
- Review webhook logs for errors
- Test webhook manually with tools like ngrok

---

## Best Practices

### ✅ DO:
- **Map data fields** consistently across systems
- **Implement error handling** for all API calls
- **Use bulk operations** for large data sets
- **Cache frequently accessed data**
- **Log all API interactions** for debugging
- **Implement retry logic** with exponential backoff

### ❌ DON'T:
- **Hardcode API credentials** in your source code
- **Make unnecessary API calls** (implement caching)
- **Ignore rate limits** (respect API quotas)
- **Store sensitive data** without encryption
- **Skip data validation** before sending to CRM

---

## Security Checklist

### 🔒 Security Measures:
- [ ] Store API keys in environment variables
- [ ] Use HTTPS for all API communications
- [ ] Implement proper error handling (don't expose sensitive data)
- [ ] Regularly rotate API keys
- [ ] Monitor API usage for unusual activity
- [ ] Validate all incoming webhook data
- [ ] Use least privilege principle for API permissions

### 🛡️ Data Protection:
- [ ] Encrypt sensitive data at rest
- [ ] Implement proper access controls
- [ ] Keep audit logs of data access
- [ ] Comply with GDPR/CCPA requirements
- [ ] Have data backup and recovery procedures

---

## Testing Your Integration

### Integration Test Checklist
```javascript
async function testCRMIntegration() {
    const tests = [
        {
            name: 'Create Contact',
            test: () => crm.createContact(testContactData)
        },
        {
            name: 'Get Contact',
            test: () => crm.getContactByEmail('test@example.com')
        },
        {
            name: 'Update Contact',
            test: () => crm.updateContact('contact-id', { phone: '+1111111111' })
        },
        {
            name: 'Create Deal',
            test: () => crm.createDeal(testDealData)
        }
    ];

    for (const test of tests) {
        try {
            console.log(`Testing: ${test.name}`);
            await test.test();
            console.log(`✅ ${test.name} passed`);
        } catch (error) {
            console.log(`❌ ${test.name} failed:`, error.message);
        }
    }
}

// Run tests
testCRMIntegration();
```

---

## Getting Help

### Before Contacting Support:
1. **Test with simple operations** first
2. **Check API documentation** for changes
3. **Verify credentials** are correct
4. **Review error messages** carefully
5. **Check rate limits** haven't been exceeded

### CRM-Specific Support:
- **HubSpot**: https://developers.hubspot.com/support
- **Salesforce**: https://developer.salesforce.com/support
- **Google Sheets**: https://developers.google.com/sheets/api/support
- **Airtable**: https://support.airtable.com/hc/en-us/articles/360051564873-Airtable-API-support
- **Pipedrive**: https://support.pipedrive.com/hc/en-us

---

*Congratulations! You now have comprehensive integration guides for all major platforms. Start with one integration, test thoroughly, then expand to others as needed.*