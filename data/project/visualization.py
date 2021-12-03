import math

from data.project.model import CompanyDataset
import numpy as np
import matplotlib.pyplot as plt


def avg_age_by_company(dataset: CompanyDataset) -> None:
    companies_num = {}
    emp_age = {}
    avg_age = []
    for person in dataset.people:
        if person.company_name not in companies_num:
            companies_num[person.company_name] = 1
        elif person.company_name in companies_num:
            companies_num[person.company_name] += 1
    for company in companies_num:
        if company not in emp_age.keys():
            emp_age[company] = 0
    for person in dataset.people:
        emp_age[person.company_name] += person.age
    for c in companies_num.keys():
        avg_age.append(int(emp_age[c] / companies_num[c]))


    x = np.arange(len(companies_num.keys()))  # the label locations
    width = 0.15  # the width of the bars

    fig, ax = plt.subplots()
    series_total = ax.bar(x, avg_age, width, label="Average age")
    ax.set_ylabel("Average age")
    ax.set_title("Average age by company")
    ax.set_xticks(x)
    ax.set_xticklabels(companies_num.keys(), rotation=45)
    ax.legend()

    ax.bar_label(series_total)
    fig.tight_layout()

    plt.show()


def employees_by_companies(dataset: CompanyDataset) -> None:
    companies = list(set({person.company_name for person in dataset.people}))
    values = [0 for _ in companies]
    for person in dataset.people:
        values[companies.index(person.company_name)] += 1

    x = np.arange(len(companies))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    series = ax.bar(x , values, width)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Number of employees")
    ax.set_title("Number of employees per company")
    ax.set_xticks(x)
    ax.set_xticklabels(companies, rotation=45)
    ax.bar_label(series)

    ax.tick_params(axis="both", which="major", labelsize=10)

    fig.tight_layout()

    plt.show()


def distribution_of_paygrades(dataset: CompanyDataset) -> None:
    paygrade = list(set({job.pay_grade for job in dataset.jobs}))
    values = [0 for _ in paygrade]
    percentages = []
    for job in dataset.jobs:
        values[paygrade.index(job.pay_grade)] += 1
    for i in range(len(values)):
        percentages.append((values[i]/sum(values))*100)



    fig1, ax = plt.subplots()
    ax.pie(percentages, labels=paygrade, autopct="%1.1f%%", startangle=90, rotatelabels=True, pctdistance=0.7)
    ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    ax.tick_params(axis="both", which="major", labelsize=8)
    plt.title("Distribution of pay grades between all employees")

    plt.show()


def distances_by_types_with_limit(dataset: CompanyDataset) -> None:
    types = list({car.type for car in dataset.cars})
    values = [0 for _ in types]
    for transaction in dataset.transactions:
        car = next(car for car in dataset.cars if car.plate == transaction.car)
        values[types.index(car.type)] += transaction.length

    limit = 0.05

    total_length = sum([transaction.length for transaction in dataset.transactions])
    filtered_labels = [types[i] for i in range(len(types)) if values[i] >= total_length * limit]
    filtered_values = [values[i] for i in range(len(types)) if values[i] >= total_length * limit]
    other_length = 0
    for transaction in dataset.transactions:
        car = next(car for car in dataset.cars if car.plate == transaction.car)
        if car.type not in filtered_labels:
            other_length += transaction.length

    filtered_labels.append("other")
    filtered_values.append(other_length)

    explode = [0.2 if label == "other" else 0 for label in filtered_labels]

    fig1, ax1 = plt.subplots()
    ax1.pie(filtered_values, labels=filtered_labels, explode=explode, autopct="%1.1f%%", startangle=90,
            rotatelabels=True, pctdistance=0.7)
    ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.

    ax1.tick_params(axis="both", which="major", labelsize=10)

    plt.show()


def genders_by_ages_heatmap(dataset: CompanyDataset) -> None:
    genders = ["males", "females"]
    ages = [f"{i * 10}-{(i + 1) * 10 - 1}" for i in range(11)]
    values = np.zeros((len(genders), len(ages)))
    for person in dataset.people:
        values[0 if person.male else 1, person.age // 10] += 1

    fig, ax = plt.subplots()
    im = ax.imshow(values)

    # We want to show all ticks...
    ax.set_xticks(np.arange(len(ages)))
    ax.set_yticks(np.arange(len(genders)))
    # ... and label them with the respective list entries
    ax.set_xticklabels(ages)
    ax.set_yticklabels(genders)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(genders)):
        for j in range(len(ages)):
            text = ax.text(j, i, int(values[i, j]), ha="center", va="center", color="w")

    ax.set_title("Heatmap of genders and ages")
    fig.tight_layout()
    plt.show()


def distances_by_countries_and_sexes(dataset: CompanyDataset) -> None:
    countries = list({airport.country for airport in dataset.airports})
    values_male = [0 for _ in countries]
    values_female = [0 for _ in countries]

    for transaction in dataset.transactions:
        airport = next(airport for airport in dataset.airports if airport.code == transaction.airport)
        person = next(person for person in dataset.people if person.id == transaction.person)
        country_index = countries.index(airport.country)
        if person.male:
            values_male[country_index] += transaction.length
        else:
            values_female[country_index] += transaction.length

    non_zero_indices = {i for i in range(len(countries)) if values_male[i] + values_female[i] > 0}
    countries = [countries[i] for i in non_zero_indices]
    values_male = [values_male[i] for i in non_zero_indices]
    values_female = [values_female[i] for i in non_zero_indices]

    x = np.arange(len(countries))  # the label locations
    width = 0.3  # the width of the bars

    fig, ax = plt.subplots()
    series_males = ax.bar(x - width / 2, values_male, width, label="Males")
    series_females = ax.bar(x + width / 2, values_female, width, label="Females")

    ax.set_ylabel("Total distance")
    ax.set_title("Countries of airports")
    ax.set_xticks(x)
    ax.set_xticklabels(countries, rotation=90)
    ax.legend()

    # ax.bar_label(series_males, padding=3)
    # ax.bar_label(series_females, padding=3)

    fig.tight_layout()

    plt.show()
