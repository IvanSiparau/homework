import scrapy
from urllib.parse import urlencode
from urllib.parse import urljoin

queries = ['anime']


class SpiderSteamItem(scrapy.Item):
    name = scrapy.Field()
    date = scrapy.Field()
    tag = scrapy.Field()
    price = scrapy.Field()
    developer = scrapy.Field()
    path = scrapy.Field()


class SteamProductSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']

    def start_requests(self):
        for query in queries:
            for i in range(1, 3):
                url = f'https://store.steampowered.com/search/?term={query}&page={str(i)}'
                yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response, **kwargs):
        for url in response.css('div.search_results a::attr(href)'):
            yield response.follow(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = SpiderSteamItem()
        name = response.css("div.apphub_AppName::text").get()
        date = response.css("div.date::text").get()
        tag = response.xpath("//a[@class='app_tag']/text()").extract()
        for i in range(len(tag)):
            tag[i] = tag[i].replace("\n", "").replace("\t", "").replace("\r", "")
        price = response.css("div.game_purchase_price.price::text").get()
        developer = response.xpath('//div[@class="dev_row"]/div[@id="developers_list"]/a/text()').extract()
        path = \
            response.xpath('//div[@class="page_title_area game_title_area page_content"]/div["breadcrumbs"]/div["blockbg"]/a/text()').extract()
        if name is not None and date.split()[2] > "2000":
            item["name"] = name
            item["date"] = date
            item["tag"] = tag
            item["price"] = price.replace("\t", "").replace("\r", "").replace("\n", "")
            item["developer"] = developer
            item["path"] = path[1:]
            return item
