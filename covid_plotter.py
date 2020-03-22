import argparse
import collections
import csv
import datetime
import glob
import matplotlib.pyplot as plt
#from matplotlib.dates import (YEARLY, DateFormatter, rrulewrapper, RRuleLocator, drange)
#import numpy as np
import os
import sys

DateTimeTupleMaker = collections.namedtuple('DateTimeTuple', 'iso days')
FileDataTupleMaker = collections.namedtuple('FileDataTuple', 'date data')
DateTimeEpoch = datetime.datetime(2020, 1, 22)

# Indexes into data
Province = 0
Country = 1
LastUpdate = 2
Confirmed = 3
Deaths = 4
Recovered = 5


def parse_command_line():
    default_data = os.path.join(os.path.dirname(__file__), 'COVID-19')

    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('--type', action='store', required=True, help='The plot to generate from the data')
    parser.add_argument('--data', action='store', default=default_data, required=False, help='Path to the JHU data')

    return parser.parse_args()


def get_time_from_filename(filename):
    tokens = os.path.splitext(os.path.basename(filename))[0].split('-')
    date = datetime.datetime(int(tokens[2]), int(tokens[0]), int(tokens[1]))
    iso_time = date.isoformat()

    return DateTimeTupleMaker(date.isoformat(), (date - DateTimeEpoch).total_seconds() / 86400)


def parse_data_file(filename, country_name_map):

    file_time = get_time_from_filename(filename)
    #print(file_time)
    with open(filename) as file:
        tokens = os.path.splitext(os.path.basename(filename))[0].split('-')
        date = datetime.datetime(int(tokens[2]), int(tokens[0]), int(tokens[1]))
        iso_time= date.isoformat()
        #print("Date: {}".format(iso_time))
        data_reader = csv.reader(file, delimiter=',')
        first_row = True
        data = []
        for row in data_reader:
            if not first_row:
                row[Country] = country_name_map.get(row[Country], row[Country])
                row[Confirmed] = int(row[Confirmed]) if len(row[Confirmed]) > 0 else 0
                row[Recovered] = int(row[Recovered]) if len(row[Recovered]) > 0 else 0
                row[Deaths] = int(row[Deaths]) if len(row[Deaths]) > 0 else 0
                data.append(row)
            first_row = False

        return FileDataTupleMaker(file_time, data)

def collect_data(path):
    try:
        country_name_map = {'Mainland China': 'China'}
        file_pattern = os.path.join(path, 'csse_covid_19_data/csse_covid_19_daily_reports/*.csv')
        #print(file_pattern)
        data_files = glob.glob(file_pattern)
        #print data_files

        all_data = []
        for file in data_files:
            file_data = parse_data_file(file, country_name_map)
            all_data.append(file_data)
        #print(all_data)
        return all_data

    except Exception as e:
        print("Exception thrown while parsing data: {}".format(e))
        sys.exit(-1)

def get_cumulative_data_by_country(country, data):

    results = []
    for datum in data:
        total_confirmed = 0
        total_deaths = 0
        total_recovered = 0
        for entry in datum.data:
            if entry[Country] == country:
                total_confirmed += entry[Confirmed]
                total_deaths += entry[Deaths]
                total_recovered += entry[Recovered]

        results.append((datum.date, total_confirmed, total_deaths, total_recovered))

    return results


def get_cumulative_data_by_province(country, data):
    pass

def plot_data(data):
    date = []
    confirmed = []
    deaths = []
    recovered = []

    for datum in data:
        date.append(datum[0].days)
        confirmed.append(datum[1])
        deaths.append(datum[2])
        recovered.append(datum[3])

    dataset = {'Date' : date, 'Confirmed' : confirmed, 'Deaths' : deaths, 'Recovered' : recovered}

    plt.plot('Date', 'Confirmed', data=dataset, marker='o', label='Confirmed')
    plt.plot('Date', 'Deaths', data=dataset, marker='x', label='Deaths')
    plt.plot('Date', 'Recovered', data=dataset, marker='+', label='Recovered')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    print("""\
COVID-19 data plotter
By default this program assumes the the JHU data is checked out at the same level as this file
To get the JHU data clone https://github.com/CSSEGISandData/COVID-19
""")

    args = parse_command_line()
    print("The parsed arguments are:\n{}".format(args))
    print("Collecting data")
    covid_data = collect_data(args.data)
    country_data = get_cumulative_data_by_country('China', covid_data)
    plot_data(country_data)