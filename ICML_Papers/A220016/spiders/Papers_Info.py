from __future__ import absolute_import

import json
import re

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.spiders import Rule
from scrapy_splash import SplashRequest

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem, PaperInfoItem, AuthorItem


class PapersInfo(BasePortiaSpider):
    name = "Papers_Info"
    allowed_domains = [u'icml.cc']

    rules = [
        Rule(
            LinkExtractor(
                allow=(),
                deny=('.*')
            ),
            callback='parse_item',
            follow=True
        )
    ]
    start_urls = [u'http://icml.cc/2016/?page_id=1649']


    def parse_item(self, response):
        papers_selector = response.selector.css('div[id="schedule"] > ul > li')
        for paper_selector in papers_selector:
          paper = PaperInfoItem()
          paper["Paper_Title"] = paper_selector.css(
              'span.titlepaper > a[href="#"]::text').extract_first()
          if not paper["Title"]: continue
          authors_selector = paper_selector.css('span.authors')
          authors = []
          author_list = authors_selector.extract_first().split(">,")
          for author in author_list:
            author_item = AuthorItem()
            author_and_affil = re.search('(^.*>\s*|^\s*)(.*)\s+<i>(.*?)</i',
                                         author)
            if not author_and_affil: continue
            author_item["Author"] = author_and_affil.group(2)
            author_item["Affiliation"] = author_and_affil.group(3)
            authors.append(dict(author_item))

          paper["Authors"] = authors

          yield paper


    def start_requests(self):
        for url in self.start_urls:
            print('URL: ' + str(url))
            yield SplashRequest(url, self.parse_item, args={'wait': 3},
                                endpoint='render.html')
