# Generated by Django 3.2.23 on 2024-12-05 10:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0002_rename_geojsonfeaturecollection_featurecollection'),
    ]

    operations = [
        migrations.AddField(
            model_name='route',
            name='feature_collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='routing.featurecollection'),
        ),
    ]
