# -*- coding: utf-8 -*-
import scrapy
import json
import re

from locations.items import GeojsonPointItem


class QuiznosSpider(scrapy.Spider):
    name = "quiznos"
    item_attributes = { 'brand': "Quizno's", 'brand_wikidata': "Q1936229" }
    allowed_domains = ["https://restaurants.quiznos.com"]
    start_urls = (
        'https://restaurants.quiznos.com/data/stores.json',
    )

    def store_hours(self, store_hours):
        if store_hours == '' or store_hours == ' - ' or store_hours.lower().find('close') > -1:
            return ''

        if store_hours == 'Open 24 Hours - Open 24 Hours':
            return '24/7'

        day_groups = []
        this_day_group = None
        hour_intervals = []

        interval = store_hours.split(' - ')
        start_time = interval[0].split(' ')
        end_time = interval[1].split(' ')
        start_hour = start_time[0].split(':')
        end_hour = end_time[0].split(':')

        hour_intervals.append('{}:{}-{}:{}'.format(
            start_hour[0],
            start_hour[1],
            int(end_hour[0]) + 12 if end_time[1] == 'PM' else end_hour[0],
            end_hour[1],
        ))

        hours = ','.join(hour_intervals)

        if not this_day_group:
            this_day_group = {
                'from_day': 'Su',
                'to_day': 'Sa',
                'hours': hours
            }

        day_groups.append(this_day_group)

        opening_hours = ""
        if len(day_groups) == 1 and day_groups[0]['hours'] in ('00:00-23:59', '00:00-00:00'):
            opening_hours = '24/7'
        else:
            for day_group in day_groups:
                if day_group['from_day'] == day_group['to_day']:
                    opening_hours += '{from_day} {hours}; '.format(**day_group)
                elif day_group['from_day'] == 'Su' and day_group['to_day'] == 'Sa':
                    opening_hours += '{hours}; '.format(**day_group)
                else:
                    opening_hours += '{from_day}-{to_day} {hours}; '.format(**day_group)
            opening_hours = opening_hours[:-2]

        return opening_hours

    def parse(self, response):
        data = response.body_as_unicode()
        stores = json.loads(re.search(r'storeList\((.*)\)', data).group(1))

        for store in stores:
            properties = {
                "lat": store.get('latitude'),
                "lon": store.get('longitude'),
                "ref": str(store.get('storeid')),
                "phone": store.get('phone'),
                "name": store.get('restaurantname'),
                "opening_hours": self.store_hours(store.get('businesshours')),
                "addr_full": store.get('address1'),
                "city": store.get('city'),
                "state": store.get('statecode'),
                "postcode": store.get('zipcode'),
                "website": response.urljoin(store.get('url')),
            }

            yield GeojsonPointItem(**properties)
