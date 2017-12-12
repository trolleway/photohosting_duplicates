#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
from shutil import copyfile
import os
import requests



class mapillary:

    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def __init__(self):
    
        import flickr_keys
        

        self.data = []
        self.client_id=flickr_keys.mapillary_client_id
        self.mapillary_username = flickr_keys.mapillary_username
        self.DEBUG = False
        


        
    def search_mapillary(self,timestamp):
        search_endpoint = 'https://a.mapillary.com/v3/images'
        response = requests.get(search_endpoint, params = {
        'client_id':self.client_id,
        'usernames':self.mapillary_username,
        'start_time':timestamp,
        'end_time':timestamp,
        })
        assert response.status_code / 100 == 2 , 'HTTP CODE ' + str(response.status_code)
        json = response.json()
        
        return int(len(json['features']))
        
