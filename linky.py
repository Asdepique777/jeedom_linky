#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Retrieves energy consumption data from your Enedis (ERDF) account."""

# Linkindle - Linky energy consumption curves on a Kindle display.
# Copyright (C) 2016 Baptiste Candellier
# corrected (C) 2017 epierre
#
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

import base64
import requests

LOGIN_BASE_URI = 'https://espace-client-connexion.enedis.fr'
API_BASE_URI = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers'

API_ENDPOINT_LOGIN = '/auth/UI/Login'
API_ENDPOINT_HOME = '/home'
API_ENDPOINT_DATA = '/suivi-de-consommation'

DATA_NOT_REQUESTED = -1
DATA_NOT_AVAILABLE = -2

class LinkyLoginException(Exception):
    """Thrown if an error was encountered while retrieving energy consumption data."""
    pass

def login(username, password):
    """Logs the user into the Linky API.
    """
    session = requests.Session()

    payload = {'IDToken1': username,
               'IDToken2': password,
               'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
               'encoded': 'true',
               'gx_charset': 'UTF-8'}

    #print (payload)

    req = session.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)

    if not 'iPlanetDirectoryPro' in session.cookies:
        raise LinkyLoginException("Login unsuccessful. Check your credentials.")

    return session

def get_data_per_hour(session, start_date, end_date):
    """Retrieves hourly energy consumption data."""
    return _get_data(session, 'urlCdcHeure', start_date, end_date)

def get_data_per_day(session, start_date, end_date):
    """Retrieves daily energy consumption data."""
    return _get_data(session, 'urlCdcJour', start_date, end_date)

def get_data_per_month(session, start_date, end_date):
    """Retrieves monthly energy consumption data."""
    return _get_data(session, 'urlCdcMois', start_date, end_date)

def get_data_per_year(session):
    """Retrieves yearly energy consumption data."""
    return _get_data(session, 'urlCdcAn')

def _get_data(session, resource_id, start_date=None, end_date=None):
    iden = 'lincspartdisplaycdc_WAR_lincspartcdcportlet'

    # We send the session token so that the server knows who we are
    payload = {
        '_' + iden + '_dateDebut': start_date,
        '_' + iden + '_dateFin': end_date
    }

    params = {
        'p_p_id': iden,
        'p_p_lifecycle': 2,
        'p_p_state': 'normal',
        'p_p_mode': 'view',
        'p_p_resource_id': resource_id,
        'p_p_cacheability': 'cacheLevelPage',
        'p_p_col_id': 'column-1',
        'p_p_col_count': 2
    }

    #print (params)
    #print (payload)


    req = session.post(API_BASE_URI + API_ENDPOINT_DATA, \
                        allow_redirects=False, data=payload, params=params)

    if req.status_code >= 300 and req.status_code < 400:
        # So... apparently, we may need to do that once again if we hit a 302
        # ¯\_(ツ)_/¯
        req = session.post(API_BASE_URI + API_ENDPOINT_DATA, \
                            allow_redirects=False, data=payload, params=params)

    #print (req.status_code)
    #print (req.headers)
    #print (req.content)

    return req.json()
