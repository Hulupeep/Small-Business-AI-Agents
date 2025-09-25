"""
Clinical Records Assistant Agent
GDPR-compliant patient record management
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json
import hashlib
import uuid

class ClinicalRecordsAssistant:
    """AI-powered clinical records management with GDPR compliance"""

    def __init__(self, llm: ChatOpenAI, practice_config: Dict[str, Any]):
        self.llm = llm
        self.practice_config = practice_config
        self.records_database = {}  # In production, this would be encrypted database
        self.audit_log = []
        self.consent_records = {}
        self.retention_policies = self._initialize_retention_policies()

    def _initialize_retention_policies(self) -> Dict[str, int]:
        """Initialize GDPR-compliant data retention policies"""
        return {
            'clinical_notes': 7,      # 7 years
            'x_rays': 7,              # 7 years
            'treatment_records': 7,   # 7 years
            'payment_records': 6,     # 6 years for tax purposes
            'correspondence': 3,      # 3 years
            'appointment_history': 7, # 7 years
            'consent_forms': 7,       # 7 years
            'referral_letters': 7     # 7 years
        }

    def create_patient_record(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new patient record with GDPR compliance"""

        # Generate unique patient ID
        patient_id = f"PAT_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8].upper()}"

        # Encrypt sensitive data
        encrypted_data = self._encrypt_sensitive_data(patient_data)

        # Create audit trail entry
        self._create_audit_entry('CREATE_RECORD', patient_id, 'Patient record created')

        patient_record = {
            'patient_id': patient_id,
            'personal_info': {
                'name': encrypted_data['name'],
                'date_of_birth': encrypted_data['date_of_birth'],
                'address': encrypted_data['address'],
                'phone': encrypted_data['phone'],
                'email': encrypted_data['email'],
                'emergency_contact': encrypted_data.get('emergency_contact')
            },
            'medical_history': {
                'allergies': patient_data.get('allergies', []),
                'medications': patient_data.get('medications', []),
                'medical_conditions': patient_data.get('medical_conditions', []),
                'previous_dental_work': patient_data.get('previous_dental_work', [])
            },
            'dental_history': {
                'last_visit': patient_data.get('last_visit'),
                'dental_concerns': patient_data.get('dental_concerns', []),
                'oral_hygiene_habits': patient_data.get('oral_hygiene_habits', {})
            },
            'consent_records': {
                'data_processing': False,
                'treatment_consent': False,
                'marketing_consent': False,
                'data_sharing_consent': False
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'gdpr_compliance': {
                'consent_obtained': False,
                'data_retention_policy': 'clinical_notes',
                'anonymization_date': (datetime.now() + timedelta(days=365*7)).isoformat()
            }
        }

        self.records_database[patient_id] = patient_record
        return {'success': True, 'patient_id': patient_id, 'record': patient_record}

    def _encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive patient data (simulation)"""
        # In production, use proper encryption libraries
        encrypted_data = {}
        for key, value in data.items():
            if key in ['name', 'date_of_birth', 'address', 'phone', 'email']:
                # Simulate encryption with hash (use proper encryption in production)
                encrypted_data[key] = f"ENCRYPTED_{hashlib.sha256(str(value).encode()).hexdigest()[:16]}"
            else:
                encrypted_data[key] = value
        return encrypted_data

    def update_clinical_notes(self, patient_id: str, visit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update clinical notes with voice-to-text processing"""

        if patient_id not in self.records_database:
            return {'success': False, 'error': 'Patient not found'}

        # Process voice-to-text notes
        processed_notes = self._process_clinical_notes(visit_data.get('notes', ''))

        visit_record = {
            'visit_id': f"VIS_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'date': visit_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'time': visit_data.get('time', datetime.now().strftime('%H:%M')),
            'dentist': visit_data.get('dentist'),
            'treatment_type': visit_data.get('treatment_type'),
            'clinical_notes': processed_notes,
            'diagnosis': visit_data.get('diagnosis'),
            'treatment_performed': visit_data.get('treatment_performed', []),
            'prescriptions': visit_data.get('prescriptions', []),
            'follow_up_required': visit_data.get('follow_up_required', False),
            'next_appointment': visit_data.get('next_appointment'),
            'pain_score': visit_data.get('pain_score'),
            'vital_signs': visit_data.get('vital_signs', {}),
            'created_by': visit_data.get('created_by'),
            'created_at': datetime.now().isoformat()
        }

        # Add visit to patient record
        if 'visits' not in self.records_database[patient_id]:
            self.records_database[patient_id]['visits'] = []

        self.records_database[patient_id]['visits'].append(visit_record)
        self.records_database[patient_id]['last_updated'] = datetime.now().isoformat()

        # Create audit entry
        self._create_audit_entry('UPDATE_NOTES', patient_id, f"Clinical notes updated for visit {visit_record['visit_id']}")

        # Check for drug interactions
        interaction_warnings = self._check_drug_interactions(
            visit_data.get('prescriptions', []),
            self.records_database[patient_id]['medical_history']['medications']
        )

        return {
            'success': True,
            'visit_id': visit_record['visit_id'],
            'interaction_warnings': interaction_warnings,
            'processed_notes': processed_notes
        }

    def _process_clinical_notes(self, raw_notes: str) -> Dict[str, Any]:
        """Process voice-to-text clinical notes with dental terminology"""

        # Dental terminology dictionary for processing
        dental_terms = {
            'upper right': 'UR',
            'upper left': 'UL',
            'lower right': 'LR',
            'lower left': 'LL',
            'central incisor': 'CI',
            'lateral incisor': 'LI',
            'canine': 'C',
            'first premolar': '1PM',
            'second premolar': '2PM',
            'first molar': '1M',
            'second molar': '2M',
            'third molar': '3M',
            'amalgam': 'AM',
            'composite': 'CO',
            'crown': 'CR',
            'bridge': 'BR'
        }

        processed_notes = raw_notes.lower()

        # Replace dental terminology
        for term, abbreviation in dental_terms.items():
            processed_notes = processed_notes.replace(term, abbreviation)

        # Extract structured information
        extracted_info = {
            'raw_text': raw_notes,
            'processed_text': processed_notes,
            'tooth_chart': self._extract_tooth_chart(processed_notes),
            'treatment_codes': self._extract_treatment_codes(processed_notes),
            'pain_indicators': self._extract_pain_indicators(processed_notes),
            'urgency_flags': self._extract_urgency_flags(processed_notes)
        }

        return extracted_info

    def _extract_tooth_chart(self, notes: str) -> Dict[str, Any]:
        """Extract tooth-specific information from notes"""
        # Simplified tooth chart extraction
        tooth_info = {}

        # Look for tooth numbers and conditions
        import re
        tooth_pattern = r'tooth (\d+)|(\d+)\s*(caries|filling|crown|extraction)'
        matches = re.findall(tooth_pattern, notes)

        for match in matches:
            tooth_num = match[0] or match[1]
            condition = match[2] if match[2] else 'mentioned'
            if tooth_num:
                tooth_info[f"tooth_{tooth_num}"] = condition

        return tooth_info

    def _extract_treatment_codes(self, notes: str) -> List[str]:
        """Extract treatment procedure codes"""
        treatment_codes = []

        code_mappings = {
            'examination': 'D0150',
            'cleaning': 'D1110',
            'filling': 'D2140',
            'root canal': 'D3310',
            'crown': 'D2740',
            'extraction': 'D7140'
        }

        for treatment, code in code_mappings.items():
            if treatment in notes:
                treatment_codes.append(code)

        return treatment_codes

    def _extract_pain_indicators(self, notes: str) -> Dict[str, Any]:
        """Extract pain and discomfort indicators"""
        pain_keywords = ['pain', 'ache', 'sensitive', 'tender', 'discomfort', 'swelling']
        severity_keywords = ['mild', 'moderate', 'severe', 'extreme']

        pain_info = {
            'has_pain': any(keyword in notes for keyword in pain_keywords),
            'pain_keywords': [kw for kw in pain_keywords if kw in notes],
            'severity': next((sev for sev in severity_keywords if sev in notes), 'unknown')
        }

        return pain_info

    def _extract_urgency_flags(self, notes: str) -> List[str]:
        """Extract urgency indicators from notes"""
        urgency_keywords = ['emergency', 'urgent', 'immediate', 'asap', 'severe', 'infection']
        return [keyword for keyword in urgency_keywords if keyword in notes]

    def _check_drug_interactions(self, new_prescriptions: List[str],
                                current_medications: List[str]) -> List[Dict[str, Any]]:
        """Check for drug interactions"""

        # Simplified drug interaction checking
        # In production, integrate with pharmaceutical databases
        interactions = []

        interaction_matrix = {
            'amoxicillin': ['warfarin', 'methotrexate'],
            'ibuprofen': ['warfarin', 'lisinopril', 'methotrexate'],
            'acetaminophen': ['warfarin'],
            'codeine': ['tramadol', 'morphine']
        }

        for new_drug in new_prescriptions:
            new_drug_lower = new_drug.lower()
            for current_drug in current_medications:
                current_drug_lower = current_drug.lower()

                # Check if interaction exists
                if (new_drug_lower in interaction_matrix and
                    current_drug_lower in interaction_matrix[new_drug_lower]):

                    interactions.append({
                        'drug1': new_drug,
                        'drug2': current_drug,
                        'severity': 'moderate',
                        'description': f'Potential interaction between {new_drug} and {current_drug}',
                        'recommendation': 'Monitor patient closely'
                    })

        return interactions

    def manage_images(self, patient_id: str, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage X-rays and clinical images"""

        if patient_id not in self.records_database:
            return {'success': False, 'error': 'Patient not found'}

        image_record = {
            'image_id': f"IMG_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'image_type': image_data.get('type', 'x_ray'),
            'description': image_data.get('description'),
            'date_taken': image_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'dentist': image_data.get('dentist'),
            'file_path': image_data.get('file_path'),
            'file_size': image_data.get('file_size'),
            'image_quality': image_data.get('quality', 'good'),
            'findings': image_data.get('findings', []),
            'ai_analysis': self._analyze_image_ai(image_data),
            'created_at': datetime.now().isoformat()
        }

        # Add image to patient record
        if 'images' not in self.records_database[patient_id]:
            self.records_database[patient_id]['images'] = []

        self.records_database[patient_id]['images'].append(image_record)

        # Create audit entry
        self._create_audit_entry('ADD_IMAGE', patient_id, f"Image {image_record['image_id']} added")

        return {'success': True, 'image_id': image_record['image_id'], 'ai_analysis': image_record['ai_analysis']}

    def _analyze_image_ai(self, image_data: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered image analysis for diagnostic assistance"""

        # Simulated AI analysis
        # In production, integrate with medical imaging AI services
        analysis = {
            'caries_detected': False,
            'bone_loss': 'minimal',
            'root_canal_quality': 'good',
            'crown_fit': 'acceptable',
            'recommendations': [],
            'confidence_score': 0.85,
            'requires_human_review': False
        }

        image_type = image_data.get('type', 'x_ray')

        if image_type == 'bitewing':
            analysis['caries_detected'] = True
            analysis['recommendations'].append('Consider restorative treatment')
        elif image_type == 'panoramic':
            analysis['bone_loss'] = 'moderate'
            analysis['recommendations'].append('Periodontal evaluation recommended')

        return analysis

    def generate_referral_letter(self, patient_id: str, referral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate referral letter to specialists"""

        if patient_id not in self.records_database:
            return {'success': False, 'error': 'Patient not found'}

        patient_record = self.records_database[patient_id]

        referral_letter = {
            'letter_id': f"REF_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'referring_dentist': referral_data.get('referring_dentist'),
            'specialist_type': referral_data.get('specialist_type'),
            'specialist_name': referral_data.get('specialist_name'),
            'reason_for_referral': referral_data.get('reason'),
            'urgency': referral_data.get('urgency', 'routine'),
            'patient_summary': self._generate_patient_summary(patient_record),
            'relevant_history': self._extract_relevant_history(patient_record, referral_data.get('specialist_type')),
            'current_treatment': referral_data.get('current_treatment'),
            'expected_treatment': referral_data.get('expected_treatment'),
            'return_to_gdp': referral_data.get('return_to_gdp', True),
            'created_at': datetime.now().isoformat()
        }

        # Store referral in patient record
        if 'referrals' not in patient_record:
            patient_record['referrals'] = []

        patient_record['referrals'].append(referral_letter)

        # Create audit entry
        self._create_audit_entry('CREATE_REFERRAL', patient_id, f"Referral {referral_letter['letter_id']} created")

        return {'success': True, 'referral_letter': referral_letter}

    def _generate_patient_summary(self, patient_record: Dict[str, Any]) -> str:
        """Generate patient summary for referral"""

        summary_parts = []

        # Demographics (anonymized)
        summary_parts.append(f"Patient: {patient_record['patient_id']}")

        # Medical history
        medical_history = patient_record.get('medical_history', {})
        if medical_history.get('allergies'):
            summary_parts.append(f"Allergies: {', '.join(medical_history['allergies'])}")

        if medical_history.get('medical_conditions'):
            summary_parts.append(f"Medical conditions: {', '.join(medical_history['medical_conditions'])}")

        # Recent visits
        visits = patient_record.get('visits', [])
        if visits:
            last_visit = visits[-1]
            summary_parts.append(f"Last visit: {last_visit['date']} - {last_visit['treatment_type']}")

        return '. '.join(summary_parts)

    def _extract_relevant_history(self, patient_record: Dict[str, Any], specialist_type: str) -> str:
        """Extract history relevant to specialist type"""

        relevant_history = []

        visits = patient_record.get('visits', [])

        # Filter visits based on specialist type
        if specialist_type == 'periodontist':
            relevant_visits = [v for v in visits if 'gum' in v.get('treatment_type', '').lower() or
                             'periodontal' in v.get('treatment_type', '').lower()]
        elif specialist_type == 'endodontist':
            relevant_visits = [v for v in visits if 'root canal' in v.get('treatment_type', '').lower() or
                             'endodontic' in v.get('treatment_type', '').lower()]
        elif specialist_type == 'oral_surgeon':
            relevant_visits = [v for v in visits if 'extraction' in v.get('treatment_type', '').lower() or
                             'surgery' in v.get('treatment_type', '').lower()]
        else:
            relevant_visits = visits[-3:]  # Last 3 visits for other specialists

        for visit in relevant_visits:
            relevant_history.append(f"{visit['date']}: {visit['treatment_type']} - {visit.get('diagnosis', 'N/A')}")

        return '. '.join(relevant_history) if relevant_history else 'No relevant history found'

    def _create_audit_entry(self, action: str, patient_id: str, description: str) -> None:
        """Create GDPR-compliant audit trail entry"""

        audit_entry = {
            'audit_id': f"AUD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}",
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'patient_id': patient_id,
            'description': description,
            'user_id': 'system',  # In production, use actual user ID
            'ip_address': '127.0.0.1',  # In production, capture actual IP
            'user_agent': 'Clinical Records Assistant'
        }

        self.audit_log.append(audit_entry)

    def get_audit_trail(self, patient_id: Optional[str] = None,
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve audit trail for GDPR compliance"""

        filtered_log = self.audit_log

        if patient_id:
            filtered_log = [entry for entry in filtered_log if entry['patient_id'] == patient_id]

        if start_date:
            filtered_log = [entry for entry in filtered_log if entry['timestamp'] >= start_date]

        if end_date:
            filtered_log = [entry for entry in filtered_log if entry['timestamp'] <= end_date]

        return filtered_log

    def anonymize_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Anonymize patient data per GDPR requirements"""

        if patient_id not in self.records_database:
            return {'success': False, 'error': 'Patient not found'}

        # Anonymize personal information
        patient_record = self.records_database[patient_id]
        patient_record['personal_info'] = {
            'name': f'ANONYMIZED_{uuid.uuid4().hex[:8]}',
            'date_of_birth': 'ANONYMIZED',
            'address': 'ANONYMIZED',
            'phone': 'ANONYMIZED',
            'email': 'ANONYMIZED'
        }

        patient_record['anonymized_at'] = datetime.now().isoformat()
        patient_record['gdpr_compliance']['anonymized'] = True

        # Create audit entry
        self._create_audit_entry('ANONYMIZE_DATA', patient_id, 'Patient data anonymized per GDPR')

        return {'success': True, 'message': 'Patient data anonymized successfully'}

def create_clinical_records_agent(llm: ChatOpenAI, practice_config: Dict[str, Any]) -> AgentExecutor:
    """Create the clinical records assistant agent with tools"""

    assistant = ClinicalRecordsAssistant(llm, practice_config)

    tools = [
        Tool(
            name="create_patient_record",
            description="Create new GDPR-compliant patient record",
            func=lambda query: assistant.create_patient_record(json.loads(query))
        ),
        Tool(
            name="update_clinical_notes",
            description="Update clinical notes with voice-to-text processing",
            func=lambda query: assistant.update_clinical_notes(**json.loads(query))
        ),
        Tool(
            name="manage_images",
            description="Manage X-rays and clinical images with AI analysis",
            func=lambda query: assistant.manage_images(**json.loads(query))
        ),
        Tool(
            name="generate_referral_letter",
            description="Generate specialist referral letter",
            func=lambda query: assistant.generate_referral_letter(**json.loads(query))
        ),
        Tool(
            name="get_audit_trail",
            description="Retrieve GDPR-compliant audit trail",
            func=lambda query: assistant.get_audit_trail(**json.loads(query))
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI clinical records assistant for a dental practice.
        You manage patient records with strict GDPR compliance, process clinical notes,
        manage medical images, and maintain comprehensive audit trails.

        GDPR Compliance Requirements:
        - All patient data must be encrypted
        - Consent must be obtained for data processing
        - Audit trails required for all actions
        - Data retention policies enforced
        - Right to be forgotten implemented

        Practice Configuration:
        - Retention Policies: {retention_policies}
        - Encryption: AES-256 required
        - Audit Trail: Comprehensive logging

        Be thorough, accurate, and maintain strict confidentiality."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)