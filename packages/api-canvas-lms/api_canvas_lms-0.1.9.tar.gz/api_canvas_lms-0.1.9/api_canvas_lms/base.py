""" 
Module : Base module for Canvas
Fecha : 19/09/2020
Version : 1.0.0
Author : Jaime Gomez
"""

from datetime import timedelta
import datetime
import requests
import json
import logging

# Create a logger for this module
logger = logging.getLogger(__name__)

API_REST_PATH = 'https://tecsup.instructure.com/api/v1'

class BaseCanvas:

    def __init__(self, access_token):
        # TOKEN
        self.access_token = access_token

    def get(self, url, data = None):
        url = url.replace('<path>', API_REST_PATH)
        if data == None : 
            r = requests.get(url, headers = self.auth_headers())
        else:
            r = requests.get(url, headers = self.auth_headers(), data = data)
        #print("URL ==>", url)
        #print(r)
        if r.status_code >= 400:
            #raise Exception("Unauthorized, Verify course and access_token")
            raise Exception(r.json()["errors"])
        return r.json()

    def get_all_pages(self, url, params = None):
        
        url = url.replace('<path>', API_REST_PATH)
        
        data = []

        while url:
        
            logging.debug(url)
            
            r = requests.get(url, headers = self.auth_headers(), params = params)
            
            logging.debug(r)
            
            if r.status_code >= 400:
                raise Exception(r.json())
        
            if r.status_code == 200:
                data.extend(r.json())
                # Check for 'Link' header to get next page
                if 'next' in r.links:
                    url = r.links['next']['url']
                else:
                    url = None
            else:
                raise Exception(f'Failed to retrieve courses: {r.status_code}')

        return data
    
    def post(self, url, data):
        url = url.replace('<path>', API_REST_PATH)
        #print("URL ==>", url)
        #print("DATA ==>", data)
        r = requests.post(url, headers = self.auth_headers(), data = data)
        #print("RESPONSE ==>",  r.json())
        if r.status_code >= 400:
            #print(r.json()["errors"])
            #raise Exception("Unauthorized, Verify course and access_token")
            raise Exception(r.json()["errors"])
        return r.json()

    def put(self, url, data):
        url = url.replace('<path>', API_REST_PATH)
        #print("URL ==>", url)
        #print("DATA ==>", data)
        r = requests.put(url, headers = self.auth_headers(), data = data)
        #print(r.json())
        if r.status_code >= 400:
            #raise Exception("Unauthorized, Verify course and access_token")
            raise Exception(r.json()["errors"])
        return r.json()

    def delete(self, url):
        url = url.replace('<path>', API_REST_PATH)
        #print("URL ==>", url)
        r = requests.delete(url, headers = self.auth_headers())
        #print(r.json())
        if r.status_code >= 400:
            #raise Exception("Unauthorized, Verify course and access_token")
            raise Exception(r.json()["errors"])
        return r.json()
        
    def auth_headers(self):
        token = 'Bearer ' + self.access_token
        return {'Authorization': token}
