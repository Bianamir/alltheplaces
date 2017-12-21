# -*- coding: utf-8 -*-
import scrapy
import re

from locations.items import GeojsonPointItem


class TheLibrarySpider(scrapy.Spider):
    name = "thelibrary"
    allowed_domains = ['worldcat.org']
    start_urls = (
        'http://www.worldcat.org/libraries/sitemap_index.xml',
    )

    def parse(self, response):
        response.selector.remove_namespaces()
        xml_urls = response.xpath('//sitemap/loc/text()').extract()
        for path in xml_urls:
            yield scrapy.Request(
                path.strip(),
                callback=self.parse_sitemap,
            )
        else:
            pass

    def parse_sitemap(self, response):
        response.selector.remove_namespaces()
        xml_urls = response.xpath('//url/loc/text()').extract()
        for path in xml_urls:
            yield scrapy.Request(
                path.strip(),
                callback=self.parse_store,
            )
        else:
            pass

    def parse_store(self, response):

        if "United States" in response.css('#lib-data').extract_first():
            properties = {
            'name': response.xpath('//h1/text()').extract_first().strip(),
            'ref': response.xpath('//h1/text()').extract_first().strip(),
            'addr_full': response.xpath('//div[@id="lib-data"]/p/text()').extract_first().strip(),
            'city': response.xpath('//div[@id="lib-data"]/p/text()').extract()[1].strip().split(',')[0],
            'state': response.xpath('//div[@id="lib-data"]/p/text()').extract()[1].split(',')[1].strip().split('\xa0')[0],
            'postcode': response.xpath('//div[@id="lib-data"]/p/text()').extract()[1].split(',')[1].strip().split('\t')[-1],
            # 'phone':  phoneNumber,
            'website': response.request.url,
            # 'lat': float(response.xpath('//div/div[@class="location-actions"]/a[@href]').extract_first().split('q=')[1].split('%')[0].split(',')[0]),
            # 'lon': float(response.xpath('//div/div[@class="location-actions"]/a[@href]').extract_first().split('q=')[1].split('%')[0].split(',')[1]),
            }
        else:
            # if response.xpath('//div[@id="lib-data"]/p[2]').extract_first():
            #     phoneNumber = response.xpath('//div[@id="lib-data"]/p[2]').extract_first().split('\xa0')[1].split('<br>')[0]
            # else:
            #     phoneNumber = response.xpath('//div[@id="lib-data"]/p[2]').extract_first()


            properties = {
                'name': response.xpath('//h1/text()').extract_first().strip(),
                'ref': response.xpath('//h1/text()').extract_first().strip(),
                'addr_full': response.css('#lib-data').extract_first().split('<p>')[1].split('\n\t\t\t\t\t\t')[1].replace('<br>',''),
                'city': response.css('#lib-data').extract_first().split('<p>')[1].split('\n\t\t\t\t\t\t')[2].split(',')[0],
                'state': response.xpath('//div[@id="lib-data"]/p/text()').extract()[1].split(',')[1].strip().split('\xa0')[0],
                'country': response.css('#lib-data').extract_first().split('<p>')[1].split('\n\t\t\t\t\t\t')[4].split('<')[-2].replace('br>',''),
                'postcode': response.css('#lib-data').extract_first().split('<p>')[1].split('\n\t\t\t\t\t\t')[3].replace('\xa0',''),
                'phone': response.xpath('//div[@id="lib-data"]/p[3]').extract_first().split('\xa0')[1].split('<br>')[0],
                'website': response.request.url,
                # 'lat': float(response.xpath('//div/div[@class="location-actions"]/a[@href]').extract_first().split('q=')[1].split('%')[0].split(',')[0]),
                # 'lon': float(response.xpath('//div/div[@class="location-actions"]/a[@href]').extract_first().split('q=')[1].split('%')[0].split(',')[1]),
            }

        yield GeojsonPointItem(**properties)