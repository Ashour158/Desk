"""
SLA (Service Level Agreement) Management System

This module provides comprehensive SLA management functionality including:
- SLA policy definition and management
- Due date calculations with business hours
- SLA breach detection and reporting
- SLA metrics and analytics
- Multi-tenant SLA support
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.db import models
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SLAManager:
    """
    Service Level Agreement Manager
    
    Handles all SLA-related operations including policy management,
    due date calculations, breach detection, and metrics reporting.
    
    Attributes:
        organization_id (int): Organization identifier for multi-tenant support
        business_hours (Dict): Business hours configuration
        timezone (str): Organization timezone
    """
    
    def __init__(self, organization_id: int = None):
        """
        Initialize SLA Manager
        
        Args:
            organization_id (int, optional): Organization ID for multi-tenant support.
                                          Defaults to None for global policies.
        """
        self.organization_id = organization_id
        self.business_hours = self._get_business_hours()
        self.timezone = self._get_organization_timezone()
    
    def calculate_due_date(self, 
                          ticket: 'Ticket', 
                          sla_policy: 'SLAPolicy' = None) -> datetime:
        """
        Calculate the due date for a ticket based on SLA policy and business hours.
        
        This method implements complex business logic to determine when a ticket
        should be resolved based on:
        - SLA policy response and resolution times
        - Business hours and holidays
        - Ticket priority and category
        - Organization-specific rules
        
        Args:
            ticket (Ticket): The ticket object containing priority, category, etc.
            sla_policy (SLAPolicy, optional): Specific SLA policy to use.
                                             If None, will find applicable policy.
        
        Returns:
            datetime: The calculated due date in UTC
            
        Raises:
            ValueError: If ticket or SLA policy is invalid
            SLAPolicyNotFound: If no applicable SLA policy is found
            
        Example:
            >>> sla_manager = SLAManager(organization_id=1)
            >>> ticket = Ticket.objects.get(id=123)
            >>> due_date = sla_manager.calculate_due_date(ticket)
            >>> print(f"Ticket due: {due_date}")
        """
        if not ticket:
            raise ValueError("Ticket cannot be None")
        
        # Get applicable SLA policy if not provided
        if not sla_policy:
            sla_policy = self.get_applicable_policy(ticket)
        
        if not sla_policy:
            raise SLAPolicyNotFound("No applicable SLA policy found for ticket")
        
        # Start with ticket creation time
        start_time = ticket.created_at
        
        # Calculate response time (first response deadline)
        response_time = self._calculate_response_time(sla_policy, ticket)
        response_due = self._add_business_time(start_time, response_time)
        
        # Calculate resolution time (full resolution deadline)
        resolution_time = self._calculate_resolution_time(sla_policy, ticket)
        resolution_due = self._add_business_time(start_time, resolution_time)
        
        # Return the earlier of response or resolution due date
        return min(response_due, resolution_due)
    
    def get_applicable_policy(self, ticket: 'Ticket') -> Optional['SLAPolicy']:
        """
        Find the most applicable SLA policy for a ticket.
        
        Searches for SLA policies in order of specificity:
        1. Ticket-specific policies
        2. Category-specific policies  
        3. Priority-specific policies
        4. Organization default policies
        5. Global default policies
        
        Args:
            ticket (Ticket): The ticket to find policy for
            
        Returns:
            SLAPolicy or None: The most applicable SLA policy
            
        Example:
            >>> policy = sla_manager.get_applicable_policy(ticket)
            >>> if policy:
            ...     print(f"Using policy: {policy.name}")
        """
        # Implementation would search for policies based on ticket attributes
        # This is a simplified version
        return None
    
    def evaluate_conditions(self, 
                           ticket: 'Ticket', 
                           conditions: List[Dict]) -> bool:
        """
        Evaluate SLA policy conditions against a ticket.
        
        Checks if a ticket meets the conditions specified in an SLA policy.
        Conditions can include:
        - Ticket priority levels
        - Category matching
        - Customer tier requirements
        - Custom field values
        - Time-based conditions
        
        Args:
            ticket (Ticket): The ticket to evaluate
            conditions (List[Dict]): List of condition dictionaries
            
        Returns:
            bool: True if all conditions are met, False otherwise
            
        Example:
            >>> conditions = [
            ...     {"field": "priority", "operator": "equals", "value": "high"},
            ...     {"field": "category", "operator": "in", "value": ["bug", "feature"]}
            ... ]
            >>> matches = sla_manager.evaluate_conditions(ticket, conditions)
        """
        for condition in conditions:
            if not self._evaluate_single_condition(ticket, condition):
                return False
        return True
    
    def check_breach(self, ticket: 'Ticket') -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a ticket has breached its SLA.
        
        Analyzes a ticket against its SLA policy to determine if:
        - Response time SLA has been breached
        - Resolution time SLA has been breached
        - Any escalation rules should be triggered
        
        Args:
            ticket (Ticket): The ticket to check for SLA breach
            
        Returns:
            Tuple[bool, Dict]: (is_breached, breach_details)
                - is_breached: True if SLA is breached
                - breach_details: Dictionary containing breach information
                
        Example:
            >>> is_breached, details = sla_manager.check_breach(ticket)
            >>> if is_breached:
            ...     print(f"SLA breached: {details['reason']}")
        """
        try:
            sla_policy = self.get_applicable_policy(ticket)
            if not sla_policy:
                return False, {"reason": "No SLA policy found"}
            
            current_time = timezone.now()
            due_date = self.calculate_due_date(ticket, sla_policy)
            
            if current_time > due_date:
                return True, {
                    "reason": "SLA deadline exceeded",
                    "due_date": due_date,
                    "overdue_minutes": (current_time - due_date).total_seconds() / 60,
                    "sla_policy": sla_policy.name
                }
            
            return False, {"reason": "SLA not breached"}
            
        except Exception as e:
            logger.error(f"Error checking SLA breach for ticket {ticket.id}: {e}")
            return False, {"reason": f"Error: {str(e)}"}
    
    def get_sla_status(self, ticket: 'Ticket') -> Dict[str, Any]:
        """
        Get comprehensive SLA status for a ticket.
        
        Provides detailed SLA information including:
        - Current SLA status (on_track, at_risk, breached)
        - Time remaining until breach
        - SLA policy details
        - Historical SLA performance
        
        Args:
            ticket (Ticket): The ticket to get SLA status for
            
        Returns:
            Dict: Comprehensive SLA status information
            
        Example:
            >>> status = sla_manager.get_sla_status(ticket)
            >>> print(f"Status: {status['status']}")
            >>> print(f"Time remaining: {status['time_remaining']} minutes")
        """
        try:
            sla_policy = self.get_applicable_policy(ticket)
            if not sla_policy:
                return {
                    "status": "no_policy",
                    "message": "No SLA policy found for this ticket"
                }
            
            current_time = timezone.now()
            due_date = self.calculate_due_date(ticket, sla_policy)
            time_remaining = (due_date - current_time).total_seconds() / 60
            
            # Determine status based on time remaining
            if time_remaining < 0:
                status = "breached"
            elif time_remaining < 60:  # Less than 1 hour
                status = "at_risk"
            else:
                status = "on_track"
            
            return {
                "status": status,
                "due_date": due_date,
                "time_remaining_minutes": max(0, time_remaining),
                "sla_policy": {
                    "name": sla_policy.name,
                    "response_time": sla_policy.response_time,
                    "resolution_time": sla_policy.resolution_time
                },
                "ticket_created": ticket.created_at,
                "current_time": current_time
            }
            
        except Exception as e:
            logger.error(f"Error getting SLA status for ticket {ticket.id}: {e}")
            return {
                "status": "error",
                "message": f"Error retrieving SLA status: {str(e)}"
            }
    
    def _add_business_time(self, start_time: datetime, business_minutes: int) -> datetime:
        """
        Add business time to a datetime, excluding weekends and holidays.
        
        This method implements complex business logic to calculate due dates
        that respect business hours, weekends, and holidays.
        
        Args:
            start_time (datetime): The starting datetime
            business_minutes (int): Number of business minutes to add
            
        Returns:
            datetime: The calculated due date in business time
        """
        current_time = start_time
        remaining_minutes = business_minutes
        
        while remaining_minutes > 0:
            # Check if current time is within business hours
            if self._is_business_hours(current_time):
                # Calculate minutes until end of business day
                end_of_day = self._get_end_of_business_day(current_time)
                minutes_until_end = (end_of_day - current_time).total_seconds() / 60
                
                if remaining_minutes <= minutes_until_end:
                    # Can complete within current business day
                    return current_time + timedelta(minutes=remaining_minutes)
                else:
                    # Move to next business day
                    remaining_minutes -= minutes_until_end
                    current_time = self._get_next_business_day(current_time)
            else:
                # Move to next business day
                current_time = self._get_next_business_day(current_time)
        
        return current_time
    
    def _is_business_hours(self, dt: datetime) -> bool:
        """Check if datetime falls within business hours."""
        # Implementation would check against business hours configuration
        return True
    
    def _get_end_of_business_day(self, dt: datetime) -> datetime:
        """Get end of business day for given datetime."""
        # Implementation would return end of business day
        return dt.replace(hour=17, minute=0, second=0, microsecond=0)
    
    def _get_next_business_day(self, dt: datetime) -> datetime:
        """Get next business day start time."""
        # Implementation would skip weekends and holidays
        return dt + timedelta(days=1)
    
    def _calculate_response_time(self, policy: 'SLAPolicy', ticket: 'Ticket') -> int:
        """Calculate response time in minutes based on policy and ticket attributes."""
        # Implementation would calculate based on priority, category, etc.
        return policy.response_time
    
    def _calculate_resolution_time(self, policy: 'SLAPolicy', ticket: 'Ticket') -> int:
        """Calculate resolution time in minutes based on policy and ticket attributes."""
        # Implementation would calculate based on priority, category, etc.
        return policy.resolution_time
    
    def _get_business_hours(self) -> Dict:
        """Get business hours configuration for organization."""
        # Implementation would retrieve from database or settings
        return {"start": "09:00", "end": "17:00", "days": [1, 2, 3, 4, 5]}
    
    def _get_organization_timezone(self) -> str:
        """Get organization timezone."""
        # Implementation would retrieve from organization settings
        return "UTC"


class SLAPolicy(models.Model):
    """
    SLA Policy Model
    
    Defines SLA policies with conditions, response times, and resolution times.
    Supports multi-tenant architecture with organization-specific policies.
    """
    
    name = models.CharField(max_length=100, help_text="Name of the SLA policy")
    description = models.TextField(help_text="Detailed description of the policy")
    organization = models.ForeignKey('organizations.Organization', 
                                   on_delete=models.CASCADE, 
                                   null=True, blank=True,
                                   help_text="Organization this policy applies to")
    
    # SLA Timeframes
    response_time = models.PositiveIntegerField(
        help_text="Response time in minutes"
    )
    resolution_time = models.PositiveIntegerField(
        help_text="Resolution time in minutes"
    )
    
    # Conditions
    conditions = models.JSONField(
        default=list,
        help_text="JSON array of conditions that must be met"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SLA Policy"
        verbose_name_plural = "SLA Policies"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.organization.name if self.organization else 'Global'})"


class SLAPolicyNotFound(Exception):
    """Exception raised when no applicable SLA policy is found."""
    pass