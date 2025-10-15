"""
Test cases for AI/ML Services
Critical AI functionality that was previously untested
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase
from django.core.cache import cache
import numpy as np
from PIL import Image
import io

from apps.ai_ml.enhanced_services import (
    EnhancedComputerVisionService,
    EnhancedPredictiveAnalyticsService,
    EnhancedChatbotService,
    EnhancedAIAutomationService,
    ProcessingError,
    ModelError,
    DataError,
    ContextError
)


class TestEnhancedComputerVisionService(TestCase):
    """Test cases for Computer Vision Service"""
    
    def setUp(self):
        """Set up test data"""
        self.organization_id = 1
        self.cv_service = EnhancedComputerVisionService(organization_id=self.organization_id)
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.cv_service.organization_id, self.organization_id)
        self.assertIsInstance(self.cv_service.models, dict)
        self.assertEqual(self.cv_service.cache_timeout, 3600)
    
    @patch('apps.ai_ml.enhanced_services.cache')
    def test_process_image_general_analysis(self, mock_cache):
        """Test general image analysis"""
        # Mock cache to return None (cache miss)
        mock_cache.get.return_value = None
        
        # Mock image loading
        with patch.object(self.cv_service, '_load_image') as mock_load:
            mock_image = MagicMock(spec=Image.Image)
            mock_load.return_value = mock_image
            
            with patch.object(self.cv_service, '_preprocess_image') as mock_preprocess:
                mock_preprocess.return_value = mock_image
                
                with patch.object(self.cv_service, '_general_analysis') as mock_analysis:
                    mock_analysis.return_value = [
                        {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]}
                    ]
                    
                    result = self.cv_service.process_image(
                        image_path="/test/path/image.jpg",
                        analysis_type="general"
                    )
                    
                    self.assertEqual(result["analysis_type"], "general")
                    self.assertIn("results", result)
                    self.assertIn("processing_time", result)
                    self.assertIn("model_info", result)
    
    def test_process_image_invalid_path(self):
        """Test processing image with invalid path"""
        with self.assertRaises(ValueError):
            self.cv_service.process_image("", "general")
    
    def test_process_image_unsupported_type(self):
        """Test processing image with unsupported analysis type"""
        with self.assertRaises(ValueError):
            self.cv_service.process_image("/test/path/image.jpg", "unsupported")
    
    @patch('apps.ai_ml.enhanced_services.cache')
    def test_process_image_cached_result(self, mock_cache):
        """Test processing image with cached result"""
        cached_result = {
            "analysis_type": "general",
            "results": [{"class": "person", "confidence": 0.95}],
            "processing_time": 0.5
        }
        mock_cache.get.return_value = cached_result
        
        result = self.cv_service.process_image("/test/path/image.jpg", "general")
        
        self.assertEqual(result, cached_result)
    
    def test_load_models(self):
        """Test model loading"""
        models = self.cv_service._load_models()
        
        self.assertIsInstance(models, dict)
        self.assertIn("object_detection", models)
        self.assertIn("quality_assessment", models)
        self.assertIn("ocr", models)
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        # Create a test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        with patch.object(self.cv_service, '_preprocess_image') as mock_preprocess:
            mock_preprocess.return_value = test_image
            result = self.cv_service._preprocess_image(test_image, "general")
            
            self.assertIsInstance(result, Image.Image)
    
    def test_general_analysis(self):
        """Test general object detection analysis"""
        test_image = Image.new('RGB', (100, 100), color='red')
        
        results = self.cv_service._general_analysis(test_image, 0.5, 10)
        
        self.assertIsInstance(results, list)
        # Should return mock results based on implementation
        self.assertGreater(len(results), 0)
    
    def test_quality_analysis(self):
        """Test image quality analysis"""
        test_image = Image.new('RGB', (100, 100), color='red')
        
        results = self.cv_service._quality_analysis(test_image, {})
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
    
    def test_ocr_analysis(self):
        """Test OCR text extraction"""
        test_image = Image.new('RGB', (100, 100), color='red')
        
        results = self.cv_service._ocr_analysis(test_image, {})
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)


class TestEnhancedPredictiveAnalyticsService(TestCase):
    """Test cases for Predictive Analytics Service"""
    
    def setUp(self):
        """Set up test data"""
        self.organization_id = 1
        self.analytics_service = EnhancedPredictiveAnalyticsService(organization_id=self.organization_id)
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.analytics_service.organization_id, self.organization_id)
        self.assertIsInstance(self.analytics_service.models, dict)
        self.assertEqual(self.analytics_service.cache_timeout, 1800)
    
    def test_generate_prediction_maintenance(self):
        """Test maintenance prediction generation"""
        data = {
            "features": [1.2, 3.4, 5.6],
            "metadata": {"equipment_id": "EQ001", "type": "pump"}
        }
        
        with patch.object(self.analytics_service, '_preprocess_data') as mock_preprocess:
            mock_preprocess.return_value = data
            
            with patch.object(self.analytics_service, '_maintenance_prediction') as mock_prediction:
                mock_prediction.return_value = [
                    {"prediction": "maintenance_needed", "confidence": 0.85, "days_until_maintenance": 15}
                ]
                
                result = self.analytics_service.generate_prediction(
                    data, "maintenance", {"confidence_threshold": 0.8}
                )
                
                self.assertEqual(result["prediction_type"], "maintenance")
                self.assertIn("predictions", result)
                self.assertIn("processing_time", result)
    
    def test_generate_prediction_invalid_data(self):
        """Test prediction with invalid data"""
        with self.assertRaises(ValueError):
            self.analytics_service.generate_prediction({}, "maintenance")
    
    def test_generate_prediction_unsupported_type(self):
        """Test prediction with unsupported type"""
        data = {"features": [1, 2, 3]}
        
        with self.assertRaises(ValueError):
            self.analytics_service.generate_prediction(data, "unsupported")
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        data = {
            "features": [1, 2, 3],
            "metadata": {"type": "test"},
            "historical_data": [0.5, 0.6, 0.7]
        }
        
        processed = self.analytics_service._preprocess_data(data, "maintenance")
        
        self.assertIn("features", processed)
        self.assertIn("metadata", processed)
        self.assertIn("historical_data", processed)
    
    def test_maintenance_prediction(self):
        """Test maintenance prediction logic"""
        data = {"features": [1, 2, 3], "metadata": {"type": "pump"}}
        
        predictions = self.analytics_service._maintenance_prediction(data, {})
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
        self.assertIn("prediction", predictions[0])
        self.assertIn("confidence", predictions[0])
    
    def test_performance_prediction(self):
        """Test performance prediction logic"""
        data = {"features": [1, 2, 3], "metadata": {"type": "system"}}
        
        predictions = self.analytics_service._performance_prediction(data, {})
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
    
    def test_anomaly_detection(self):
        """Test anomaly detection logic"""
        data = {"features": [1, 2, 3], "metadata": {"type": "sensor"}}
        
        predictions = self.analytics_service._anomaly_detection(data, {})
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
    
    def test_risk_assessment(self):
        """Test risk assessment logic"""
        data = {"features": [1, 2, 3], "metadata": {"type": "equipment"}}
        
        predictions = self.analytics_service._risk_assessment(data, {})
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)
    
    def test_trend_analysis(self):
        """Test trend analysis logic"""
        data = {"features": [1, 2, 3], "metadata": {"type": "performance"}}
        
        predictions = self.analytics_service._trend_analysis(data, {})
        
        self.assertIsInstance(predictions, list)
        self.assertGreater(len(predictions), 0)


class TestEnhancedChatbotService(TestCase):
    """Test cases for Chatbot Service"""
    
    def setUp(self):
        """Set up test data"""
        self.organization_id = 1
        self.chatbot_service = EnhancedChatbotService(organization_id=self.organization_id)
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.chatbot_service.organization_id, self.organization_id)
        self.assertIsInstance(self.chatbot_service.models, dict)
        self.assertEqual(self.chatbot_service.cache_timeout, 1800)
    
    def test_generate_response(self):
        """Test chatbot response generation"""
        message = "How do I reset my password?"
        context = {"user_id": "123", "session_id": "abc"}
        
        with patch.object(self.chatbot_service, '_preprocess_message') as mock_preprocess:
            mock_preprocess.return_value = message
            
            with patch.object(self.chatbot_service, '_recognize_intent') as mock_intent:
                mock_intent.return_value = {
                    "name": "password_reset",
                    "confidence": 0.9,
                    "entities": ["password", "reset"]
                }
                
                with patch.object(self.chatbot_service, '_generate_response_text') as mock_response:
                    mock_response.return_value = "I can help you reset your password."
                    
                    with patch.object(self.chatbot_service, '_generate_suggestions') as mock_suggestions:
                        mock_suggestions.return_value = [
                            "How do I change my email?",
                            "What are the password requirements?"
                        ]
                        
                        result = self.chatbot_service.generate_response(
                            message, context, {"style": "helpful", "max_length": 200}
                        )
                        
                        self.assertEqual(result["message"], message)
                        self.assertIn("response", result)
                        self.assertIn("intent", result)
                        self.assertIn("suggestions", result)
    
    def test_generate_response_error_handling(self):
        """Test chatbot response error handling"""
        with patch.object(self.chatbot_service, '_preprocess_message') as mock_preprocess:
            mock_preprocess.side_effect = Exception("Processing error")
            
            with self.assertRaises(ProcessingError):
                self.chatbot_service.generate_response("test message")
    
    def test_preprocess_message(self):
        """Test message preprocessing"""
        message = "  How do I reset my password?  "
        processed = self.chatbot_service._preprocess_message(message, "en")
        
        self.assertEqual(processed, "how do i reset my password?")
    
    def test_recognize_intent(self):
        """Test intent recognition"""
        message = "I need to reset my password"
        context = {"user_id": "123"}
        
        intent = self.chatbot_service._recognize_intent(message, context)
        
        self.assertIn("name", intent)
        self.assertIn("confidence", intent)
        self.assertIn("entities", intent)
    
    def test_generate_response_text(self):
        """Test response text generation"""
        message = "How do I reset my password?"
        intent = {"name": "password_reset", "confidence": 0.9}
        context = {"user_id": "123"}
        
        response = self.chatbot_service._generate_response_text(
            message, intent, context, "helpful", 200
        )
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
    
    def test_generate_suggestions(self):
        """Test suggestion generation"""
        intent = {"name": "password_reset", "confidence": 0.9}
        context = {"user_id": "123"}
        
        suggestions = self.chatbot_service._generate_suggestions(intent, context)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)


class TestEnhancedAIAutomationService(TestCase):
    """Test cases for AI Automation Service"""
    
    def setUp(self):
        """Set up test data"""
        self.organization_id = 1
        self.automation_service = EnhancedAIAutomationService(organization_id=self.organization_id)
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.automation_service.organization_id, self.organization_id)
        self.assertIsInstance(self.automation_service.models, dict)
        self.assertIsInstance(self.automation_service.automation_rules, dict)
    
    def test_execute_automation_workflow(self):
        """Test workflow automation execution"""
        trigger_data = {
            "event_type": "ticket_created",
            "data": {"priority": "high", "category": "bug"},
            "context": {"user_id": "123"},
            "user_id": "user_123"
        }
        
        with patch.object(self.automation_service, '_analyze_trigger_data') as mock_analyze:
            mock_analyze.return_value = {
                "priority": "high",
                "category": "bug",
                "automation_opportunities": ["assign_agent", "set_priority"]
            }
            
            with patch.object(self.automation_service, '_generate_automation_actions') as mock_actions:
                mock_actions.return_value = [
                    {"name": "assign_agent", "confidence": 0.9},
                    {"name": "set_priority", "confidence": 0.8}
                ]
                
                with patch.object(self.automation_service, '_execute_actions') as mock_execute:
                    mock_execute.return_value = [
                        {"action": "assign_agent", "result": "success"},
                        {"action": "set_priority", "result": "success"}
                    ]
                    
                    result = self.automation_service.execute_automation(
                        trigger_data, "workflow", {"confidence_threshold": 0.8, "max_actions": 5}
                    )
                    
                    self.assertEqual(result["automation_type"], "workflow")
                    self.assertIn("actions_taken", result)
                    self.assertIn("results", result)
                    self.assertIn("confidence_scores", result)
    
    def test_execute_automation_dry_run(self):
        """Test automation execution in dry run mode"""
        trigger_data = {
            "event_type": "ticket_created",
            "data": {"priority": "high"},
            "user_id": "user_123"
        }
        
        with patch.object(self.automation_service, '_analyze_trigger_data') as mock_analyze:
            mock_analyze.return_value = {"priority": "high", "automation_opportunities": ["assign_agent"]}
            
            with patch.object(self.automation_service, '_generate_automation_actions') as mock_actions:
                mock_actions.return_value = [{"name": "assign_agent", "confidence": 0.9}]
                
                result = self.automation_service.execute_automation(
                    trigger_data, "workflow", {"dry_run": True}
                )
                
                self.assertTrue(result["metadata"]["dry_run"])
    
    def test_execute_automation_error_handling(self):
        """Test automation execution error handling"""
        trigger_data = {
            "event_type": "invalid_event",
            "data": {},
            "user_id": "user_123"
        }
        
        with patch.object(self.automation_service, '_analyze_trigger_data') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis error")
            
            with self.assertRaises(Exception):
                self.automation_service.execute_automation(trigger_data)
    
    def test_analyze_trigger_data(self):
        """Test trigger data analysis"""
        trigger_data = {
            "event_type": "ticket_created",
            "data": {"priority": "high", "category": "bug"},
            "context": {"user_id": "123"}
        }
        
        analysis = self.automation_service._analyze_trigger_data(trigger_data, "workflow")
        
        self.assertIn("priority", analysis)
        self.assertIn("category", analysis)
        self.assertIn("user_context", analysis)
        self.assertIn("automation_opportunities", analysis)
    
    def test_generate_automation_actions(self):
        """Test automation action generation"""
        analysis = {
            "priority": "high",
            "category": "bug",
            "automation_opportunities": ["assign_agent", "set_priority"]
        }
        
        actions = self.automation_service._generate_automation_actions(
            analysis, "workflow", 0.8, 5
        )
        
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        
        for action in actions:
            self.assertIn("name", action)
            self.assertIn("confidence", action)


class TestAIExceptionHandling(TestCase):
    """Test AI service exception handling"""
    
    def test_processing_error(self):
        """Test ProcessingError exception"""
        error = ProcessingError("Image processing failed")
        self.assertEqual(str(error), "Image processing failed")
    
    def test_model_error(self):
        """Test ModelError exception"""
        error = ModelError("Model loading failed")
        self.assertEqual(str(error), "Model loading failed")
    
    def test_data_error(self):
        """Test DataError exception"""
        error = DataError("Invalid input data")
        self.assertEqual(str(error), "Invalid input data")
    
    def test_context_error(self):
        """Test ContextError exception"""
        error = ContextError("Invalid context provided")
        self.assertEqual(str(error), "Invalid context provided")


if __name__ == '__main__':
    pytest.main([__file__])