"""
Patient Communication Platform Agent
Personalized patient engagement and education
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import json
import uuid

class PatientCommunicationPlatform:
    """AI-powered patient communication and engagement"""

    def __init__(self, llm: ChatOpenAI, practice_config: Dict[str, Any]):
        self.llm = llm
        self.practice_config = practice_config
        self.communication_log = {}
        self.patient_preferences = {}
        self.educational_content = self._initialize_educational_content()
        self.questionnaire_templates = self._initialize_questionnaires()
        self.communication_templates = self._initialize_communication_templates()

    def _initialize_educational_content(self) -> Dict[str, Any]:
        """Initialize oral health educational content library"""
        return {
            'general_oral_health': {
                'title': 'Maintaining Good Oral Health',
                'content': 'Daily brushing with fluoride toothpaste, regular flossing, and routine dental checkups are essential...',
                'target_conditions': ['general', 'prevention'],
                'age_groups': ['all'],
                'reading_level': 'elementary'
            },
            'gum_disease_prevention': {
                'title': 'Preventing Gum Disease',
                'content': 'Gum disease begins with plaque buildup along the gum line. Regular cleaning and proper technique...',
                'target_conditions': ['gingivitis', 'periodontitis'],
                'age_groups': ['adult', 'senior'],
                'reading_level': 'intermediate'
            },
            'cavity_prevention': {
                'title': 'Cavity Prevention Tips',
                'content': 'Cavities form when bacteria in your mouth produce acids that attack tooth enamel...',
                'target_conditions': ['caries', 'decay'],
                'age_groups': ['children', 'adult'],
                'reading_level': 'elementary'
            },
            'post_extraction_care': {
                'title': 'After Tooth Extraction Care',
                'content': 'Following tooth extraction, proper care prevents complications and promotes healing...',
                'target_conditions': ['post_extraction'],
                'age_groups': ['all'],
                'reading_level': 'intermediate'
            },
            'root_canal_aftercare': {
                'title': 'Root Canal Recovery',
                'content': 'After root canal treatment, some discomfort is normal. Follow these guidelines...',
                'target_conditions': ['post_endodontic'],
                'age_groups': ['adult'],
                'reading_level': 'intermediate'
            },
            'crown_maintenance': {
                'title': 'Caring for Your Dental Crown',
                'content': 'Dental crowns can last many years with proper care. Avoid hard foods and maintain good hygiene...',
                'target_conditions': ['crown', 'restoration'],
                'age_groups': ['adult', 'senior'],
                'reading_level': 'intermediate'
            },
            'children_dental_care': {
                'title': 'Children\'s Dental Health',
                'content': 'Starting dental care early sets the foundation for lifelong oral health...',
                'target_conditions': ['pediatric'],
                'age_groups': ['children'],
                'reading_level': 'elementary'
            },
            'orthodontic_care': {
                'title': 'Caring for Braces',
                'content': 'Orthodontic treatment requires special attention to oral hygiene...',
                'target_conditions': ['orthodontic'],
                'age_groups': ['children', 'teen', 'adult'],
                'reading_level': 'intermediate'
            }
        }

    def _initialize_questionnaires(self) -> Dict[str, Any]:
        """Initialize adaptive health questionnaire templates"""
        return {
            'new_patient': {
                'title': 'New Patient Health Questionnaire',
                'sections': [
                    {
                        'name': 'personal_info',
                        'questions': [
                            {'id': 'emergency_contact', 'type': 'text', 'required': True},
                            {'id': 'insurance_provider', 'type': 'select', 'options': ['VHI', 'Laya', 'Irish Life Health', 'PRSI', 'None']},
                            {'id': 'preferred_contact', 'type': 'select', 'options': ['phone', 'email', 'sms']}
                        ]
                    },
                    {
                        'name': 'medical_history',
                        'questions': [
                            {'id': 'allergies', 'type': 'text', 'required': True},
                            {'id': 'medications', 'type': 'text', 'required': True},
                            {'id': 'medical_conditions', 'type': 'checklist', 'options': ['diabetes', 'heart_disease', 'high_blood_pressure', 'anxiety']},
                            {'id': 'pregnancy', 'type': 'boolean', 'conditional': 'gender=female'}
                        ]
                    },
                    {
                        'name': 'dental_history',
                        'questions': [
                            {'id': 'last_visit', 'type': 'date'},
                            {'id': 'dental_anxiety', 'type': 'scale', 'min': 1, 'max': 10},
                            {'id': 'current_concerns', 'type': 'text'},
                            {'id': 'oral_hygiene_frequency', 'type': 'select', 'options': ['twice_daily', 'once_daily', 'occasionally', 'rarely']}
                        ]
                    }
                ]
            },
            'pre_treatment': {
                'title': 'Pre-Treatment Assessment',
                'sections': [
                    {
                        'name': 'current_health',
                        'questions': [
                            {'id': 'medication_changes', 'type': 'boolean'},
                            {'id': 'health_changes', 'type': 'boolean'},
                            {'id': 'pain_level', 'type': 'scale', 'min': 0, 'max': 10},
                            {'id': 'last_meal', 'type': 'datetime'},
                            {'id': 'anxiety_level', 'type': 'scale', 'min': 1, 'max': 10}
                        ]
                    }
                ]
            },
            'post_treatment': {
                'title': 'Post-Treatment Follow-up',
                'sections': [
                    {
                        'name': 'recovery_assessment',
                        'questions': [
                            {'id': 'pain_level', 'type': 'scale', 'min': 0, 'max': 10},
                            {'id': 'swelling', 'type': 'boolean'},
                            {'id': 'bleeding', 'type': 'boolean'},
                            {'id': 'medication_compliance', 'type': 'boolean'},
                            {'id': 'satisfaction', 'type': 'scale', 'min': 1, 'max': 10},
                            {'id': 'additional_concerns', 'type': 'text'}
                        ]
                    }
                ]
            }
        }

    def _initialize_communication_templates(self) -> Dict[str, Any]:
        """Initialize communication message templates"""
        return {
            'appointment_confirmation': {
                'subject': 'Appointment Confirmation - {practice_name}',
                'template': """Dear {patient_name},

This confirms your appointment:
📅 Date: {appointment_date}
🕐 Time: {appointment_time}
👨‍⚕️ Dentist: {dentist_name}
🦷 Treatment: {treatment_type}

Preparation instructions:
{preparation_instructions}

Location: {practice_address}
Phone: {practice_phone}

Please arrive 15 minutes early.

Best regards,
{practice_name} Team"""
            },
            'appointment_reminder': {
                'subject': 'Appointment Reminder - Tomorrow at {appointment_time}',
                'template': """Hi {patient_name},

Friendly reminder of your appointment tomorrow:
📅 {appointment_date} at {appointment_time}
👨‍⚕️ With {dentist_name}
🦷 For {treatment_type}

{reminder_instructions}

Need to reschedule? Call us at {practice_phone}

See you tomorrow!
{practice_name}"""
            },
            'post_treatment_followup': {
                'subject': 'How are you feeling? - Follow-up from {practice_name}',
                'template': """Hello {patient_name},

I hope you're recovering well from your {treatment_type} yesterday.

{personalized_care_instructions}

Please monitor for:
{warning_signs}

Questions or concerns? Call us at {practice_phone}

Your next appointment: {next_appointment}

Take care,
{dentist_name}"""
            },
            'recall_reminder': {
                'subject': 'Time for Your Checkup! - {practice_name}',
                'template': """Dear {patient_name},

It's been 6 months since your last visit - time for your routine checkup!

Regular checkups help:
✓ Prevent serious problems
✓ Catch issues early
✓ Keep your smile healthy

Book online: {booking_link}
Or call: {practice_phone}

We look forward to seeing you soon!

{practice_name} Team"""
            },
            'educational_newsletter': {
                'subject': '{month} Dental Health Tips from {practice_name}',
                'template': """Hello {patient_name},

This month's focus: {topic}

{educational_content}

{seasonal_tips}

Practice News:
{practice_updates}

Questions? We're here to help!
{practice_phone} | {practice_email}

Healthy smiles,
{practice_name}"""
            }
        }

    def send_appointment_confirmation(self, confirmation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send intelligent appointment confirmation"""

        patient_id = confirmation_data['patient_id']
        appointment_data = confirmation_data['appointment']

        # Get patient preferences
        preferences = self.patient_preferences.get(patient_id, {})
        preferred_method = preferences.get('communication_method', 'email')
        preferred_time = preferences.get('contact_time', 'afternoon')

        # Generate preparation instructions based on treatment
        preparation_instructions = self._generate_preparation_instructions(
            appointment_data['treatment_type']
        )

        # Personalize message
        message_content = self._personalize_message(
            'appointment_confirmation',
            patient_id,
            {
                **appointment_data,
                'preparation_instructions': preparation_instructions,
                'practice_name': self.practice_config.get('name', 'Dental Practice'),
                'practice_address': self.practice_config.get('address', ''),
                'practice_phone': self.practice_config.get('phone', '')
            }
        )

        communication_record = {
            'communication_id': f"COM_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'type': 'appointment_confirmation',
            'method': preferred_method,
            'content': message_content,
            'sent_at': datetime.now().isoformat(),
            'delivery_status': 'sent',
            'opened': False,
            'clicked': False
        }

        # Store communication
        if patient_id not in self.communication_log:
            self.communication_log[patient_id] = []
        self.communication_log[patient_id].append(communication_record)

        return {
            'success': True,
            'communication_id': communication_record['communication_id'],
            'method': preferred_method,
            'estimated_delivery': 'immediate'
        }

    def _generate_preparation_instructions(self, treatment_type: str) -> str:
        """Generate treatment-specific preparation instructions"""

        instructions = {
            'cleaning': "Please brush and floss before your appointment. Avoid eating for 30 minutes beforehand.",
            'filling': "You may eat normally before your appointment. We'll use local anesthetic if needed.",
            'root_canal': "Take any prescribed antibiotics as directed. Avoid hard foods on the affected side.",
            'extraction': "Do not eat or drink for 2 hours before surgery. Arrange transport home.",
            'crown': "Avoid sticky foods on temporary crown. Gentle brushing around the area.",
            'checkup': "Normal eating and drinking. Bring any medications you're currently taking.",
            'emergency': "Come in immediately. If severe pain, take over-the-counter pain relief as directed."
        }

        return instructions.get(treatment_type, "Please arrive 15 minutes early and bring a list of current medications.")

    def _personalize_message(self, template_type: str, patient_id: str,
                           variables: Dict[str, Any]) -> Dict[str, str]:
        """Personalize message content based on patient profile"""

        template = self.communication_templates[template_type]

        # Get patient-specific data
        patient_data = self.patient_preferences.get(patient_id, {})

        # Merge variables with patient data
        all_variables = {
            **variables,
            'patient_name': patient_data.get('name', 'Valued Patient'),
            **self.practice_config
        }

        # Format subject and content
        subject = template['subject'].format(**all_variables)
        content = template['template'].format(**all_variables)

        return {
            'subject': subject,
            'content': content,
            'personalization_score': self._calculate_personalization_score(patient_id, template_type)
        }

    def _calculate_personalization_score(self, patient_id: str, template_type: str) -> float:
        """Calculate personalization effectiveness score"""

        preferences = self.patient_preferences.get(patient_id, {})
        score = 0.5  # Base score

        # Increase score based on available personalization data
        if preferences.get('name'):
            score += 0.1
        if preferences.get('communication_method'):
            score += 0.1
        if preferences.get('treatment_history'):
            score += 0.1
        if preferences.get('language_preference'):
            score += 0.1
        if preferences.get('contact_time'):
            score += 0.1

        return min(1.0, score)

    def create_adaptive_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create adaptive health questionnaire based on patient profile"""

        patient_id = questionnaire_data['patient_id']
        questionnaire_type = questionnaire_data['type']

        if questionnaire_type not in self.questionnaire_templates:
            return {'success': False, 'error': 'Unknown questionnaire type'}

        base_template = self.questionnaire_templates[questionnaire_type]

        # Adapt questionnaire based on patient history
        adapted_questionnaire = self._adapt_questionnaire(patient_id, base_template)

        questionnaire_record = {
            'questionnaire_id': f"QUE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'type': questionnaire_type,
            'questions': adapted_questionnaire['questions'],
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'responses': {},
            'completion_percentage': 0,
            'estimated_time': adapted_questionnaire['estimated_time']
        }

        return {
            'success': True,
            'questionnaire': questionnaire_record,
            'delivery_method': 'patient_portal'  # or email/sms link
        }

    def _adapt_questionnaire(self, patient_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt questionnaire questions based on patient profile"""

        patient_data = self.patient_preferences.get(patient_id, {})
        treatment_history = patient_data.get('treatment_history', [])

        adapted_questions = []
        estimated_time = 5  # Base time in minutes

        for section in template['sections']:
            for question in section['questions']:
                # Check if question should be included based on conditions
                include_question = True

                if 'conditional' in question:
                    condition = question['conditional']
                    include_question = self._evaluate_condition(condition, patient_data)

                if include_question:
                    # Adapt question based on patient history
                    adapted_question = self._adapt_question(question, treatment_history)
                    adapted_questions.append(adapted_question)
                    estimated_time += 0.5  # Add time per question

        return {
            'questions': adapted_questions,
            'estimated_time': int(estimated_time)
        }

    def _evaluate_condition(self, condition: str, patient_data: Dict[str, Any]) -> bool:
        """Evaluate conditional logic for questionnaire questions"""

        # Simple condition evaluation (expand as needed)
        if '=' in condition:
            field, value = condition.split('=')
            return patient_data.get(field) == value

        return True

    def _adapt_question(self, question: Dict[str, Any], treatment_history: List[str]) -> Dict[str, Any]:
        """Adapt individual question based on treatment history"""

        adapted_question = question.copy()

        # Add follow-up questions based on treatment history
        if question['id'] == 'medications' and 'antibiotic' in treatment_history:
            adapted_question['follow_up'] = {
                'id': 'antibiotic_allergies',
                'type': 'boolean',
                'text': 'Have you experienced any antibiotic allergies?'
            }

        return adapted_question

    def send_educational_content(self, education_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send personalized oral health education"""

        patient_id = education_data['patient_id']
        patient_data = self.patient_preferences.get(patient_id, {})

        # Determine relevant educational content
        relevant_content = self._select_educational_content(
            patient_data.get('conditions', []),
            patient_data.get('age_group', 'adult'),
            patient_data.get('reading_level', 'intermediate')
        )

        # Personalize content
        personalized_content = self._personalize_educational_content(
            relevant_content, patient_data
        )

        education_record = {
            'education_id': f"EDU_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'patient_id': patient_id,
            'content_type': relevant_content['title'],
            'personalized_content': personalized_content,
            'delivery_method': patient_data.get('communication_method', 'email'),
            'sent_at': datetime.now().isoformat(),
            'engagement_tracking': True
        }

        return {
            'success': True,
            'education_record': education_record,
            'content_relevance_score': self._calculate_content_relevance(relevant_content, patient_data)
        }

    def _select_educational_content(self, conditions: List[str], age_group: str,
                                  reading_level: str) -> Dict[str, Any]:
        """Select most relevant educational content"""

        best_match = None
        best_score = 0

        for content_id, content in self.educational_content.items():
            score = 0

            # Score based on conditions
            for condition in conditions:
                if condition in content['target_conditions']:
                    score += 3

            # Score based on age group
            if age_group in content['age_groups'] or 'all' in content['age_groups']:
                score += 2

            # Score based on reading level
            if content['reading_level'] == reading_level:
                score += 1

            if score > best_score:
                best_score = score
                best_match = content

        return best_match or self.educational_content['general_oral_health']

    def _personalize_educational_content(self, content: Dict[str, Any],
                                       patient_data: Dict[str, Any]) -> str:
        """Personalize educational content for patient"""

        personalized_content = content['content']

        # Add patient-specific information
        patient_name = patient_data.get('name', 'there')
        personalized_content = f"Hi {patient_name}! " + personalized_content

        # Add relevant tips based on patient profile
        if 'diabetes' in patient_data.get('conditions', []):
            personalized_content += "\n\nSpecial note for diabetes management: Monitor your blood sugar levels closely, as dental infections can affect glucose control."

        if patient_data.get('age_group') == 'senior':
            personalized_content += "\n\nFor seniors: Pay special attention to dry mouth, which can increase cavity risk. Stay hydrated and discuss medications with your dentist."

        return personalized_content

    def _calculate_content_relevance(self, content: Dict[str, Any],
                                   patient_data: Dict[str, Any]) -> float:
        """Calculate content relevance score"""

        relevance_score = 0.5  # Base relevance

        # Increase score for condition matches
        patient_conditions = patient_data.get('conditions', [])
        matching_conditions = [c for c in patient_conditions if c in content['target_conditions']]
        relevance_score += len(matching_conditions) * 0.15

        # Age group relevance
        if patient_data.get('age_group', 'adult') in content['age_groups'] or 'all' in content['age_groups']:
            relevance_score += 0.1

        # Reading level match
        if content['reading_level'] == patient_data.get('reading_level', 'intermediate'):
            relevance_score += 0.1

        return min(1.0, relevance_score)

    def track_engagement_analytics(self, patient_id: Optional[str] = None) -> Dict[str, Any]:
        """Track patient communication engagement analytics"""

        analytics = {
            'total_communications': 0,
            'engagement_rate': 0,
            'preferred_methods': {},
            'response_rates': {},
            'patient_analytics': []
        }

        patients_to_analyze = [patient_id] if patient_id else list(self.communication_log.keys())

        for pid in patients_to_analyze:
            if pid in self.communication_log:
                patient_communications = self.communication_log[pid]
                patient_stats = self._calculate_patient_engagement(patient_communications)

                analytics['patient_analytics'].append({
                    'patient_id': pid,
                    **patient_stats
                })

                analytics['total_communications'] += len(patient_communications)

                # Aggregate method preferences
                for comm in patient_communications:
                    method = comm['method']
                    analytics['preferred_methods'][method] = analytics['preferred_methods'].get(method, 0) + 1

        # Calculate overall engagement rate
        if analytics['total_communications'] > 0:
            total_engaged = sum(p['engagement_score'] for p in analytics['patient_analytics'])
            analytics['engagement_rate'] = total_engaged / len(analytics['patient_analytics'])

        return analytics

    def _calculate_patient_engagement(self, communications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate engagement metrics for individual patient"""

        total_sent = len(communications)
        opened = sum(1 for c in communications if c.get('opened', False))
        clicked = sum(1 for c in communications if c.get('clicked', False))
        responded = sum(1 for c in communications if c.get('response_received', False))

        engagement_score = 0
        if total_sent > 0:
            engagement_score = (opened * 0.3 + clicked * 0.4 + responded * 0.3) / total_sent

        return {
            'total_communications': total_sent,
            'open_rate': opened / total_sent if total_sent > 0 else 0,
            'click_rate': clicked / total_sent if total_sent > 0 else 0,
            'response_rate': responded / total_sent if total_sent > 0 else 0,
            'engagement_score': engagement_score,
            'last_communication': communications[-1]['sent_at'] if communications else None
        }

def create_patient_communication_agent(llm: ChatOpenAI, practice_config: Dict[str, Any]) -> AgentExecutor:
    """Create the patient communication platform agent with tools"""

    platform = PatientCommunicationPlatform(llm, practice_config)

    tools = [
        Tool(
            name="send_appointment_confirmation",
            description="Send intelligent appointment confirmation with preparation instructions",
            func=lambda query: platform.send_appointment_confirmation(json.loads(query))
        ),
        Tool(
            name="create_adaptive_questionnaire",
            description="Create adaptive health questionnaire based on patient profile",
            func=lambda query: platform.create_adaptive_questionnaire(json.loads(query))
        ),
        Tool(
            name="send_educational_content",
            description="Send personalized oral health education content",
            func=lambda query: platform.send_educational_content(json.loads(query))
        ),
        Tool(
            name="track_engagement_analytics",
            description="Track patient communication engagement and analytics",
            func=lambda query: platform.track_engagement_analytics(**json.loads(query) if query.strip() else {})
        )
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an AI patient communication specialist for a dental practice.
        You manage all patient communications including confirmations, reminders,
        educational content, and engagement tracking. Always personalize
        communications based on patient preferences and treatment history.

        Practice Configuration:
        - Communication Methods: {communication_methods}
        - Languages Supported: {languages}
        - Educational Content: Comprehensive library
        - Engagement Tracking: Advanced analytics

        Be personable, informative, and considerate of patient preferences."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}")
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True)