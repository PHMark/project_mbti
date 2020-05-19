# -*- coding: utf-8 -*-

import scrapy
from scrapy import Field
from scrapy.loader.processors import TakeFirst, MapCompose


class PersonaliticsItem(scrapy.Item):
	# Main fields
	topic = Field()
	user_id = Field(output_processor=MapCompose(lambda x: x.strip('/profiles/').strip()))
	user_type = Field(output_processor=MapCompose(lambda x: x.strip()))
	parent_text = Field(output_processor=MapCompose(lambda x: x.strip())) 
	child_text = Field(output_processor=MapCompose(lambda x: x.strip()))
	date = Field()

	# Housekeeping fields
	source = Field()
	project = Field()
	spider = Field()
	server = Field()
	created_at = Field(output_processor=TakeFirst())


