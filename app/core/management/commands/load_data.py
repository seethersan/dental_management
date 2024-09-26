import json
from django.core.management.base import BaseCommand
from core.models import Country, State, City


class Command(BaseCommand):
    help = "Load countries, states, and cities data from JSON file"

    def handle(self, *args, **kwargs):
        with open("static/geo_data.json", "r") as file:
            data = json.load(file)

        for country_data in data:
            country, created = Country.objects.get_or_create(name=country_data["name"])
            print(
                f"Country {country.name} {'created' if created else 'already exists'}"
            )

            for state_data in country_data["states"]:
                state, created = State.objects.get_or_create(
                    country=country, name=state_data["name"]
                )
                print(
                    f"  State {state.name} {'created' if created else 'already exists'}"
                )

                for city_data in state_data["cities"]:
                    city, created = City.objects.get_or_create(
                        state=state, name=city_data["name"]
                    )
                    print(
                        f"    City {city.name} {'created' if created else 'already exists'}"
                    )
