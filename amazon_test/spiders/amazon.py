import scrapy


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com']

    keywords = ["cellphone"]
    start_urls = [f'https://www.amazon.com/s?k={keyword}' for keyword in keywords]

    def parse(self, response):
        good_names = response.xpath(
            '//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/span/text()').extract()
        good_urls = response.xpath('//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div/div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a/@href').extract()
        for i in range(0, len(good_urls)):
            item = {}
            good_name = good_names[i]
            good_url = "https://www.amazon.com" + good_urls[i]
            print(f"[GOODNAME] : {good_name}")
            print(f"[GOODURL] : {good_url}")
            item["good_name"] = good_name
            item["good_url"] = good_url
            yield scrapy.Request(url=good_url, callback=self.parse_detail, meta={"item" : item})
        try:
            next_url = response.xpath('//*[@id="search"]/div[1]/div/div[1]/div/span[3]/div[2]/div[last()-2]/span/div/div/ul/li[last()]/a/@href').extract()
            next_url = "https://www.amazon.com" + next_url[0]
            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse)
        except:
            print(f"{self.keyword} crawl finish")

    def parse_detail(self, response):
        item = response.meta["item"]
        print(f"[RESPONSE STATUS] : {response.status}")
        price = self.parse_element(response, '//*[@id="priceblock_ourprice"]/text()')
        star_level = self.parse_element(response, '//*[@id="acrCustomerReviewText"]/text()')
        answers = self.parse_element(response, '//*[@id="askATFLink"]/span/text()')
        # html = response.body.decode("utf-8")
        item["price"] = price
        item["star_level"] = star_level
        item["answers"] = answers
        print(f"[PRICE] : {price}")
        yield item

    def parse_element(self, response, element):
        try:
            result = response.xpath(element).extract()[0]
        except:
            result = ""
        return result