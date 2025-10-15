"""
Workflow automation platform models.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class VisualWorkflow(models.Model):
    """Visual workflow builder."""

    WORKFLOW_TYPES = [
        ("approval", "Approval Workflow"),
        ("notification", "Notification Workflow"),
        ("data_processing", "Data Processing"),
        ("integration", "Integration Workflow"),
        ("escalation", "Escalation Workflow"),
        ("automation", "Automation Workflow"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    workflow_type = models.CharField(max_length=50, choices=WORKFLOW_TYPES)
    description = models.TextField(blank=True)

    # Workflow definition
    workflow_definition = models.JSONField(default=dict)
    nodes = models.JSONField(default=list)
    connections = models.JSONField(default=list)
    variables = models.JSONField(default=dict)

    # Triggers
    triggers = models.JSONField(default=list)
    conditions = models.JSONField(default=list)

    # Execution
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)
    next_execution = models.DateTimeField(blank=True, null=True)

    # Performance
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)

    # Status
    is_published = models.BooleanField(default=False)
    is_template = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class WorkflowNode(models.Model):
    """Workflow nodes and steps."""

    NODE_TYPES = [
        ("start", "Start Node"),
        ("end", "End Node"),
        ("action", "Action Node"),
        ("condition", "Condition Node"),
        ("gateway", "Gateway Node"),
        ("timer", "Timer Node"),
        ("user_task", "User Task"),
        ("service_task", "Service Task"),
        ("script", "Script Node"),
        ("subprocess", "Subprocess"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    workflow = models.ForeignKey(
        VisualWorkflow, on_delete=models.CASCADE, related_name="node_set"
    )

    # Node details
    node_id = models.CharField(max_length=100)
    node_type = models.CharField(max_length=50, choices=NODE_TYPES)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Position and appearance
    position_x = models.FloatField(default=0.0)
    position_y = models.FloatField(default=0.0)
    width = models.FloatField(default=100.0)
    height = models.FloatField(default=50.0)

    # Configuration
    configuration = models.JSONField(default=dict)
    input_mapping = models.JSONField(default=dict)
    output_mapping = models.JSONField(default=dict)

    # Execution
    is_active = models.BooleanField(default=True)
    execution_order = models.IntegerField(default=0)
    timeout_seconds = models.IntegerField(default=300)

    # Status
    last_executed = models.DateTimeField(blank=True, null=True)
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["execution_order", "node_id"]
        unique_together = ["workflow", "node_id"]

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"


class RPAIntegration(models.Model):
    """Robotic Process Automation integration."""

    RPA_TYPES = [
        ("ui_automation", "UI Automation"),
        ("api_automation", "API Automation"),
        ("data_extraction", "Data Extraction"),
        ("form_filling", "Form Filling"),
        ("file_processing", "File Processing"),
        ("email_automation", "Email Automation"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    rpa_type = models.CharField(max_length=50, choices=RPA_TYPES)
    description = models.TextField(blank=True)

    # RPA configuration
    target_application = models.CharField(max_length=255)
    automation_script = models.TextField()
    input_parameters = models.JSONField(default=dict)
    output_mapping = models.JSONField(default=dict)

    # Execution
    is_active = models.BooleanField(default=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)
    next_execution = models.DateTimeField(blank=True, null=True)

    # Performance
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)

    # Status
    is_running = models.BooleanField(default=False)
    last_execution = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class ProcessMining(models.Model):
    """Process mining and analysis."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    # Process details
    process_name = models.CharField(max_length=255)
    process_type = models.CharField(max_length=100)
    data_source = models.CharField(max_length=255)

    # Mining configuration
    time_window = models.IntegerField(default=30)  # days
    event_log = models.JSONField(default=list)
    process_model = models.JSONField(default=dict)

    # Analysis results
    bottlenecks = models.JSONField(default=list)
    inefficiencies = models.JSONField(default=list)
    optimization_opportunities = models.JSONField(default=list)
    performance_metrics = models.JSONField(default=dict)

    # Status
    is_active = models.BooleanField(default=True)
    last_analyzed = models.DateTimeField(blank=True, null=True)
    analysis_status = models.CharField(max_length=50, default="pending")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class AutomationAI(models.Model):
    """AI-powered automation."""

    AI_TYPES = [
        ("natural_language", "Natural Language Processing"),
        ("machine_learning", "Machine Learning"),
        ("computer_vision", "Computer Vision"),
        ("predictive_analytics", "Predictive Analytics"),
        ("sentiment_analysis", "Sentiment Analysis"),
        ("document_processing", "Document Processing"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    ai_type = models.CharField(max_length=50, choices=AI_TYPES)
    description = models.TextField(blank=True)

    # AI configuration
    model_name = models.CharField(max_length=255)
    model_version = models.CharField(max_length=50)
    training_data = models.JSONField(default=list)
    model_parameters = models.JSONField(default=dict)

    # Performance
    accuracy = models.FloatField(default=0.0)
    precision = models.FloatField(default=0.0)
    recall = models.FloatField(default=0.0)
    f1_score = models.FloatField(default=0.0)

    # Usage
    prediction_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_trained = models.BooleanField(default=False)
    last_trained = models.DateTimeField(blank=True, null=True)
    last_prediction = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class WorkflowTemplate(models.Model):
    """Pre-built workflow templates."""

    TEMPLATE_CATEGORIES = [
        ("onboarding", "Onboarding"),
        ("approval", "Approval"),
        ("notification", "Notification"),
        ("escalation", "Escalation"),
        ("integration", "Integration"),
        ("compliance", "Compliance"),
        ("hr", "Human Resources"),
        ("finance", "Finance"),
        ("support", "Support"),
        ("sales", "Sales"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=TEMPLATE_CATEGORIES)
    description = models.TextField(blank=True)

    # Template details
    use_case = models.CharField(max_length=255)
    complexity = models.CharField(max_length=20, default="medium")
    estimated_time = models.IntegerField(default=0)  # minutes

    # Template configuration
    template_definition = models.JSONField(default=dict)
    required_variables = models.JSONField(default=list)
    setup_instructions = models.TextField()

    # Usage
    usage_count = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    rating = models.FloatField(default=0.0)

    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-usage_count", "name"]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class AutomationAnalytics(models.Model):
    """Automation analytics and metrics."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    automation_type = models.CharField(max_length=50)
    automation_id = models.UUIDField()

    # Metrics
    execution_count = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    average_execution_time = models.FloatField(default=0.0)
    total_time_saved = models.FloatField(default=0.0)  # hours

    # Performance
    success_rate = models.FloatField(default=0.0)
    error_rate = models.FloatField(default=0.0)
    throughput = models.FloatField(default=0.0)
    efficiency_score = models.FloatField(default=0.0)

    # Cost savings
    cost_savings = models.FloatField(default=0.0)
    roi_percentage = models.FloatField(default=0.0)
    break_even_point = models.DateTimeField(blank=True, null=True)

    # Trends
    performance_trend = models.JSONField(default=list)
    usage_trend = models.JSONField(default=list)
    cost_trend = models.JSONField(default=list)

    # Status
    is_active = models.BooleanField(default=True)
    last_analyzed = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_analyzed"]
        unique_together = ["organization", "automation_type", "automation_id"]

    def __str__(self):
        return f"{self.organization.name} - {self.automation_type}"


class WorkflowExecution(models.Model):
    """Workflow execution logs."""

    EXECUTION_STATUS = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("paused", "Paused"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    workflow = models.ForeignKey(
        VisualWorkflow, on_delete=models.CASCADE, related_name="executions"
    )

    # Execution details
    execution_id = models.UUIDField(default=uuid.uuid4, unique=True)
    status = models.CharField(
        max_length=20, choices=EXECUTION_STATUS, default="pending"
    )
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Performance
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(default=0.0)

    # Results
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)

    # Context
    triggered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    trigger_type = models.CharField(max_length=50, blank=True)
    trigger_data = models.JSONField(default=dict)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_time"]
        indexes = [
            models.Index(fields=["organization", "workflow"]),
            models.Index(fields=["status", "start_time"]),
        ]

    def __str__(self):
        return f"{self.workflow.name} - {self.execution_id}"


class WorkflowStep(models.Model):
    """Individual workflow steps and their execution."""

    organization = models.ForeignKey(
        "organizations.Organization", on_delete=models.CASCADE
    )
    execution = models.ForeignKey(
        WorkflowExecution, on_delete=models.CASCADE, related_name="steps"
    )
    node = models.ForeignKey(WorkflowNode, on_delete=models.CASCADE)

    # Step details
    step_name = models.CharField(max_length=255)
    step_type = models.CharField(max_length=50)
    input_data = models.JSONField(default=dict)
    output_data = models.JSONField(default=dict)

    # Execution
    status = models.CharField(
        max_length=20, choices=WorkflowExecution.EXECUTION_STATUS, default="pending"
    )
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.FloatField(default=0.0)

    # Results
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["organization", "execution"]),
            models.Index(fields=["node", "status"]),
        ]

    def __str__(self):
        return f"{self.execution.workflow.name} - {self.step_name}"
