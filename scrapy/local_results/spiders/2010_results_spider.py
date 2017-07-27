# -*- coding: utf-8 -*-

import scrapy
from ..items import LocalResultsItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
import re

class spider_dep_2010(CrawlSpider):
	name = "spider_dep_2010"
	allowed_domains = ['cvk.gov.ua']
	#start_urls = ["http://www.cvk.gov.ua/pls/vm2010/WP0011"]
	start_urls = ["http://www.cvk.gov.ua/pls/vm2010/WP0022?PT001F01=800&PMENU=0",
				"http://www.cvk.gov.ua/pls/vm2010/WP0022?PT001F01=801&PMENU=0"]
	#start_urls = ["http://www.cvk.gov.ua/pls/vm2010/WP0022?PT001F01=800&PMENU=0"]
	all_particles = ["wm00113", "wm00114", "WM002", "WM041", "WM02815", "WM0240"]
	particles_interesting = ["wm00114"]
	
	particles_deny = list(set(all_particles) - set(particles_interesting))
	custom_settings = {
			"ITEM_PIPELINES": {
			'local_results.pipelines.LocalResultsPipeline': 300,
			'local_results.pipelines.CSVPipeline': 350}}
	COUNCIL_TYPES = {
            "pid112=12":u'обласна',
            "pid112=30":u'міська',
            "pid112=21":u'районна',
            "pid112=41":u'районна у місті',
            "pid112=33":u'міська'
            #"pid112=61":u'сільска',
            #"pid112=51":u'селищна'
	}
	rules = (
			#Rule(LxmlLinkExtractor(deny = ["WM003125\?"] + particles_deny), follow = True),
			#Rule(LxmlLinkExtractor(allow = ('/pls/vm2010/',))),
			Rule(LxmlLinkExtractor(allow = ('/pls/vm2010/'), deny = ['WM003126\?', "WM003125\?", 'WM02815\?'] + particles_deny + ['pxto=1', 'pxto=2']), follow = True),
			Rule(LxmlLinkExtractor(allow = ('WM003125\?', 'WM003126\?')), callback = 'parse_region', follow = False)
			)
	election_id_re = re.compile("pt00_t001f01=(\d{3})")
	elections = {'801':u"Позачергові місцеві вибори 25.05.2014",
				'800':u"Чергові місцеві вибори 31.10.2010"}
	download_delay = 0.5
	def parse_region(self, response):
		region_name = response.css(".p1::text").extract_first().strip()
		links = response.css(".a1small")
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
		url = response.url
		election_id_matched = self.election_id_re.search(url)
		election_id = election_id_matched.group(1)
		table_councilmen = response.xpath(u'//table[@class="t2"]//tr[contains(., "Відомості про обраного депутата")]/..')
		table_ex = response.xpath(u'//table[@class="t2"][contains(., "Відомості про вибулих")]')
		rows = table_councilmen.css('tr:not(:first-child)')
		for r in rows:
			if r.css('.td10'):
				nominated_by = r.css('.td10 b::text').extract_first().strip()
			else:
				item = LocalResultsItem()
				if r.css('td:nth-child(2) a'):
					item["district_number"] = r.css('td:nth-child(2) a::text').extract_first().strip()
					item["candidate_type"] = "majoritarian"
				else:
					item["candidate_type"] = "list"
				fullname = r.css('td:nth-child(3) b::text').extract_first().strip()
				full_info = r.css('td:nth-child(5)::text').extract_first().strip()
				item["person_name"] = fullname
				item["nominated_by"] = nominated_by
				item["full_info"] = full_info
				item["election"] = self.elections[election_id]
				item["council"] = response.meta['council']
				item["council_type"] = response.meta['council_type']
				item["region"] = response.meta['region']
				item["result_is_elected"] = True
				yield item
		rows = table_ex.css('tr:not(:first-child)')
		for r in rows:
			if r.css('.td10small'):
				nominated_by = r.css('.td10small b::text').extract_first().strip()
			else:
				item = LocalResultsItem()
				if r.css('td:nth-child(1) a'):
					item["district_number"] = r.css('td:nth-child(1) a::text').extract_first().strip()
					item["candidate_type"] = "majoritarian"
				else:
					item["candidate_type"] = "list"
				#print(r.extract())
				fullname = r.css('td:nth-child(2) b::text').extract_first().strip()
				full_info = r.css('td:nth-child(3)::text').extract_first().strip()
				item["person_name"] = fullname
				item["nominated_by"] = nominated_by
				item["full_info"] = full_info
				item["election"] = self.elections[election_id]
				item["council"] = response.meta['council']
				item["council_type"] = response.meta['council_type']
				item["region"] = response.meta['region']
				item['comment'] = u"вибув"
				item["result_is_elected"] = True
				yield item
