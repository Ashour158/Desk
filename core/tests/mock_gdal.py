"""
Mock GDAL library for testing purposes.
This provides basic GDAL functionality without requiring the actual GDAL installation.
"""

class MockGDAL:
    """Mock GDAL class for testing"""
    def __init__(self, *args, **kwargs):
        pass

class MockPoint:
    """Mock Point class for testing"""
    def __init__(self, x, y, srid=None):
        self.x = x
        self.y = y
        self.srid = srid or 4326
    
    def __str__(self):
        return f"POINT({self.x} {self.y})"

# Mock the GDAL library
import sys
from unittest.mock import MagicMock

# Create mock modules
mock_gdal = MagicMock()
mock_gdal.Point = MockPoint

# Add to sys.modules
sys.modules['django.contrib.gis.geos'] = mock_gdal
sys.modules['django.contrib.gis.gdal'] = mock_gdal
sys.modules['django.contrib.gis'] = mock_gdal
