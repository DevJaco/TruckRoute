from django.shortcuts import render
from rest_framework import viewsets
from django.core.serializers import serialize

from .models import Route, FeatureCollection
from .serializers import RouteSerializer, FeatureCollectionSerializer

from rest_framework.response import Response
import json

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    


class FeatureCollectionViewSet(viewsets.ModelViewSet):
    queryset = FeatureCollection.objects.all()
    serializer_class = FeatureCollectionSerializer

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        features = collection.feature_set.prefetch_related('segment_set').all()
        
        for feature in features:
            segments = feature.segment_set.prefetch_related('step_set').all()

            for segment in segments:
                print(segment.step_set.all())

        geojson_features = serialize(
            'geojson', features,
            geometry_field='geometry',
            fields=('segment_set', 'summary', 'way_points')
        )
        geojson_data = json.loads(geojson_features)

        return Response(geojson_data)
