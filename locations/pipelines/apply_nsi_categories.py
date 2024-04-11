import re
from itertools import chain

from scrapy import Spider

from locations.categories import get_category_tags
from locations.items import Feature
from locations.name_suggestion_index import NSI


class ApplyNSICategoriesPipeline:
    nsi = NSI()

    wikidata_cache = {}
    strip_names = None

    def process_item(self, item, spider: Spider):
        if item.get("nsi_id"):
            return item

        code = item.get("brand_wikidata", item.get("operator_wikidata"))
        if not code:
            return item

        if self.strip_names is None:
            self.strip_names = getattr(spider, "strip_names", set())

        if not self.wikidata_cache.get(code):
            # wikidata_cache will usually only hold one thing, but can contain more with more complex spiders
            # The key thing is that we don't have to call nsi.iter_nsi on every process_item
            self.wikidata_cache[code] = list(self.nsi.iter_nsi(code))

        matches = self.wikidata_cache.get(code)

        if len(matches) == 0 and item.get("brand_wikidata"):
            spider.crawler.stats.inc_value("atp/nsi/brand_missing")
            return item
        elif len(matches) == 0 and item.get("operator_wikidata"):
            spider.crawler.stats.inc_value("atp/nsi/operator_missing")
            return item

        if len(matches) == 1:
            spider.crawler.stats.inc_value("atp/nsi/perfect_match")
            return self.apply_tags(matches[0], item)

        if cc := item.get("country"):
            matches = self.filter_cc(matches, cc.lower(), get_category_tags(item))

            if len(matches) == 1:
                spider.crawler.stats.inc_value("atp/nsi/cc_match")
                return self.apply_tags(matches[0], item)

        if categories := get_category_tags(item):
            matches = self.filter_categories(matches, categories)

            if len(matches) == 1:
                spider.crawler.stats.inc_value("atp/nsi/category_match")
                return self.apply_tags(matches[0], item)

        spider.crawler.stats.inc_value("atp/nsi/match_failed")
        return item

    def filter_cc(self, matches: list[dict], cc: str, categories: dict = None) -> list[dict]:
        """Filter matches by country code, attempt to find a better match if category is supplied.
        :param matches: list of matches from NSI
        :param cc: country code in lower case
        :param categories: category tags
        :return: filtered list of matches
        """
        includes = []
        globals_matches = []

        for match in matches:
            if cc in match["locationSet"].get("exclude", []):
                continue

            include = match["locationSet"].get("include", [])
            # Ignore non string such as: {"include":[[-122.835,45.5,2]]}
            include = filter(lambda i: isinstance(i, str), include)
            # "gb-eng" -> "gb"
            include = [i.split("-")[0] for i in include]
            if cc in include:
                includes.append(match)
            if "001" in include:  # 001 being global in NSI
                globals_matches.append(match)

        if categories:
            includes = self.filter_categories(includes, categories)
            globals_matches = self.filter_categories(globals_matches, categories)

        return includes or globals_matches

    def filter_categories(self, matches: list[dict], categories: dict) -> list[dict]:
        """Filter matches by category tags. If two category tags are supplied,
        both tags have to present on the NSI item for a match to occur.
        :param matches: list of matches from NSI
        :param tags: category tags
        :return: filtered list of matches
        """
        results = []

        for match in matches:
            if get_category_tags(match["tags"]) == categories:
                results.append(match)

        return results

    def apply_tags(self, match, item):
        extras = item.get("extras", {})
        item["nsi_id"] = match["id"]

        self.clean_name(match, self.strip_names, item)

        # Apply NSI tags to item
        for key, value in match["tags"].items():
            if key == "brand:wikidata":
                key = "brand_wikidata"
            elif key == "operator:wikidata":
                key = "operator_wikidata"

            # Fields defined in Feature are added directly otherwise add them to extras
            # Never override anything set by the spider
            if key in item.fields:
                if item.get(key) is None:
                    item[key] = value
            else:
                if extras.get(key) is None:
                    extras[key] = value

        item["extras"] = extras

        return item

    @staticmethod
    def clean_name(nsi_entry: dict, strip_names: set[str], item: Feature):
        if not item.get("name"):
            # No name, nothing to clean
            return
        if "branch" in item["extras"]:
            # If branch is set, assume the spider has already cleaned this
            return

        for strip_name in chain(
            strip_names,
            filter(
                None,
                [
                    nsi_entry["tags"].get("name"),
                    nsi_entry["tags"].get("brand"),
                    nsi_entry["tags"].get("operator"),
                ],
            ),
        ):
            if strip_name.upper() in item["name"].upper():
                item["extras"]["branch"] = re.sub(strip_name, "", item.pop("name"), flags=re.IGNORECASE).strip(" -")
                break
