from scrapy.spiders import SitemapSpider

from locations.structured_data_spider import StructuredDataSpider


class TheCheesecakeFactorySpider(SitemapSpider, StructuredDataSpider):
    download_delay = 0.1
    name = "thecheesecakefactory"
    item_attributes = {"brand": "The Cheesecake Factory", "brand_wikidata": "Q1045842"}
    allowed_domains = [
        "www.thecheesecakefactory.com",
        "locations.thecheesecakefactory.com",
    ]
    sitemap_urls = ["https://locations.thecheesecakefactory.com/robots.txt"]
    sitemap_rules = [(r"https:\/\/locations\.thecheesecakefactory\.com\/.+\.html", "parse_sd")]
