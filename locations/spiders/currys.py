from scrapy.spiders import SitemapSpider

from locations.structured_data_spider import StructuredDataSpider


class CurrysSpider(SitemapSpider, StructuredDataSpider):
    name = "currys_gb"
    item_attributes = {"brand": "currys", "brand_wikidata": "Q3246464"}
    sitemap_rules = ["https://www.currys.co.uk/sitemap-stores-curryspcworlduk.xml"]

    def pre_process_data(self, ld_data, **kwargs):
        if isinstance(ld_data["openingHoursSpecification"], dict):
            ld_data["openingHoursSpecification"] = [ld_data["openingHoursSpecification"]]
        for rule in ld_data["openingHoursSpecification"]:
            rule["opens"] = rule["opens"].strip()
            rule["closes"] = rule["closes"].strip()

    def post_process_item(self, item, response, ld_data, **kwargs):
        item["lat"] = response.xpath('//input[@class="storeDetailLat"]/@value').get()
        item["lon"] = response.xpath('//input[@class="storeDetailLong"]/@value').get()
        item["name"] = response.xpath('//h1[@class="store-information-page-title"]/text()').get().strip()
        yield item
