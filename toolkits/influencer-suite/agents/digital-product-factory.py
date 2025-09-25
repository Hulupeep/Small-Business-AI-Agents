"""
Digital Product Factory - AI Agent
Automated course creation and student success management
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import openai
import requests
from pathlib import Path
import zipfile
import io

class ProductType(Enum):
    COURSE = "course"
    TEMPLATE = "template"
    RESOURCE_PACK = "resource_pack"
    CERTIFICATION = "certification"
    COMMUNITY = "community"

class ProductStatus(Enum):
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    PUBLISHED = "published"
    ARCHIVED = "archived"

@dataclass
class Course:
    id: str
    title: str
    description: str
    price: float
    modules: List[Dict]
    resources: List[Dict]
    status: ProductStatus
    target_audience: str
    learning_objectives: List[str]
    estimated_completion_time: str
    difficulty_level: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Student:
    id: str
    email: str
    name: str
    enrolled_courses: List[str]
    progress: Dict[str, float]  # course_id -> completion percentage
    last_activity: datetime
    engagement_score: float
    preferred_learning_style: str
    notes: str

@dataclass
class Template:
    id: str
    name: str
    category: str
    description: str
    file_type: str
    use_cases: List[str]
    customization_options: Dict
    preview_url: str
    download_count: int

class DigitalProductFactory:
    def __init__(self, config: Dict):
        self.config = config
        self.openai_client = openai.OpenAI(api_key=config['openai_api_key'])
        self.db_path = config.get('database_path', 'product_factory.db')
        self.content_storage_path = config.get('content_storage_path', './product_content/')

        # Initialize database
        self._init_database()

        # Course templates and structures
        self.course_structures = {
            'ai_productivity': {
                'modules': [
                    'Introduction to AI Productivity',
                    'Essential AI Tools Overview',
                    'Workflow Automation Setup',
                    'Content Creation with AI',
                    'Advanced Integrations',
                    'Scaling Your System'
                ],
                'estimated_hours': 8,
                'difficulty': 'intermediate'
            },
            'content_automation': {
                'modules': [
                    'Content Strategy Foundations',
                    'AI Writing Tools Mastery',
                    'Visual Content Automation',
                    'Distribution Automation',
                    'Performance Analytics',
                    'Scaling Content Operations'
                ],
                'estimated_hours': 6,
                'difficulty': 'beginner'
            },
            'lead_generation': {
                'modules': [
                    'Lead Generation Strategy',
                    'LinkedIn Automation Setup',
                    'Email Sequence Design',
                    'Funnel Optimization',
                    'Conversion Tracking',
                    'Scale and Optimize'
                ],
                'estimated_hours': 10,
                'difficulty': 'advanced'
            }
        }

        # Template categories
        self.template_categories = {
            'social_media': [
                'LinkedIn post templates',
                'Twitter thread frameworks',
                'Instagram story templates',
                'Video script outlines'
            ],
            'email_marketing': [
                'Welcome sequence templates',
                'Sales email frameworks',
                'Newsletter templates',
                'Nurture sequence flows'
            ],
            'productivity': [
                'Daily planning templates',
                'Project management frameworks',
                'Goal tracking sheets',
                'Habit tracker templates'
            ],
            'business': [
                'SOP templates',
                'Client onboarding flows',
                'Pricing calculators',
                'Proposal templates'
            ]
        }

    def _init_database(self):
        """Initialize database for product management"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Courses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price REAL,
                modules TEXT,
                resources TEXT,
                status TEXT,
                target_audience TEXT,
                learning_objectives TEXT,
                estimated_completion_time TEXT,
                difficulty_level TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')

        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT,
                enrolled_courses TEXT,
                progress TEXT,
                last_activity TIMESTAMP,
                engagement_score REAL DEFAULT 0.0,
                preferred_learning_style TEXT,
                notes TEXT
            )
        ''')

        # Templates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                file_type TEXT,
                use_cases TEXT,
                customization_options TEXT,
                preview_url TEXT,
                download_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Student progress tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_id TEXT,
                module_id TEXT,
                completion_percentage REAL,
                time_spent INTEGER,
                last_accessed TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        # Assessments and completion
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT,
                course_id TEXT,
                assessment_type TEXT,
                score REAL,
                completed_at TIMESTAMP,
                certificate_issued BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (student_id) REFERENCES students (id)
            )
        ''')

        conn.commit()
        conn.close()

    def generate_course_outline(self, topic: str, target_audience: str, course_length: str = "8 hours") -> Dict:
        """Generate comprehensive course outline using AI"""

        outline_prompt = f"""
        Create a comprehensive course outline for:

        Topic: {topic}
        Target Audience: {target_audience}
        Course Length: {course_length}

        Generate a course structure with:
        1. Course title and compelling subtitle
        2. Course description (2-3 paragraphs)
        3. Learning objectives (5-7 specific outcomes)
        4. 6-8 modules with:
           - Module title
           - Module description
           - Key lessons (3-5 per module)
           - Practical exercises
           - Time estimate
        5. Resource requirements
        6. Prerequisites
        7. Certification criteria
        8. Bonus materials suggestions

        Focus on AI/productivity niche with actionable, implementable content.
        Include hands-on exercises and real-world applications.

        Return as detailed JSON structure.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": outline_prompt}],
            temperature=0.7
        )

        try:
            outline = json.loads(response.choices[0].message.content)
        except:
            # Fallback outline
            outline = {
                "title": f"Mastering {topic}",
                "subtitle": f"Complete Guide for {target_audience}",
                "description": f"Comprehensive course on {topic} designed specifically for {target_audience}",
                "modules": [
                    {"title": "Introduction", "lessons": ["Overview", "Setup", "Foundations"]},
                    {"title": "Core Concepts", "lessons": ["Theory", "Practice", "Implementation"]},
                    {"title": "Advanced Techniques", "lessons": ["Optimization", "Scaling", "Integration"]},
                    {"title": "Real-World Applications", "lessons": ["Case Studies", "Projects", "Next Steps"]}
                ]
            }

        return outline

    def create_course_content(self, course_id: str, outline: Dict) -> Dict:
        """Generate detailed course content for each module"""

        course_content = {
            'course_id': course_id,
            'modules': [],
            'resources': [],
            'assessments': []
        }

        for i, module in enumerate(outline.get('modules', [])):
            module_content = self._generate_module_content(
                module_title=module['title'],
                module_description=module.get('description', ''),
                lessons=module.get('lessons', []),
                course_topic=outline.get('title', ''),
                module_number=i + 1
            )

            course_content['modules'].append(module_content)

            # Generate assessments for each module
            assessment = self._generate_module_assessment(module['title'], module_content)
            course_content['assessments'].append(assessment)

        # Generate course resources
        course_content['resources'] = self._generate_course_resources(outline)

        return course_content

    def _generate_module_content(self, module_title: str, module_description: str,
                                lessons: List[str], course_topic: str, module_number: int) -> Dict:
        """Generate detailed content for a single module"""

        content_prompt = f"""
        Create detailed content for Module {module_number}: {module_title}

        Course Topic: {course_topic}
        Module Description: {module_description}
        Lessons: {lessons}

        For each lesson, provide:
        1. Lesson objectives (2-3 specific goals)
        2. Lesson content (500-800 words, actionable and practical)
        3. Key takeaways (3-5 bullet points)
        4. Practical exercise or worksheet
        5. Additional resources (tools, links, readings)
        6. Video script outline (if applicable)

        Target audience: AI/productivity professionals
        Tone: Expert but accessible, actionable, results-focused

        Include specific examples, tools, and step-by-step instructions.
        Make content immediately implementable.

        Return as structured JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": content_prompt}],
            temperature=0.7,
            max_tokens=3000
        )

        try:
            module_content = json.loads(response.choices[0].message.content)
        except:
            # Fallback content structure
            module_content = {
                "title": module_title,
                "lessons": [
                    {
                        "title": lesson,
                        "content": f"Detailed content for {lesson}",
                        "exercise": f"Practical exercise for {lesson}",
                        "resources": ["Tool recommendation", "Additional reading"]
                    }
                    for lesson in lessons
                ]
            }

        return module_content

    def _generate_module_assessment(self, module_title: str, module_content: Dict) -> Dict:
        """Generate assessment for module"""

        assessment_prompt = f"""
        Create an assessment for Module: {module_title}

        Module Content Summary: {json.dumps(module_content, indent=2)[:1000]}...

        Create:
        1. 5 multiple choice questions (with 4 options each)
        2. 3 practical scenario questions
        3. 1 implementation project
        4. Grading criteria
        5. Pass/fail thresholds

        Focus on practical application and real-world scenarios.
        Questions should test understanding, not memorization.

        Return as JSON with questions, answers, and grading rubric.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": assessment_prompt}],
            temperature=0.6
        )

        try:
            assessment = json.loads(response.choices[0].message.content)
        except:
            # Fallback assessment
            assessment = {
                "multiple_choice": [
                    {
                        "question": f"Key concept from {module_title}?",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": "A"
                    }
                ],
                "practical_scenarios": [
                    f"How would you apply {module_title} concepts in a real scenario?"
                ],
                "pass_threshold": 80
            }

        return assessment

    def _generate_course_resources(self, outline: Dict) -> List[Dict]:
        """Generate supplementary resources for the course"""

        resources_prompt = f"""
        Create supplementary resources for course: {outline.get('title', '')}

        Course Topic: {outline.get('description', '')}

        Generate:
        1. Resource library (10-15 tools/links with descriptions)
        2. Templates and worksheets (5-8 practical tools)
        3. Checklists (3-5 actionable checklists)
        4. Bonus materials (case studies, advanced guides)
        5. Community resources (discussion prompts, networking tips)

        Focus on AI/productivity tools and resources.
        Include specific tools, platforms, and actionable resources.
        Provide brief descriptions and use cases for each.

        Return as structured JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": resources_prompt}],
            temperature=0.7
        )

        try:
            resources = json.loads(response.choices[0].message.content)
            return resources.get('resources', [])
        except:
            # Fallback resources
            return [
                {
                    "type": "tool",
                    "name": "AI Productivity Toolkit",
                    "description": "Essential tools for automation",
                    "url": "https://example.com/tools"
                },
                {
                    "type": "template",
                    "name": "Workflow Templates",
                    "description": "Ready-to-use automation templates",
                    "url": "https://example.com/templates"
                }
            ]

    def create_template_library(self, category: str, template_count: int = 10) -> List[Template]:
        """Generate template library for specific category"""

        templates = []

        for i in range(template_count):
            template_prompt = f"""
            Create a professional template for category: {category}

            Template #{i+1} should include:
            1. Template name and purpose
            2. Detailed description
            3. Use cases (3-5 scenarios)
            4. Customization options
            5. Step-by-step usage instructions
            6. Example content/structure
            7. Tips for optimization

            Target: AI/productivity professionals
            Make it practical and immediately usable.

            Return as JSON with all template details.
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": template_prompt}],
                temperature=0.8
            )

            try:
                template_data = json.loads(response.choices[0].message.content)

                template = Template(
                    id=f"{category}_{i+1}",
                    name=template_data.get('name', f'{category} Template {i+1}'),
                    category=category,
                    description=template_data.get('description', ''),
                    file_type=template_data.get('file_type', 'document'),
                    use_cases=template_data.get('use_cases', []),
                    customization_options=template_data.get('customization_options', {}),
                    preview_url=f"/templates/{category}_{i+1}_preview",
                    download_count=0
                )

                templates.append(template)
                self._save_template(template)

            except Exception as e:
                print(f"Error generating template {i+1}: {e}")

        return templates

    def track_student_progress(self, student_id: str, course_id: str, module_id: str,
                             completion_percentage: float, time_spent: int) -> Dict:
        """Track and analyze student progress"""

        # Update progress in database
        self._update_student_progress(student_id, course_id, module_id, completion_percentage, time_spent)

        # Analyze progress and trigger interventions if needed
        progress_analysis = self._analyze_student_progress(student_id, course_id)

        # Check for completion milestones
        if completion_percentage >= 100:
            self._handle_module_completion(student_id, course_id, module_id)

        # Generate personalized recommendations
        recommendations = self._generate_learning_recommendations(student_id, progress_analysis)

        return {
            'progress_updated': True,
            'completion_percentage': completion_percentage,
            'analysis': progress_analysis,
            'recommendations': recommendations,
            'next_actions': self._get_next_actions(student_id, course_id)
        }

    def _analyze_student_progress(self, student_id: str, course_id: str) -> Dict:
        """Analyze student learning patterns and performance"""

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get progress data
        cursor.execute('''
            SELECT module_id, completion_percentage, time_spent, last_accessed
            FROM progress_tracking
            WHERE student_id = ? AND course_id = ?
            ORDER BY last_accessed
        ''', (student_id, course_id))

        progress_data = cursor.fetchall()
        conn.close()

        if not progress_data:
            return {'status': 'no_data', 'analysis': 'Insufficient data for analysis'}

        # Calculate metrics
        total_modules = len(progress_data)
        completed_modules = sum(1 for p in progress_data if p[1] >= 100)
        avg_completion = sum(p[1] for p in progress_data) / total_modules
        total_time = sum(p[2] for p in progress_data)

        # Identify patterns
        analysis = {
            'overall_progress': avg_completion,
            'modules_completed': completed_modules,
            'total_modules': total_modules,
            'time_invested': total_time,
            'learning_pace': self._calculate_learning_pace(progress_data),
            'engagement_level': self._calculate_engagement_level(progress_data),
            'risk_factors': self._identify_risk_factors(progress_data),
            'strengths': self._identify_strengths(progress_data)
        }

        return analysis

    def _calculate_learning_pace(self, progress_data: List[Tuple]) -> str:
        """Calculate student's learning pace"""

        if len(progress_data) < 2:
            return "insufficient_data"

        # Calculate average time between module starts
        start_times = [datetime.fromisoformat(p[3]) for p in progress_data if p[3]]

        if len(start_times) < 2:
            return "insufficient_data"

        time_diffs = [(start_times[i] - start_times[i-1]).days for i in range(1, len(start_times))]
        avg_days_between = sum(time_diffs) / len(time_diffs)

        if avg_days_between <= 2:
            return "fast"
        elif avg_days_between <= 7:
            return "moderate"
        else:
            return "slow"

    def _calculate_engagement_level(self, progress_data: List[Tuple]) -> str:
        """Calculate student engagement level"""

        total_time = sum(p[2] for p in progress_data)
        total_modules = len(progress_data)

        if total_modules == 0:
            return "no_engagement"

        avg_time_per_module = total_time / total_modules

        # Based on expected time per module (assuming 1 hour per module)
        if avg_time_per_module >= 3600:  # 1+ hours
            return "high"
        elif avg_time_per_module >= 1800:  # 30+ minutes
            return "moderate"
        else:
            return "low"

    def _identify_risk_factors(self, progress_data: List[Tuple]) -> List[str]:
        """Identify factors that may lead to course abandonment"""

        risk_factors = []

        # Check for stalled progress
        last_activity = max([datetime.fromisoformat(p[3]) for p in progress_data if p[3]], default=None)
        if last_activity and (datetime.now() - last_activity).days > 14:
            risk_factors.append("inactive_for_14_days")

        # Check for low completion rates
        avg_completion = sum(p[1] for p in progress_data) / len(progress_data)
        if avg_completion < 30:
            risk_factors.append("low_completion_rate")

        # Check for modules with very low time investment
        low_time_modules = sum(1 for p in progress_data if p[2] < 300)  # Less than 5 minutes
        if low_time_modules > len(progress_data) * 0.5:
            risk_factors.append("insufficient_time_investment")

        return risk_factors

    def _identify_strengths(self, progress_data: List[Tuple]) -> List[str]:
        """Identify student strengths and positive patterns"""

        strengths = []

        # Consistent progress
        completion_rates = [p[1] for p in progress_data]
        if len(completion_rates) >= 3 and all(completion_rates[i] >= completion_rates[i-1] for i in range(1, len(completion_rates))):
            strengths.append("consistent_progress")

        # High engagement
        avg_time = sum(p[2] for p in progress_data) / len(progress_data)
        if avg_time >= 3600:  # 1+ hours per module
            strengths.append("high_engagement")

        # Fast completion
        completed_modules = sum(1 for p in progress_data if p[1] >= 100)
        if completed_modules >= len(progress_data) * 0.8:
            strengths.append("high_completion_rate")

        return strengths

    def _generate_learning_recommendations(self, student_id: str, analysis: Dict) -> List[str]:
        """Generate personalized learning recommendations"""

        recommendations = []

        # Based on engagement level
        if analysis.get('engagement_level') == 'low':
            recommendations.extend([
                "Consider breaking study sessions into smaller chunks",
                "Try the mobile app for learning on-the-go",
                "Join the community discussion for motivation"
            ])

        # Based on learning pace
        if analysis.get('learning_pace') == 'slow':
            recommendations.extend([
                "Set aside dedicated time blocks for learning",
                "Use the calendar integration to schedule study time",
                "Consider the accountability partner program"
            ])

        # Based on risk factors
        risk_factors = analysis.get('risk_factors', [])
        if 'inactive_for_14_days' in risk_factors:
            recommendations.append("Welcome back! Start with a quick review of your last module")

        if 'low_completion_rate' in risk_factors:
            recommendations.append("Focus on completing one module fully before moving to the next")

        return recommendations

    def generate_completion_certificate(self, student_id: str, course_id: str) -> Dict:
        """Generate course completion certificate"""

        # Verify completion requirements
        completion_status = self._verify_course_completion(student_id, course_id)

        if not completion_status['completed']:
            return {
                'certificate_generated': False,
                'reason': completion_status['missing_requirements']
            }

        # Get student and course details
        student = self._get_student_details(student_id)
        course = self._get_course_details(course_id)

        # Generate certificate data
        certificate_data = {
            'certificate_id': f"CERT_{student_id}_{course_id}_{datetime.now().strftime('%Y%m%d')}",
            'student_name': student['name'],
            'course_title': course['title'],
            'completion_date': datetime.now().strftime('%B %d, %Y'),
            'instructor_signature': 'AI Productivity Expert',
            'skills_acquired': course.get('learning_objectives', []),
            'course_hours': course.get('estimated_completion_time', 'N/A')
        }

        # Save certificate record
        self._save_certificate_record(student_id, course_id, certificate_data)

        # Generate certificate PDF (in real implementation)
        # certificate_pdf = self._generate_certificate_pdf(certificate_data)

        return {
            'certificate_generated': True,
            'certificate_data': certificate_data,
            'download_url': f"/certificates/{certificate_data['certificate_id']}.pdf"
        }

    def optimize_course_content(self, course_id: str) -> Dict:
        """Optimize course content based on student performance data"""

        # Analyze student performance across all modules
        performance_analysis = self._analyze_course_performance(course_id)

        # Identify problematic modules
        problem_modules = self._identify_problem_modules(course_id, performance_analysis)

        # Generate optimization recommendations
        optimization_prompt = f"""
        Optimize course content based on student performance data:

        Course ID: {course_id}
        Performance Analysis: {json.dumps(performance_analysis, indent=2)}
        Problem Modules: {problem_modules}

        Provide specific recommendations for:
        1. Content improvements (clarity, examples, exercises)
        2. Module restructuring (order, pacing, difficulty)
        3. Additional resources needed
        4. Assessment modifications
        5. Engagement strategies

        Focus on improving completion rates and learning outcomes.
        Be specific and actionable.

        Return as structured JSON.
        """

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": optimization_prompt}],
            temperature=0.7
        )

        try:
            optimizations = json.loads(response.choices[0].message.content)
        except:
            optimizations = {
                "content_improvements": ["Add more examples", "Simplify complex concepts"],
                "restructuring": ["Reorder modules by difficulty"],
                "resources": ["Add video explanations"],
                "assessments": ["Simplify quiz questions"],
                "engagement": ["Add interactive elements"]
            }

        return {
            'course_id': course_id,
            'analysis': performance_analysis,
            'problem_areas': problem_modules,
            'recommendations': optimizations,
            'priority_actions': self._prioritize_optimizations(optimizations)
        }

    def create_product_bundle(self, products: List[str], bundle_name: str, discount_percentage: float) -> Dict:
        """Create product bundle with automatic pricing and content organization"""

        bundle_data = {
            'bundle_id': f"bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': bundle_name,
            'products': products,
            'discount_percentage': discount_percentage,
            'created_at': datetime.now().isoformat()
        }

        # Calculate bundle pricing
        total_individual_price = 0
        product_details = []

        for product_id in products:
            product = self._get_course_details(product_id)
            if product:
                total_individual_price += product.get('price', 0)
                product_details.append(product)

        bundle_price = total_individual_price * (1 - discount_percentage / 100)

        bundle_data.update({
            'individual_price': total_individual_price,
            'bundle_price': bundle_price,
            'savings': total_individual_price - bundle_price,
            'product_details': product_details
        })

        # Generate bundle description and marketing copy
        bundle_description = self._generate_bundle_description(product_details, bundle_name)
        bundle_data['description'] = bundle_description

        # Save bundle to database
        self._save_product_bundle(bundle_data)

        return bundle_data

    # Database helper methods
    def _save_course(self, course: Course):
        """Save course to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO courses
            (id, title, description, price, modules, resources, status, target_audience,
             learning_objectives, estimated_completion_time, difficulty_level, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            course.id, course.title, course.description, course.price,
            json.dumps(course.modules), json.dumps(course.resources),
            course.status.value, course.target_audience,
            json.dumps(course.learning_objectives), course.estimated_completion_time,
            course.difficulty_level, course.created_at.isoformat(),
            course.updated_at.isoformat()
        ))

        conn.commit()
        conn.close()

    def _save_template(self, template: Template):
        """Save template to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO templates
            (id, name, category, description, file_type, use_cases,
             customization_options, preview_url, download_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            template.id, template.name, template.category, template.description,
            template.file_type, json.dumps(template.use_cases),
            json.dumps(template.customization_options), template.preview_url,
            template.download_count
        ))

        conn.commit()
        conn.close()

    def _update_student_progress(self, student_id: str, course_id: str, module_id: str,
                               completion_percentage: float, time_spent: int):
        """Update student progress in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO progress_tracking
            (student_id, course_id, module_id, completion_percentage, time_spent, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, course_id, module_id, completion_percentage, time_spent,
              datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def _get_course_details(self, course_id: str) -> Dict:
        """Get course details from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return {}

        return {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'price': row[3],
            'modules': json.loads(row[4]) if row[4] else [],
            'resources': json.loads(row[5]) if row[5] else [],
            'status': row[6],
            'target_audience': row[7],
            'learning_objectives': json.loads(row[8]) if row[8] else [],
            'estimated_completion_time': row[9],
            'difficulty_level': row[10]
        }

    def _verify_course_completion(self, student_id: str, course_id: str) -> Dict:
        """Verify if student has completed course requirements"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check module completion
        cursor.execute('''
            SELECT AVG(completion_percentage) as avg_completion,
                   COUNT(*) as modules_tracked,
                   COUNT(CASE WHEN completion_percentage >= 100 THEN 1 END) as completed_modules
            FROM progress_tracking
            WHERE student_id = ? AND course_id = ?
        ''', (student_id, course_id))

        progress_result = cursor.fetchone()

        # Check assessments
        cursor.execute('''
            SELECT AVG(score) as avg_score,
                   COUNT(*) as assessments_taken
            FROM assessments
            WHERE student_id = ? AND course_id = ?
        ''', (student_id, course_id))

        assessment_result = cursor.fetchone()
        conn.close()

        avg_completion = progress_result[0] if progress_result[0] else 0
        avg_score = assessment_result[0] if assessment_result[0] else 0

        # Completion requirements
        completion_threshold = 80  # 80% average completion
        score_threshold = 70       # 70% average assessment score

        completed = (avg_completion >= completion_threshold and
                    avg_score >= score_threshold)

        missing_requirements = []
        if avg_completion < completion_threshold:
            missing_requirements.append(f"Module completion: {avg_completion:.1f}% (need {completion_threshold}%)")
        if avg_score < score_threshold:
            missing_requirements.append(f"Assessment score: {avg_score:.1f}% (need {score_threshold}%)")

        return {
            'completed': completed,
            'avg_completion': avg_completion,
            'avg_score': avg_score,
            'missing_requirements': missing_requirements
        }

    # Additional helper methods for optimization, analytics, and automation would be implemented here

# Example usage
if __name__ == "__main__":
    config = {
        'openai_api_key': 'your-openai-key',
        'database_path': 'product_factory.db',
        'content_storage_path': './course_content/'
    }

    factory = DigitalProductFactory(config)

    # Generate course outline
    outline = factory.generate_course_outline(
        topic="AI Productivity Automation",
        target_audience="Small business owners and entrepreneurs",
        course_length="8 hours"
    )

    print("Course outline generated:")
    print(json.dumps(outline, indent=2))

    # Create course content
    course_content = factory.create_course_content("ai_productivity_101", outline)

    # Track student progress
    progress = factory.track_student_progress(
        student_id="student_123",
        course_id="ai_productivity_101",
        module_id="module_1",
        completion_percentage=75.0,
        time_spent=3600
    )

    print("Progress tracking:", json.dumps(progress, indent=2, default=str))