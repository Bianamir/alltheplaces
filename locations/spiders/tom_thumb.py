import scrapy
import re
from locations.items import GeojsonPointItem


class TomThumbSpider(scrapy.Spider):
    name = "tom_thumb"
    item_attributes = {"brand": "Tom Thumb", "brand_wikidata": "Q7817826"}
    allowed_domains = ["local.tomthumb.com"]
    start_urls = ("https://local.tomthumb.com/sitemap.xml",)

    def parse_store(self, response):
        ref = re.search(r".*\/([0-9]+[a-z\-]+)\.html", response.url).group(1)
        name = response.xpath(
            "//div[@class='Heading--lead ContentBanner-title']/text()"
        ).extract_first()
        addr_full = response.xpath(
            "//meta[@itemprop='streetAddress']/@content"
        ).extract_first()
        city = response.xpath(
            "//meta[@itemprop='addressLocality']/@content"
        ).extract_first()
        postcode = response.xpath(
            "//span[@itemprop='postalCode']/text()"
        ).extract_first()
        geo_region = (
            response.xpath("//meta[@name='geo.region']/@content")
            .extract_first()
            .split("-")
        )
        coordinates = (
            response.xpath("//meta[@name='geo.position']/@content")
            .extract_first()
            .split(";")
        )
        phone = response.xpath(
            "//div[@class='Phone-display Phone-display--withLink']/text()"
        ).extract_first()

        properties = {
            "ref": ref,
            "name": name,
            "addr_full": addr_full,
            "city": city,
            "postcode": postcode,
            "state": geo_region[1],
            "country": geo_region[0],
            "lat": coordinates[0],
            "lon": coordinates[1],
            "phone": phone,
            "website": response.url,
        }

        yield GeojsonPointItem(**properties)

    def parse(self, response):
        response.selector.remove_namespaces()
        urls = response.xpath("//loc").re(
            r"https://local.tomthumb.com\/[a-z]{2}\/[a-z\-]+\/[0-9]+[a-z\-]+\.html"
        )
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_store)
