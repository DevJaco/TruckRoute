from django.contrib.gis.db import models


# Storing bounding box to be used by multiple models
class BoundingBox(models.Model):
    coordinates = models.PolygonField()

    def __str__(self) -> str:
        # Should be no more and no less than 4 coordinates since its a bounding box
        return f'[{self.coordinates}]'

# Storing waypoint so we can access on other models


class WayPoint(models.Model):
    coordinate = models.PointField()

    def __str__(self) -> str:
        return f'({self.coordinate.x, self.coordinate.y})'


class Metadata(models.Model):
    attribution = models.CharField(max_length=255)
    service = models.CharField(max_length=255)
    timestamp = models.BigIntegerField()
    query = models.JSONField()
    engine = models.JSONField()


class FeatureCollection(models.Model):
    bbox = models.ForeignKey(BoundingBox, on_delete=models.CASCADE)
    metadata = models.OneToOneField(Metadata, on_delete=models.CASCADE)


class FeatureSummary(models.Model):
    distance = models.FloatField()
    duration = models.FloatField()


class Feature(models.Model):
    feature_collection = models.ForeignKey(
        FeatureCollection, on_delete=models.CASCADE)
    summary = models.OneToOneField(FeatureSummary, on_delete=models.CASCADE)
    geometry = models.LineStringField()  # Stores the LineString of the route
    way_points = models.ManyToManyField(WayPoint)
    bbox = models.ForeignKey(BoundingBox, on_delete=models.CASCADE)


class Segment(models.Model):
    distance = models.FloatField()
    duration = models.FloatField()
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)


class Step(models.Model):

    INSTRUCTION_TYPE_CHOICES = (
        (0,	"Left"),
        (1,	"Right"),
        (2,	"Sharp left"),
        (3,	"Sharp right"),
        (4,	"Slight left"),
        (5,	"Slight right"),
        (6,	"Straight"),
        (7,	"Enter roundabout"),
        (8,	"Exit roundabout"),
        (9,	"U-turn"),
        (10, "Goal"),
        (11, "Depart"),
        (12, "Keep left"),
        (13, "Keep right")
    )

    distance = models.FloatField()
    duration = models.FloatField()
    instruction = models.CharField(max_length=255)
    type = models.SmallIntegerField(choices=INSTRUCTION_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    way_points = models.ManyToManyField(WayPoint)
    segment = models.ForeignKey(Segment, on_delete=models.CASCADE)


class Route(models.Model):
    # Using point fields to ensure accuracy of output and ensuring all
    # start and end locations are accessible unlike using addresses.
    start_location = models.PointField()
    end_location = models.PointField()
    feature_collection = models.ForeignKey(
        FeatureCollection, on_delete=models.CASCADE)

STATE_CHOICES = (
    (1, 'AL'), (2, 'AK'), (3, 'AZ'), (4, 'AR'), (5, 'CA'),
    (6, 'CO'), (7, 'CT'), (8, 'DE'), (9, 'FL'), (10, 'GA'),
    (11, 'HI'), (12, 'ID'), (13, 'IL'), (14, 'IN'), (15, 'IA'),
    (16, 'KS'), (17, 'KY'), (18, 'LA'), (19, 'ME'), (20, 'MD'),
    (21, 'MA'), (22, 'MI'), (23, 'MN'), (24, 'MS'), (25, 'MO'),
    (26, 'MT'), (27, 'NE'), (28, 'NV'), (29, 'NH'), (30, 'NJ'),
    (31, 'NM'), (32, 'NY'), (33, 'NC'), (34, 'ND'), (35, 'OH'),
    (36, 'OK'), (37, 'OR'), (38, 'PA'), (39, 'RI'), (40, 'SC'),
    (41, 'SD'), (42, 'TN'), (43, 'TX'), (44, 'UT'), (45, 'VT'),
    (46, 'VA'), (47, 'WA'), (48, 'WV'), (49, 'WI'), (50, 'WY'),
    
    (51, 'AB'), (52, 'BC'), (53, 'MB'), (54, 'NB'), (55, 'NL'),
    (56, 'NS'), (57, 'ON'), (58, 'PE'), (59, 'QC'), (60, 'SK'), (61, 'YT')
)

class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.IntegerField(choices=STATE_CHOICES)

    location = models.PointField(null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.name}, {self.state}'

class TruckStop(models.Model):

    
    opis_id = models.IntegerField()
    name = models.CharField(max_length=1023)
    address = models.CharField(max_length=1023)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    state = models.SmallIntegerField(choices=STATE_CHOICES)
    #  use an integer field here as we will price in cents for accuracy.
    fuel_retail_price = models.IntegerField(help_text="Truck Stop fuel price in cents. (USD)")
    coordinate = models.PointField(blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.name}, {self.address}, {self.city}, {self.state}'
    