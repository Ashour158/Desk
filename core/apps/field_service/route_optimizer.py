"""
Route optimization for field service technicians.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.utils import timezone
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

from .models import WorkOrder, Technician, Route
from apps.organizations.models import Organization

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """Route optimization using Google OR-Tools."""

    def __init__(self):
        self.google_maps_api_key = None  # Set from settings

    def optimize_daily_routes(self, date, organization):
        """Optimize routes for all technicians on a given date."""
        try:
            # Get work orders for the date
            work_orders = WorkOrder.objects.filter(
                organization=organization,
                scheduled_start__date=date,
                status="scheduled",
            )

            if not work_orders.exists():
                return []

            # Get available technicians
            technicians = Technician.objects.filter(
                organization=organization,
                is_active=True,
                availability_status="available",
            )

            if not technicians.exists():
                return []

            # Group work orders by technician skills
            assignments = self.match_skills_to_technicians(work_orders, technicians)

            optimized_routes = []

            for technician, assigned_orders in assignments.items():
                if assigned_orders:
                    route = self.optimize_technician_route(
                        technician, assigned_orders, date
                    )
                    if route:
                        optimized_routes.append(route)

            return optimized_routes

        except Exception as e:
            logger.error(f"Error optimizing routes: {str(e)}")
            return []

    def match_skills_to_technicians(self, work_orders, technicians):
        """Match work orders to technicians based on skills."""
        assignments = {tech: [] for tech in technicians}

        for work_order in work_orders:
            best_technician = self.find_best_technician_for_work_order(
                work_order, technicians
            )
            if best_technician:
                assignments[best_technician].append(work_order)

        return assignments

    def find_best_technician_for_work_order(self, work_order, technicians):
        """Find the best technician for a work order."""
        best_technician = None
        best_score = -1

        for technician in technicians:
            score = self.calculate_technician_score(work_order, technician)
            if score > best_score:
                best_score = score
                best_technician = technician

        return best_technician

    def calculate_technician_score(self, work_order, technician):
        """Calculate score for technician-work order match."""
        score = 0

        # Skill matching
        if work_order.required_skills:
            required_skills = work_order.required_skills
            technician_skills = technician.skills or []

            skill_match_count = sum(
                1 for skill in required_skills if skill in technician_skills
            )
            skill_score = (
                skill_match_count / len(required_skills) if required_skills else 1
            )
            score += skill_score * 50

        # Availability
        if technician.availability_status == "available":
            score += 20
        elif technician.availability_status == "busy":
            score += 10

        # Workload (fewer current assignments = higher score)
        current_assignments = WorkOrder.objects.filter(
            assigned_technician=technician, status__in=["scheduled", "in_progress"]
        ).count()
        workload_score = max(0, 20 - current_assignments)
        score += workload_score

        # Location proximity (if work order has location)
        if work_order.location and technician.current_location:
            try:
                distance = work_order.location.distance(technician.current_location)
                # Convert to miles and score (closer = higher score)
                distance_miles = distance.mi
                proximity_score = max(0, 20 - distance_miles)
                score += proximity_score
            except:
                pass

        return score

    def optimize_technician_route(self, technician, work_orders, date):
        """Optimize route for a single technician."""
        try:
            if not work_orders:
                return None

            # Get technician's starting location
            start_location = technician.current_location
            if not start_location:
                # Use organization's default location or technician's home
                start_location = Point(-74.006, 40.7128)  # Default to NYC

            # Solve TSP using OR-Tools
            optimized_sequence = self.solve_tsp(start_location, work_orders)

            if not optimized_sequence:
                return None

            # Create route record
            route = Route.objects.create(
                organization=technician.organization,
                technician=technician,
                route_date=date,
                work_orders=[wo.id for wo in optimized_sequence],
                optimized_sequence=optimized_sequence,
                total_distance=self.calculate_total_distance(optimized_sequence),
                total_duration=self.calculate_total_duration(optimized_sequence),
            )

            # Update work order assignments
            for i, work_order in enumerate(optimized_sequence):
                work_order.assigned_technician = technician
                work_order.route_order = i + 1
                work_order.save()

            logger.info(
                f"Optimized route for technician {technician.user.full_name}: {len(optimized_sequence)} work orders"
            )
            return route

        except Exception as e:
            logger.error(
                f"Error optimizing route for technician {technician.id}: {str(e)}"
            )
            return None

    def solve_tsp(self, start_location, work_orders):
        """Solve Traveling Salesman Problem using OR-Tools."""
        try:
            from ortools.constraint_solver import routing_enums_pb2
            from ortools.constraint_solver import pywrapcp

            # Create distance matrix
            locations = [start_location] + [
                wo.location for wo in work_orders if wo.location
            ]

            if len(locations) < 2:
                return work_orders

            # Calculate distance matrix
            distance_matrix = self.calculate_distance_matrix(locations)

            # Create routing model
            manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
            routing = pywrapcp.RoutingModel(manager)

            # Define cost function
            def distance_callback(from_index, to_index):
                return int(distance_matrix[from_index][to_index])

            transit_callback_index = routing.RegisterTransitCallback(distance_callback)
            routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

            # Set search parameters
            search_parameters = pywrapcp.DefaultRoutingSearchParameters()
            search_parameters.first_solution_strategy = (
                routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
            )
            search_parameters.local_search_metaheuristic = (
                routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
            )
            search_parameters.time_limit.seconds = 30

            # Solve
            solution = routing.SolveWithParameters(search_parameters)

            if solution:
                # Extract route
                route_indices = []
                index = routing.Start(0)
                while not routing.IsEnd(index):
                    route_indices.append(index)
                    index = solution.Value(routing.NextVar(index))

                # Map back to work orders
                optimized_sequence = []
                for i in route_indices[1:]:  # Skip start location
                    if i <= len(work_orders):
                        optimized_sequence.append(work_orders[i - 1])

                return optimized_sequence

            return work_orders

        except ImportError:
            logger.warning(
                "OR-Tools not available, using simple distance-based sorting"
            )
            return self.simple_route_optimization(start_location, work_orders)
        except Exception as e:
            logger.error(f"Error solving TSP: {str(e)}")
            return work_orders

    def simple_route_optimization(self, start_location, work_orders):
        """Simple route optimization based on distance."""
        try:
            # Sort work orders by distance from start location
            work_orders_with_distance = []

            for work_order in work_orders:
                if work_order.location:
                    distance = start_location.distance(work_order.location)
                    work_orders_with_distance.append((work_order, distance))
                else:
                    work_orders_with_distance.append((work_order, float("inf")))

            # Sort by distance
            work_orders_with_distance.sort(key=lambda x: x[1])

            return [wo for wo, _ in work_orders_with_distance]

        except Exception as e:
            logger.error(f"Error in simple route optimization: {str(e)}")
            return work_orders

    def calculate_distance_matrix(self, locations):
        """Calculate distance matrix between locations."""
        matrix = []

        for i, location1 in enumerate(locations):
            row = []
            for j, location2 in enumerate(locations):
                if i == j:
                    row.append(0)
                else:
                    try:
                        distance = location1.distance(location2)
                        # Convert to meters and round
                        distance_meters = distance.m
                        row.append(int(distance_meters))
                    except:
                        row.append(0)
            matrix.append(row)

        return matrix

    def calculate_total_distance(self, work_orders):
        """Calculate total distance for optimized route."""
        if not work_orders:
            return 0

        total_distance = 0

        for i in range(len(work_orders) - 1):
            current = work_orders[i]
            next_wo = work_orders[i + 1]

            if current.location and next_wo.location:
                distance = current.location.distance(next_wo.location)
                total_distance += distance.m

        return total_distance

    def calculate_total_duration(self, work_orders):
        """Calculate total duration for optimized route."""
        if not work_orders:
            return 0

        total_duration = 0

        for work_order in work_orders:
            if work_order.estimated_duration:
                total_duration += work_order.estimated_duration

        # Add travel time (estimate 1 minute per 100 meters)
        total_distance = self.calculate_total_distance(work_orders)
        travel_time = (total_distance / 100) * 60  # Convert to minutes

        return total_duration + travel_time

    def get_route_optimization_stats(self, organization, start_date, end_date):
        """Get route optimization statistics."""
        try:
            routes = Route.objects.filter(
                organization=organization,
                route_date__gte=start_date,
                route_date__lte=end_date,
            )

            total_routes = routes.count()
            total_distance = sum(route.total_distance for route in routes)
            total_duration = sum(route.total_duration for route in routes)
            avg_distance = total_distance / total_routes if total_routes > 0 else 0
            avg_duration = total_duration / total_routes if total_routes > 0 else 0

            return {
                "total_routes": total_routes,
                "total_distance": total_distance,
                "total_duration": total_duration,
                "avg_distance": avg_distance,
                "avg_duration": avg_duration,
            }

        except Exception as e:
            logger.error(f"Error getting route optimization stats: {str(e)}")
            return {}

    def suggest_route_improvements(self, route):
        """Suggest improvements for a route."""
        improvements = []

        # Check for long distances between consecutive work orders
        work_orders = route.work_orders.all()
        for i in range(len(work_orders) - 1):
            current = work_orders[i]
            next_wo = work_orders[i + 1]

            if current.location and next_wo.location:
                distance = current.location.distance(next_wo.location)
                if distance.m > 10000:  # More than 10km
                    improvements.append(
                        {
                            "type": "long_distance",
                            "message": f"Long distance between {current.title} and {next_wo.title}",
                            "distance": distance.m,
                        }
                    )

        # Check for time conflicts
        for i in range(len(work_orders) - 1):
            current = work_orders[i]
            next_wo = work_orders[i + 1]

            if current.scheduled_end and next_wo.scheduled_start:
                if current.scheduled_end > next_wo.scheduled_start:
                    improvements.append(
                        {
                            "type": "time_conflict",
                            "message": f"Time conflict between {current.title} and {next_wo.title}",
                            "current_end": current.scheduled_end,
                            "next_start": next_wo.scheduled_start,
                        }
                    )

        return improvements
