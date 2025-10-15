"""
Enhanced Advanced Workflow & Automation Platform models for advanced capabilities.
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.apps.organizations.models import Organization

User = get_user_model()


class IntelligentProcessAutomation(models.Model):
    """Intelligent Process Automation (IPA) with AI-driven process discovery and self-healing workflows."""

    IPA_TYPE_CHOICES = [
        ("process_discovery", "Process Discovery"),
        ("self_healing", "Self-Healing"),
        ("intelligent_routing", "Intelligent Routing"),
        ("predictive_automation", "Predictive Automation"),
        ("cognitive_automation", "Cognitive Automation"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    ipa_type = models.CharField(max_length=50, choices=IPA_TYPE_CHOICES)
    process_definition = models.JSONField(default=dict)
    ai_models = models.JSONField(default=list)
    self_healing_config = models.JSONField(default=dict)
    process_discovery_rules = models.JSONField(default=list)
    intelligent_routing = models.JSONField(default=dict)
    total_processes = models.PositiveIntegerField(default=0)
    automated_processes = models.PositiveIntegerField(default=0)
    self_healing_events = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Intelligent Process Automation"
        verbose_name_plural = "Intelligent Process Automations"

    def __str__(self):
        return self.name


class WorkflowEngine(models.Model):
    """Advanced Workflow Engine with complex workflow designer and parallel process execution."""

    ENGINE_TYPE_CHOICES = [
        ("visual_designer", "Visual Designer"),
        ("parallel_execution", "Parallel Execution"),
        ("conditional_logic", "Conditional Logic"),
        ("event_driven", "Event-Driven"),
        ("state_machine", "State Machine"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    engine_type = models.CharField(max_length=50, choices=ENGINE_TYPE_CHOICES)
    workflow_definition = models.JSONField(default=dict)
    execution_engine = models.JSONField(default=dict)
    parallel_processing = models.JSONField(default=dict)
    conditional_logic = models.JSONField(default=dict)
    event_handlers = models.JSONField(default=list)
    total_workflows = models.PositiveIntegerField(default=0)
    active_workflows = models.PositiveIntegerField(default=0)
    total_executions = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workflow Engine"
        verbose_name_plural = "Workflow Engines"

    def __str__(self):
        return self.name


class ProcessIntelligence(models.Model):
    """Process Intelligence Platform with process mining, performance analytics, and optimization recommendations."""

    INTELLIGENCE_TYPE_CHOICES = [
        ("process_mining", "Process Mining"),
        ("performance_analytics", "Performance Analytics"),
        ("optimization_recommendations", "Optimization Recommendations"),
        ("bottleneck_analysis", "Bottleneck Analysis"),
        ("resource_optimization", "Resource Optimization"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    intelligence_type = models.CharField(
        max_length=50, choices=INTELLIGENCE_TYPE_CHOICES
    )
    process_mining_config = models.JSONField(default=dict)
    performance_analytics = models.JSONField(default=dict)
    optimization_rules = models.JSONField(default=list)
    bottleneck_detection = models.JSONField(default=dict)
    resource_optimization = models.JSONField(default=dict)
    total_processes_analyzed = models.PositiveIntegerField(default=0)
    optimization_recommendations = models.PositiveIntegerField(default=0)
    performance_improvements = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Process Intelligence"
        verbose_name_plural = "Process Intelligences"

    def __str__(self):
        return self.name


class AutomationMarketplace(models.Model):
    """Automation Marketplace with pre-built templates and community automation library."""

    MARKETPLACE_TYPE_CHOICES = [
        ("template_library", "Template Library"),
        ("community_automation", "Community Automation"),
        ("enterprise_automation", "Enterprise Automation"),
        ("custom_automation", "Custom Automation"),
        ("ai_automation", "AI Automation"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    marketplace_type = models.CharField(max_length=50, choices=MARKETPLACE_TYPE_CHOICES)
    automation_templates = models.JSONField(default=list)
    community_library = models.JSONField(default=dict)
    enterprise_automations = models.JSONField(default=list)
    custom_automations = models.JSONField(default=list)
    ai_automations = models.JSONField(default=list)
    total_templates = models.PositiveIntegerField(default=0)
    downloads = models.PositiveIntegerField(default=0)
    community_contributions = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Automation Marketplace"
        verbose_name_plural = "Automation Marketplaces"

    def __str__(self):
        return self.name


class IntegrationAutomation(models.Model):
    """Advanced Integration Automation with cross-system workflow automation and event-driven automation."""

    AUTOMATION_TYPE_CHOICES = [
        ("cross_system", "Cross-System"),
        ("event_driven", "Event-Driven"),
        ("api_automation", "API Automation"),
        ("data_automation", "Data Automation"),
        ("workflow_automation", "Workflow Automation"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    automation_type = models.CharField(max_length=50, choices=AUTOMATION_TYPE_CHOICES)
    integration_config = models.JSONField(default=dict)
    event_driven_config = models.JSONField(default=dict)
    api_automation = models.JSONField(default=dict)
    data_automation = models.JSONField(default=dict)
    workflow_automation = models.JSONField(default=dict)
    total_integrations = models.PositiveIntegerField(default=0)
    automated_integrations = models.PositiveIntegerField(default=0)
    cross_system_automations = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Integration Automation"
        verbose_name_plural = "Integration Automations"

    def __str__(self):
        return self.name


class WorkflowTemplate(models.Model):
    """Workflow Template for reusable workflow definitions."""

    TEMPLATE_TYPE_CHOICES = [
        ("business_process", "Business Process"),
        ("technical_process", "Technical Process"),
        ("approval_process", "Approval Process"),
        ("data_process", "Data Process"),
        ("integration_process", "Integration Process"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=50, choices=TEMPLATE_TYPE_CHOICES)
    template_definition = models.JSONField(default=dict)
    template_config = models.JSONField(default=dict)
    required_fields = models.JSONField(default=list)
    optional_fields = models.JSONField(default=list)
    template_category = models.CharField(max_length=100)
    template_description = models.TextField()
    total_uses = models.PositiveIntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workflow Template"
        verbose_name_plural = "Workflow Templates"

    def __str__(self):
        return self.name


class WorkflowExecution(models.Model):
    """Workflow Execution for tracking workflow runs."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    workflow_engine = models.ForeignKey(WorkflowEngine, on_delete=models.CASCADE)
    execution_id = models.CharField(max_length=100, unique=True)
    workflow_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    execution_data = models.JSONField(default=dict)
    execution_log = models.JSONField(default=list)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Workflow Execution"
        verbose_name_plural = "Workflow Executions"

    def __str__(self):
        return f"{self.execution_id} - {self.workflow_name}"


class ProcessMetric(models.Model):
    """Process Metric for tracking workflow and automation performance."""

    METRIC_TYPE_CHOICES = [
        ("execution_time", "Execution Time"),
        ("success_rate", "Success Rate"),
        ("error_rate", "Error Rate"),
        ("throughput", "Throughput"),
        ("resource_usage", "Resource Usage"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    metric_name = models.CharField(max_length=200)
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPE_CHOICES)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50)
    target_value = models.FloatField(null=True, blank=True)
    metric_data = models.JSONField(default=dict)
    measurement_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Process Metric"
        verbose_name_plural = "Process Metrics"

    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"


class AutomationRule(models.Model):
    """Automation Rule for defining automation triggers and actions."""

    RULE_TYPE_CHOICES = [
        ("trigger", "Trigger"),
        ("action", "Action"),
        ("condition", "Condition"),
        ("exception", "Exception"),
        ("escalation", "Escalation"),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rule_type = models.CharField(max_length=50, choices=RULE_TYPE_CHOICES)
    rule_definition = models.JSONField(default=dict)
    trigger_conditions = models.JSONField(default=list)
    action_sequences = models.JSONField(default=list)
    exception_handling = models.JSONField(default=dict)
    escalation_rules = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Automation Rule"
        verbose_name_plural = "Automation Rules"

    def __str__(self):
        return self.name
