# -*- coding: utf-8 -*-
import re

import scrapy
import json

from locations.items import GeojsonPointItem

class GuzmanyGomezSpider(scrapy.Spider):
    #download_delay = 0.3
    name = "gyg"
    item_attributes = {'brand': "Guzman Y Gomez"}
    allowed_domains = ["guzmanygomez.com.au"]
    start_urls = ([
        'https://www.guzmanygomez.com.au/wp-json/wpapi/v2/getall',
    ])

    def parse(self, response):
        data = json.loads(json.dumps(response.json()))

        for i in data:
            properties = {
                'ref': i['OrderLink'],
                'name': i['Name'],
                'addr_full': i['Address1'],
                'city': i['City'],
                'state': i['State'],
                'postcode': i['Postcode'],
                'country': "AU",
                'phone': i['Phone'],
                'lat': i['Latitude'],
                'lon': i['Longitude'],
            }
            yield GeojsonPointItem(**properties)