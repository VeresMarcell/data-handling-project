from __future__ import annotations

from dataclasses import field, dataclass
import random
from typing import Type, cast

from faker import Faker
from faker_airtravel import AirTravelProvider
from faker_vehicle import VehicleProvider
from data.project.base import Dataset, Entity


# TODO replace this module with your own types

@dataclass
class RentalDataset(Dataset):
    people: list[Person]
    cars: list[Car]
    airports: list[Airport]
    transactions: list[Transaction]

    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Person, Car, Airport, Transaction]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return RentalDataset(
            cast(list[Person], entities[0]),
            cast(list[Car], entities[1]),
            cast(list[Airport], entities[2]),
            cast(list[Transaction], entities[3])
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Person] = self.people
        res[Car] = self.cars
        res[Airport] = self.airports
        res[Transaction] = self.transactions

        return res

    @staticmethod
    def generate(
            count_of_customers: int,
            count_of_cars: int,
            count_of_airports: int,
            count_of_transactions: int):

        def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                            unique: bool = False, min_age: int = 0, max_age: int = 100) -> list[Person]:
            assert n > 0
            assert 0 <= male_ratio <= 1
            assert 0 <= min_age <= max_age

            fake = Faker(locale)
            people = []
            for i in range(n):
                male = random.random() < male_ratio
                generator = fake if not unique else fake.unique
                people.append(Person(
                    "P-" + (str(i).zfill(6)),
                    generator.name_male() if male else generator.name_female(),
                    random.randint(min_age, max_age),
                    male))

            return people

        def generate_cars(n: int, automatic_ratio: float = 0.2, locale: str = "hu_HU", unique: bool = False,
                          min_year: int = 1950, max_year: int = 2021) -> list[Car]:
            assert n > 0
            assert 0 < automatic_ratio < 1
            assert 1950 <= min_year
            assert min_year <= max_year <= 2021

            fake_plate = Faker(locale)
            fake_plate.add_provider(VehicleProvider)
            if unique:
                fake_plate = fake_plate.unique
            fake_type = Faker()
            fake_type.add_provider(VehicleProvider)

            cars = []
            for i in range(n):
                automatic = random.random() < automatic_ratio
                cars.append(Car(
                    fake_plate.license_plate(),
                    fake_type.vehicle_make(),
                    random.randint(min_year, max_year),
                    automatic))

            return cars

        def generate_airports(n: int, country: str = None, city: str = None,
                              unique: bool = False, attempts: int = None) -> list[Airport]:
            assert n > 0
            assert attempts is None or attempts >= n

            fake = Faker()
            fake.add_provider(AirTravelProvider)

            airports = []
            for i in range(n if attempts is None else attempts):
                values = fake.airport_object()

                actual = Airport(
                    values["icao"],
                    values["airport"],
                    values["city"],
                    values["state"],
                    values["country"])

                if len(actual.code) == 0:
                    continue
                if country is not None and country != actual.country:
                    continue
                if city is not None and city != actual.city:
                    continue
                if unique and actual in airports:
                    continue

                airports.append(actual)

            return airports

        def generate_transactions(n: int, people: list[Person], cars: list[Car], airports: list[Airport]) -> list[
            Transaction]:
            assert n > 0
            assert len(people) > 0
            assert len(cars) > 0
            assert len(airports) > 0

            trips = []
            for i in range(n):
                person = random.choice(people)
                car = random.choice(cars)
                airport = random.choice(airports)
                trips.append(
                    Transaction(f"T-{str(i).zfill(6)}", airport.code, person.id, car.plate, random.randint(100, 1000)))

            return trips

        people = generate_people(count_of_customers)
        cars = generate_cars(count_of_cars)
        airports = generate_airports(count_of_airports, unique=True)
        transactions = generate_transactions(count_of_transactions, people, cars, airports)
        return RentalDataset(people, cars, airports, transactions)


@dataclass
class Transaction(Entity):
    id: str = field(hash=True)
    airport: str = field(repr=True, compare=False)
    person: str = field(repr=True, compare=False)
    car: str = field(repr=True, compare=False)
    length: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Transaction:
        return Transaction(seq[0], seq[1], seq[2], seq[3], int(seq[4]))

    def to_sequence(self) -> list[str]:
        return [self.id, self.airport, self.person, self.car, str(self.length)]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "airport", "person", "car", "length"]

    @staticmethod
    def collection_name() -> str:
        return "transactions"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Transaction.collection_name()} (
            id VARCHAR(8) NOT NULL PRIMARY KEY,
            airport CHAR(4) NOT NULL,
            person VARCHAR(8) NOT NULL,
            car VARCHAR(20) NOT NULL,
            length SMALLINT,
            
            FOREIGN KEY (airport) REFERENCES {Airport.collection_name()}(code),
            FOREIGN KEY (person) REFERENCES {Person.collection_name()}(id),
            FOREIGN KEY (car) REFERENCES {Car.collection_name()}(plate)
        );
         """


@dataclass
class Airport(Entity):
    code: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    city: str = field(repr=True, compare=False)
    state: str = field(repr=True, compare=False)
    country: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Airport:
        return Airport(seq[0], seq[1], seq[2], seq[3], seq[4])

    def to_sequence(self) -> list[str]:
        return [self.code, self.name, self.city, self.state, self.country]

    @staticmethod
    def field_names() -> list[str]:
        return ["code", "name", "city", "state", "country"]

    @staticmethod
    def collection_name() -> str:
        return "airports"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Airport.collection_name()} (
            code CHAR(4) NOT NULL PRIMARY KEY,
            name VARCHAR(100),
            city VARCHAR(50),
            state VARCHAR(50),
            country VARCHAR(50)
        );
        """


@dataclass
class Car(Entity):
    plate: str = field(hash=True)
    type: str = field(repr=True, compare=False)
    year: int = field(repr=True, compare=False)
    automatic: bool = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Car:
        return Car(seq[0], seq[1], int(seq[2]), bool(seq[3]))

    def to_sequence(self) -> list[str]:
        return [self.plate, self.type, str(self.year), str(int(self.automatic))]

    @staticmethod
    def field_names() -> list[str]:
        return ["plate", "type", "year", "automatic"]

    @staticmethod
    def collection_name() -> str:
        return "cars"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Car.collection_name()} (
            plate VARCHAR(20) NOT NULL PRIMARY KEY,
            type VARCHAR(20),
            year SMALLINT,
            automatic BOOLEAN
        );
        """


@dataclass
class Person(Entity):
    id: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)
    male: bool = field(default=True, repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Person:
        return Person(seq[0], seq[1], int(seq[2]), bool(seq[3]))

    def to_sequence(self) -> list[str]:
        return [self.id, self.name, str(self.age), str(int(self.male))]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "name", "age", "male"]

    @staticmethod
    def collection_name() -> str:
        return "people"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Person.collection_name()} (
            id VARCHAR(8) NOT NULL PRIMARY KEY,
            name VARCHAR(50),
            age TINYINT,
            male BOOLEAN
        );
        """
