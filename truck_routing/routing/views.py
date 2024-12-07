from rest_framework import viewsets
from django.core.serializers import serialize

from .models import Route, FeatureCollection, TruckStop
from .serializers import RouteSerializer, FeatureCollectionSerializer, TruckStopSerializer

from rest_framework.response import Response
import json

class FeatureCollectionViewSet(viewsets.ModelViewSet):
    queryset = FeatureCollection.objects.all()
    serializer_class = FeatureCollectionSerializer

    def retrieve(self, request, *args, **kwargs):
        collection = self.get_object()
        features = collection.feature_set.prefetch_related('segment_set').all()

        # This can be converted using drf-gis
        geojson_features = serialize(
            'geojson', features,
            geometry_field='geometry',
            fields=('segment_set', 'summary', 'way_points')
        )
        geojson_data = json.loads(geojson_features)

        return Response(geojson_data)

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

class TruckStopViewSet(viewsets.ModelViewSet):
    queryset = TruckStop.objects.all()
    serializer_class = TruckStopSerializer

    
