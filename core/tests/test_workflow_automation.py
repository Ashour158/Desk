"""
Comprehensive Workflow Automation Engine Tests
Tests critical workflow automation logic including execution, validation, and error handling.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from decimal import Decimal

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.tickets.models import Ticket
from apps.automation.models import AutomationRule, Workflow, WorkflowStep, WorkflowExecution
from apps.automation.engine import WorkflowEngine
from apps.field_service.models import WorkOrder, Technician
from apps.notifications.models import Notification

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class WorkflowEngineTest(EnhancedTransactionTestCase):
    """Test Workflow Engine with comprehensive automation logic coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.workflow_engine = WorkflowEngine()
        
        # Create test workflow
        self.workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            description="Test workflow for automation testing",
            is_active=True,
            trigger_conditions={
                'event': 'ticket_created',
                'priority': 'high'
            }
        )
        
        # Create workflow steps
        self.step1 = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Assign Ticket",
            step_type="action",
            step_order=1,
            step_config={
                'action': 'assign_ticket',
                'assignee': 'auto'
            }
        )
        
        self.step2 = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Send Notification",
            step_type="notification",
            step_order=2,
            step_config={
                'notification_type': 'email',
                'template': 'ticket_assigned'
            }
        )
        
        # Create test ticket
        self.ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Workflow Ticket",
            description="Test ticket for workflow automation",
            priority="high",
            status="open"
        )
    
    def test_execute_workflow_success(self):
        """Test successful workflow execution."""
        with patch.object(self.workflow_engine, '_execute_step') as mock_execute:
            mock_execute.return_value = {'status': 'success', 'result': 'completed'}
            
            result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
            
            self.assertIn('status', result)
            self.assertIn('execution_id', result)
            self.assertEqual(result['status'], 'success')
            self.assertEqual(mock_execute.call_count, 2)  # Two steps
    
    def test_execute_workflow_step_failure(self):
        """Test workflow execution with step failure."""
        with patch.object(self.workflow_engine, '_execute_step') as mock_execute:
            # First step succeeds, second fails
            mock_execute.side_effect = [
                {'status': 'success', 'result': 'completed'},
                {'status': 'error', 'result': 'step_failed'}
            ]
            
            result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
            
            self.assertIn('status', result)
            self.assertIn('error', result)
            self.assertEqual(result['status'], 'error')
    
    def test_execute_workflow_inactive_workflow(self):
        """Test workflow execution with inactive workflow."""
        # Deactivate workflow
        self.workflow.is_active = False
        self.workflow.save()
        
        result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
        
        self.assertIn('error', result)
        self.assertIn('Workflow is not active', result['error'])
    
    def test_execute_workflow_no_steps(self):
        """Test workflow execution with no steps."""
        # Delete all steps
        WorkflowStep.objects.filter(workflow=self.workflow).delete()
        
        result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
        
        self.assertIn('error', result)
        self.assertIn('No steps found', result['error'])
    
    def test_validate_workflow_success(self):
        """Test successful workflow validation."""
        result = self.workflow_engine.validate_workflow(self.workflow)
        
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_workflow_missing_steps(self):
        """Test workflow validation with missing steps."""
        # Delete all steps
        WorkflowStep.objects.filter(workflow=self.workflow).delete()
        
        result = self.workflow_engine.validate_workflow(self.workflow)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('No steps found', result['errors'])
    
    def test_validate_workflow_invalid_step_config(self):
        """Test workflow validation with invalid step configuration."""
        # Update step with invalid config
        self.step1.step_config = {'invalid': 'config'}
        self.step1.save()
        
        result = self.workflow_engine.validate_workflow(self.workflow)
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_validate_workflow_duplicate_step_order(self):
        """Test workflow validation with duplicate step order."""
        # Create duplicate step order
        WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Duplicate Step",
            step_type="action",
            step_order=1,  # Same order as step1
            step_config={'action': 'test'}
        )
        
        result = self.workflow_engine.validate_workflow(self.workflow)
        
        self.assertFalse(result['is_valid'])
        self.assertIn('Duplicate step order', result['errors'])
    
    def test_handle_workflow_errors_success(self):
        """Test successful workflow error handling."""
        error = Exception("Test error")
        
        with patch.object(self.workflow_engine, '_log_error') as mock_log:
            result = self.workflow_engine.handle_workflow_errors(error, self.workflow, self.ticket)
            
            self.assertIn('status', result)
            self.assertIn('error_handled', result)
            self.assertTrue(result['error_handled'])
            mock_log.assert_called_once()
    
    def test_handle_workflow_errors_critical(self):
        """Test workflow error handling for critical errors."""
        error = Exception("Critical system error")
        
        with patch.object(self.workflow_engine, '_log_error') as mock_log:
            with patch.object(self.workflow_engine, '_notify_admins') as mock_notify:
                result = self.workflow_engine.handle_workflow_errors(error, self.workflow, self.ticket)
                
                self.assertIn('status', result)
                self.assertIn('error_handled', result)
                self.assertTrue(result['error_handled'])
                mock_log.assert_called_once()
                mock_notify.assert_called_once()
    
    def test_execute_step_action_success(self):
        """Test successful action step execution."""
        step_config = {
            'action': 'assign_ticket',
            'assignee': 'auto'
        }
        
        with patch.object(self.workflow_engine, '_assign_ticket') as mock_assign:
            mock_assign.return_value = {'status': 'success', 'assigned_to': 'agent_123'}
            
            result = self.workflow_engine._execute_step(self.step1, self.ticket)
            
            self.assertEqual(result['status'], 'success')
            mock_assign.assert_called_once_with(self.ticket, step_config)
    
    def test_execute_step_notification_success(self):
        """Test successful notification step execution."""
        step_config = {
            'notification_type': 'email',
            'template': 'ticket_assigned'
        }
        
        with patch.object(self.workflow_engine, '_send_notification') as mock_notify:
            mock_notify.return_value = {'status': 'success', 'sent': True}
            
            result = self.workflow_engine._execute_step(self.step2, self.ticket)
            
            self.assertEqual(result['status'], 'success')
            mock_notify.assert_called_once_with(self.ticket, step_config)
    
    def test_execute_step_condition_success(self):
        """Test successful condition step execution."""
        # Create condition step
        condition_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Check Priority",
            step_type="condition",
            step_order=3,
            step_config={
                'condition': 'priority_equals',
                'value': 'high'
            }
        )
        
        with patch.object(self.workflow_engine, '_evaluate_condition') as mock_evaluate:
            mock_evaluate.return_value = True
            
            result = self.workflow_engine._execute_step(condition_step, self.ticket)
            
            self.assertEqual(result['status'], 'success')
            self.assertTrue(result['condition_met'])
            mock_evaluate.assert_called_once_with(self.ticket, condition_step.step_config)
    
    def test_execute_step_condition_failure(self):
        """Test condition step execution with false condition."""
        # Create condition step
        condition_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Check Priority",
            step_type="condition",
            step_order=3,
            step_config={
                'condition': 'priority_equals',
                'value': 'low'
            }
        )
        
        with patch.object(self.workflow_engine, '_evaluate_condition') as mock_evaluate:
            mock_evaluate.return_value = False
            
            result = self.workflow_engine._execute_step(condition_step, self.ticket)
            
            self.assertEqual(result['status'], 'skipped')
            self.assertFalse(result['condition_met'])
    
    def test_execute_step_unknown_type(self):
        """Test step execution with unknown step type."""
        # Create step with unknown type
        unknown_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Unknown Step",
            step_type="unknown",
            step_order=3,
            step_config={}
        )
        
        result = self.workflow_engine._execute_step(unknown_step, self.ticket)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unknown step type', result['error'])
    
    def test_assign_ticket_auto_success(self):
        """Test automatic ticket assignment."""
        step_config = {
            'action': 'assign_ticket',
            'assignee': 'auto'
        }
        
        with patch.object(self.workflow_engine, '_find_best_assignee') as mock_find:
            mock_find.return_value = 'agent_123'
            
            with patch.object(self.workflow_engine, '_assign_ticket_to_agent') as mock_assign:
                mock_assign.return_value = {'status': 'success'}
                
                result = self.workflow_engine._assign_ticket(self.ticket, step_config)
                
                self.assertEqual(result['status'], 'success')
                mock_find.assert_called_once_with(self.ticket)
                mock_assign.assert_called_once_with(self.ticket, 'agent_123')
    
    def test_assign_ticket_specific_agent(self):
        """Test ticket assignment to specific agent."""
        step_config = {
            'action': 'assign_ticket',
            'assignee': 'agent_456'
        }
        
        with patch.object(self.workflow_engine, '_assign_ticket_to_agent') as mock_assign:
            mock_assign.return_value = {'status': 'success'}
            
            result = self.workflow_engine._assign_ticket(self.ticket, step_config)
            
            self.assertEqual(result['status'], 'success')
            mock_assign.assert_called_once_with(self.ticket, 'agent_456')
    
    def test_assign_ticket_agent_not_found(self):
        """Test ticket assignment with agent not found."""
        step_config = {
            'action': 'assign_ticket',
            'assignee': 'nonexistent_agent'
        }
        
        with patch.object(self.workflow_engine, '_assign_ticket_to_agent') as mock_assign:
            mock_assign.side_effect = Exception("Agent not found")
            
            result = self.workflow_engine._assign_ticket(self.ticket, step_config)
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('Agent not found', result['error'])
    
    def test_send_notification_email_success(self):
        """Test successful email notification."""
        step_config = {
            'notification_type': 'email',
            'template': 'ticket_assigned',
            'recipients': ['user@example.com']
        }
        
        with patch.object(self.workflow_engine, '_send_email_notification') as mock_send:
            mock_send.return_value = {'status': 'success', 'sent': True}
            
            result = self.workflow_engine._send_notification(self.ticket, step_config)
            
            self.assertEqual(result['status'], 'success')
            mock_send.assert_called_once_with(self.ticket, step_config)
    
    def test_send_notification_sms_success(self):
        """Test successful SMS notification."""
        step_config = {
            'notification_type': 'sms',
            'template': 'ticket_assigned',
            'recipients': ['+1234567890']
        }
        
        with patch.object(self.workflow_engine, '_send_sms_notification') as mock_send:
            mock_send.return_value = {'status': 'success', 'sent': True}
            
            result = self.workflow_engine._send_notification(self.ticket, step_config)
            
            self.assertEqual(result['status'], 'success')
            mock_send.assert_called_once_with(self.ticket, step_config)
    
    def test_send_notification_push_success(self):
        """Test successful push notification."""
        step_config = {
            'notification_type': 'push',
            'template': 'ticket_assigned',
            'recipients': ['user_123']
        }
        
        with patch.object(self.workflow_engine, '_send_push_notification') as mock_send:
            mock_send.return_value = {'status': 'success', 'sent': True}
            
            result = self.workflow_engine._send_notification(self.ticket, step_config)
            
            self.assertEqual(result['status'], 'success')
            mock_send.assert_called_once_with(self.ticket, step_config)
    
    def test_send_notification_unknown_type(self):
        """Test notification with unknown type."""
        step_config = {
            'notification_type': 'unknown',
            'template': 'ticket_assigned'
        }
        
        result = self.workflow_engine._send_notification(self.ticket, step_config)
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Unknown notification type', result['error'])
    
    def test_evaluate_condition_priority_equals(self):
        """Test condition evaluation for priority equals."""
        condition_config = {
            'condition': 'priority_equals',
            'value': 'high'
        }
        
        result = self.workflow_engine._evaluate_condition(self.ticket, condition_config)
        
        self.assertTrue(result)
    
    def test_evaluate_condition_priority_not_equals(self):
        """Test condition evaluation for priority not equals."""
        condition_config = {
            'condition': 'priority_equals',
            'value': 'low'
        }
        
        result = self.workflow_engine._evaluate_condition(self.ticket, condition_config)
        
        self.assertFalse(result)
    
    def test_evaluate_condition_status_equals(self):
        """Test condition evaluation for status equals."""
        condition_config = {
            'condition': 'status_equals',
            'value': 'open'
        }
        
        result = self.workflow_engine._evaluate_condition(self.ticket, condition_config)
        
        self.assertTrue(result)
    
    def test_evaluate_condition_custom_field(self):
        """Test condition evaluation for custom field."""
        condition_config = {
            'condition': 'custom_field_equals',
            'field': 'department',
            'value': 'IT'
        }
        
        # Set custom field
        self.ticket.custom_fields = {'department': 'IT'}
        self.ticket.save()
        
        result = self.workflow_engine._evaluate_condition(self.ticket, condition_config)
        
        self.assertTrue(result)
    
    def test_evaluate_condition_unknown_condition(self):
        """Test condition evaluation with unknown condition."""
        condition_config = {
            'condition': 'unknown_condition',
            'value': 'test'
        }
        
        result = self.workflow_engine._evaluate_condition(self.ticket, condition_config)
        
        self.assertFalse(result)
    
    def test_find_best_assignee_by_skills(self):
        """Test finding best assignee by skills."""
        # Create technician with matching skills
        technician = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Test Technician",
            skills=["technical", "hardware"],
            is_active=True
        )
        
        with patch.object(self.workflow_engine, '_get_ticket_required_skills') as mock_skills:
            mock_skills.return_value = ["technical", "hardware"]
            
            with patch.object(self.workflow_engine, '_get_available_technicians') as mock_available:
                mock_available.return_value = [technician]
                
                result = self.workflow_engine._find_best_assignee(self.ticket)
                
                self.assertEqual(result, technician.id)
    
    def test_find_best_assignee_by_workload(self):
        """Test finding best assignee by workload."""
        # Create technicians with different workloads
        technician1 = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Technician 1",
            skills=["technical"],
            is_active=True
        )
        
        technician2 = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Technician 2",
            skills=["technical"],
            is_active=True
        )
        
        with patch.object(self.workflow_engine, '_get_available_technicians') as mock_available:
            mock_available.return_value = [technician1, technician2]
            
            with patch.object(self.workflow_engine, '_get_technician_workload') as mock_workload:
                mock_workload.side_effect = [5, 3]  # technician2 has lighter workload
                
                result = self.workflow_engine._find_best_assignee(self.ticket)
                
                self.assertEqual(result, technician2.id)
    
    def test_find_best_assignee_no_available(self):
        """Test finding best assignee when none available."""
        with patch.object(self.workflow_engine, '_get_available_technicians') as mock_available:
            mock_available.return_value = []
            
            result = self.workflow_engine._find_best_assignee(self.ticket)
            
            self.assertIsNone(result)
    
    def test_workflow_execution_logging(self):
        """Test workflow execution logging."""
        with patch.object(self.workflow_engine, '_log_execution') as mock_log:
            self.workflow_engine.execute_workflow(self.workflow, self.ticket)
            
            mock_log.assert_called_once()
    
    def test_workflow_execution_metrics(self):
        """Test workflow execution metrics collection."""
        with patch.object(self.workflow_engine, '_collect_metrics') as mock_metrics:
            self.workflow_engine.execute_workflow(self.workflow, self.ticket)
            
            mock_metrics.assert_called_once()
    
    def test_workflow_execution_timeout(self):
        """Test workflow execution timeout."""
        # Create step that takes too long
        slow_step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Slow Step",
            step_type="action",
            step_order=3,
            step_config={'action': 'slow_operation'}
        )
        
        with patch.object(self.workflow_engine, '_execute_step') as mock_execute:
            mock_execute.side_effect = TimeoutError("Step timeout")
            
            result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
            
            self.assertEqual(result['status'], 'error')
            self.assertIn('timeout', result['error'].lower())
    
    def test_workflow_execution_retry_mechanism(self):
        """Test workflow execution retry mechanism."""
        with patch.object(self.workflow_engine, '_execute_step') as mock_execute:
            # First call fails, second succeeds
            mock_execute.side_effect = [
                {'status': 'error', 'result': 'temporary_failure'},
                {'status': 'success', 'result': 'completed'}
            ]
            
            with patch.object(self.workflow_engine, '_should_retry') as mock_retry:
                mock_retry.return_value = True
                
                result = self.workflow_engine.execute_workflow(self.workflow, self.ticket)
                
                self.assertEqual(result['status'], 'success')
                self.assertEqual(mock_execute.call_count, 2)


class WorkflowModelTest(EnhancedTransactionTestCase):
    """Test Workflow model functionality."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
    
    def test_workflow_creation(self):
        """Test workflow creation with valid data."""
        workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            description="Test workflow description",
            is_active=True,
            trigger_conditions={
                'event': 'ticket_created',
                'priority': 'high'
            }
        )
        
        self.assertEqual(workflow.name, "Test Workflow")
        self.assertTrue(workflow.is_active)
        self.assertIsNotNone(workflow.trigger_conditions)
    
    def test_workflow_string_representation(self):
        """Test workflow string representation."""
        workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            is_active=True
        )
        
        self.assertEqual(str(workflow), "Test Workflow")
    
    def test_workflow_trigger_conditions_validation(self):
        """Test workflow trigger conditions validation."""
        with self.assertRaises(ValueError):
            Workflow.objects.create(
                organization=self.organization,
                name="Invalid Workflow",
                is_active=True,
                trigger_conditions={
                    'invalid_condition': 'test'
                }
            )


class WorkflowStepModelTest(EnhancedTransactionTestCase):
    """Test WorkflowStep model functionality."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            is_active=True
        )
    
    def test_workflow_step_creation(self):
        """Test workflow step creation with valid data."""
        step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Test Step",
            step_type="action",
            step_order=1,
            step_config={
                'action': 'assign_ticket',
                'assignee': 'auto'
            }
        )
        
        self.assertEqual(step.step_name, "Test Step")
        self.assertEqual(step.step_type, "action")
        self.assertEqual(step.step_order, 1)
        self.assertIsNotNone(step.step_config)
    
    def test_workflow_step_string_representation(self):
        """Test workflow step string representation."""
        step = WorkflowStep.objects.create(
            workflow=self.workflow,
            step_name="Test Step",
            step_type="action",
            step_order=1
        )
        
        self.assertEqual(str(step), "Test Step")
    
    def test_workflow_step_config_validation(self):
        """Test workflow step configuration validation."""
        with self.assertRaises(ValueError):
            WorkflowStep.objects.create(
                workflow=self.workflow,
                step_name="Invalid Step",
                step_type="action",
                step_order=1,
                step_config={
                    'invalid_config': 'test'
                }
            )


class WorkflowExecutionModelTest(EnhancedTransactionTestCase):
    """Test WorkflowExecution model functionality."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.workflow = Workflow.objects.create(
            organization=self.organization,
            name="Test Workflow",
            is_active=True
        )
        self.ticket = Ticket.objects.create(
            organization=self.organization,
            customer=self.user,
            subject="Test Ticket",
            description="Test description"
        )
    
    def test_workflow_execution_creation(self):
        """Test workflow execution creation with valid data."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            entity_type="ticket",
            entity_id=self.ticket.id,
            status="running",
            execution_data={
                'ticket_id': self.ticket.id,
                'priority': 'high'
            }
        )
        
        self.assertEqual(execution.workflow, self.workflow)
        self.assertEqual(execution.entity_type, "ticket")
        self.assertEqual(execution.entity_id, self.ticket.id)
        self.assertEqual(execution.status, "running")
        self.assertIsNotNone(execution.execution_data)
    
    def test_workflow_execution_string_representation(self):
        """Test workflow execution string representation."""
        execution = WorkflowExecution.objects.create(
            workflow=self.workflow,
            entity_type="ticket",
            entity_id=self.ticket.id,
            status="running"
        )
        
        self.assertEqual(str(execution), f"WorkflowExecution {execution.id}")


# Export test classes
__all__ = [
    'WorkflowEngineTest',
    'WorkflowModelTest',
    'WorkflowStepModelTest',
    'WorkflowExecutionModelTest'
]
