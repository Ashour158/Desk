"""
Comprehensive Transaction Decorators for All Critical Operations
"""

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def atomic_operation(func):
    """
    Enhanced decorator for atomic database operations with comprehensive error handling.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                result = func(*args, **kwargs)
                logger.info(f"Atomic operation completed successfully: {func.__name__}")
                return result
        except Exception as e:
            logger.error(f"Atomic operation failed: {func.__name__} - {e}")
            # Clear related caches on failure
            cache.delete_pattern(f"*_{func.__name__}_*")
            raise
    return wrapper


def atomic_async_operation(func):
    """
    Enhanced decorator for atomic async database operations.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            with transaction.atomic():
                result = await func(*args, **kwargs)
                logger.info(f"Atomic async operation completed successfully: {func.__name__}")
                return result
        except Exception as e:
            logger.error(f"Atomic async operation failed: {func.__name__} - {e}")
            # Clear related caches on failure
            cache.delete_pattern(f"*_{func.__name__}_*")
            raise
    return wrapper


class ComprehensiveAutomationService:
    """
    Automation service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def create_automation_rule(self, rule_data):
        """
        Create automation rule with atomic transaction.
        """
        from apps.automation.models import AutomationRule, EmailTemplate, Webhook
        
        # Create the rule
        rule = AutomationRule.objects.create(
            organization=rule_data['organization'],
            name=rule_data['name'],
            description=rule_data['description'],
            trigger_type=rule_data['trigger_type'],
            trigger_conditions=rule_data['trigger_conditions'],
            actions=rule_data['actions'],
            execution_order=rule_data.get('execution_order', 0),
            is_active=rule_data.get('is_active', True),
            stop_on_match=rule_data.get('stop_on_match', False)
        )
        
        # Create related objects atomically
        if 'email_template' in rule_data:
            EmailTemplate.objects.create(
                organization=rule.organization,
                rule=rule,
                name=rule_data['email_template']['name'],
                subject=rule_data['email_template']['subject'],
                body=rule_data['email_template']['body'],
                is_active=True
            )
        
        if 'webhook' in rule_data:
            Webhook.objects.create(
                organization=rule.organization,
                rule=rule,
                name=rule_data['webhook']['name'],
                url=rule_data['webhook']['url'],
                method=rule_data['webhook'].get('method', 'POST'),
                headers=rule_data['webhook'].get('headers', {}),
                is_active=True
            )
        
        # Clear automation cache
        cache.delete_pattern(f"automation_*_{rule.organization.id}")
        
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
            success=True,
            executed_at=timezone.now()
        )
        
        try:
            # Execute actions atomically
            for action in rule.actions:
                result = self._execute_action(action, entity_data)
                execution.actions_executed.append({
                    'action': action,
                    'result': result,
                    'timestamp': timezone.now().isoformat()
                })
            
            execution.success = True
            execution.save()
            
            # Update rule statistics
            rule.execution_count += 1
            rule.save(update_fields=['execution_count'])
            
        except Exception as e:
            execution.success = False
            execution.error_message = str(e)
            execution.save()
            raise
        
        return execution
    
    def _execute_action(self, action, entity_data):
        """Execute individual action."""
        # Implementation depends on action type
        return {"status": "executed", "action": action}


class ComprehensiveWorkflowService:
    """
    Workflow service with comprehensive transaction handling.
    """
    
    @atomic_async_operation
    async def create_workflow(self, workflow_config):
        """
        Create workflow with atomic transaction.
        """
        from apps.advanced_workflow.models import WorkflowEngine, WorkflowStep
        
        # Create workflow
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
        
        # Create workflow steps atomically
        if 'steps' in workflow_config:
            for i, step_data in enumerate(workflow_config['steps']):
                WorkflowStep.objects.create(
                    workflow=workflow,
                    step_name=step_data['name'],
                    step_order=i + 1,
                    step_type=step_data['type'],
                    step_config=step_data['config'],
                    is_active=True
                )
        
        # Clear workflow cache
        cache.delete_pattern(f"workflow_*_{workflow.organization.id}")
        
        return workflow
    
    @atomic_async_operation
    async def execute_workflow(self, workflow_id, execution_data):
        """
        Execute workflow with atomic transaction.
        """
        from apps.advanced_workflow.models import WorkflowEngine, WorkflowExecution
        
        workflow = WorkflowEngine.objects.get(id=workflow_id)
        
        # Create execution record
        execution = WorkflowExecution.objects.create(
            organization=workflow.organization,
            workflow_engine=workflow,
            execution_id=f"WF_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            workflow_name=workflow.name,
            status='running',
            execution_data=execution_data,
            execution_log=[],
            started_at=timezone.now()
        )
        
        try:
            # Execute workflow steps atomically
            results = await self._execute_workflow_steps(workflow, execution_data)
            
            # Update execution
            execution.status = 'completed'
            execution.execution_log = results['log']
            execution.completed_at = timezone.now()
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
            execution.completed_at = timezone.now()
            execution.save()
            
            # Update workflow statistics
            workflow.total_executions += 1
            workflow.failed_executions += 1
            workflow.save()
            
            raise
        
        return execution
    
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


class ComprehensiveCommunicationService:
    """
    Communication service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def send_message(self, message_config):
        """
        Send message with atomic transaction.
        """
        from apps.communication_platform.models import CommunicationMessage, CommunicationSession, CommunicationLog
        
        # Create message
        message = CommunicationMessage.objects.create(
            organization=message_config['organization'],
            session_id=message_config.get('session_id'),
            message_type=message_config.get('message_type', 'text'),
            content=message_config.get('content', ''),
            sender=message_config.get('sender', 'System'),
            recipient=message_config.get('recipient', 'All'),
            message_data=message_config.get('message_data', {}),
            sent_at=timezone.now()
        )
        
        # Update session statistics atomically
        if message.session_id:
            try:
                session = CommunicationSession.objects.get(session_id=message.session_id)
                session.message_count += 1
                session.last_activity = timezone.now()
                session.save()
            except CommunicationSession.DoesNotExist:
                pass
        
        # Log communication atomically
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
        
        # Clear communication cache
        cache.delete_pattern(f"communication_*_{message.organization.id}")
        
        return message
    
    @atomic_operation
    def create_communication_session(self, session_config):
        """
        Create communication session with atomic transaction.
        """
        from apps.communication_platform.models import CommunicationSession, CommunicationParticipant
        
        # Create session
        session = CommunicationSession.objects.create(
            organization=session_config['organization'],
            session_id=session_config['session_id'],
            session_type=session_config.get('session_type', 'chat'),
            status='active',
            created_by=session_config.get('created_by'),
            started_at=timezone.now()
        )
        
        # Add participants atomically
        if 'participants' in session_config:
            for participant_data in session_config['participants']:
                CommunicationParticipant.objects.create(
                    session=session,
                    user=participant_data['user'],
                    role=participant_data.get('role', 'participant'),
                    joined_at=timezone.now()
                )
        
        return session


class ComprehensiveIntegrationService:
    """
    Integration service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def create_integration(self, integration_config):
        """
        Create integration with atomic transaction.
        """
        from apps.integration_platform.models import Integration, IntegrationLog
        
        # Create integration
        integration = Integration.objects.create(
            organization=integration_config['organization'],
            name=integration_config['name'],
            integration_type=integration_config['type'],
            configuration=integration_config['configuration'],
            is_active=integration_config.get('is_active', True),
            total_calls=0,
            successful_calls=0,
            failed_calls=0,
            created_by=integration_config.get('created_by')
        )
        
        # Log integration creation atomically
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
        
        # Clear integration cache
        cache.delete_pattern(f"integration_*_{integration.organization.id}")
        
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
            
            # Update integration statistics atomically
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
            # Update integration statistics atomically
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


class ComprehensiveAIMLService:
    """
    AI/ML service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def train_ai_model(self, model_config):
        """
        Train AI model with atomic transaction.
        """
        from apps.ai_ml.models import AIModel, AIProcessingJob, AIModelPerformance
        
        # Create model
        model = AIModel.objects.create(
            organization=model_config['organization'],
            name=model_config['name'],
            model_type=model_config['type'],
            configuration=model_config['configuration'],
            training_data=model_config['training_data'],
            is_active=False,  # Will be activated after training
            created_by=model_config.get('created_by')
        )
        
        # Create processing job
        job = AIProcessingJob.objects.create(
            organization=model.organization,
            job_type='model_training',
            input_data=model_config['training_data'],
            ai_model_id=str(model.id),
            status='running',
            started_at=timezone.now()
        )
        
        try:
            # Execute training logic
            training_result = self._execute_training_logic(model, model_config)
            
            # Update job
            job.output_data = training_result
            job.status = 'completed'
            job.processing_completed = timezone.now()
            job.save()
            
            # Activate model
            model.is_active = True
            model.save()
            
            # Create performance metrics
            AIModelPerformance.objects.create(
                model=model,
                metric_name='training_accuracy',
                metric_value=training_result.get('accuracy', 0.0),
                metric_unit='percentage',
                recorded_at=timezone.now()
            )
            
        except Exception as e:
            # Update job with error
            job.status = 'failed'
            job.error_message = str(e)
            job.processing_completed = timezone.now()
            job.save()
            
            raise
        
        return model
    
    def _execute_training_logic(self, model, config):
        """Execute training logic."""
        # Implementation depends on model type
        return {"accuracy": 0.95, "loss": 0.05}


class ComprehensiveSecurityService:
    """
    Security service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def process_security_event(self, event_data):
        """
        Process security event with atomic transaction.
        """
        from apps.advanced_security.models import SecurityEvent, SecurityAuditLog, SecurityRule
        
        # Create security event
        event = SecurityEvent.objects.create(
            organization=event_data['organization'],
            event_type=event_data['type'],
            severity=event_data['severity'],
            description=event_data['description'],
            user=event_data.get('user'),
            ip_address=event_data.get('ip_address'),
            user_agent=event_data.get('user_agent'),
            metadata=event_data.get('metadata', {}),
            occurred_at=timezone.now()
        )
        
        # Create audit log
        SecurityAuditLog.objects.create(
            organization=event.organization,
            event=event,
            log_type='security_event',
            severity=event.severity,
            message=f"Security event: {event.description}",
            user=event.user,
            metadata=event.metadata
        )
        
        # Check security rules atomically
        applicable_rules = SecurityRule.objects.filter(
            organization=event.organization,
            is_active=True,
            event_types__contains=[event.event_type]
        )
        
        for rule in applicable_rules:
            if self._evaluate_security_rule(rule, event):
                self._execute_security_action(rule, event)
        
        return event
    
    def _evaluate_security_rule(self, rule, event):
        """Evaluate security rule."""
        # Implementation depends on rule type
        return True
    
    def _execute_security_action(self, rule, event):
        """Execute security action."""
        # Implementation depends on action type
        pass


class ComprehensiveUserService:
    """
    User service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def update_user_profile(self, user_id, profile_data):
        """
        Update user profile with atomic transaction.
        """
        from apps.accounts.models import User, UserProfile, UserPermission
        
        user = User.objects.get(id=user_id)
        
        # Update user fields
        for field, value in profile_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        user.save()
        
        # Update or create profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={'organization': user.organization}
        )
        
        # Update profile fields
        profile_fields = ['phone', 'address', 'timezone', 'preferences']
        for field in profile_fields:
            if field in profile_data:
                setattr(profile, field, profile_data[field])
        profile.save()
        
        # Update permissions if provided
        if 'permissions' in profile_data:
            # Remove existing permissions
            user.permissions.all().delete()
            
            # Add new permissions
            for permission_data in profile_data['permissions']:
                UserPermission.objects.create(
                    user=user,
                    permission=permission_data['permission'],
                    granted_by=profile_data.get('granted_by'),
                    granted_at=timezone.now()
                )
        
        # Clear user cache
        cache.delete_pattern(f"user_*_{user.id}")
        cache.delete_pattern(f"profile_*_{user.id}")
        
        return user


class ComprehensiveKnowledgeBaseService:
    """
    Knowledge base service with comprehensive transaction handling.
    """
    
    @atomic_operation
    def create_kb_article(self, article_data):
        """
        Create knowledge base article with atomic transaction.
        """
        from apps.knowledge_base.models import KBArticle, KBArticleView, KBArticleTag
        
        # Create article
        article = KBArticle.objects.create(
            organization=article_data['organization'],
            title=article_data['title'],
            content=article_data['content'],
            author=article_data['author'],
            category=article_data.get('category'),
            status=article_data.get('status', 'draft'),
            is_featured=article_data.get('is_featured', False),
            view_count=0,
            helpful_count=0,
            published_at=timezone.now() if article_data.get('status') == 'published' else None
        )
        
        # Add tags atomically
        if 'tags' in article_data:
            for tag_name in article_data['tags']:
                KBArticleTag.objects.get_or_create(
                    article=article,
                    tag=tag_name
                )
        
        # Create initial view if published
        if article.status == 'published':
            KBArticleView.objects.create(
                article=article,
                user=article.author,
                ip_address='127.0.0.1',  # System view
                viewed_at=timezone.now()
            )
            article.view_count = 1
            article.save()
        
        # Clear knowledge base cache
        cache.delete_pattern(f"kb_*_{article.organization.id}")
        
        return article
    
    @atomic_operation
    def update_article_view_count(self, article_id, user, ip_address):
        """
        Update article view count with atomic transaction.
        """
        from apps.knowledge_base.models import KBArticle, KBArticleView
        
        article = KBArticle.objects.get(id=article_id)
        
        # Create view record
        KBArticleView.objects.create(
            article=article,
            user=user,
            ip_address=ip_address,
            viewed_at=timezone.now()
        )
        
        # Update view count atomically
        article.view_count += 1
        article.save(update_fields=['view_count'])
        
        return article
