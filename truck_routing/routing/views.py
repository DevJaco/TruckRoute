from django.shortcuts import render
from rest_framework import viewsets
from django.core.serializers import serialize

from .models import Route, FeatureCollection
from .serializers import RouteSerializer, FeatureCollectionSerializer

from rest_framework.response import Response
import json

from rest_framework.decorators import action
import math
from django.contrib.gis.geos import Point, LineString


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    

import math

# https://www.movable-type.co.uk/scripts/latlong.html

def interpolate_geo_point(start_point, end_point, fraction):
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


def calculate_fuel_stops(route_segments):

    MAX_RANGE = 500  # Maximum range in miles
    FUEL_EFFICIENCY = 10  # Miles per gallon
    REFUEL_BUFFER = 50 # Miles to look for station before empty
    FUEL_PRICE_PER_GALLON = 3.5  # Fuel price in USD per gallon

    stops = []  # Distances where refueling is needed
    total_fuel_cost = 0  # Total fuel cost
    remaining_range = MAX_RANGE  # Remaining range at the start of the trip
    cumulative_distance = 0  # Total distance traveled so far


    # (step.distance / 1000) * 0.62137119
    for segment in route_segments:
        
        segment_distance = ((segment.distance / 1000) * 0.62137119)
        current_segment_distance = segment_distance
        cumulative_distance += segment_distance
        

        # Process this segment
        while segment_distance > remaining_range:
            # Stop when range is depleted
            # This will always be a multiple of 500 minus the refuel buffer.
            # stops.append(math.ceil(refill_distance))

            total_fuel_cost += (remaining_range / FUEL_EFFICIENCY) * FUEL_PRICE_PER_GALLON

            segment_distance -= remaining_range

            # Finding the percetage along the segment we need to refuel at.
            percentage_segment = (current_segment_distance - segment_distance - REFUEL_BUFFER) / current_segment_distance
            
            if segment.type != 10:
                interpolated_point = interpolate_geo_point(segment.way_points.first().coordinate, segment.way_points.last().coordinate, percentage_segment)
                stops.append(interpolated_point)

            remaining_range = MAX_RANGE  # Reset range after refueling

        # After processing the segment, update remaining range
        remaining_range -= segment_distance

    # Final fuel cost for any leftover range
    if remaining_range < MAX_RANGE:
        total_fuel_cost += ((MAX_RANGE - remaining_range) / FUEL_EFFICIENCY) * FUEL_PRICE_PER_GALLON

    return stops, total_fuel_cost



def snap_to_linestring_geodjango(intermediate_point, linestring):
    """
    Snap a point to the nearest point on a LineString using GeoDjango.

    Parameters:
        intermediate_point (Point): the point to snap.
        linestring_coords (LineString): the LineString.

    Returns:
        snapped_point (Point): the snapped point.
    """
    # Convert the intermediate point and LineString coordinates to GeoDjango objects

    # Find the nearest point on the LineString to the given point
    snapped_point = linestring.interpolate(
        linestring.project(intermediate_point)
    )

    # Return the snapped point as (latitude, longitude)
    return snapped_point.y, snapped_point.x  # Convert back to lat, lon order

# Example usage

class FeatureCollectionViewSet(viewsets.ModelViewSet):
    queryset = FeatureCollection.objects.all()
    serializer_class = FeatureCollectionSerializer

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        features = collection.feature_set.prefetch_related('segment_set').all()
        
        for feature in features:
            segments = feature.segment_set.prefetch_related('step_set').all()

            for segment in segments:
                steps = [step for step in segment.step_set.all()]
                fuel_stops, total_cost = calculate_fuel_stops(steps)

                for stop in fuel_stops:
                    print(snap_to_linestring_geodjango(stop, feature.geometry))

                print(f"Fuel stops required at distances: {fuel_stops}")
                print(f"Total fuel cost: ${total_cost:.2f}")



        geojson_features = serialize(
            'geojson', features,
            geometry_field='geometry',
            fields=('segment_set', 'summary', 'way_points')
        )
        geojson_data = json.loads(geojson_features)

        return Response(geojson_data)

