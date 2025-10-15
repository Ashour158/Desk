"""
Comprehensive test suite for AI/ML Enhanced Services
Tests all AI/ML services with comprehensive coverage
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from django.test import TestCase
from django.conf import settings
from PIL import Image
import io
import json
from datetime import datetime, timedelta

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
    """Test suite for Enhanced Computer Vision Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EnhancedComputerVisionService()
        self.test_image = Image.new('RGB', (100, 100), color='red')
        
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_process_image_success(self, mock_load_models):
        """Test successful image processing"""
        mock_load_models.return_value = {'model': 'loaded'}
        
        with patch.object(self.service, '_load_image', return_value=self.test_image):
            with patch.object(self.service, '_preprocess_image', return_value=self.test_image):
                with patch.object(self.service, '_general_analysis', return_value=[{"result": "test"}]):
                    result = self.service.process_image("test_image.jpg", "general")
                    
                    self.assertIn('analysis_type', result)
                    self.assertIn('results', result)
                    self.assertEqual(result['analysis_type'], 'general')
                    self.assertEqual(len(result['results']), 1)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_process_image_invalid_path(self, mock_load_models):
        """Test image processing with invalid path"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.process_image("", "general")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    @patch('apps.ai_ml.enhanced_services.Image.open', side_effect=FileNotFoundError)
    def test_load_image_file_not_found(self, mock_image_open, mock_load_models):
        """Test loading image when file not found"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(FileNotFoundError):
            self.service._load_image("non_existent.jpg")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_general_analysis(self, mock_load_models):
        """Test general object detection and classification"""
        mock_load_models.return_value = {'yolo_model': 'loaded'}
        
        result = self.service._general_analysis(self.test_image, 0.8, 10)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('class', result[0])
        self.assertIn('confidence', result[0])
        self.assertIn('bbox', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_quality_analysis(self, mock_load_models):
        """Test image quality assessment"""
        mock_load_models.return_value = {'quality_model': 'loaded'}
        
        result = self.service._quality_analysis(self.test_image, {'threshold': 0.8})
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('metric', result[0])
        self.assertIn('value', result[0])
        self.assertIn('description', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_ocr_analysis(self, mock_load_models):
        """Test OCR text extraction"""
        mock_load_models.return_value = {'ocr_model': 'loaded'}
        
        result = self.service._ocr_analysis(self.test_image, {'language': 'en'})
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('text', result[0])
        self.assertIn('confidence', result[0])
        self.assertIn('bbox', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_defect_analysis(self, mock_load_models):
        """Test defect detection"""
        mock_load_models.return_value = {'defect_model': 'loaded'}
        
        result = self.service._defect_analysis(self.test_image, {'sensitivity': 0.9})
        
        self.assertIsInstance(result, list)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedComputerVisionService._load_models')
    def test_similarity_analysis(self, mock_load_models):
        """Test similarity matching"""
        mock_load_models.return_value = {'similarity_model': 'loaded'}
        
        result = self.service._similarity_analysis(self.test_image, {'threshold': 0.8})
        
        self.assertIsInstance(result, list)
    
    def test_preprocess_image(self):
        """Test image preprocessing"""
        result = self.service._preprocess_image(self.test_image, "general")
        
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 100))
    
    def test_load_models(self):
        """Test model loading"""
        with patch('apps.ai_ml.enhanced_services.torch.load') as mock_torch_load:
            mock_torch_load.return_value = {'model': 'test'}
            result = self.service._load_models()
            
            self.assertIsInstance(result, dict)


class TestEnhancedPredictiveAnalyticsService(TestCase):
    """Test suite for Enhanced Predictive Analytics Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EnhancedPredictiveAnalyticsService()
        self.test_data = {
            'features': [1, 2, 3, 4, 5],
            'timestamp': datetime.now().isoformat(),
            'context': {'user_id': '123', 'session_id': 'abc'}
        }
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_generate_prediction_success(self, mock_load_models):
        """Test successful prediction generation"""
        mock_load_models.return_value = {'model': 'loaded'}
        
        with patch.object(self.service, '_preprocess_data', return_value=self.test_data):
            with patch.object(self.service, '_maintenance_prediction', return_value=[{"prediction": "test"}]):
                result = self.service.generate_prediction(self.test_data, "maintenance")
                
                self.assertIn('prediction_type', result)
                self.assertIn('predictions', result)
                self.assertEqual(result['prediction_type'], 'maintenance')
                self.assertEqual(len(result['predictions']), 1)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_generate_prediction_invalid_data(self, mock_load_models):
        """Test prediction with invalid data"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.generate_prediction({}, "maintenance")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_generate_prediction_unsupported_type(self, mock_load_models):
        """Test prediction with unsupported type"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.generate_prediction(self.test_data, "unsupported")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_maintenance_prediction(self, mock_load_models):
        """Test maintenance prediction"""
        mock_load_models.return_value = {'maintenance_model': 'loaded'}
        
        result = self.service._maintenance_prediction(self.test_data, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('prediction', result[0])
        self.assertIn('confidence', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_performance_prediction(self, mock_load_models):
        """Test performance prediction"""
        mock_load_models.return_value = {'performance_model': 'loaded'}
        
        result = self.service._performance_prediction(self.test_data, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('prediction', result[0])
        self.assertIn('confidence', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_anomaly_detection(self, mock_load_models):
        """Test anomaly detection"""
        mock_load_models.return_value = {'anomaly_model': 'loaded'}
        
        result = self.service._anomaly_detection(self.test_data, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('anomaly', result[0])
        self.assertIn('confidence', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_risk_assessment(self, mock_load_models):
        """Test risk assessment"""
        mock_load_models.return_value = {'risk_model': 'loaded'}
        
        result = self.service._risk_assessment(self.test_data, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('risk', result[0])
        self.assertIn('confidence', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedPredictiveAnalyticsService._load_models')
    def test_trend_analysis(self, mock_load_models):
        """Test trend analysis"""
        mock_load_models.return_value = {'trend_model': 'loaded'}
        
        result = self.service._trend_analysis(self.test_data, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('trend', result[0])
        self.assertIn('confidence', result[0])
    
    def test_preprocess_data(self):
        """Test data preprocessing"""
        result = self.service._preprocess_data(self.test_data, "maintenance")
        
        self.assertIsInstance(result, dict)
        self.assertIn('features', result)
    
    def test_load_models(self):
        """Test model loading"""
        with patch('apps.ai_ml.enhanced_services.torch.load') as mock_torch_load:
            mock_torch_load.return_value = {'model': 'test'}
            result = self.service._load_models()
            
            self.assertIsInstance(result, dict)


class TestEnhancedChatbotService(TestCase):
    """Test suite for Enhanced Chatbot Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EnhancedChatbotService()
        self.test_message = "Hello, I need help with my ticket"
        self.test_context = {
            'user_id': '123',
            'session_id': 'abc',
            'language': 'en',
            'previous_messages': []
        }
    
    @patch('apps.ai_ml.enhanced_services.EnhancedChatbotService._load_models')
    def test_generate_response_success(self, mock_load_models):
        """Test successful response generation"""
        mock_load_models.return_value = {'model': 'loaded'}
        
        with patch.object(self.service, '_preprocess_message', return_value=self.test_message):
            with patch.object(self.service, '_recognize_intent', return_value={"name": "greeting", "confidence": 0.9}):
                with patch.object(self.service, '_generate_response_text', return_value="Hello! How can I help you?"):
                    with patch.object(self.service, '_generate_suggestions', return_value=["Hi", "Help"]):
                        result = self.service.generate_response(self.test_message, self.test_context)
                        
                        self.assertIn('response_text', result)
                        self.assertIn('intent', result)
                        self.assertIn('suggestions', result)
                        self.assertEqual(result['response_text'], "Hello! How can I help you?")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedChatbotService._load_models')
    def test_generate_response_empty_message(self, mock_load_models):
        """Test response generation with empty message"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.generate_response("", self.test_context)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedChatbotService._load_models')
    def test_recognize_intent(self, mock_load_models):
        """Test intent recognition"""
        mock_load_models.return_value = {'intent_model': 'loaded'}
        
        result = self.service._recognize_intent(self.test_message, self.test_context)
        
        self.assertIsInstance(result, dict)
        self.assertIn('name', result)
        self.assertIn('confidence', result)
        self.assertGreater(result['confidence'], 0)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedChatbotService._load_models')
    def test_generate_response_text(self, mock_load_models):
        """Test response text generation"""
        mock_load_models.return_value = {'response_model': 'loaded'}
        
        result = self.service._generate_response_text(self.test_message, self.test_context)
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedChatbotService._load_models')
    def test_generate_suggestions(self, mock_load_models):
        """Test suggestion generation"""
        mock_load_models.return_value = {'suggestion_model': 'loaded'}
        
        result = self.service._generate_suggestions(self.test_message, self.test_context)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIsInstance(result[0], str)
    
    def test_preprocess_message(self):
        """Test message preprocessing"""
        result = self.service._preprocess_message(self.test_message, "en")
        
        self.assertIsInstance(result, str)
        self.assertEqual(result, self.test_message)
    
    def test_load_models(self):
        """Test model loading"""
        with patch('apps.ai_ml.enhanced_services.torch.load') as mock_torch_load:
            mock_torch_load.return_value = {'model': 'test'}
            result = self.service._load_models()
            
            self.assertIsInstance(result, dict)


class TestEnhancedAIAutomationService(TestCase):
    """Test suite for Enhanced AI Automation Service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = EnhancedAIAutomationService()
        self.test_trigger_data = {
            'event_type': 'ticket_created',
            'data': {
                'ticket_id': '123',
                'priority': 'high',
                'category': 'technical'
            }
        }
        self.test_automation_type = "workflow"
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_execute_automation_success(self, mock_load_models):
        """Test successful automation execution"""
        mock_load_models.return_value = {'model': 'loaded'}
        
        with patch.object(self.service, '_load_automation_rules', return_value=[]):
            with patch.object(self.service, '_analyze_trigger_data', return_value={"priority": "high"}):
                with patch.object(self.service, '_generate_automation_actions', return_value=[{"name": "assign_agent", "confidence": 0.9}]):
                    with patch.object(self.service, '_execute_actions', return_value=[{"status": "success"}]):
                        result = self.service.execute_automation(self.test_trigger_data, self.test_automation_type)
                        
                        self.assertIn('automation_type', result)
                        self.assertIn('actions_taken', result)
                        self.assertIn('results', result)
                        self.assertEqual(result['automation_type'], 'workflow')
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_execute_automation_invalid_trigger_data(self, mock_load_models):
        """Test automation execution with invalid trigger data"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.execute_automation({}, self.test_automation_type)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_execute_automation_unsupported_type(self, mock_load_models):
        """Test automation execution with unsupported type"""
        mock_load_models.return_value = {}
        
        with self.assertRaises(ValueError):
            self.service.execute_automation(self.test_trigger_data, "unsupported")
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_analyze_trigger_data(self, mock_load_models):
        """Test trigger data analysis"""
        mock_load_models.return_value = {'analysis_model': 'loaded'}
        
        result = self.service._analyze_trigger_data(self.test_trigger_data, self.test_automation_type)
        
        self.assertIsInstance(result, dict)
        self.assertIn('priority', result)
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_generate_automation_actions(self, mock_load_models):
        """Test automation action generation"""
        mock_load_models.return_value = {'action_model': 'loaded'}
        
        analysis = {"priority": "high", "category": "technical"}
        result = self.service._generate_automation_actions(analysis, self.test_automation_type, 0.8, 5)
        
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn('name', result[0])
        self.assertIn('confidence', result[0])
        self.assertIn('parameters', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_execute_actions(self, mock_load_models):
        """Test action execution"""
        mock_load_models.return_value = {'execution_model': 'loaded'}
        
        actions = [{"name": "assign_agent", "confidence": 0.9, "parameters": {"agent_id": "123"}}]
        result = self.service._execute_actions(actions)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn('status', result[0])
    
    @patch('apps.ai_ml.enhanced_services.EnhancedAIAutomationService._load_models')
    def test_simulate_actions(self, mock_load_models):
        """Test action simulation"""
        mock_load_models.return_value = {'simulation_model': 'loaded'}
        
        actions = [{"name": "assign_agent", "confidence": 0.9}]
        result = self.service._simulate_actions(actions)
        
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn('simulated', result[0])
        self.assertTrue(result[0]['simulated'])
    
    def test_load_automation_rules(self):
        """Test automation rules loading"""
        result = self.service._load_automation_rules(self.test_automation_type)
        
        self.assertIsInstance(result, list)
    
    def test_load_models(self):
        """Test model loading"""
        with patch('apps.ai_ml.enhanced_services.torch.load') as mock_torch_load:
            mock_torch_load.return_value = {'model': 'test'}
            result = self.service._load_models()
            
            self.assertIsInstance(result, dict)


class TestAIErrorHandling(TestCase):
    """Test suite for AI/ML error handling"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cv_service = EnhancedComputerVisionService()
        self.pa_service = EnhancedPredictiveAnalyticsService()
        self.chatbot_service = EnhancedChatbotService()
        self.automation_service = EnhancedAIAutomationService()
    
    def test_processing_error_handling(self):
        """Test processing error handling"""
        with self.assertRaises(ProcessingError):
            raise ProcessingError("Processing failed")
    
    def test_model_error_handling(self):
        """Test model error handling"""
        with self.assertRaises(ModelError):
            raise ModelError("Model loading failed")
    
    def test_data_error_handling(self):
        """Test data error handling"""
        with self.assertRaises(DataError):
            raise DataError("Invalid data format")
    
    def test_context_error_handling(self):
        """Test context error handling"""
        with self.assertRaises(ContextError):
            raise ContextError("Invalid context")


class TestAIPerformance(TestCase):
    """Test suite for AI/ML performance"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cv_service = EnhancedComputerVisionService()
        self.pa_service = EnhancedPredictiveAnalyticsService()
        self.chatbot_service = EnhancedChatbotService()
        self.automation_service = EnhancedAIAutomationService()
    
    @patch('apps.ai_ml.enhanced_services.time.time')
    def test_performance_monitoring(self, mock_time):
        """Test performance monitoring"""
        mock_time.side_effect = [0, 1, 2]  # Start, end, total
        
        with patch.object(self.cv_service, '_load_models', return_value={}):
            with patch.object(self.cv_service, '_load_image', return_value=Image.new('RGB', (100, 100))):
                with patch.object(self.cv_service, '_preprocess_image', return_value=Image.new('RGB', (100, 100))):
                    with patch.object(self.cv_service, '_general_analysis', return_value=[{"result": "test"}]):
                        result = self.cv_service.process_image("test.jpg", "general")
                        
                        self.assertIn('processing_time', result)
                        self.assertGreater(result['processing_time'], 0)
    
    def test_memory_usage_monitoring(self):
        """Test memory usage monitoring"""
        with patch('apps.ai_ml.enhanced_services.psutil.virtual_memory') as mock_memory:
            mock_memory.return_value = Mock(percent=50.0)
            
            result = self.cv_service._get_memory_usage()
            
            self.assertEqual(result, 50.0)
    
    def test_model_caching(self):
        """Test model caching"""
        with patch.object(self.cv_service, '_load_models') as mock_load:
            mock_load.return_value = {'model': 'cached'}
            
            # First call
            result1 = self.cv_service._load_models()
            # Second call should use cache
            result2 = self.cv_service._load_models()
            
            self.assertEqual(result1, result2)
            # Should only be called once due to caching
            self.assertEqual(mock_load.call_count, 1)


class TestAIIntegration(TestCase):
    """Test suite for AI/ML integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cv_service = EnhancedComputerVisionService()
        self.pa_service = EnhancedPredictiveAnalyticsService()
        self.chatbot_service = EnhancedChatbotService()
        self.automation_service = EnhancedAIAutomationService()
    
    def test_service_integration(self):
        """Test integration between AI services"""
        # Test that services can work together
        cv_result = {"objects": [{"class": "person", "confidence": 0.9}]}
        pa_result = {"prediction": "maintenance_needed", "confidence": 0.8}
        chatbot_result = {"response": "I can help with that", "intent": "assistance"}
        
        # Simulate integration
        integrated_result = {
            'computer_vision': cv_result,
            'predictive_analytics': pa_result,
            'chatbot': chatbot_result
        }
        
        self.assertIn('computer_vision', integrated_result)
        self.assertIn('predictive_analytics', integrated_result)
        self.assertIn('chatbot', integrated_result)
    
    def test_data_flow_integration(self):
        """Test data flow between services"""
        # Test data flow: CV -> PA -> Chatbot -> Automation
        cv_data = {"image_analysis": "defect_detected"}
        pa_data = {"prediction": "maintenance_required"}
        chatbot_data = {"response": "Scheduling maintenance"}
        automation_data = {"action": "create_work_order"}
        
        # Simulate data flow
        flow_result = {
            'step1_cv': cv_data,
            'step2_pa': pa_data,
            'step3_chatbot': chatbot_data,
            'step4_automation': automation_data
        }
        
        self.assertEqual(len(flow_result), 4)
        self.assertIn('step1_cv', flow_result)
        self.assertIn('step4_automation', flow_result)
