import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcbtksItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.cbtks.com/learn/education/{}'

class CcbtksSpider(scrapy.Spider):
	name = 'cbtks'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 20:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('//span[@property="datePublished"]/text()').get()
		date = re.findall(r'\w+\s\d+\,\s\d+', date)
		title = response.xpath('(//h1)[2]/text()').get()
		content = response.xpath('//div[@property="mainEntityOfPage"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcbtksItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
