# Generated by Django 3.2.23 on 2024-12-05 10:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('routing', '0003_route_feature_collection'),
    ]

    operations = [
        migrations.AlterField(
            model_name='route',
            name='feature_collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='routing.featurecollection'),
        ),
    ]
