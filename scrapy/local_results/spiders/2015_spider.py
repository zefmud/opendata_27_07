# -*- coding: utf-8 -*-


import scrapy
from ..items import LocalResultsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

class spider_2015(CrawlSpider):
	name = "spider2015"
	start_urls = ["http://www.cvk.gov.ua/pls/vm2015/WM001?pt001f01=100"]
	allowed_domains = ['cvk.gov.ua']
	
	all_particles = ['PVM111\?', 'PVM109\?', 'PVM050\?', 'PVM006\?', 'PVM156\?', 'PVM008\?', 'PVM069\?',
					 'PVM117\?', 'PVM105\?', 'PVM011\?', 'PVM003\?', 'PVM071\?',
					 'PVM009\?', 'PVM029\?', 'PVM005\?', 'PVM004\?', 'PVM063\?', 'PVM120\?', 'PVM070\?', 'PVM002\?', "PVM032\?"]
	particles_interesting = ['PVM002\?']
	particles_deny = list(set(all_particles) - set(particles_interesting))
	custom_settings = {
		"ITEM_PIPELINES": {
		'local_results.pipelines.LocalResultsPipeline': 300,
		'local_results.pipelines.CSVPipeline': 350
		 }
	}
	COUNCIL_TYPES = {
			"pid112=12":u'обласна',
			"pid112=30":u'міська',
			"pid112=21":u'районна',
			"pid112=41":u'районна у місті',
			"pid112=33":u'міська',
			"pid112=61":u'сільска',
			"pid112=51":u'селищна'
		}
	
	rules = (
		Rule(LxmlLinkExtractor(allow = ('/pls/vm2015/', '(wm001)|(WM001\?)|(PVM002\?)|(PVM037\?)'), deny = ["PVM037\?"] + particles_deny ), follow = True),
		Rule(LxmlLinkExtractor(allow = ("PVM037\?")), callback = 'parse_region')
		)
	
	def parse_region(self, response):
		region_name = response.css(".p1::text").extract_first().strip()
		links = response.css(".a1")
		for link in links:
			council_name = link.css('::text').extract_first().strip()
			href = link.css('a::attr(href)').extract_first()
			if [ct for ct in self.COUNCIL_TYPES.keys() if ct in href.lower()]:
				yield scrapy.Request(response.urljoin(href), callback = self.parse_council, meta = {
					"region": region_name,
					"council":council_name,
					"council_type": [self.COUNCIL_TYPES[k] for k in self.COUNCIL_TYPES.keys() if k in href.lower()][0]
				})
	
	def parse_council(self, response):
		election = response.css('.t0 b::text').extract_first().strip()
		rows = response.xpath('//table[@class="t2"][last()]//tr[position()>1]')
		for r in rows:
			if r.css('.td10'):
				nominated_by = r.css('.td10 b::text').extract_first().strip()
			else:
				item = LocalResultsItem()
				number = r.css('td::text').extract_first().strip()
				fullname = r.css('td:nth-child(2)::text').extract_first().strip()
				full_info = r.css('td:nth-child(3)::text').extract_first().strip()	
				item["person_name"] = fullname
				item["nominated_by"] = nominated_by
				item["full_info"] = full_info
				if number == u"Перший кандидат":
					item["list_number"] = 1
					item["candidate_type"] = "list"
				else:
					item["district_number"] = number					
					item["candidate_type"] = "majoritarian"
				item["election"] = election
				item["council"] = response.meta['council']
				item["council_type"] = response.meta['council_type']
				item["region"] = response.meta['region']
				print(r.extract)
				if r.css('td:nth-child(5)::text').extract_first():
					item["result_percent"]  = r.css('td:nth-child(5)::text').extract_first().strip().replace(",",".")
				item["result_is_elected"] = True
				yield item
