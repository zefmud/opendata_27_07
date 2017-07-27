# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from scrapy import signals
from scrapy.exporters import CsvItemExporter

class LocalResultsPipeline(object):
	date_re = re.compile('\d{2}\.\d{2}\.(\d{4})')
	
	def change_date_format(self, s):
		parts = s.split(".")
		return parts[2] + '-' + parts[1] + '-' + parts[0]
		
	def get_convocation_number(self, item):
		election_type = item['election_type']
		if item['council_type'] != 	u"Верховна Рада":
			if item['election_type'] != "midterm":
				return item['election_date'][0:4]
			else:
				return ''
		 	
	def get_election_type(self, s):
		if u"позачергові" in s.lower():
			return "irregular"
		elif u"чергові" in s.lower():
			return "regular"
		elif u"проміжні" in s.lower():
			return "midterm"
		elif u"повторні" in s.lower():
			return "repeated"
		elif u"перші" in s.lower():
			return "first"
		
	def process_item(self, item, spider):
		if (u"міськ" in item["election"]) and (u"голов" in item["election"]):
			item["council"] += u" - міський голова"
		if not 'election_date' in item.keys():
			election_date_matched = self.date_re.search(item['election'])
			item['election_date'] = self.change_date_format(election_date_matched.group(0))
		if not 'election_type' in item.keys():
			item['election_type'] = self.get_election_type(item['election'])
		if not 'birthyear' in item.keys():
			birth_date_matched = self.date_re.search(item['full_info'])
			if birth_date_matched:
				item['birth_year'] = birth_date_matched.group(1)
		if not 'party_membership' in item.keys():
			party_re = re.compile(u',\s+(безпартійн[^,]+|член[^,]+|позапартійн[^,]+),', re.UNICODE)
			party_re_matched = party_re.search(item['full_info'])
			item['party_membership'] = party_re_matched.group(1).replace(u"позапартійн", u"безпартійн")
		if not 'convocation_number' in item.keys():
			item['convocation_number'] = self.get_convocation_number(item)
		return item
		


class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    file = open('%s_items.csv' % spider.name, 'w+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = ["election", "election_type", "election_date", "council", "council_type", "convocation_number", "region", 
										"place", "person_name", "birth_year", "nominated_by", "party_membership", "candidate_type", "list_number", 
										"district_number", "district_center", "district_description", "result_is_elected", "result_percent",
										"comment", "person_id", "convocation_id", "district_id", "election_id", 'full_info']
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item
