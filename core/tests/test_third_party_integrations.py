"""
Third-Party Integration Testing Suite
Comprehensive testing for external service integrations
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from unittest.mock import patch, Mock
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
from apps.integrations.models import Integration, Webhook

User = get_user_model()
logger = logging.getLogger(__name__)


class ThirdPartyIntegrationTestSuite:
    """Comprehensive third-party integration testing suite"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = []
        self.integration_tests = []
        
    def run_all_integration_tests(self):
        """Run all third-party integration tests"""
        logger.info("🔌 Starting Third-Party Integration Test Suite")
        logger.info("=" * 60)
        
        try:
            # Payment Gateway Integration Tests
            self.test_payment_gateway_integrations()
            
            # Email Service Integration Tests
            self.test_email_service_integrations()
            
            # SMS Service Integration Tests
            self.test_sms_service_integrations()
            
            # Cloud Storage Integration Tests
            self.test_cloud_storage_integrations()
            
            # Analytics Service Integration Tests
            self.test_analytics_service_integrations()
            
            # CRM Integration Tests
            self.test_crm_integrations()
            
            # Webhook Integration Tests
            self.test_webhook_integrations()
            
            # API Integration Tests
            self.test_api_integrations()
            
            # Generate integration report
            self.generate_integration_report()
            
        except Exception as e:
            logger.error(f"❌ Integration test suite failed: {e}")
            return False
            
        return True
    
    def test_payment_gateway_integrations(self):
        """Test payment gateway integrations"""
        logger.info("\n💳 Testing Payment Gateway Integrations...")
        
        payment_tests = [
            {
                "name": "Stripe Integration",
                "test": self.test_stripe_integration
            },
            {
                "name": "PayPal Integration",
                "test": self.test_paypal_integration
            },
            {
                "name": "Square Integration",
                "test": self.test_square_integration
            },
            {
                "name": "Payment Processing",
                "test": self.test_payment_processing
            },
            {
                "name": "Refund Processing",
                "test": self.test_refund_processing
            }
        ]
        
        for test in payment_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "Payment Gateway",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "Payment Gateway",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_stripe_integration(self):
        """Test Stripe payment integration"""
        try:
            # Test Stripe API connection
            response = requests.get(f"{self.base_url}/api/v1/payments/stripe/status/")
            if response.status_code == 200:
                logger.info("    ✅ Stripe API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Stripe API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Stripe integration test failed: {e}")
            return False
    
    def test_paypal_integration(self):
        """Test PayPal payment integration"""
        try:
            # Test PayPal API connection
            response = requests.get(f"{self.base_url}/api/v1/payments/paypal/status/")
            if response.status_code == 200:
                logger.info("    ✅ PayPal API connection successful")
                return True
            else:
                logger.warning("    ⚠️ PayPal API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ PayPal integration test failed: {e}")
            return False
    
    def test_square_integration(self):
        """Test Square payment integration"""
        try:
            # Test Square API connection
            response = requests.get(f"{self.base_url}/api/v1/payments/square/status/")
            if response.status_code == 200:
                logger.info("    ✅ Square API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Square API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Square integration test failed: {e}")
            return False
    
    def test_payment_processing(self):
        """Test payment processing"""
        try:
            # Test payment processing endpoint
            payment_data = {
                "amount": 1000,  # $10.00
                "currency": "usd",
                "payment_method": "card",
                "description": "Test payment"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/payments/process/", json=payment_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ Payment processing successful")
                return True
            else:
                logger.warning("    ⚠️ Payment processing failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Payment processing test failed: {e}")
            return False
    
    def test_refund_processing(self):
        """Test refund processing"""
        try:
            # Test refund processing endpoint
            refund_data = {
                "payment_id": "test_payment_123",
                "amount": 500,  # $5.00
                "reason": "Test refund"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/payments/refund/", json=refund_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ Refund processing successful")
                return True
            else:
                logger.warning("    ⚠️ Refund processing failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Refund processing test failed: {e}")
            return False
    
    def test_email_service_integrations(self):
        """Test email service integrations"""
        logger.info("\n📧 Testing Email Service Integrations...")
        
        email_tests = [
            {
                "name": "SendGrid Integration",
                "test": self.test_sendgrid_integration
            },
            {
                "name": "Mailgun Integration",
                "test": self.test_mailgun_integration
            },
            {
                "name": "AWS SES Integration",
                "test": self.test_aws_ses_integration
            },
            {
                "name": "Email Sending",
                "test": self.test_email_sending
            },
            {
                "name": "Email Templates",
                "test": self.test_email_templates
            }
        ]
        
        for test in email_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "Email Service",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "Email Service",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_sendgrid_integration(self):
        """Test SendGrid email integration"""
        try:
            # Test SendGrid API connection
            response = requests.get(f"{self.base_url}/api/v1/email/sendgrid/status/")
            if response.status_code == 200:
                logger.info("    ✅ SendGrid API connection successful")
                return True
            else:
                logger.warning("    ⚠️ SendGrid API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ SendGrid integration test failed: {e}")
            return False
    
    def test_mailgun_integration(self):
        """Test Mailgun email integration"""
        try:
            # Test Mailgun API connection
            response = requests.get(f"{self.base_url}/api/v1/email/mailgun/status/")
            if response.status_code == 200:
                logger.info("    ✅ Mailgun API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Mailgun API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Mailgun integration test failed: {e}")
            return False
    
    def test_aws_ses_integration(self):
        """Test AWS SES email integration"""
        try:
            # Test AWS SES API connection
            response = requests.get(f"{self.base_url}/api/v1/email/aws-ses/status/")
            if response.status_code == 200:
                logger.info("    ✅ AWS SES API connection successful")
                return True
            else:
                logger.warning("    ⚠️ AWS SES API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ AWS SES integration test failed: {e}")
            return False
    
    def test_email_sending(self):
        """Test email sending functionality"""
        try:
            # Test email sending endpoint
            email_data = {
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email",
                "template": "test_template"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/email/send/", json=email_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ Email sending successful")
                return True
            else:
                logger.warning("    ⚠️ Email sending failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Email sending test failed: {e}")
            return False
    
    def test_email_templates(self):
        """Test email template functionality"""
        try:
            # Test email template endpoint
            response = requests.get(f"{self.base_url}/api/v1/email/templates/")
            if response.status_code == 200:
                logger.info("    ✅ Email templates accessible")
                return True
            else:
                logger.warning("    ⚠️ Email templates not accessible")
                return False
        except Exception as e:
            logger.error(f"    ❌ Email templates test failed: {e}")
            return False
    
    def test_sms_service_integrations(self):
        """Test SMS service integrations"""
        logger.info("\n📱 Testing SMS Service Integrations...")
        
        sms_tests = [
            {
                "name": "Twilio Integration",
                "test": self.test_twilio_integration
            },
            {
                "name": "AWS SNS Integration",
                "test": self.test_aws_sns_integration
            },
            {
                "name": "SMS Sending",
                "test": self.test_sms_sending
            },
            {
                "name": "SMS Templates",
                "test": self.test_sms_templates
            }
        ]
        
        for test in sms_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "SMS Service",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "SMS Service",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_twilio_integration(self):
        """Test Twilio SMS integration"""
        try:
            # Test Twilio API connection
            response = requests.get(f"{self.base_url}/api/v1/sms/twilio/status/")
            if response.status_code == 200:
                logger.info("    ✅ Twilio API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Twilio API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Twilio integration test failed: {e}")
            return False
    
    def test_aws_sns_integration(self):
        """Test AWS SNS SMS integration"""
        try:
            # Test AWS SNS API connection
            response = requests.get(f"{self.base_url}/api/v1/sms/aws-sns/status/")
            if response.status_code == 200:
                logger.info("    ✅ AWS SNS API connection successful")
                return True
            else:
                logger.warning("    ⚠️ AWS SNS API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ AWS SNS integration test failed: {e}")
            return False
    
    def test_sms_sending(self):
        """Test SMS sending functionality"""
        try:
            # Test SMS sending endpoint
            sms_data = {
                "to": "+1234567890",
                "message": "Test SMS message",
                "template": "test_template"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/sms/send/", json=sms_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ SMS sending successful")
                return True
            else:
                logger.warning("    ⚠️ SMS sending failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ SMS sending test failed: {e}")
            return False
    
    def test_sms_templates(self):
        """Test SMS template functionality"""
        try:
            # Test SMS template endpoint
            response = requests.get(f"{self.base_url}/api/v1/sms/templates/")
            if response.status_code == 200:
                logger.info("    ✅ SMS templates accessible")
                return True
            else:
                logger.warning("    ⚠️ SMS templates not accessible")
                return False
        except Exception as e:
            logger.error(f"    ❌ SMS templates test failed: {e}")
            return False
    
    def test_cloud_storage_integrations(self):
        """Test cloud storage integrations"""
        logger.info("\n☁️ Testing Cloud Storage Integrations...")
        
        storage_tests = [
            {
                "name": "AWS S3 Integration",
                "test": self.test_aws_s3_integration
            },
            {
                "name": "Google Cloud Storage Integration",
                "test": self.test_gcs_integration
            },
            {
                "name": "Azure Blob Storage Integration",
                "test": self.test_azure_blob_integration
            },
            {
                "name": "File Upload",
                "test": self.test_file_upload
            },
            {
                "name": "File Download",
                "test": self.test_file_download
            }
        ]
        
        for test in storage_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "Cloud Storage",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "Cloud Storage",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_aws_s3_integration(self):
        """Test AWS S3 storage integration"""
        try:
            # Test AWS S3 API connection
            response = requests.get(f"{self.base_url}/api/v1/storage/aws-s3/status/")
            if response.status_code == 200:
                logger.info("    ✅ AWS S3 API connection successful")
                return True
            else:
                logger.warning("    ⚠️ AWS S3 API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ AWS S3 integration test failed: {e}")
            return False
    
    def test_gcs_integration(self):
        """Test Google Cloud Storage integration"""
        try:
            # Test GCS API connection
            response = requests.get(f"{self.base_url}/api/v1/storage/gcs/status/")
            if response.status_code == 200:
                logger.info("    ✅ GCS API connection successful")
                return True
            else:
                logger.warning("    ⚠️ GCS API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ GCS integration test failed: {e}")
            return False
    
    def test_azure_blob_integration(self):
        """Test Azure Blob Storage integration"""
        try:
            # Test Azure Blob API connection
            response = requests.get(f"{self.base_url}/api/v1/storage/azure-blob/status/")
            if response.status_code == 200:
                logger.info("    ✅ Azure Blob API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Azure Blob API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Azure Blob integration test failed: {e}")
            return False
    
    def test_file_upload(self):
        """Test file upload functionality"""
        try:
            # Test file upload endpoint
            files = {'file': ('test.txt', 'Test file content', 'text/plain')}
            response = requests.post(f"{self.base_url}/api/v1/storage/upload/", files=files)
            if response.status_code in [200, 201]:
                logger.info("    ✅ File upload successful")
                return True
            else:
                logger.warning("    ⚠️ File upload failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ File upload test failed: {e}")
            return False
    
    def test_file_download(self):
        """Test file download functionality"""
        try:
            # Test file download endpoint
            response = requests.get(f"{self.base_url}/api/v1/storage/download/test.txt")
            if response.status_code == 200:
                logger.info("    ✅ File download successful")
                return True
            else:
                logger.warning("    ⚠️ File download failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ File download test failed: {e}")
            return False
    
    def test_analytics_service_integrations(self):
        """Test analytics service integrations"""
        logger.info("\n📊 Testing Analytics Service Integrations...")
        
        analytics_tests = [
            {
                "name": "Google Analytics Integration",
                "test": self.test_google_analytics_integration
            },
            {
                "name": "Mixpanel Integration",
                "test": self.test_mixpanel_integration
            },
            {
                "name": "Amplitude Integration",
                "test": self.test_amplitude_integration
            },
            {
                "name": "Analytics Data Collection",
                "test": self.test_analytics_data_collection
            }
        ]
        
        for test in analytics_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "Analytics Service",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "Analytics Service",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_google_analytics_integration(self):
        """Test Google Analytics integration"""
        try:
            # Test Google Analytics API connection
            response = requests.get(f"{self.base_url}/api/v1/analytics/google/status/")
            if response.status_code == 200:
                logger.info("    ✅ Google Analytics API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Google Analytics API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Google Analytics integration test failed: {e}")
            return False
    
    def test_mixpanel_integration(self):
        """Test Mixpanel integration"""
        try:
            # Test Mixpanel API connection
            response = requests.get(f"{self.base_url}/api/v1/analytics/mixpanel/status/")
            if response.status_code == 200:
                logger.info("    ✅ Mixpanel API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Mixpanel API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Mixpanel integration test failed: {e}")
            return False
    
    def test_amplitude_integration(self):
        """Test Amplitude integration"""
        try:
            # Test Amplitude API connection
            response = requests.get(f"{self.base_url}/api/v1/analytics/amplitude/status/")
            if response.status_code == 200:
                logger.info("    ✅ Amplitude API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Amplitude API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Amplitude integration test failed: {e}")
            return False
    
    def test_analytics_data_collection(self):
        """Test analytics data collection"""
        try:
            # Test analytics data collection endpoint
            analytics_data = {
                "event": "test_event",
                "properties": {
                    "user_id": "test_user",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(f"{self.base_url}/api/v1/analytics/track/", json=analytics_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ Analytics data collection successful")
                return True
            else:
                logger.warning("    ⚠️ Analytics data collection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Analytics data collection test failed: {e}")
            return False
    
    def test_crm_integrations(self):
        """Test CRM integrations"""
        logger.info("\n👥 Testing CRM Integrations...")
        
        crm_tests = [
            {
                "name": "Salesforce Integration",
                "test": self.test_salesforce_integration
            },
            {
                "name": "HubSpot Integration",
                "test": self.test_hubspot_integration
            },
            {
                "name": "Pipedrive Integration",
                "test": self.test_pipedrive_integration
            },
            {
                "name": "CRM Data Sync",
                "test": self.test_crm_data_sync
            }
        ]
        
        for test in crm_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "CRM",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "CRM",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_salesforce_integration(self):
        """Test Salesforce CRM integration"""
        try:
            # Test Salesforce API connection
            response = requests.get(f"{self.base_url}/api/v1/crm/salesforce/status/")
            if response.status_code == 200:
                logger.info("    ✅ Salesforce API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Salesforce API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Salesforce integration test failed: {e}")
            return False
    
    def test_hubspot_integration(self):
        """Test HubSpot CRM integration"""
        try:
            # Test HubSpot API connection
            response = requests.get(f"{self.base_url}/api/v1/crm/hubspot/status/")
            if response.status_code == 200:
                logger.info("    ✅ HubSpot API connection successful")
                return True
            else:
                logger.warning("    ⚠️ HubSpot API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ HubSpot integration test failed: {e}")
            return False
    
    def test_pipedrive_integration(self):
        """Test Pipedrive CRM integration"""
        try:
            # Test Pipedrive API connection
            response = requests.get(f"{self.base_url}/api/v1/crm/pipedrive/status/")
            if response.status_code == 200:
                logger.info("    ✅ Pipedrive API connection successful")
                return True
            else:
                logger.warning("    ⚠️ Pipedrive API connection failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Pipedrive integration test failed: {e}")
            return False
    
    def test_crm_data_sync(self):
        """Test CRM data synchronization"""
        try:
            # Test CRM data sync endpoint
            sync_data = {
                "source": "helpdesk",
                "target": "crm",
                "data_type": "contact"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/crm/sync/", json=sync_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ CRM data sync successful")
                return True
            else:
                logger.warning("    ⚠️ CRM data sync failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ CRM data sync test failed: {e}")
            return False
    
    def test_webhook_integrations(self):
        """Test webhook integrations"""
        logger.info("\n🔗 Testing Webhook Integrations...")
        
        webhook_tests = [
            {
                "name": "Webhook Registration",
                "test": self.test_webhook_registration
            },
            {
                "name": "Webhook Delivery",
                "test": self.test_webhook_delivery
            },
            {
                "name": "Webhook Retry Logic",
                "test": self.test_webhook_retry
            },
            {
                "name": "Webhook Security",
                "test": self.test_webhook_security
            }
        ]
        
        for test in webhook_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "Webhook",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "Webhook",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_webhook_registration(self):
        """Test webhook registration"""
        try:
            # Test webhook registration endpoint
            webhook_data = {
                "url": "https://example.com/webhook",
                "events": ["ticket.created", "ticket.updated"],
                "secret": "test_secret"
            }
            
            response = requests.post(f"{self.base_url}/api/v1/webhooks/", json=webhook_data)
            if response.status_code in [200, 201]:
                logger.info("    ✅ Webhook registration successful")
                return True
            else:
                logger.warning("    ⚠️ Webhook registration failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Webhook registration test failed: {e}")
            return False
    
    def test_webhook_delivery(self):
        """Test webhook delivery"""
        try:
            # Test webhook delivery
            response = requests.post(f"{self.base_url}/api/v1/webhooks/test/")
            if response.status_code in [200, 201]:
                logger.info("    ✅ Webhook delivery successful")
                return True
            else:
                logger.warning("    ⚠️ Webhook delivery failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Webhook delivery test failed: {e}")
            return False
    
    def test_webhook_retry(self):
        """Test webhook retry logic"""
        try:
            # Test webhook retry logic
            response = requests.post(f"{self.base_url}/api/v1/webhooks/retry/")
            if response.status_code in [200, 201]:
                logger.info("    ✅ Webhook retry logic successful")
                return True
            else:
                logger.warning("    ⚠️ Webhook retry logic failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Webhook retry test failed: {e}")
            return False
    
    def test_webhook_security(self):
        """Test webhook security"""
        try:
            # Test webhook security
            response = requests.get(f"{self.base_url}/api/v1/webhooks/security/")
            if response.status_code == 200:
                logger.info("    ✅ Webhook security successful")
                return True
            else:
                logger.warning("    ⚠️ Webhook security failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ Webhook security test failed: {e}")
            return False
    
    def test_api_integrations(self):
        """Test API integrations"""
        logger.info("\n🔌 Testing API Integrations...")
        
        api_tests = [
            {
                "name": "REST API Integration",
                "test": self.test_rest_api_integration
            },
            {
                "name": "GraphQL API Integration",
                "test": self.test_graphql_api_integration
            },
            {
                "name": "API Rate Limiting",
                "test": self.test_api_rate_limiting
            },
            {
                "name": "API Authentication",
                "test": self.test_api_authentication
            }
        ]
        
        for test in api_tests:
            try:
                logger.info(f"  Testing: {test['name']}")
                result = test['test']()
                self.test_results.append({
                    "category": "API",
                    "test": test['name'],
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"    ❌ {test['name']} failed: {e}")
                self.test_results.append({
                    "category": "API",
                    "test": test['name'],
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
    
    def test_rest_api_integration(self):
        """Test REST API integration"""
        try:
            # Test REST API endpoints
            endpoints = [
                "/api/v1/health/",
                "/api/v1/tickets/",
                "/api/v1/users/",
                "/api/v1/organizations/"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code not in [200, 401, 403]:  # 401/403 are acceptable for protected endpoints
                    return False
            
            logger.info("    ✅ REST API integration successful")
            return True
        except Exception as e:
            logger.error(f"    ❌ REST API integration test failed: {e}")
            return False
    
    def test_graphql_api_integration(self):
        """Test GraphQL API integration"""
        try:
            # Test GraphQL API endpoint
            response = requests.post(f"{self.base_url}/graphql/", json={
                "query": "{ __schema { types { name } } }"
            })
            if response.status_code in [200, 401, 403]:  # 401/403 are acceptable for protected endpoints
                logger.info("    ✅ GraphQL API integration successful")
                return True
            else:
                logger.warning("    ⚠️ GraphQL API integration failed")
                return False
        except Exception as e:
            logger.error(f"    ❌ GraphQL API integration test failed: {e}")
            return False
    
    def test_api_rate_limiting(self):
        """Test API rate limiting"""
        try:
            # Test API rate limiting
            for i in range(100):  # Make many requests
                response = requests.get(f"{self.base_url}/api/v1/health/")
                if response.status_code == 429:  # Rate limited
                    logger.info("    ✅ API rate limiting working")
                    return True
            
            logger.warning("    ⚠️ API rate limiting not working")
            return False
        except Exception as e:
            logger.error(f"    ❌ API rate limiting test failed: {e}")
            return False
    
    def test_api_authentication(self):
        """Test API authentication"""
        try:
            # Test API authentication
            response = requests.get(f"{self.base_url}/api/v1/tickets/")
            if response.status_code == 401:  # Unauthorized
                logger.info("    ✅ API authentication working")
                return True
            else:
                logger.warning("    ⚠️ API authentication not working")
                return False
        except Exception as e:
            logger.error(f"    ❌ API authentication test failed: {e}")
            return False
    
    def generate_integration_report(self):
        """Generate comprehensive integration report"""
        logger.info("\n📊 Generating Integration Report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASSED'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAILED'])
        
        # Categorize results
        categories = {}
        for result in self.test_results:
            category = result['category']
            if category not in categories:
                categories[category] = {'total': 0, 'passed': 0, 'failed': 0}
            categories[category]['total'] += 1
            if result['status'] == 'PASSED':
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        # Generate report
        report = {
            "test_suite": "Third-Party Integration Test Suite",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "categories": categories,
            "test_results": self.test_results
        }
        
        # Save report to file
        report_file = f"integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("🔌 INTEGRATION TEST RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {passed_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📊 Success Rate: {report['summary']['success_rate']:.2f}%")
        logger.info(f"📄 Report saved to: {report_file}")
        
        # Print category results
        for category, stats in categories.items():
            logger.info(f"\n📋 {category}:")
            logger.info(f"  Total: {stats['total']}")
            logger.info(f"  ✅ Passed: {stats['passed']}")
            logger.info(f"  ❌ Failed: {stats['failed']}")
            logger.info(f"  📊 Success Rate: {(stats['passed'] / stats['total'] * 100):.2f}%")
        
        if report['summary']['success_rate'] >= 90:
            logger.info("🎉 Excellent! Integration is well implemented.")
        elif report['summary']['success_rate'] >= 75:
            logger.info("✅ Good! Integration is mostly implemented.")
        elif report['summary']['success_rate'] >= 50:
            logger.info("⚠️ Fair! Integration needs improvement.")
        else:
            logger.info("❌ Poor! Integration needs significant improvements.")
        
        return report


def main():
    """Main function to run integration tests"""
    print("🔌 Third-Party Integration Test Suite")
    print("=" * 40)
    
    # Run integration test suite
    test_suite = ThirdPartyIntegrationTestSuite()
    success = test_suite.run_all_integration_tests()
    
    if success:
        print("\n✅ Integration test suite completed successfully!")
    else:
        print("\n❌ Integration test suite encountered errors!")
    
    return success


if __name__ == "__main__":
    main()
