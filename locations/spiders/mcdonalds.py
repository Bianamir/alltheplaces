# -*- coding: utf-8 -*-
import scrapy
import json

from locations.items import GeojsonPointItem

countries = ['us', 'ca', 'cr', 'au', 'jp', 'nl', 'pa', 'de', 'fr', 'sv', 'se', 'gt', 'uk', 'hk', 'bs', 'nz',
             'sz', 'ie', 'at', 'be', 'br', 'sg', 'es', 'dk', 'ph', 'my', 'no', 'ad', 'fi', 'th', 'lu', 'vu',
             'it', 'mx', 'cu', 'tr', 'ar', 'rs', 'hu', 'ru', 'cn', 'cl', 'id', 'pt', 'gr', 'uy', 'cz', 'pl',
             'mc', 'bn', 'ma', 'il', 'si', 'sa', 'kw', 'om', 'eg', 'bg', 'bh', 'lv', 'ae', 'ee', 'ro', 'mt',
             'co', 'sk', 'za', 'qa', 'hr', 'ws', 'fj', 'lt', 'in', 'pe', 'jo', 'py', 'do', 'by', 'tt', 'ua',
             'cy', 'ec', 'bo', 'sr', 'ni', 'kr', 'lb', 'pk', 'lk', 'sm', 'az', 'mr', 'iq', 'ba', 'vn', 'kz',
             'gb']


class McDonaldsSpider(scrapy.Spider):
    name = "mcdonalds"
    allowed_domains = ["www.mcdonalds.com"]

    urls = []

    for country in countries:
        url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=44.97&longitude=-93.21&radius=100000&maxResults=300000&country=' + country + '&language=en-' + country
        urls.append(url)

    start_urls = tuple(urls)

    def store_hours(self, store_hours):
        if not store_hours:
            return None
        if all([h == '' for h in store_hours.values()]):
            return None

        day_groups = []
        this_day_group = None
        for day in ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'):
            hours = store_hours.get('hours' + day)
            if not hours:
                continue

            hours = hours.replace(' - ', '-')
            day_short = day[:2]

            if not this_day_group:
                this_day_group = dict(from_day=day_short, to_day=day_short, hours=hours)
            elif this_day_group['hours'] == hours:
                this_day_group['to_day'] = day_short
            elif this_day_group['hours'] != hours:
                day_groups.append(this_day_group)
                this_day_group = dict(from_day=day_short, to_day=day_short, hours=hours)
        day_groups.append(this_day_group)

        if len(day_groups) == 1:
            opening_hours = day_groups[0]['hours']
            if opening_hours == '04:00-04:00':
                opening_hours = '24/7'
        else:
            opening_hours = ''
            for day_group in day_groups:
                if day_group['from_day'] == day_group['to_day']:
                    opening_hours += '{from_day} {hours}; '.format(**day_group)
                else:
                    opening_hours += '{from_day}-{to_day} {hours}; '.format(**day_group)
            opening_hours = opening_hours[:-2]

        return opening_hours

    def parse(self, response):
        data = json.loads(response.body_as_unicode())

        for store in data.get('features', []):
            store_info = store['properties']

            properties = {
                "ref": store_info['id'],
                'addr_full': store_info['addressLine1'],
                'city': store_info['addressLine3'],
                'state': store_info['subDivision'],
                'country': store_info['addressLine4'],
                'postcode': store_info['postcode'],
                'phone': store_info.get('telephone'),
                'lon': store['geometry']['coordinates'][0],
                'lat': store['geometry']['coordinates'][1],
            }

            hours = store_info.get('restauranthours')
            try:
                hours = self.store_hours(hours)
                if hours:
                    properties['opening_hours'] = hours
            except:
                self.logger.exception("Couldn't process opening hours: %s", hours)

            yield GeojsonPointItem(**properties)
