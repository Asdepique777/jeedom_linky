#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Generates energy consumption JSON files from Enedis (ERDF) consumption data
collected via their  website (API).
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
import logging
import sys
import json
import linky
from dateutil.relativedelta import relativedelta

USERNAME = os.environ['LINKY_USERNAME']
PASSWORD = os.environ['LINKY_PASSWORD']
BASEDIR = os.environ['BASE_DIR']

# Generate y axis (consumption values) 
def generate_y_axis(res):
    y_values = []

    # Extract data points from the source dictionary into a list
    for ordre, datapoint in enumerate(res['graphe']['data']):
        value = datapoint['valeur']

        # Remove any invalid values
        # (they're error codes on the API side, but useless here)
        if value < 0:
            value = 0

        y_values.insert(ordre, value)

    return y_values

# Generate x axis (time values)  
def generate_x_axis(res, time_delta_unit, time_format, inc):
    x_values = []

    # Extract start date and parse it
    start_date_queried_str = res['graphe']['periode']['dateDebut']
    start_date_queried = datetime.datetime.strptime(start_date_queried_str, "%d/%m/%Y").date()

    # Calculate final start date using the "offset" attribute returned by the API
    kwargs = {}
    kwargs[time_delta_unit] = res['graphe']['decalage'] * inc
    start_date = start_date_queried - relativedelta(**kwargs)

    # Generate X axis time labels for every data point
    for ordre, _ in enumerate(res['graphe']['data']):
        kwargs = {}
        kwargs[time_delta_unit] = ordre * inc
        x_values.insert(ordre, (start_date + relativedelta(**kwargs)).strftime(time_format))

    return x_values

# Date formatting 
def dtostr(date):
    return date.strftime("%d/%m/%Y")


# Export the JSON file for half-hours power measure (for the last pas day)
def export_hours_values(res):
    hours_x_values = generate_x_axis(res, \
                                    'hours', "%H:%M", 0.5)
    hours_y_values = generate_y_axis(res)
    hours_values = []

    for i in range(0,len(hours_x_values)):
        hours_values.append({"time" : hours_x_values[i], "conso" : hours_y_values[i]})
    with open(BASEDIR+"/export_hours_values.json", 'w+') as outfile:
        json.dump(hours_values, outfile)

# Export the JSON file for daily consumption (for the past rolling 30 days)
def export_days_values(res):
    days_x_values = generate_x_axis(res, \
                                    'days', "%d %b", 1)
    days_y_values = generate_y_axis(res)
    days_values = []

    for i in range(0,len(days_x_values)):
        days_values.append({"time" : days_x_values[i], "conso" : days_y_values[i]})
    with open(BASEDIR+"/export_days_values.json", 'w+') as outfile:
        json.dump(days_values, outfile)

# Export the JSON file for monthly consumption (for the current year, starting 12 months from today)
def export_months_values(res):
    months_x_values = generate_x_axis(res, \
                                    'months', "%b", 1)
    months_y_values = generate_y_axis(res)
    months_values = []

    for i in range(0,len(months_x_values)):
        months_values.append({"time" : months_x_values[i], "conso" : months_y_values[i]})
    with open(BASEDIR+"/export_months_values.json", 'w+') as outfile:
        json.dump(months_values, outfile)

# Export the JSON file for yearly consumption
def export_years_values(res):
    years_x_values = generate_x_axis(res, \
                                    'years', "%Y", 1)
    years_y_values = generate_y_axis(res)
    years_values = []

    for i in range(0,len(years_x_values)):
        years_values.append({"time" : years_x_values[i], "conso" : years_y_values[i]})
    with open(BASEDIR+"/export_years_values.json", 'w+') as outfile:
        json.dump(years_values, outfile)




# Main script 
def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    try:
        logging.info("logging in as %s...", USERNAME)
        token = linky.login(USERNAME, PASSWORD)
        logging.info("logged in successfully!")

        logging.info("retreiving data...")
        today = datetime.date.today()
        
        # Years
        res_year = linky.get_data_per_year(token)

        # 12 months ago - today
        res_month = linky.get_data_per_month(token, dtostr(today - relativedelta(months=11)), \
                                             dtostr(today))


        # One month ago - yesterday
        res_day = linky.get_data_per_day(token, dtostr(today - relativedelta(days=1, months=1)), \
                                         dtostr(today - relativedelta(days=1)))


        # Yesterday - today
        res_hour = linky.get_data_per_hour(token, dtostr(today - relativedelta(days=1)), \
                                           dtostr(today))
        

        logging.info("got data!")
############################################
		# Export of the JSON files, with exception handling as Enedis website is not robust and return empty data often
        try:
            export_hours_values(res_hour)
        except Exception as exc:
        	# logging.info("hours values non exported")
            logging.error(exc)

        try:
            export_days_values(res_day)
        except Exception:
            logging.info("days values non exported")

        try:
            export_months_values(res_month)
        except Exception:
            logging.info("months values non exported")

        try:
            export_years_values(res_year)
        except Exception:
        	logging.info("years values non exported")

############################################
 
    except linky.LinkyLoginException as exc:
        logging.error(exc)
        sys.exit(1)



if __name__ == "__main__":
    main()