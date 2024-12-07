import math
from .models import City, TruckStop

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

import os

def interpolate_geo_point(start_point, end_point, fraction):
    # https://www.movable-type.co.uk/scripts/latlong.html
    # Convert degrees to radians
    lat1, lon1 = math.radians(start_point.y), math.radians(start_point.x)
    lat2, lon2 = math.radians(end_point.y), math.radians(end_point.x)    
    # Calculate angular distance
    delta = math.acos(
        math.sin(lat1) * math.sin(lat2) +
        math.cos(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    )

    if delta == 0:  # Avoid division by zero if the points are identical
         return Point(start_point.x, start_point.y)
    
    # Calculate interpolation factors
    a = math.sin((1 - fraction) * delta) / math.sin(delta)
    b = math.sin(fraction * delta) / math.sin(delta)

    # Interpolate x, y, z coordinates
    x = a * math.cos(lat1) * math.cos(lon1) + b * math.cos(lat2) * math.cos(lon2)
    y = a * math.cos(lat1) * math.sin(lon1) + b * math.cos(lat2) * math.sin(lon2)
    z = a * math.sin(lat1) + b * math.sin(lat2)
    
     # Convert back to latitude and longitude in radians
    lat_i = math.atan2(z, math.sqrt(x**2 + y**2))
    lon_i = math.atan2(y, x)
    
    # Convert back to degrees
    lat_i_deg = math.degrees(lat_i)
    lon_i_deg = math.degrees(lon_i)
    
    
    # Convert radians to degrees
    return Point(lon_i_deg, lat_i_deg)


def calculate_fuel_stops(route_steps):

    MAX_RANGE = os.environ.get('MAX_RANGE', 500)  # Maximum range in miles
    REFUEL_BUFFER = os.environ.get('REFUEL_BUFFER', 50) # Miles to look for station before empty

    stops = []  # Distances where refueling is needed
    remaining_range = MAX_RANGE  # Remaining range at the start of the trip
    cumulative_distance = 0  # Total distance traveled so far

    for segment in route_steps:
        
        segment_distance = ((segment.distance / 1000) * 0.62137119)
        current_segment_distance = segment_distance
        cumulative_distance += segment_distance
        
        while segment_distance > remaining_range - REFUEL_BUFFER:
            segment_distance -= remaining_range

            # Finding the percetage along the segment we need to refuel at.
            percentage_segment = (current_segment_distance - segment_distance) / current_segment_distance
            
            if segment.type != 10:
                interpolated_point = interpolate_geo_point(segment.way_points.first().coordinate, segment.way_points.last().coordinate, percentage_segment)
                stop = {
                    'point': interpolated_point,
                    'distance': remaining_range
                }
                stops.append(stop)

            remaining_range = MAX_RANGE

        remaining_range -= segment_distance

    # Final stop for leftover range
    if remaining_range < MAX_RANGE:
        final_point = route_steps[-1].way_points.first().coordinate
        stop = {
            'point': final_point,
            # Refill to the top at the end
            'distance': MAX_RANGE - remaining_range
        }

    return stops



def snap_to_linestring_geodjango(intermediate_point, linestring):
    """
    Snap a point to the nearest point on a LineString using GeoDjango.

    Parameters:
        intermediate_point (Point): the point to snap.
        linestring_coords (LineString): the LineString.

    Returns:
        snapped_point (Point): the snapped point.
    """
    snapped_point = linestring.interpolate(
        linestring.project(intermediate_point)
    )

    return snapped_point


def find_nearest_truck_stops(stop_point):
    # Search for the closest city with at least one truck stop
    closest_city_with_stops = (
        City.objects.filter(truckstop__isnull=False)
        .annotate(distance=Distance('location', stop_point))
        .order_by('distance')
        .first()
    )

    if closest_city_with_stops:
        optimal_truck_stop = (
            TruckStop.objects.filter(city=closest_city_with_stops)
            .order_by('fuel_retail_price')
            .first()
        )
        return optimal_truck_stop

    # If no city with truck stops is nearby, expand the search
    nearest_truck_stop = (
        TruckStop.objects.annotate(distance=Distance('city__location', stop_point))
        .order_by('distance', 'fuel_retail_price')
        .first()
    )

    return nearest_truck_stop