from django.urls import path, include
from rest_framework.routers import DefaultRouter

from routing import views

router = DefaultRouter()
router.register(r'routes', views.RouteViewSet,
                basename='routes')
router.register(r'feature-collections', views.FeatureCollectionViewSet,
                basename='feature-collections')
router.register(r'truck-stops', views.TruckStopViewSet,
                basename='truck-stops')

urlpatterns = [
    path('', include(router.urls)),
]
