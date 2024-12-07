from django.contrib import admin

from .models import Route, BoundingBox, Feature, FeatureCollection, Metadata, Segment, Step, WayPoint, FeatureSummary, City, TruckStop

class FeatureInline(admin.StackedInline):
    model = Feature
    extra = 1

class FeatureCollectionAdmin(admin.ModelAdmin):
    inlines = [FeatureInline]

class StepAdmin(admin.ModelAdmin):
    filter_horizontal = ['way_points']

class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state_label_display']
    list_filter = ['state']

    def state_label_display(self, obj):
        return obj.get_state_display()

admin.site.register(Route)
admin.site.register(BoundingBox)
admin.site.register(Feature)
admin.site.register(FeatureCollection, FeatureCollectionAdmin)
admin.site.register(Metadata)
admin.site.register(Segment)
admin.site.register(Step, StepAdmin)
admin.site.register(WayPoint)
admin.site.register(FeatureSummary)
admin.site.register(City, CityAdmin)
admin.site.register(TruckStop)