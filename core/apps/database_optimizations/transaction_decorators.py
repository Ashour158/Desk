"""
Database transaction decorators for critical operations.
"""

from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def atomic_operation(func):
    """
    Decorator for atomic database operations.
    """
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Atomic operation failed: {func.__name__} - {e}")
            raise
    return wrapper


def atomic_async_operation(func):
    """
    Decorator for atomic async database operations.
    """
    async def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Atomic async operation failed: {func.__name__} - {e}")
            raise
    return wrapper


class TransactionManager:
    """
    Context manager for complex database transactions.
    """
    
    def __init__(self, savepoint=True):
        self.savepoint = savepoint
        self.savepoint_id = None
    
    def __enter__(self):
        if self.savepoint:
            self.savepoint_id = transaction.savepoint()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Rollback on exception
            if self.savepoint_id:
                transaction.savepoint_rollback(self.savepoint_id)
            logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            # Commit on success
            if self.savepoint_id:
                transaction.savepoint_commit(self.savepoint_id)
            logger.debug("Transaction committed successfully")


# Optimized service methods with transaction handling
class OptimizedAutomationService:
    """
    Automation service with proper transaction handling.
    """
    
    @atomic_operation
    def create_automation_rule(self, rule_data):
        """
        Create automation rule with atomic transaction.
        """
        from apps.automation.models import AutomationRule
        
        rule = AutomationRule.objects.create(
            organization=rule_data['organization'],
            name=rule_data['name'],
            description=rule_data['description'],
            trigger_conditions=rule_data['trigger_conditions'],
            actions=rule_data['actions'],
            is_active=rule_data.get('is_active', True),
            priority=rule_data.get('priority', 1)
        )
        
        # Create related objects
        if 'email_template' in rule_data:
            self._create_email_template(rule, rule_data['email_template'])
        
        if 'webhook' in rule_data:
            self._create_webhook(rule, rule_data['webhook'])
        
        return rule
    
    @atomic_operation
    def execute_automation_rule(self, rule_id, entity_data):
        """
        Execute automation rule with atomic transaction.
        """
        from apps.automation.models import AutomationRule, AutomationExecution
        
        rule = AutomationRule.objects.get(id=rule_id)
        
        # Create execution record
        execution = AutomationExecution.objects.create(
            rule=rule,
            entity_type=entity_data['entity_type'],
            entity_id=entity_data['entity_id'],
            trigger_data=entity_data.get('trigger_data', {}),
            actions_executed=[],
            success=True
        )
        
        # Execute actions
        try:
            for action in rule.actions:
                result = self._execute_action(action, entity_data)
                execution.actions_executed.append({
                    'action': action,
                    'result': result,
                    'timestamp': timezone.now().isoformat()
                })
            
            execution.success = True
            execution.save()
            
        except Exception as e:
            execution.success = False
            execution.error_message = str(e)
            execution.save()
            raise
        
        return execution
    
    def _create_email_template(self, rule, template_data):
        """Create email template for rule."""
        from apps.automation.models import EmailTemplate
        
        return EmailTemplate.objects.create(
            organization=rule.organization,
            rule=rule,
            name=template_data['name'],
            subject=template_data['subject'],
            body=template_data['body'],
            is_active=True
        )
    
    def _create_webhook(self, rule, webhook_data):
        """Create webhook for rule."""
        from apps.automation.models import Webhook
        
        return Webhook.objects.create(
            organization=rule.organization,
            rule=rule,
            name=webhook_data['name'],
            url=webhook_data['url'],
            method=webhook_data.get('method', 'POST'),
            headers=webhook_data.get('headers', {}),
            is_active=True
        )
    
    def _execute_action(self, action, entity_data):
        """Execute individual action."""
        # Implementation depends on action type
        return {"status": "executed", "action": action}


class OptimizedWorkflowService:
    """
    Workflow service with proper transaction handling.
    """
    
    @atomic_async_operation
    async def create_workflow(self, workflow_config):
        """
        Create workflow with atomic transaction.
        """
        from apps.workflow_automation.models import WorkflowEngine
        
        workflow = WorkflowEngine.objects.create(
            organization=workflow_config['organization'],
            name=workflow_config['name'],
            description=workflow_config.get('description', ''),
            workflow_definition=workflow_config['workflow_definition'],
            is_active=workflow_config.get('is_active', True),
            total_workflows=0,
            total_executions=0,
            successful_executions=0,
            failed_executions=0
        )
        
        # Create workflow steps
        if 'steps' in workflow_config:
            await self._create_workflow_steps(workflow, workflow_config['steps'])
        
        return workflow
    
    @atomic_async_operation
    async def execute_workflow(self, workflow_id, execution_data):
        """
        Execute workflow with atomic transaction.
        """
        from apps.workflow_automation.models import WorkflowEngine, WorkflowExecution
        
        workflow = WorkflowEngine.objects.get(id=workflow_id)
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            organization=workflow.organization,
            workflow_engine=workflow,
            execution_id=f"WF_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_name=workflow.name,
            status='running',
            execution_data=execution_data,
            execution_log=[]
        )
        
        try:
            # Execute workflow steps
            results = await self._execute_workflow_steps(workflow, execution_data)
            
            # Update execution
            execution.status = 'completed'
            execution.execution_log = results['log']
            execution.save()
            
            # Update workflow statistics
            workflow.total_executions += 1
            workflow.successful_executions += 1
            workflow.save()
            
        except Exception as e:
            # Update execution with error
            execution.status = 'failed'
            execution.execution_log.append({
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            })
            execution.save()
            
            # Update workflow statistics
            workflow.total_executions += 1
            workflow.failed_executions += 1
            workflow.save()
            
            raise
        
        return execution
    
    async def _create_workflow_steps(self, workflow, steps_data):
        """Create workflow steps."""
        from apps.workflow_automation.models import WorkflowStep
        
        for i, step_data in enumerate(steps_data):
            WorkflowStep.objects.create(
                workflow=workflow,
                step_name=step_data['name'],
                step_order=i + 1,
                step_type=step_data['type'],
                step_config=step_data['config'],
                is_active=True
            )
    
    async def _execute_workflow_steps(self, workflow, execution_data):
        """Execute workflow steps."""
        # Implementation depends on workflow type
        return {
            'status': 'completed',
            'log': [
                {
                    'step': 'initialization',
                    'status': 'completed',
                    'timestamp': timezone.now().isoformat()
                }
            ]
        }


class OptimizedCommunicationService:
    """
    Communication service with proper transaction handling.
    """
    
    @atomic_operation
    def send_message(self, message_config):
        """
        Send message with atomic transaction.
        """
        from apps.communication_platform.models import CommunicationMessage
        
        message = CommunicationMessage.objects.create(
            organization=message_config['organization'],
            session_id=message_config.get('session_id'),
            message_type=message_config.get('message_type', 'text'),
            content=message_config.get('content', ''),
            sender=message_config.get('sender', 'System'),
            recipient=message_config.get('recipient', 'All'),
            message_data=message_config.get('message_data', {})
        )
        
        # Update session statistics
        if message.session_id:
            self._update_session_stats(message.session_id)
        
        # Log communication
        self._log_communication(message)
        
        return message
    
    def _update_session_stats(self, session_id):
        """Update session statistics."""
        from apps.communication_platform.models import CommunicationSession
        
        try:
            session = CommunicationSession.objects.get(session_id=session_id)
            session.message_count += 1
            session.last_activity = timezone.now()
            session.save()
        except CommunicationSession.DoesNotExist:
            pass
    
    def _log_communication(self, message):
        """Log communication activity."""
        from apps.communication_platform.models import CommunicationLog
        
        CommunicationLog.objects.create(
            organization=message.organization,
            log_type='message_sent',
            subject=f"Message sent to {message.recipient}",
            description=f"Message: {message.content[:100]}...",
            user_id=message.sender,
            metadata={
                'message_id': str(message.id),
                'message_type': message.message_type,
                'session_id': message.session_id
            }
        )


class OptimizedIntegrationService:
    """
    Integration service with proper transaction handling.
    """
    
    @atomic_operation
    def create_integration(self, integration_config):
        """
        Create integration with atomic transaction.
        """
        from apps.integration_platform.models import Integration
        
        integration = Integration.objects.create(
            organization=integration_config['organization'],
            name=integration_config['name'],
            integration_type=integration_config['type'],
            configuration=integration_config['configuration'],
            is_active=integration_config.get('is_active', True),
            total_calls=0,
            successful_calls=0,
            failed_calls=0
        )
        
        # Create integration logs
        self._log_integration_creation(integration)
        
        return integration
    
    @atomic_operation
    def execute_integration(self, integration_id, data):
        """
        Execute integration with atomic transaction.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        integration = Integration.objects.get(id=integration_id)
        
        # Log integration attempt
        log = IntegrationLog.objects.create(
            organization=integration.organization,
            log_type='integration_call',
            severity='info',
            message=f"Integration call for {integration.name}",
            integration_id=integration_id,
            metadata={'data': data}
        )
        
        try:
            # Execute integration logic
            result = self._execute_integration_logic(integration, data)
            
            # Update integration statistics
            integration.total_calls += 1
            integration.successful_calls += 1
            integration.save()
            
            # Update log
            log.severity = 'info'
            log.message = f"Integration call successful for {integration.name}"
            log.metadata['result'] = result
            log.save()
            
            return result
            
        except Exception as e:
            # Update integration statistics
            integration.total_calls += 1
            integration.failed_calls += 1
            integration.save()
            
            # Update log
            log.severity = 'error'
            log.message = f"Integration call failed for {integration.name}: {str(e)}"
            log.metadata['error'] = str(e)
            log.save()
            
            raise
    
    def _execute_integration_logic(self, integration, data):
        """Execute integration logic."""
        # Implementation depends on integration type
        return {"status": "success", "data": data}
    
    def _log_integration_creation(self, integration):
        """Log integration creation."""
        from apps.integration_platform.models import IntegrationLog
        
        IntegrationLog.objects.create(
            organization=integration.organization,
            log_type='integration_created',
            severity='info',
            message=f"Integration created: {integration.name}",
            integration_id=str(integration.id),
            metadata={
                'integration_type': integration.integration_type,
                'is_active': integration.is_active
            }
        )

