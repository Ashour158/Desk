"""
Operator evaluation utilities to reduce complexity in compare_values functions.
"""

import re
from typing import Any, Dict, List
from .constants import (
    OPERATOR_EQUALS,
    OPERATOR_NOT_EQUALS,
    OPERATOR_CONTAINS,
    OPERATOR_NOT_CONTAINS,
    OPERATOR_STARTS_WITH,
    OPERATOR_ENDS_WITH,
    OPERATOR_IN,
    OPERATOR_NOT_IN,
    OPERATOR_GREATER_THAN,
    OPERATOR_LESS_THAN,
    OPERATOR_GREATER_THAN_OR_EQUAL,
    OPERATOR_LESS_THAN_OR_EQUAL,
    OPERATOR_IS_EMPTY,
    OPERATOR_IS_NOT_EMPTY,
    OPERATOR_REGEX,
)


class OperatorEvaluator:
    """Handles operator evaluation with reduced complexity."""
    
    def __init__(self):
        self.operators = {
            OPERATOR_EQUALS: self._equals,
            OPERATOR_NOT_EQUALS: self._not_equals,
            OPERATOR_CONTAINS: self._contains,
            OPERATOR_NOT_CONTAINS: self._not_contains,
            OPERATOR_STARTS_WITH: self._starts_with,
            OPERATOR_ENDS_WITH: self._ends_with,
            OPERATOR_IN: self._in_list,
            OPERATOR_NOT_IN: self._not_in_list,
            OPERATOR_GREATER_THAN: self._greater_than,
            OPERATOR_LESS_THAN: self._less_than,
            OPERATOR_GREATER_THAN_OR_EQUAL: self._greater_than_or_equal,
            OPERATOR_LESS_THAN_OR_EQUAL: self._less_than_or_equal,
            OPERATOR_IS_EMPTY: self._is_empty,
            OPERATOR_IS_NOT_EMPTY: self._is_not_empty,
            OPERATOR_REGEX: self._regex_match,
        }
    
    def evaluate(self, field_value: Any, operator: str, expected_value: Any) -> bool:
        """Evaluate field value against expected value using operator."""
        if field_value is None:
            return False
        
        # Normalize string values for comparison
        if isinstance(expected_value, str) and hasattr(field_value, "lower"):
            field_value = str(field_value).lower()
            expected_value = expected_value.lower()
        
        # Get operator function
        operator_func = self.operators.get(operator)
        if not operator_func:
            return False
        
        return operator_func(field_value, expected_value)
    
    def _equals(self, field_value: Any, expected_value: Any) -> bool:
        """Check if values are equal."""
        return field_value == expected_value
    
    def _not_equals(self, field_value: Any, expected_value: Any) -> bool:
        """Check if values are not equal."""
        return field_value != expected_value
    
    def _contains(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value contains expected value."""
        return expected_value in str(field_value)
    
    def _not_contains(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value does not contain expected value."""
        return expected_value not in str(field_value)
    
    def _starts_with(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value starts with expected value."""
        return str(field_value).startswith(expected_value)
    
    def _ends_with(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value ends with expected value."""
        return str(field_value).endswith(expected_value)
    
    def _in_list(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is in expected list."""
        return field_value in expected_value
    
    def _not_in_list(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is not in expected list."""
        return field_value not in expected_value
    
    def _greater_than(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is greater than expected value."""
        return field_value > expected_value
    
    def _less_than(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is less than expected value."""
        return field_value < expected_value
    
    def _greater_than_or_equal(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is greater than or equal to expected value."""
        return field_value >= expected_value
    
    def _less_than_or_equal(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is less than or equal to expected value."""
        return field_value <= expected_value
    
    def _is_empty(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is empty."""
        return not field_value or str(field_value).strip() == ""
    
    def _is_not_empty(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value is not empty."""
        return field_value and str(field_value).strip() != ""
    
    def _regex_match(self, field_value: Any, expected_value: Any) -> bool:
        """Check if field value matches regex pattern."""
        try:
            return bool(re.search(expected_value, str(field_value)))
        except re.error:
            return False


class BusinessHoursCalculator:
    """Handles business hours calculations with reduced complexity."""
    
    def __init__(self):
        self.operator_evaluator = OperatorEvaluator()
    
    def add_business_time(self, start_time, duration, business_hours=None):
        """Add business time to start time."""
        if not business_hours:
            return start_time + duration
        
        current_time = start_time
        remaining_duration = duration
        
        while remaining_duration.total_seconds() > 0:
            current_time = self._process_business_day(
                current_time, remaining_duration, business_hours
            )
            remaining_duration = self._calculate_remaining_duration(
                current_time, remaining_duration, business_hours
            )
        
        return current_time
    
    def _process_business_day(self, current_time, remaining_duration, business_hours):
        """Process a single business day."""
        day_name = current_time.strftime("%A").lower()
        day_hours = business_hours.get(day_name, {})
        
        if not day_hours.get("enabled", False):
            return self._get_next_business_day(current_time, business_hours)
        
        business_start, business_end = self._get_business_hours(current_time, day_hours)
        
        # Adjust current time to business hours
        if current_time < business_start:
            current_time = business_start
        elif current_time >= business_end:
            return self._get_next_business_day(current_time, business_hours)
        
        return current_time
    
    def _get_business_hours(self, current_time, day_hours):
        """Get business start and end times for a day."""
        start_hour = self._parse_time(day_hours.get("start", "09:00"))
        end_hour = self._parse_time(day_hours.get("end", "17:00"))
        
        business_start = current_time.replace(
            hour=start_hour.hour, minute=start_hour.minute, second=0, microsecond=0
        )
        business_end = current_time.replace(
            hour=end_hour.hour, minute=end_hour.minute, second=0, microsecond=0
        )
        
        return business_start, business_end
    
    def _calculate_remaining_duration(self, current_time, remaining_duration, business_hours):
        """Calculate remaining duration after processing current day."""
        day_name = current_time.strftime("%A").lower()
        day_hours = business_hours.get(day_name, {})
        
        if not day_hours.get("enabled", False):
            return remaining_duration
        
        _, business_end = self._get_business_hours(current_time, day_hours)
        time_remaining_today = business_end - current_time
        
        if remaining_duration <= time_remaining_today:
            return remaining_duration - remaining_duration  # Zero duration
        else:
            return remaining_duration - time_remaining_today
    
    def _get_next_business_day(self, current_time, business_hours):
        """Get the next business day start time."""
        from datetime import timedelta
        from .constants import SLA_MAX_DAYS_TO_CHECK
        
        next_day = current_time + timedelta(days=1)
        
        for _ in range(SLA_MAX_DAYS_TO_CHECK):
            day_name = next_day.strftime("%A").lower()
            day_hours = business_hours.get(day_name, {})
            
            if day_hours.get("enabled", False):
                start_hour = self._parse_time(day_hours.get("start", "09:00"))
                return next_day.replace(
                    hour=start_hour.hour,
                    minute=start_hour.minute,
                    second=0,
                    microsecond=0,
                )
            
            next_day += timedelta(days=1)
        
        # Fallback to next day at 9 AM
        return current_time + timedelta(days=1)
    
    def _parse_time(self, time_str):
        """Parse time string (HH:MM) to time object."""
        from datetime import time
        from .constants import DEFAULT_BUSINESS_START_TIME
        
        try:
            hour, minute = map(int, time_str.split(":"))
            return time(hour, minute)
        except (ValueError, AttributeError):
            return DEFAULT_BUSINESS_START_TIME
