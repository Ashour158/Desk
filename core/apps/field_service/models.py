"""
Field Service Management models.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models as gis_models
from apps.organizations.managers import TenantAwareModel, TenantManager

User = get_user_model()


class Technician(TenantAwareModel):
    """
    Field service technicians.
    """

    AVAILABILITY_STATUS = [
        ("available", "Available"),
        ("on_job", "On Job"),
        ("off_duty", "Off Duty"),
        ("break", "On Break"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="technician_profile"
    )
    employee_id = models.CharField(max_length=50, blank=True, help_text="Employee ID")

    # Skills and qualifications
    skills = models.JSONField(default=list, help_text="Technical skills")
    certifications = models.JSONField(
        default=list, help_text="Professional certifications"
    )
    experience_years = models.PositiveIntegerField(
        default=0, help_text="Years of experience"
    )

    # Location and availability
    current_location = gis_models.PointField(
        null=True, blank=True, help_text="Current GPS location"
    )
    availability_status = models.CharField(
        max_length=20, choices=AVAILABILITY_STATUS, default="available"
    )
    working_hours = models.JSONField(default=dict, help_text="Working hours schedule")
    max_jobs_per_day = models.PositiveIntegerField(
        default=8, help_text="Maximum jobs per day"
    )

    # Tools and equipment
    tools_assigned = models.JSONField(
        default=list, help_text="Assigned tools and equipment"
    )
    vehicle_info = models.JSONField(default=dict, help_text="Vehicle information")

    # Performance metrics
    total_jobs_completed = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    on_time_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "technicians"
        verbose_name = "Technician"
        verbose_name_plural = "Technicians"
        ordering = ["user__full_name"]

    def __str__(self):
        return f"{self.user.full_name} ({self.employee_id or 'No ID'})"

    @property
    def is_available(self):
        """Check if technician is available for new jobs."""
        return self.availability_status == "available"

    @property
    def current_jobs_count(self):
        """Get count of current active jobs."""
        return self.job_assignments.filter(
            status__in=["assigned", "in_progress"]
        ).count()

    @property
    def can_take_more_jobs(self):
        """Check if technician can take more jobs."""
        return self.current_jobs_count < self.max_jobs_per_day


class WorkOrder(TenantAwareModel):
    """
    Field service work orders.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("on_hold", "On Hold"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    WORK_TYPES = [
        ("installation", "Installation"),
        ("repair", "Repair"),
        ("maintenance", "Maintenance"),
        ("inspection", "Inspection"),
        ("delivery", "Delivery"),
        ("consultation", "Consultation"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_number = models.CharField(
        max_length=50, unique=True, help_text="Work order number"
    )

    # Source tracking
    source_ticket = models.ForeignKey(
        'tickets.Ticket',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='work_orders',
        help_text="Ticket that generated this work order"
    )
    
    SOURCE_CHOICES = [
        ('manual', 'Manual Creation'),
        ('ticket', 'Auto-generated from Ticket'),
        ('scheduled', 'Scheduled Maintenance'),
        ('contract', 'Contract-based'),
    ]
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual',
        help_text="Source of work order creation"
    )

    # Basic information
    title = models.CharField(max_length=500, help_text="Work order title")
    description = models.TextField(help_text="Detailed description")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="medium"
    )
    work_type = models.CharField(max_length=20, choices=WORK_TYPES, default="repair")

    # Customer and location
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="work_orders",
        help_text="Customer for this work order",
    )
    service_location = models.JSONField(
        default=dict, help_text="Service location details"
    )
    location_coordinates = gis_models.PointField(
        null=True, blank=True, help_text="GPS coordinates"
    )

    # Scheduling
    scheduled_start = models.DateTimeField(
        null=True, blank=True, help_text="Scheduled start time"
    )
    scheduled_end = models.DateTimeField(
        null=True, blank=True, help_text="Scheduled end time"
    )
    estimated_duration = models.PositiveIntegerField(
        default=60, help_text="Estimated duration in minutes"
    )
    actual_start = models.DateTimeField(
        null=True, blank=True, help_text="Actual start time"
    )
    actual_end = models.DateTimeField(
        null=True, blank=True, help_text="Actual end time"
    )

    # Assignment
    assigned_technicians = models.JSONField(
        default=list, help_text="List of assigned technician IDs"
    )
    required_skills = models.JSONField(
        default=list, help_text="Required skills for this job"
    )

    # Parts and materials
    parts_required = models.JSONField(
        default=list, help_text="Required parts and materials"
    )
    parts_used = models.JSONField(default=list, help_text="Parts actually used")

    # Cost and billing
    cost_estimate = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Estimated cost"
    )
    final_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Final cost"
    )
    invoice_id = models.UUIDField(null=True, blank=True, help_text="Related invoice ID")

    # Custom fields
    custom_fields = models.JSONField(default=dict, help_text="Custom field values")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "work_orders"
        verbose_name = "Work Order"
        verbose_name_plural = "Work Orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "priority"]),
            models.Index(fields=["organization", "customer"]),
            models.Index(fields=["work_order_number"]),
            models.Index(fields=["source_ticket"]),
            models.Index(fields=["source"]),
        ]

    def __str__(self):
        return f"{self.work_order_number}: {self.title}"

    def save(self, *args, **kwargs):
        """Generate work order number if not provided."""
        if not self.work_order_number:
            self.work_order_number = self.generate_work_order_number()
        super().save(*args, **kwargs)

    def generate_work_order_number(self):
        """Generate unique work order number."""
        from django.db import connection

        with connection.cursor() as cursor:
            cursor.execute("SELECT nextval('work_order_number_seq')")
            number = cursor.fetchone()[0]
        return f"WO-{number:06d}"

    @property
    def is_active(self):
        """Check if work order is active."""
        return self.status in ["scheduled", "assigned", "in_progress"]

    @property
    def is_completed(self):
        """Check if work order is completed."""
        return self.status == "completed"

    @property
    def duration_minutes(self):
        """Calculate actual duration in minutes."""
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).total_seconds() / 60
        return None


class JobAssignment(models.Model):
    """
    Assignment of technicians to work orders.
    """

    STATUS_CHOICES = [
        ("assigned", "Assigned"),
        ("accepted", "Accepted"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, related_name="job_assignments"
    )
    technician = models.ForeignKey(
        Technician, on_delete=models.CASCADE, related_name="job_assignments"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="assigned")

    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Performance metrics
    travel_time = models.PositiveIntegerField(
        default=0, help_text="Travel time in minutes"
    )
    work_time = models.PositiveIntegerField(default=0, help_text="Work time in minutes")
    distance_traveled = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, help_text="Distance in km"
    )

    # Notes and feedback
    notes = models.TextField(blank=True, help_text="Assignment notes")
    customer_rating = models.PositiveIntegerField(
        null=True, blank=True, help_text="Customer rating (1-5)"
    )
    customer_feedback = models.TextField(blank=True, help_text="Customer feedback")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "job_assignments"
        verbose_name = "Job Assignment"
        verbose_name_plural = "Job Assignments"
        ordering = ["-assigned_at"]
        unique_together = ["work_order", "technician"]

    def __str__(self):
        return f"{self.work_order.work_order_number} - {self.technician.user.full_name}"


class ServiceReport(models.Model):
    """
    Service reports completed by technicians.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order = models.ForeignKey(
        WorkOrder, on_delete=models.CASCADE, related_name="service_reports"
    )
    technician = models.ForeignKey(
        Technician, on_delete=models.CASCADE, related_name="service_reports"
    )

    # Work performed
    work_performed = models.TextField(help_text="Description of work performed")
    parts_used = models.JSONField(default=list, help_text="Parts and materials used")
    labor_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, help_text="Labor hours"
    )

    # Customer interaction
    customer_signature = models.TextField(
        blank=True, help_text="Base64 encoded signature"
    )
    customer_feedback = models.TextField(blank=True, help_text="Customer feedback")
    customer_rating = models.PositiveIntegerField(
        null=True, blank=True, help_text="Customer rating (1-5)"
    )

    # Documentation
    photos = models.JSONField(default=list, help_text="List of photo URLs")
    documents = models.JSONField(default=list, help_text="List of document URLs")

    # Issues and recommendations
    reported_issues = models.JSONField(
        default=list, help_text="Issues found during service"
    )
    recommendations = models.TextField(
        blank=True, help_text="Recommendations for customer"
    )
    follow_up_required = models.BooleanField(
        default=False, help_text="Follow-up required"
    )
    follow_up_date = models.DateTimeField(
        null=True, blank=True, help_text="Follow-up date"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "service_reports"
        verbose_name = "Service Report"
        verbose_name_plural = "Service Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Service Report for {self.work_order.work_order_number}"


class Asset(TenantAwareModel):
    """
    Customer assets and equipment.
    """

    ASSET_TYPES = [
        ("equipment", "Equipment"),
        ("vehicle", "Vehicle"),
        ("building", "Building"),
        ("furniture", "Furniture"),
        ("electronics", "Electronics"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("under_maintenance", "Under Maintenance"),
        ("retired", "Retired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assets")

    # Asset information
    asset_type = models.CharField(
        max_length=20, choices=ASSET_TYPES, default="equipment"
    )
    name = models.CharField(max_length=255, help_text="Asset name")
    model = models.CharField(max_length=255, blank=True, help_text="Asset model")
    serial_number = models.CharField(
        max_length=100, blank=True, help_text="Serial number"
    )
    manufacturer = models.CharField(
        max_length=255, blank=True, help_text="Manufacturer"
    )

    # Location and status
    location = models.JSONField(default=dict, help_text="Asset location details")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Dates
    installation_date = models.DateField(
        null=True, blank=True, help_text="Installation date"
    )
    warranty_expiry = models.DateField(
        null=True, blank=True, help_text="Warranty expiry date"
    )
    last_service_date = models.DateField(
        null=True, blank=True, help_text="Last service date"
    )
    next_service_date = models.DateField(
        null=True, blank=True, help_text="Next scheduled service"
    )

    # Maintenance
    maintenance_schedule = models.JSONField(
        default=dict, help_text="Maintenance schedule"
    )
    service_history = models.JSONField(default=list, help_text="Service history")

    # Custom fields
    custom_fields = models.JSONField(default=dict, help_text="Custom asset fields")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "assets"
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        ordering = ["name"]
        unique_together = ["organization", "serial_number"]

    def __str__(self):
        return f"{self.name} ({self.customer.full_name})"

    @property
    def is_under_warranty(self):
        """Check if asset is under warranty."""
        if not self.warranty_expiry:
            return False
        return self.warranty_expiry > timezone.now().date()

    @property
    def is_due_for_service(self):
        """Check if asset is due for service."""
        if not self.next_service_date:
            return False
        return self.next_service_date <= timezone.now().date()


class InventoryItem(TenantAwareModel):
    """
    Inventory items and parts.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_name = models.CharField(max_length=255, help_text="Item name")
    sku = models.CharField(max_length=100, unique=True, help_text="Stock keeping unit")
    description = models.TextField(blank=True, help_text="Item description")
    category = models.CharField(max_length=100, blank=True, help_text="Item category")

    # Stock information
    quantity_on_hand = models.PositiveIntegerField(
        default=0, help_text="Current stock quantity"
    )
    reorder_level = models.PositiveIntegerField(
        default=0, help_text="Reorder threshold"
    )
    max_stock_level = models.PositiveIntegerField(
        default=0, help_text="Maximum stock level"
    )

    # Pricing
    unit_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Unit cost"
    )
    selling_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, help_text="Selling price"
    )

    # Supplier information
    supplier = models.CharField(
        max_length=255, blank=True, help_text="Primary supplier"
    )
    supplier_sku = models.CharField(
        max_length=100, blank=True, help_text="Supplier SKU"
    )
    supplier_contact = models.JSONField(
        default=dict, help_text="Supplier contact information"
    )

    # Location
    warehouse_location = models.CharField(
        max_length=255, blank=True, help_text="Warehouse location"
    )
    bin_location = models.CharField(
        max_length=50, blank=True, help_text="Bin/shelf location"
    )

    # Status
    is_active = models.BooleanField(default=True, help_text="Item is active")
    is_tracked = models.BooleanField(default=True, help_text="Track inventory levels")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "inventory_items"
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        ordering = ["item_name"]
        unique_together = ["organization", "sku"]

    def __str__(self):
        return f"{self.item_name} ({self.sku})"

    @property
    def is_low_stock(self):
        """Check if item is low on stock."""
        return self.quantity_on_hand <= self.reorder_level

    @property
    def needs_reorder(self):
        """Check if item needs reordering."""
        return self.is_tracked and self.is_low_stock


class Route(TenantAwareModel):
    """
    Optimized routes for technicians.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    technician = models.ForeignKey(
        Technician, on_delete=models.CASCADE, related_name="routes"
    )
    route_date = models.DateField(help_text="Route date")

    # Route information
    work_orders = models.JSONField(default=list, help_text="List of work order IDs")
    optimized_sequence = models.JSONField(
        default=list, help_text="Optimized visit sequence"
    )
    total_distance = models.DecimalField(
        max_digits=8, decimal_places=2, default=0, help_text="Total distance in km"
    )
    total_duration = models.PositiveIntegerField(
        default=0, help_text="Total duration in minutes"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = TenantManager()

    class Meta:
        db_table = "routes"
        verbose_name = "Route"
        verbose_name_plural = "Routes"
        ordering = ["-route_date"]
        unique_together = ["organization", "technician", "route_date"]

    def __str__(self):
        return f"Route for {self.technician.user.full_name} on {self.route_date}"




class TicketToWorkOrderRule(TenantAwareModel):
    """
    Rules for automatic work order creation from tickets.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Rule name")
    description = models.TextField(blank=True, help_text="Rule description")
    is_active = models.BooleanField(default=True, help_text="Whether rule is active")
    priority = models.IntegerField(
        default=0, help_text="Higher priority rules execute first"
    )

    # Conditions (when to create work order)
    ticket_categories = models.JSONField(
        default=list,
        help_text="List of ticket categories that trigger work order creation",
    )
    ticket_priorities = models.JSONField(
        default=list, help_text="List of ticket priorities (e.g., ['high', 'urgent'])"
    )
    ticket_tags = models.JSONField(
        default=list, help_text="List of tags that trigger work order creation"
    )
    customer_types = models.JSONField(
        default=list,
        help_text="List of customer types (e.g., ['enterprise', 'premium'])",
    )

    # Work order template
    work_order_type = models.CharField(
        max_length=50,
        choices=WorkOrder.WORK_TYPES,
        default="repair",
        help_text="Type of work order to create",
    )
    work_order_priority = models.CharField(
        max_length=20,
        choices=WorkOrder.PRIORITY_CHOICES,
        default="medium",
        help_text="Priority for created work order",
    )
    default_duration_hours = models.IntegerField(
        default=2, help_text="Default duration in hours"
    )

    # Assignment rules
    auto_assign = models.BooleanField(
        default=True, help_text="Automatically assign technician"
    )
    assignment_logic = models.CharField(
        max_length=50,
        choices=[
            ("nearest", "Nearest Available Technician"),
            ("skill_match", "Best Skill Match"),
            ("workload", "Least Workload"),
            ("round_robin", "Round Robin"),
        ],
        default="skill_match",
        help_text="Logic for technician assignment",
    )
    required_skills = models.JSONField(
        default=list, help_text="Required skills for technician"
    )

    # Scheduling
    auto_schedule = models.BooleanField(
        default=False, help_text="Automatically schedule work order"
    )
    schedule_offset_hours = models.IntegerField(
        default=24, help_text="Hours from ticket creation to schedule work order"
    )

    # Notifications
    notify_customer = models.BooleanField(
        default=True, help_text="Notify customer when work order is created"
    )
    notify_technician = models.BooleanField(
        default=True, help_text="Notify technician when assigned"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    objects = TenantManager()

    class Meta:
        db_table = "ticket_to_work_order_rules"
        verbose_name = "Ticket to Work Order Rule"
        verbose_name_plural = "Ticket to Work Order Rules"
        ordering = ["-priority", "name"]
        indexes = [
            models.Index(fields=["organization", "is_active", "priority"]),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

    def matches_ticket(self, ticket):
        """
        Check if this rule matches the given ticket.

        Args:
            ticket: Ticket instance to check

        Returns:
            bool: True if rule matches, False otherwise
        """
        # Check category
        if self.ticket_categories and ticket.category not in self.ticket_categories:
            return False

        # Check priority
        if self.ticket_priorities and ticket.priority not in self.ticket_priorities:
            return False

        # Check tags
        if self.ticket_tags:
            ticket_tag_names = list(ticket.tags.values_list("name", flat=True))
            if not any(tag in ticket_tag_names for tag in self.ticket_tags):
                return False

        # Check customer type
        if self.customer_types:
            customer_type = getattr(ticket.customer, "customer_type", None)
            if customer_type not in self.customer_types:
                return False

        return True

