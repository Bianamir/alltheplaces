# -*- coding: utf-8 -*-
import scrapy
import json
from locations.items import GeojsonPointItem


class McLocalizer(scrapy.Spider):

    name = "mclocalizer"
    allowed_domains = ["www.mcdonalds.com", "www.mcdonalds.com.pr", "www.mcdonalds.co.cr"]
    start_urls = (
        'http://www.mcdonalds.com.pr/api/restaurantsByCountry?country=PR',
        'http://www.mcdonalds.co.cr/api/restaurantsByCountry?country=CR',
    )

    def parse(self, response):
        data = response.body_as_unicode()
        data.replace('" ', '"')
        data.replace(' "', '"')
        results = json.loads(data)
        results = results["content"]["restaurants"]
        for data in results:
            properties = {
                'ref': data['id'],
                'lon': float(data['longitude']),
                'lat': float(data['latitude']),
                
            }

            contact_info = data['name'][:data['name'].find("<br")]
            name = contact_info[:contact_info.find("</br")]

            properties["name"] = name
            properties["addr_full"] = data['name'][data['name'].find("<small>"):-8][8:]
            #  = address[8:]

            yield GeojsonPointItem(**properties)