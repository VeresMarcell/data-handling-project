from __future__ import annotations

from dataclasses import field, dataclass
import random
from typing import Type, cast
import faker
from faker import Faker
from data.project.base import Dataset, Entity


# TODO replace this module with your own types

@dataclass
class CompanyDataset(Dataset):
    people: list[Person]
    jobs: list[Job]
    companies: list[Company]


    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Person, Job, Company]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return CompanyDataset(
            cast(list[Person], entities[0]),
            cast(list[Job], entities[1]),
            cast(list[Company], entities[2]),
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Person] = self.people
        res[Job] = self.jobs
        res[Company] = self.companies


        return res

    @staticmethod
    def generate(
            count_of_employees: int,
            count_of_jobs: int,
            count_of_companies: int):

        def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                            unique: bool = False, min_age: int = 18, max_age: int = 60) -> list[Person]:
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

        def generate_jobs(n: int, min_salary: int = 2000, max_salary: int = 4500) -> list[Job]:
            assert n > 0
            assert 2000 <= min_salary
            assert min_salary <= max_salary <= 4500

            pay_grades = [1, 2, 3, 4]

            fake_type = Faker()
            fake_type.add_provider(faker.providers.job)

            jobs = []
            for i in range(n):
                salary = random.randint(min_salary, max_salary)
                ind = random.randint(pay_grades[0], pay_grades[3])
                job = Job(
                    fake_type.job(),
                    salary,
                    pay_grades[ind - 1])
                if job.pay_grade == 2:
                    job.salary = int(salary * 1.2)
                elif job.pay_grade == 3:
                    job.salary = int(salary * 1.2 * 1.4)
                elif job.pay_grade == 4:
                    job.salary = int(salary * 1.2 * 1.4 * 1.6)
                jobs.append(job)

            return jobs

        def generate_companies(n: int, attempts: int = None) -> list[Company]:
            assert n > 0
            assert attempts is None or attempts >= n

            codes = {"cs_CZ":"Czech Republic", "da_DK":"Denmark", "de_AT":"Austria", "de_CH":"Switzerland","de_DE":"Germany",
                     "el_GR":"Greece","en_AU":"Australia",
                     "en_CA":"Canada", "en_GB":"United Kingdom", "en_IE":"Ireland", "en_IN":"India","en_NZ":"New Zealand",
                     "en_PH":"Philippines", "en_US":"United States", "es_CO":"Colombia", "es_ES":"Spain",
                     "es_MX":"Mexico","fa_IR":"IR", "fi_FI":"Finland", "fil_PH":"Philippines", "fr_CH":"Switzerland",
                     "fr_FR":"France", "he_IL":"Israel", "hi_IN":"India", "hr_HR":"Croatia",
                     "hu_HU":"Hungary","hy_AM":"Armenia", "id_ID":"Indonesia","it_IT":"Italy","ja_JP":"Japan",
                     "ka_GE":"Georgia", "ko_KR":"Republic of Korea","ne_NP":"Nepal", "nl_BE":"Belgium", "nl_NL":"Netherlands",
                     "no_NO":"Norway", "pl_PL":"Poland", "pt_BR":"Brazil", "pt_PT":"Portugal", "ro_RO":"Romania",
                     "ru_RU":"Russia", "sk_SK":"Slovakia","sl_SI":"Slovenia", "sv_SE":"Sweden",
                     "ta_IN":"India", "th_TH":"Thailand", "tl_PH":"Philippines", "uk_UA":"Ukraine", "zh_CN":"Switzerland"
                    , "zh_TW":"Taiwan"}

            loc_list = list(codes.keys())

            fake = Faker()
            fake.add_provider(faker.providers.company)
            fake.add_provider(faker.providers.address)

            companies = []
            for i in range(n if attempts is None else attempts):
                locale = loc_list[random.randint(0,49)]
                fake = Faker(locale)
                company = Company(
                    fake.company(),
                    str(fake.address()),
                    fake.catch_phrase(),
                    codes[locale]
                )

                companies.append(company)

            return companies

        people = generate_people(count_of_employees)
        jobs = generate_jobs(count_of_jobs)
        companies = generate_companies(count_of_companies)
        for i in range(len(people)):
            person = people[i]
            person.job_name = jobs[random.randint(0,len(jobs)-1)].name
            person.company_name = companies[random.randint(0,len(companies)-1)].name

        return CompanyDataset(people, jobs, companies)

    @staticmethod
    def field_names() -> list[str]:
        return ["employee", "job", "company"]


@dataclass
class Company(Entity):
    name: str = field(hash=True)
    address: str = field(repr=True, compare =False)
    motto : str = field(repr=True, compare=False)
    country : str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Company:
        return Company(seq[0], seq[1], seq[2], seq[3])

    def to_sequence(self) -> list[str]:
        return [self.name, self.address, self.motto, self.country]

    @staticmethod
    def field_names() -> list[str]:
        return ["name", "address", "motto", "country"]

    @staticmethod
    def collection_name() -> str:
        return "companies"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Company.collection_name()} (
            name VARCHAR(150) NOT NULL PRIMARY KEY,
            address VARCHAR(150),
            motto  VARCHAR(250),
            country VARCHAR(100)
        );
        """


@dataclass
class Job(Entity):
    name: str = field(hash=True)
    salary: int = field(repr=True, compare=False)
    pay_grade: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Job:
        return Job(seq[0], int(seq[1]), int(seq[2]))

    def to_sequence(self) -> list[str]:
        return [self.name, str(self.salary), str(self.pay_grade)]

    @staticmethod
    def field_names() -> list[str]:
        return ["name", "salary", "pay_grade"]

    @staticmethod
    def collection_name() -> str:
        return "jobs"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Job.collection_name()} (
            name VARCHAR(150) NOT NULL PRIMARY KEY,
            salary SMALLINT,
            pay_grade SMALLINT
        );
        """


@dataclass
class Person(Entity):
    id: str = field(hash=True)
    name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)
    male: bool = field(default=True, repr=True, compare=False)
    job_name: str = field(default="unemployed",repr=True, compare=False)
    company_name:  str = field(default="unemployed",repr=True, compare=False)


    @staticmethod
    def from_sequence(seq: list[str]) -> Person:
        return Person(seq[0], seq[1], int(seq[2]),bool(seq[3]),seq[4], seq[5])

    def to_sequence(self) -> list[str]:
        return [self.id, self.name, str(self.age), str(int(self.male)), self.job_name,self.company_name]

    @staticmethod
    def field_names() -> list[str]:
        return ["id", "name", "age",  "male", "job_name", "company_name"]

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
            male BOOLEAN,
            job_name VARCHAR(100),
            company_name VARCHAR(100),
            
            FOREIGN KEY (job_name) REFERENCES {Job.collection_name()}(name),
            FOREIGN KEY (company_name) REFERENCES {Company.collection_name()}(name)
        );
        """
