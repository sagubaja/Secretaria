#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 10:45:14 2017
@author: juang
"""
from googleapiclient.discovery import build
import pprint



#clave de Google News
#Key='f7876e6069694a5a8fde3e3781c8bba8'
#base='https://newsapi.org/v1/articles?source=techcrunch&apiKey='
#textReq=base+token'

#clave para custon search - 100 search queries per day for free
my_api_key = 'AIzaSyBeyeW0aDEpSneCpbFJrLue0HDhMXmM0b0'
my_cse_id = "017581525936196135811:nuj2sn_8l7a"

def News(Frase):
    def google_search(search_term, api_key, cse_id, **kwargs):
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=search_term, cx=cse_id, sort='date:r:20140324:20140330', **kwargs).execute()
        return res['items']

    results = google_search(Frase, my_api_key, my_cse_id)
    
    return results
