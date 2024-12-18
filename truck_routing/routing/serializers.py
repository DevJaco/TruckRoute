from django.contrib.gis.geos import Polygon, Point, LineString

from rest_framework import serializers
from .models import Route, FeatureCollection, BoundingBox, Feature, FeatureSummary, Metadata, Segment, Step, WayPoint, TruckStop

import os
import requests


class BoundingBoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoundingBox
        fields = '__all__'


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = '__all__'


class FeatureSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureSummary
        fields = '__all__'


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metadata
        fields = '__all__'


class SegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segment
        fields = '__all__'


class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'


class WayPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WayPoint
        fields = '__all__'


class FeatureCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureCollection
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'
        read_only_fields = ['feature_collection']

    def create(self, validated_data):
        api_key = os.environ.get('OPENROUTE_API_KEY')
        route_response = requests.get(f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={api_key}&start={validated_data['start_location']}&end={validated_data['end_location']}")

        geojson = route_response.json()

        print(validated_data['start_location'])

        bbox = geojson['bbox']
        metadata = geojson['metadata']
        summary = geojson['features'][0]['properties']['summary']

        segments = geojson['features'][0]['properties']['segments']

        routing_waypoints = geojson['features'][0]['properties']['way_points']
        waypoints = geojson['features'][0]['geometry']['coordinates']

        bbox_poly = Polygon.from_bbox(bbox)
        bounding_box = BoundingBox(coordinates=bbox_poly)
        bounding_box.save()

        metadata_obj = Metadata(**metadata)
        metadata_obj.save()

        feature_collection = FeatureCollection(
            bbox=bounding_box, metadata=metadata_obj)
        feature_collection.save()

        feature_summary = FeatureSummary(**summary)
        feature_summary.save()

        points = [WayPoint(coordinate=Point(lng, lat))
                  for lng, lat in waypoints]
        WayPoint.objects.bulk_create(points)

        # Create a LineString instance and associate it with the points
        line_points = [
            selected_waypoint.coordinate for selected_waypoint in points]
        geometry = LineString(line_points)

        feature_waypoint_markers = [points[x] for x in routing_waypoints]

        feature = Feature(feature_collection=feature_collection,
                          summary=feature_summary, geometry=geometry, bbox=bounding_box)
        feature.save()
        feature.way_points.set(feature_waypoint_markers)
    
        for segment in segments:
            steps = segment['steps']

            segment_obj = Segment(distance=segment['distance'], duration=segment['duration'], feature=feature)
            segment_obj.save()

            for step in steps:
                step_obj = Step(distance=step['distance'], duration=step['duration'], type=step['type'], instruction=step['instruction'], name=step['name'], segment=segment_obj)
                step_obj.save()
                step_obj.way_points.set([points[x] for x in step['way_points']])

        start_lon, start_lat = validated_data['start_location'].split(',')
        end_lon, end_lat = validated_data['end_location'].split(',')

        start_point = Point(float(start_lon), float(start_lat))
        end_point = Point(float(end_lon), float(end_lat))

        route = Route(start_location=start_point, end_location=end_point,
        feature_collection = feature_collection)
        return route


class TruckStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = TruckStop
        fields = '__all__'
