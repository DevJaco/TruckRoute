from django.urls import path, include
from rest_framework.routers import DefaultRouter

from routing import views

router = DefaultRouter()
router.register(r'routes', views.RouteViewSet,
                basename='routes')
router.register(r'feature-collections', views.FeatureCollectionViewSet,
                basename='feature-collections')

urlpatterns = [
    path('', include(router.urls)),
]
