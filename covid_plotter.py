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
import traceback


DateTimeTupleMaker = collections.namedtuple('DateTimeTuple', 'iso days')
FileDataTupleMaker = collections.namedtuple('FileDataTuple', 'date data')
DateTimeEpoch = datetime.datetime(2020, 1, 22)


def get_row_data(schema, country_name_map, row):
    return [
        row[schema.Province],
        country_name_map.get(row[schema.Country], row[schema.Country]),
        row[schema.LastUpdate],
        int(row[schema.Confirmed]) if len(row[schema.Confirmed]) > 0 else 0,
        int(row[schema.Deaths]) if len(row[schema.Deaths]) > 0 else 0,
        int(row[schema.Recovered]) if len(row[schema.Recovered]) > 0 else 0,
    ]


class Schema0:
    Header = 'Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered'

    # Indexes into data
    Province = 0
    Country = 1
    LastUpdate = 2
    Confirmed = 3
    Deaths = 4
    Recovered = 5
    Active = -1

class Schema1:
    Header = 'Province/State,Country/Region,Last Update,Confirmed,Deaths,Recovered,Latitude,Longitude'

    # Indexes into data
    Province = 0
    Country = 1
    LastUpdate = 2
    Confirmed = 3
    Deaths = 4
    Recovered = 5
    Active = -1

class Schema2:
    Header = 'FIPS,Admin2,Province_State,Country_Region,Last_Update,Lat,Long_,Confirmed,Deaths,Recovered,Active,Combined_Key'

    # Indexes into data
    Province = 2
    Country = 3
    LastUpdate = 4
    Confirmed = 7
    Deaths = 8
    Recovered = 9
    Active = 10


Schemas = {Schema0.Header: Schema0, Schema1.Header: Schema1, Schema2.Header: Schema2}


Province = 0
Country = 1
LastUpdate = 2
Confirmed = 3
Deaths = 4
Recovered = 5
Active = 6


def parse_command_line():
    default_data = os.path.join(os.path.dirname(__file__), 'COVID-19')

    parser = argparse.ArgumentParser(description='Command line arguments')
    parser.add_argument('--country', action='store', default='US', required=False, help='Country to gather data.  Default is US')
    parser.add_argument('--min_day', type=int, action='store', default=None, required=False, help='Minimum day.  Default is from the start of the data')
    parser.add_argument('--max_day', type=int, action='store', default=None, required=False, help='Maximum day.  Default is to the end of the data')
    #parser.add_argument('--states', type=bool, action='store_true', default=False, required=False, help='Show states/provinces instead of total country data')
    #parser.add_argument('--type', action='store', required=True, help='The plot to generate from the data')
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
        schemaInfo = None
        for row in data_reader:
            if first_row:
                schema_string = ','.join(row)
                if schema_string == Schema2.Header:
                    pass
                if schema_string[0] == '\xef':
                    # Strip the BOM
                    schema_string = schema_string[3:]
                schema = Schemas[schema_string]
            else:
                try:
                    row = get_row_data(schema, country_name_map, row)
                    data.append(row)
                except:
                    raise
            first_row = False

        return FileDataTupleMaker(file_time, data)

def collect_data(path):
    try:
        country_name_map = {'Mainland China': 'China', 'Taiwan*': 'Taiwan'}
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
        traceback.print_exc()
        print("Exception thrown while parsing data: {}".format(e))
        sys.exit(-1)

def get_cumulative_data_by_country(country, data, min_day, max_day):

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

        if min_day is None or datum.date.days >= min_day:
            if max_day is None or datum.date.days <= max_day:
                results.append((datum.date, total_confirmed, total_deaths, total_recovered))

    return results


def get_cumulative_data_by_province(country, data):
    pass

def plot_data(title, data):
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
    plt.title(title)
    plt.legend()
    plt.show()

def get_title(country, min_day, max_day):
    title = "Total {} Cases".format(country)
    if min_day and max_day:
        pass
    elif min_day:
        pass
    elif max_day:
        pass

    return title


if __name__ == '__main__':
    print("""\
COVID-19 data plotter
By default this program assumes the the JHU data is checked out at the same level as this file
To get the JHU data clone https://github.com/CSSEGISandData/COVID-19
""")
    sys.stdout.flush()

    args = parse_command_line()
    print("The parsed arguments are:\n{}".format(args))
    print("Collecting data")
    covid_data = collect_data(args.data)
    country_data = get_cumulative_data_by_country(args.country, covid_data, args.min_day, args.max_day)
    plot_data(get_title(args.country, args.min_day, args.max_day ), country_data)