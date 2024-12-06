
import pandas as pd
from django.core.management.base import BaseCommand
from routing.models import TruckStop, City, STATE_CHOICES


class Command(BaseCommand):
    help = "Imports Truck Stops from a CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str,
                            help='The path to the CSV file.')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        STATE_MAPPING = {abbr: num for num, abbr in STATE_CHOICES}
        
        # Load the CSV file
        try:
            self.stdout.write(f"Reading data from {file_path}...")
            df = pd.read_csv(file_path)

            # Check if the required columns exist
            if not {'OPIS Truckstop ID', 'Truckstop Name', 'Address', 'City', 'State', 'Retail Price'}.issubset(df.columns):
                self.stderr.write("The CSV file is missing required columns.")
                return

            # Iterate through the DataFrame and create/update City objects
            truck_stops_to_create = []
            for _, row in df.iterrows():
                state_int = STATE_MAPPING.get(row['State'].strip())

                if state_int is None:
                    self.stderr.write(
                        f"Invalid state abbreviation: {row['State'].strip()}")
                    continue
                
                
                try:
                    city = City.objects.get(name=row['City'].strip(), state=state_int)
                except:
                    self.stderr.write(
                        f"Could not find city ({row['City'].strip()}, {row['State'].strip()})")
                    continue

                truck_stops_to_create.append(
                    TruckStop(
                        opis_id=row['OPIS Truckstop ID'],
                        name=row['Truckstop Name'].strip(),
                        address=row['Address'].strip(),
                        city=city,
                        state=state_int,
                        fuel_retail_price=row['Retail Price']
                    )
                )

            # Bulk create the cities
            TruckStop.objects.bulk_create(
                truck_stops_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f"Successfully imported {len(truck_stops_to_create)} truck stops."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))
