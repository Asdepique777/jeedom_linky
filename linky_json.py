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

import base64
import requests
import http.cookiejar

LOGIN_BASE_URI = 'https://espace-client-connexion.enedis.fr'
ACCEUIL_BASE_URI = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers/accueil'

API_BASE_URI = 'https://espace-client-particuliers.enedis.fr/group/espace-particuliers'

API_ENDPOINT_LOGIN = '/auth/UI/Login'
API_ENDPOINT_DATA = '/suivi-de-consommation'

DATA_NOT_REQUESTED = -1
DATA_NOT_AVAILABLE = -2

class LinkyLoginException(Exception):
    """Thrown if an error was encountered while retrieving energy consumption data."""
    pass

def merge_cookies(cookiejar, cookies):
    if not isinstance(cookiejar, http.cookiejar.CookieJar):
        raise ValueError('You can only merge into CookieJar')

    if isinstance(cookies, dict):
        cookiejar = cookiejar_from_dict(
            cookies, cookiejar=cookiejar, overwrite=False)
    elif isinstance(cookies, http.cookiejar.CookieJar):
        try:
            cookiejar.update(cookies)
        except AttributeError:
            for cookie_in_jar in cookies:
                cookiejar.set_cookie(cookie_in_jar)
    return cookiejar

def login(username, password):
    """Logs the user into the Linky API.
    """
    payload = {'IDToken1': username,
               'IDToken2': password,
               'SunQueryParamsString': base64.b64encode(b'realm=particuliers'),
               'encoded': 'true',
               'gx_charset': 'UTF-8'}

    # to Get the authentications cookies
    req = requests.post(LOGIN_BASE_URI + API_ENDPOINT_LOGIN, data=payload, allow_redirects=False)
    #Dont bother, get all cookies!
    session_cookie = req.cookies.get('iPlanetDirectoryPro')

    if session_cookie is None:
        raise LinkyLoginException("Login unsuccessful. Check your credentials.")

    # to Get the proper JSESSIONID cookie
    req2 = requests.get(ACCEUIL_BASE_URI,  cookies=req.cookies, allow_redirects=False)

    #return all cookies
    return merge_cookies(req.cookies,req2.cookies)

def get_data_per_hour(token, start_date, end_date):
    """Retreives hourly energy consumption data."""
    return _get_data(token, 'urlCdcHeure', start_date, end_date)

def get_data_per_day(token, start_date, end_date):
    """Retreives daily energy consumption data."""
    return _get_data(token, 'urlCdcJour', start_date, end_date)

def get_data_per_month(token, start_date, end_date):
    """Retreives monthly energy consumption data."""
    return _get_data(token, 'urlCdcMois', start_date, end_date)

def get_data_per_year(token):
    """Retreives yearly energy consumption data."""
    return _get_data(token, 'urlCdcAn')

def _get_data(cookies, resource_id, start_date=None, end_date=None):
    prefix = '_lincspartdisplaycdc_WAR_lincspartcdcportlet_'

    # We send the session token so that the server knows who we are
    #cookies = {'iPlanetDirectoryPro': token}
    payload = {
        prefix + 'dateDebut': start_date,
        prefix + 'dateFin': end_date
    }
    params = {
        'p_p_id': 'lincspartdisplaycdc_WAR_lincspartcdcportlet',
        'p_p_lifecycle': 2,
        'p_p_state': 'normal',
        'p_p_mode': 'view',
        'p_p_resource_id': resource_id,
        'p_p_cacheability': 'cacheLevelPage',
        'p_p_col_id': 'column-1',
        'p_p_col_count': 2
    }

    print (API_BASE_URI + API_ENDPOINT_DATA)
    print ("cookies",cookies)
    print ("params",params)
    print ("payload",payload)

    req = requests.Session()
    req.headers.update({'referer':'https://espace-client-particuliers.enedis.fr/group/espace-particuliers/suivi-de-consommation'})
    req.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
    req = req.post(API_BASE_URI + API_ENDPOINT_DATA, allow_redirects=False, cookies=cookies, data=payload, params=params)

    return req.json()
