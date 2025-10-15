"""
Comprehensive Route Optimization Tests
Tests critical route optimization algorithms, distance calculations, and technician assignment logic.
"""

import pytest
import math
from datetime import datetime, timedelta
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

from apps.organizations.models import Organization
from apps.accounts.models import User
from apps.field_service.models import WorkOrder, Technician, JobAssignment
from apps.field_service.route_optimizer import RouteOptimizer
from apps.common.operators import DistanceCalculator, TimeCalculator

from .test_utilities import EnhancedTransactionTestCase, TestDataFactory, TestAssertions


class RouteOptimizerTest(EnhancedTransactionTestCase):
    """Test Route Optimizer with comprehensive algorithm coverage."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.route_optimizer = RouteOptimizer()
        
        # Create test technicians
        self.technician1 = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="John Doe",
            skills=["electrical", "plumbing"],
            current_location={"lat": 40.7128, "lng": -74.0060},  # NYC
            max_daily_distance=100.0,
            hourly_rate=50.0
        )
        
        self.technician2 = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Jane Smith",
            skills=["hvac", "electrical"],
            current_location={"lat": 40.7589, "lng": -73.9851},  # NYC
            max_daily_distance=80.0,
            hourly_rate=45.0
        )
        
        # Create test work orders
        self.work_order1 = WorkOrder.objects.create(
            organization=self.organization,
            customer=self.user,
            title="Electrical Repair",
            description="Fix electrical outlet",
            location={"lat": 40.7505, "lng": -73.9934},  # NYC
            priority="high",
            estimated_duration=120,  # 2 hours
            required_skills=["electrical"],
            scheduled_date=timezone.now() + timedelta(days=1)
        )
        
        self.work_order2 = WorkOrder.objects.create(
            organization=self.organization,
            customer=self.user,
            title="HVAC Maintenance",
            description="HVAC system maintenance",
            location={"lat": 40.7614, "lng": -73.9776},  # NYC
            priority="medium",
            estimated_duration=180,  # 3 hours
            required_skills=["hvac"],
            scheduled_date=timezone.now() + timedelta(days=1)
        )
    
    def test_optimize_routes_single_technician(self):
        """Test route optimization with single technician."""
        technicians = [self.technician1]
        work_orders = [self.work_order1, self.work_order2]
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 5.0  # 5 miles
            
            with patch.object(self.route_optimizer, 'assign_technicians') as mock_assign:
                mock_assign.return_value = {
                    'assignments': [
                        {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id},
                        {'technician_id': self.technician1.id, 'work_order_id': self.work_order2.id}
                    ],
                    'total_distance': 10.0,
                    'total_time': 300.0,
                    'efficiency_score': 0.85
                }
                
                result = self.route_optimizer.optimize_routes(technicians, work_orders)
                
                self.assertIn('assignments', result)
                self.assertIn('total_distance', result)
                self.assertIn('total_time', result)
                self.assertIn('efficiency_score', result)
                self.assertEqual(len(result['assignments']), 2)
    
    def test_optimize_routes_multiple_technicians(self):
        """Test route optimization with multiple technicians."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 3.0  # 3 miles
            
            with patch.object(self.route_optimizer, 'assign_technicians') as mock_assign:
                mock_assign.return_value = {
                    'assignments': [
                        {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id},
                        {'technician_id': self.technician2.id, 'work_order_id': self.work_order2.id}
                    ],
                    'total_distance': 6.0,
                    'total_time': 300.0,
                    'efficiency_score': 0.92
                }
                
                result = self.route_optimizer.optimize_routes(technicians, work_orders)
                
                self.assertIn('assignments', result)
                self.assertEqual(len(result['assignments']), 2)
                self.assertEqual(result['efficiency_score'], 0.92)
    
    def test_optimize_routes_no_technicians(self):
        """Test route optimization with no technicians."""
        technicians = []
        work_orders = [self.work_order1, self.work_order2]
        
        result = self.route_optimizer.optimize_routes(technicians, work_orders)
        
        self.assertIn('error', result)
        self.assertIn('No technicians available', result['error'])
    
    def test_optimize_routes_no_work_orders(self):
        """Test route optimization with no work orders."""
        technicians = [self.technician1, self.technician2]
        work_orders = []
        
        result = self.route_optimizer.optimize_routes(technicians, work_orders)
        
        self.assertIn('error', result)
        self.assertIn('No work orders to optimize', result['error'])
    
    def test_calculate_distance_haversine(self):
        """Test distance calculation using Haversine formula."""
        point1 = {"lat": 40.7128, "lng": -74.0060}  # NYC
        point2 = {"lat": 40.7589, "lng": -73.9851}  # NYC
        
        with patch('apps.field_service.route_optimizer.DistanceCalculator') as mock_calc:
            mock_calc.return_value.haversine_distance.return_value = 5.2
            
            distance = self.route_optimizer.calculate_distance(point1, point2)
            
            self.assertEqual(distance, 5.2)
            mock_calc.return_value.haversine_distance.assert_called_once_with(point1, point2)
    
    def test_calculate_distance_manhattan(self):
        """Test distance calculation using Manhattan distance."""
        point1 = {"lat": 40.7128, "lng": -74.0060}
        point2 = {"lat": 40.7589, "lng": -73.9851}
        
        with patch('apps.field_service.route_optimizer.DistanceCalculator') as mock_calc:
            mock_calc.return_value.manhattan_distance.return_value = 4.8
            
            distance = self.route_optimizer.calculate_distance(point1, point2, method="manhattan")
            
            self.assertEqual(distance, 4.8)
            mock_calc.return_value.manhattan_distance.assert_called_once_with(point1, point2)
    
    def test_calculate_distance_invalid_points(self):
        """Test distance calculation with invalid points."""
        point1 = {"lat": "invalid", "lng": -74.0060}
        point2 = {"lat": 40.7589, "lng": -73.9851}
        
        with self.assertRaises(ValueError):
            self.route_optimizer.calculate_distance(point1, point2)
    
    def test_assign_technicians_skill_matching(self):
        """Test technician assignment with skill matching."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 5.0
            
            with patch.object(self.route_optimizer, 'calculate_travel_time') as mock_time:
                mock_time.return_value = 15.0  # 15 minutes
                
                result = self.route_optimizer.assign_technicians(technicians, work_orders)
                
                self.assertIn('assignments', result)
                self.assertIn('total_distance', result)
                self.assertIn('total_time', result)
                self.assertIn('efficiency_score', result)
                
                # Check that assignments respect skill requirements
                for assignment in result['assignments']:
                    technician = next(t for t in technicians if t.id == assignment['technician_id'])
                    work_order = next(w for w in work_orders if w.id == assignment['work_order_id'])
                    
                    # Technician should have required skills
                    self.assertTrue(any(skill in technician.skills for skill in work_order.required_skills))
    
    def test_assign_technicians_distance_constraints(self):
        """Test technician assignment with distance constraints."""
        # Create technician with low max distance
        limited_technician = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Limited Technician",
            skills=["electrical"],
            current_location={"lat": 40.7128, "lng": -74.0060},
            max_daily_distance=2.0,  # Very low max distance
            hourly_rate=50.0
        )
        
        technicians = [limited_technician]
        work_orders = [self.work_order1]
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 10.0  # Distance exceeds max_daily_distance
            
            result = self.route_optimizer.assign_technicians(technicians, work_orders)
            
            # Should not assign work order due to distance constraint
            self.assertEqual(len(result['assignments']), 0)
            self.assertIn('unassigned_work_orders', result)
    
    def test_assign_technicians_time_constraints(self):
        """Test technician assignment with time constraints."""
        # Create work order with very short time window
        urgent_work_order = WorkOrder.objects.create(
            organization=self.organization,
            customer=self.user,
            title="Urgent Repair",
            description="Urgent repair needed",
            location={"lat": 40.7505, "lng": -73.9934},
            priority="critical",
            estimated_duration=60,
            required_skills=["electrical"],
            scheduled_date=timezone.now() + timedelta(minutes=30)  # Very short time window
        )
        
        technicians = [self.technician1]
        work_orders = [urgent_work_order]
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 5.0
            
            with patch.object(self.route_optimizer, 'calculate_travel_time') as mock_time:
                mock_time.return_value = 45.0  # Travel time exceeds available time
                
                result = self.route_optimizer.assign_technicians(technicians, work_orders)
                
                # Should not assign due to time constraint
                self.assertEqual(len(result['assignments']), 0)
                self.assertIn('unassigned_work_orders', result)
    
    def test_calculate_travel_time(self):
        """Test travel time calculation."""
        point1 = {"lat": 40.7128, "lng": -74.0060}
        point2 = {"lat": 40.7589, "lng": -73.9851}
        distance = 5.0
        
        with patch('apps.field_service.route_optimizer.TimeCalculator') as mock_calc:
            mock_calc.return_value.calculate_travel_time.return_value = 15.0
            
            travel_time = self.route_optimizer.calculate_travel_time(point1, point2, distance)
            
            self.assertEqual(travel_time, 15.0)
            mock_calc.return_value.calculate_travel_time.assert_called_once_with(point1, point2, distance)
    
    def test_calculate_travel_time_traffic_conditions(self):
        """Test travel time calculation with traffic conditions."""
        point1 = {"lat": 40.7128, "lng": -74.0060}
        point2 = {"lat": 40.7589, "lng": -73.9851}
        distance = 5.0
        traffic_conditions = "heavy"
        
        with patch('apps.field_service.route_optimizer.TimeCalculator') as mock_calc:
            mock_calc.return_value.calculate_travel_time.return_value = 25.0
            
            travel_time = self.route_optimizer.calculate_travel_time(
                point1, point2, distance, traffic_conditions
            )
            
            self.assertEqual(travel_time, 25.0)
            mock_calc.return_value.calculate_travel_time.assert_called_once_with(
                point1, point2, distance, traffic_conditions
            )
    
    def test_optimize_route_sequence(self):
        """Test route sequence optimization."""
        work_orders = [self.work_order1, self.work_order2]
        start_location = {"lat": 40.7128, "lng": -74.0060}
        
        with patch.object(self.route_optimizer, 'calculate_distance') as mock_distance:
            mock_distance.return_value = 3.0
            
            with patch.object(self.route_optimizer, 'calculate_travel_time') as mock_time:
                mock_time.return_value = 10.0
                
                result = self.route_optimizer.optimize_route_sequence(work_orders, start_location)
                
                self.assertIn('optimized_sequence', result)
                self.assertIn('total_distance', result)
                self.assertIn('total_time', result)
                self.assertEqual(len(result['optimized_sequence']), 2)
    
    def test_optimize_route_sequence_empty_list(self):
        """Test route sequence optimization with empty work orders list."""
        work_orders = []
        start_location = {"lat": 40.7128, "lng": -74.0060}
        
        result = self.route_optimizer.optimize_route_sequence(work_orders, start_location)
        
        self.assertIn('error', result)
        self.assertIn('No work orders to optimize', result['error'])
    
    def test_calculate_efficiency_score(self):
        """Test efficiency score calculation."""
        assignments = [
            {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id, 'distance': 5.0, 'time': 120},
            {'technician_id': self.technician2.id, 'work_order_id': self.work_order2.id, 'distance': 3.0, 'time': 180}
        ]
        
        efficiency_score = self.route_optimizer.calculate_efficiency_score(assignments)
        
        self.assertIsInstance(efficiency_score, float)
        self.assertGreaterEqual(efficiency_score, 0.0)
        self.assertLessEqual(efficiency_score, 1.0)
    
    def test_calculate_efficiency_score_empty_assignments(self):
        """Test efficiency score calculation with empty assignments."""
        assignments = []
        
        efficiency_score = self.route_optimizer.calculate_efficiency_score(assignments)
        
        self.assertEqual(efficiency_score, 0.0)
    
    def test_validate_technician_availability(self):
        """Test technician availability validation."""
        technician = self.technician1
        work_order = self.work_order1
        scheduled_time = timezone.now() + timedelta(days=1)
        
        with patch.object(self.route_optimizer, 'check_technician_schedule') as mock_schedule:
            mock_schedule.return_value = True
            
            is_available = self.route_optimizer.validate_technician_availability(
                technician, work_order, scheduled_time
            )
            
            self.assertTrue(is_available)
            mock_schedule.assert_called_once_with(technician, scheduled_time, work_order.estimated_duration)
    
    def test_validate_technician_availability_conflict(self):
        """Test technician availability validation with schedule conflict."""
        technician = self.technician1
        work_order = self.work_order1
        scheduled_time = timezone.now() + timedelta(days=1)
        
        with patch.object(self.route_optimizer, 'check_technician_schedule') as mock_schedule:
            mock_schedule.return_value = False
            
            is_available = self.route_optimizer.validate_technician_availability(
                technician, work_order, scheduled_time
            )
            
            self.assertFalse(is_available)
    
    def test_validate_technician_skills(self):
        """Test technician skills validation."""
        technician = self.technician1
        work_order = self.work_order1
        
        has_skills = self.route_optimizer.validate_technician_skills(technician, work_order)
        
        self.assertTrue(has_skills)
    
    def test_validate_technician_skills_missing_skills(self):
        """Test technician skills validation with missing skills."""
        technician = self.technician1
        work_order = WorkOrder.objects.create(
            organization=self.organization,
            customer=self.user,
            title="HVAC Repair",
            description="HVAC system repair",
            location={"lat": 40.7505, "lng": -73.9934},
            priority="high",
            estimated_duration=120,
            required_skills=["hvac"],  # Technician doesn't have HVAC skills
            scheduled_date=timezone.now() + timedelta(days=1)
        )
        
        has_skills = self.route_optimizer.validate_technician_skills(technician, work_order)
        
        self.assertFalse(has_skills)
    
    def test_calculate_route_cost(self):
        """Test route cost calculation."""
        assignments = [
            {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id, 'time': 120},
            {'technician_id': self.technician2.id, 'work_order_id': self.work_order2.id, 'time': 180}
        ]
        
        with patch.object(self.route_optimizer, 'get_technician_hourly_rate') as mock_rate:
            mock_rate.side_effect = [50.0, 45.0]
            
            total_cost = self.route_optimizer.calculate_route_cost(assignments)
            
            # Expected cost: (120/60 * 50) + (180/60 * 45) = 100 + 135 = 235
            self.assertEqual(total_cost, 235.0)
    
    def test_calculate_route_cost_empty_assignments(self):
        """Test route cost calculation with empty assignments."""
        assignments = []
        
        total_cost = self.route_optimizer.calculate_route_cost(assignments)
        
        self.assertEqual(total_cost, 0.0)
    
    def test_optimize_for_cost(self):
        """Test route optimization for cost minimization."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        optimization_criteria = "cost"
        
        with patch.object(self.route_optimizer, 'assign_technicians') as mock_assign:
            mock_assign.return_value = {
                'assignments': [
                    {'technician_id': self.technician2.id, 'work_order_id': self.work_order1.id},
                    {'technician_id': self.technician1.id, 'work_order_id': self.work_order2.id}
                ],
                'total_cost': 200.0,
                'efficiency_score': 0.85
            }
            
            result = self.route_optimizer.optimize_routes(technicians, work_orders, optimization_criteria)
            
            self.assertIn('assignments', result)
            self.assertIn('total_cost', result)
            self.assertEqual(result['total_cost'], 200.0)
    
    def test_optimize_for_time(self):
        """Test route optimization for time minimization."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        optimization_criteria = "time"
        
        with patch.object(self.route_optimizer, 'assign_technicians') as mock_assign:
            mock_assign.return_value = {
                'assignments': [
                    {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id},
                    {'technician_id': self.technician2.id, 'work_order_id': self.work_order2.id}
                ],
                'total_time': 300.0,
                'efficiency_score': 0.90
            }
            
            result = self.route_optimizer.optimize_routes(technicians, work_orders, optimization_criteria)
            
            self.assertIn('assignments', result)
            self.assertIn('total_time', result)
            self.assertEqual(result['total_time'], 300.0)
    
    def test_optimize_for_distance(self):
        """Test route optimization for distance minimization."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        optimization_criteria = "distance"
        
        with patch.object(self.route_optimizer, 'assign_technicians') as mock_assign:
            mock_assign.return_value = {
                'assignments': [
                    {'technician_id': self.technician1.id, 'work_order_id': self.work_order1.id},
                    {'technician_id': self.technician2.id, 'work_order_id': self.work_order2.id}
                ],
                'total_distance': 8.0,
                'efficiency_score': 0.88
            }
            
            result = self.route_optimizer.optimize_routes(technicians, work_orders, optimization_criteria)
            
            self.assertIn('assignments', result)
            self.assertIn('total_distance', result)
            self.assertEqual(result['total_distance'], 8.0)
    
    def test_optimize_invalid_criteria(self):
        """Test route optimization with invalid criteria."""
        technicians = [self.technician1, self.technician2]
        work_orders = [self.work_order1, self.work_order2]
        optimization_criteria = "invalid"
        
        result = self.route_optimizer.optimize_routes(technicians, work_orders, optimization_criteria)
        
        self.assertIn('error', result)
        self.assertIn('Invalid optimization criteria', result['error'])


class RouteOptimizerIntegrationTest(EnhancedTransactionTestCase):
    """Integration tests for Route Optimizer with real data."""
    
    def setUp(self):
        super().setUp()
        self.organization = TestDataFactory.create_organization()
        self.user = TestDataFactory.create_user(self.organization)
        self.route_optimizer = RouteOptimizer()
    
    def test_end_to_end_route_optimization(self):
        """Test complete route optimization workflow."""
        # Create multiple technicians
        technicians = []
        for i in range(3):
            technician = Technician.objects.create(
                organization=self.organization,
                user=self.user,
                name=f"Technician {i+1}",
                skills=["electrical", "plumbing", "hvac"],
                current_location={"lat": 40.7128 + i*0.01, "lng": -74.0060 + i*0.01},
                max_daily_distance=100.0,
                hourly_rate=50.0 + i*5
            )
            technicians.append(technician)
        
        # Create multiple work orders
        work_orders = []
        for i in range(5):
            work_order = WorkOrder.objects.create(
                organization=self.organization,
                customer=self.user,
                title=f"Work Order {i+1}",
                description=f"Description for work order {i+1}",
                location={"lat": 40.7505 + i*0.01, "lng": -73.9934 + i*0.01},
                priority=["low", "medium", "high"][i % 3],
                estimated_duration=120 + i*30,
                required_skills=["electrical", "plumbing", "hvac"][i % 3],
                scheduled_date=timezone.now() + timedelta(days=1)
            )
            work_orders.append(work_order)
        
        # Optimize routes
        result = self.route_optimizer.optimize_routes(technicians, work_orders)
        
        # Verify results
        self.assertIn('assignments', result)
        self.assertIn('total_distance', result)
        self.assertIn('total_time', result)
        self.assertIn('efficiency_score', result)
        
        # Check that all work orders are assigned
        assigned_work_order_ids = [a['work_order_id'] for a in result['assignments']]
        work_order_ids = [w.id for w in work_orders]
        
        # All work orders should be assigned
        for work_order_id in work_order_ids:
            self.assertIn(work_order_id, assigned_work_order_ids)
    
    def test_route_optimization_with_constraints(self):
        """Test route optimization with various constraints."""
        # Create technician with limited capacity
        limited_technician = Technician.objects.create(
            organization=self.organization,
            user=self.user,
            name="Limited Technician",
            skills=["electrical"],
            current_location={"lat": 40.7128, "lng": -74.0060},
            max_daily_distance=10.0,  # Very limited distance
            hourly_rate=50.0
        )
        
        # Create work orders with different requirements
        work_orders = []
        for i in range(3):
            work_order = WorkOrder.objects.create(
                organization=self.organization,
                customer=self.user,
                title=f"Work Order {i+1}",
                description=f"Description for work order {i+1}",
                location={"lat": 40.7505 + i*0.1, "lng": -73.9934 + i*0.1},  # Increasing distance
                priority="high",
                estimated_duration=120,
                required_skills=["electrical"],
                scheduled_date=timezone.now() + timedelta(days=1)
            )
            work_orders.append(work_order)
        
        # Optimize routes
        result = self.route_optimizer.optimize_routes([limited_technician], work_orders)
        
        # Should have some unassigned work orders due to distance constraints
        self.assertIn('assignments', result)
        self.assertIn('unassigned_work_orders', result)
        
        # Check that assignments respect distance constraints
        for assignment in result['assignments']:
            technician = limited_technician
            work_order = next(w for w in work_orders if w.id == assignment['work_order_id'])
            
            # Calculate distance (simplified)
            distance = abs(work_order.location['lat'] - technician.current_location['lat']) + \
                      abs(work_order.location['lng'] - technician.current_location['lng'])
            
            # Distance should be within technician's max daily distance
            self.assertLessEqual(distance, technician.max_daily_distance)


# Export test classes
__all__ = [
    'RouteOptimizerTest',
    'RouteOptimizerIntegrationTest'
]