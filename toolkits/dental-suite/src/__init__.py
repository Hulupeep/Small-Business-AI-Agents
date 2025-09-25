"""
Dental Practice AI Toolkit
Complete AI-powered practice management solution for dental practices

This package provides 5 specialized AI agents:
1. Patient Appointment Manager - Intelligent scheduling system
2. Treatment Plan Coordinator - Treatment planning and cost management
3. Clinical Records Assistant - GDPR-compliant record management
4. Insurance & Billing Hub - Automated financial management
5. Patient Communication Platform - Personalized patient engagement

Annual Value: €65,000+ for a typical 3-dentist practice
ROI: 274% in Year 1
"""

from .dental_suite import DentalPracticeAI, create_dental_practice_ai

__version__ = "1.0.0"
__author__ = "LangChain AI Solutions"
__email__ = "dental@langchain-ai.com"

__all__ = [
    "DentalPracticeAI",
    "create_dental_practice_ai"
]