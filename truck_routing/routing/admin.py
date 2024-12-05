from django.contrib import admin

from .models import Route, BoundingBox, Feature, FeatureCollection, Metadata, Segment, Step, WayPoint, FeatureSummary

class FeatureInline(admin.StackedInline):
    model = Feature
    extra = 1

class FeatureCollectionAdmin(admin.ModelAdmin):
    inlines = [FeatureInline]

admin.site.register(Route)
admin.site.register(BoundingBox)
admin.site.register(Feature)
admin.site.register(FeatureCollection, FeatureCollectionAdmin)
admin.site.register(Metadata)
admin.site.register(Segment)
admin.site.register(Step)
admin.site.register(WayPoint)
admin.site.register(FeatureSummary)
