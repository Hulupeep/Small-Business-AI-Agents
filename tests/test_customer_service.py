"""
Unit tests for Customer Service Chatbot Agent
"""

import unittest
import tempfile
import os
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from agents.customer_service import (
    CustomerServiceChatbot,
    ConversationStatus,
    TicketPriority,
    KnowledgeBaseItem
)


class TestCustomerServiceChatbot(unittest.TestCase):

    def setUp(self):
        """Set up test environment"""
        # Use temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()

        self.chatbot = CustomerServiceChatbot(db_path=self.temp_db.name)
        self.customer_id = "test_customer_123"

    def tearDown(self):
        """Clean up test environment"""
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)

    def test_initialization(self):
        """Test chatbot initialization"""
        self.assertIsNotNone(self.chatbot)
        self.assertIsInstance(self.chatbot.knowledge_base, dict)
        self.assertGreater(len(self.chatbot.knowledge_base), 0)

    def test_start_conversation(self):
        """Test starting a new conversation"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        self.assertIsNotNone(conversation_id)
        self.assertIn("conv_", conversation_id)
        self.assertIn(self.customer_id[:8], conversation_id)

    def test_add_message(self):
        """Test adding messages to conversation"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        message_id = self.chatbot.add_message(
            conversation_id,
            "customer",
            "Hello, I need help"
        )

        self.assertIsNotNone(message_id)
        self.assertIn("msg_", message_id)

    def test_knowledge_base_search(self):
        """Test knowledge base search functionality"""
        # Test shipping query
        response = self.chatbot._search_knowledge_base("shipping information")
        self.assertIsNotNone(response)
        self.assertIn("shipping", response.lower())

        # Test business hours query
        response = self.chatbot._search_knowledge_base("what are your hours")
        self.assertIsNotNone(response)
        self.assertIn("hours", response.lower())

        # Test no match
        response = self.chatbot._search_knowledge_base("random unrelated query xyz")
        self.assertIsNone(response)

    def test_escalation_detection(self):
        """Test escalation keyword detection"""
        # Test escalation keywords
        escalation_messages = [
            "I want to cancel my subscription",
            "This is urgent - billing error",
            "I need to speak to a manager",
            "I want a refund immediately"
        ]

        for message in escalation_messages:
            needs_escalation = self.chatbot._needs_escalation(message)
            self.assertTrue(needs_escalation, f"Should escalate: {message}")

        # Test normal messages
        normal_messages = [
            "Hello, I have a question",
            "What are your business hours?",
            "How do I track my order?"
        ]

        for message in normal_messages:
            needs_escalation = self.chatbot._needs_escalation(message)
            self.assertFalse(needs_escalation, f"Should not escalate: {message}")

    def test_order_status_lookup(self):
        """Test order status lookup"""
        # Test valid order number
        response = self.chatbot._get_order_status("ABC123456")
        self.assertIsNotNone(response)
        self.assertIn("ABC123456", response)
        self.assertIn("order", response.lower())

    def test_conversation_flow(self):
        """Test complete conversation flow"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        # Test greeting
        messages = self.chatbot.get_conversation_history(conversation_id)
        self.assertEqual(len(messages), 1)  # Welcome message
        self.assertEqual(messages[0]["sender"], "assistant")

        # Test customer message and response
        response = self.chatbot.process_message(
            conversation_id,
            "What are your business hours?"
        )

        self.assertIsNotNone(response)
        self.assertIn("hours", response.lower())

        # Check message history
        messages = self.chatbot.get_conversation_history(conversation_id)
        self.assertEqual(len(messages), 3)  # Welcome + customer + assistant

    def test_escalation_flow(self):
        """Test escalation workflow"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        # Send escalation message
        response = self.chatbot.process_message(
            conversation_id,
            "I want to cancel my subscription immediately"
        )

        self.assertIn("human", response.lower())
        self.assertIn("support", response.lower())

    def test_order_tracking(self):
        """Test order tracking functionality"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        # Test with order number
        response = self.chatbot.process_message(
            conversation_id,
            "I need to track order ABC123456"
        )

        self.assertIn("ABC123456", response)
        self.assertIn("order", response.lower())

    def test_analytics_generation(self):
        """Test analytics generation"""
        # Create some test conversations
        for i in range(3):
            conv_id = self.chatbot.start_conversation(f"customer_{i}")
            self.chatbot.process_message(conv_id, "Hello")
            self.chatbot.process_message(conv_id, "What are your hours?")

        analytics = self.chatbot.get_analytics(30)

        self.assertIsInstance(analytics, dict)
        self.assertIn("total_conversations", analytics)
        self.assertIn("estimated_savings", analytics)
        self.assertGreaterEqual(analytics["total_conversations"], 3)

    def test_knowledge_base_addition(self):
        """Test adding new knowledge base items"""
        initial_count = len(self.chatbot.knowledge_base)

        kb_id = self.chatbot.add_knowledge_base_item(
            title="Test Item",
            content="This is a test knowledge base item.",
            category="test",
            keywords=["test", "example"]
        )

        self.assertIsNotNone(kb_id)
        self.assertEqual(len(self.chatbot.knowledge_base), initial_count + 1)
        self.assertIn(kb_id, self.chatbot.knowledge_base)

    def test_conversation_history(self):
        """Test conversation history retrieval"""
        conversation_id = self.chatbot.start_conversation(self.customer_id)

        # Add some messages
        self.chatbot.process_message(conversation_id, "Hello")
        self.chatbot.process_message(conversation_id, "What are your hours?")

        history = self.chatbot.get_conversation_history(conversation_id)

        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)

        # Check message structure
        for message in history:
            self.assertIn("sender", message)
            self.assertIn("content", message)
            self.assertIn("timestamp", message)

    def test_multiple_conversations(self):
        """Test handling multiple concurrent conversations"""
        conversations = []

        # Start multiple conversations
        for i in range(5):
            conv_id = self.chatbot.start_conversation(f"customer_{i}")
            conversations.append(conv_id)

            # Send a message in each
            response = self.chatbot.process_message(conv_id, f"Hello from customer {i}")
            self.assertIsNotNone(response)

        # Verify all conversations are tracked
        self.assertEqual(len(conversations), 5)
        self.assertEqual(len(set(conversations)), 5)  # All unique

    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with non-existent conversation
        with self.assertLogs(level='ERROR'):
            history = self.chatbot.get_conversation_history("invalid_conversation_id")
            self.assertEqual(len(history), 0)

        # Test with empty message
        conversation_id = self.chatbot.start_conversation(self.customer_id)
        response = self.chatbot.process_message(conversation_id, "")
        self.assertIsNotNone(response)  # Should handle gracefully


class TestKnowledgeBaseItem(unittest.TestCase):

    def test_knowledge_base_item_creation(self):
        """Test KnowledgeBaseItem creation"""
        item = KnowledgeBaseItem(
            kb_id="test_001",
            title="Test Title",
            content="Test content here",
            category="test",
            keywords=["test", "example"]
        )

        self.assertEqual(item.kb_id, "test_001")
        self.assertEqual(item.title, "Test Title")
        self.assertEqual(item.category, "test")
        self.assertEqual(len(item.keywords), 2)
        self.assertEqual(item.confidence_threshold, 0.7)  # Default value


if __name__ == "__main__":
    # Create logs directory for testing
    Path("logs").mkdir(exist_ok=True)

    # Run tests
    unittest.main(verbosity=2)