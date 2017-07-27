# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LocalResultsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    person_name = scrapy.Field()
    nominated_by = scrapy.Field()
    full_info = scrapy.Field()
    list_number = scrapy.Field()
    district_number = scrapy.Field()
    region = scrapy.Field()
    council = scrapy.Field()
    council_type = scrapy.Field()
    birth_year = scrapy.Field()
    party_membership = scrapy.Field()
    election = scrapy.Field()
    election_date = scrapy.Field()
    election_type = scrapy.Field()
    convocation_number = scrapy.Field()
    candidate_type = scrapy.Field()
    person_id = scrapy.Field()
    convocation_id = scrapy.Field()
    district_id = scrapy.Field()
    election_id = scrapy.Field()
    place = scrapy.Field()
    result_is_elected = scrapy.Field()
    result_percent = scrapy.Field()
    comment = scrapy.Field()
    district_center = scrapy.Field()
    district_description = scrapy.Field()


