#!/usr/bin/env python3
import argparse
import json
from datetime import datetime as dt
from datetime import timedelta
from DONKI import DONKI


'''
Write space weather notifications to json file
'''

def parsedDate(str_date):
    """Check formatting of given date strings"""
    return dt.strptime(str_date, '%Y-%m-%d').date()

parser = argparse.ArgumentParser(prog="DONKI-stream")
parser.add_argument("-o", "--output",
                    choices=["file", "kafka"],
                    default="file",
                    help="Choose the output format for the DONKI notifications. \
                        Choices: ['file', 'kafka']. Default: file.")
parser.add_argument("-d", "--date",
                    default=dt.today().strftime('%Y-%m-%d'),
                    help="Date to begin pulling data from, in YYYY-MM-DD format. Default: today.",
                    type=parsedDate)
parser.add_argument("--delta",
                    action="store_true",
                    help="***NOT YET IMPLEMENTED*** Use this flag to find the delta \
                        between date and previously stored data. If not used, only 30 days \
                        of data will be pulled from starting date.")
args = parser.parse_args()

# DETERMINE DATES
dates_list = []
delta = timedelta(days=30)

start_date = args.date
end_date = start_date - delta

date_tuple = (dt.strftime(start_date, '%Y-%m-%d'), dt.strftime(end_date, '%Y-%m-%d'))
dates_list.append(date_tuple)

# PROCESS
donki = DONKI(dates_list)

# WRITE
print(f"Attempting to write {len(donki.clean_data)} notifications to {args.output}...")

if args.output == 'file':
    with open(f'{start_date}-{end_date}DONKI.json', 'w') as outfile:
        json.dump(donki.clean_data, outfile)

if args.output == 'kafka':
    from utils.kafka_writer import KafkaWriter
    KafkaWriter(donki.clean_data)

