
import pandas as pd
from django.core.management.base import BaseCommand
from routing.models import City,  STATE_CHOICES

from django.contrib.gis.geos import Point

# NB Note: The reason we need to import the CA cities is because AL is in USA however the truck will need to travel through CA.

class Command(BaseCommand):
    help = "Imports US & CA cities from a CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument('us_file_path', type=str, help='The path to the USA CSV file.')
        parser.add_argument('ca_file_path', type=str, help='The path to the CA CSV file.')

    def handle(self, *args, **kwargs):
        us_file_path = kwargs['us_file_path']
        ca_file_path = kwargs['ca_file_path']
        STATE_MAPPING = {abbr: num for num, abbr in STATE_CHOICES}

        # Load the CSV file
        try:
            self.stdout.write(f"Reading data from {us_file_path}...")
            self.stdout.write(f"Reading data from {ca_file_path}...")
            df_us = pd.read_csv(us_file_path)
            df_ca = pd.read_csv(ca_file_path)

            df = pd.concat([df_us, df_ca], ignore_index=True)
            
            # Check if the required columns exist
            if not {'city', 'state_id',  'lat', 'lng'}.issubset(df.columns):
                self.stderr.write("The CSV file is missing required columns.")
                return

            cities_to_create = []
            existing_cities = set(
                City.objects.values_list('name', 'state')
            )  

            for _, row in df.iterrows():

                point = Point(row['lng'], row['lat'])

                city_name = row['city']
                state_int = STATE_MAPPING.get(row['state_id'])


                if state_int is None:
                    self.stderr.write(
                        f"Invalid state abbreviation: {row['state_id']}")
                    continue

                if (city_name, state_int) in existing_cities:
                        self.stdout.write(f"City '{city_name}, {state_int}' already exists. Skipping.")
                        continue


                cities_to_create.append(
                    City(
                        name=row['city'],
                        state=state_int,
                        location=point
                    )
                )

            # Bulk create the cities
            City.objects.bulk_create(cities_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Successfully imported {len(cities_to_create)} cities."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))
