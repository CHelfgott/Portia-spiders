from __future__ import absolute_import

import json

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
    allowed_domains = [u'ieeexplore.ieee.org']

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

    def __init__(self, start_urls_path='', *args, **kwargs):
        super(PapersInfo, self).__init__(*args, **kwargs)
        self.start_urls = []
        if not start_urls_path:
          return
        with open(start_urls_path) as url_file:
          urls = json.load(url_file)
          for record in urls:
            if 'Paper_URL' in record:
              self.start_urls.append(record['Paper_URL'] + u'keywords')


    def parse_item(self, response):
        paper = PaperInfoItem()

        paper["Paper_Title"] = response.css('h1.document-title > ' +
            'span[ng-bind-html="vm.displayDocTitle"]::text').extract_first()
            
        kw_selector = response.selector.css('.doc-keywords-list')
        IEEE_KW_CSS = '.doc-keywords-list-item:nth-child(1)'
        AUTHOR_KW_CSS = '.doc-keywords-list-item:nth-child(4)'
        ieee_kw_selector = kw_selector.css(IEEE_KW_CSS).css(
            'a.stats-keywords-list-item::text')
        author_kw_selector = kw_selector.css(AUTHOR_KW_CSS).css(
            'a.stats-keywords-list-item::text')

        paper["IEEE Keywords"] = ieee_kw_selector.extract()
        paper["Author Keywords"] = author_kw_selector.extract()

        author_selector = response.selector.css('div.authors-info-container')
        author_selector = author_selector.css(
            'span[ng-if="::author.affiliation"]')
        authors = []
        for author in author_selector:
          author_item = AuthorItem()
          author_item["Author"] = author.css(
              'a > span[ng-bind-html="::author.name"]::text').extract_first()
          author_item["Affiliation"] = author.css(
              'a::attr(qtip-text)').extract_first()
          authors.append(dict(author_item))

        paper["Authors"] = authors

        yield paper


    def start_requests(self):
        for url in self.start_urls:
            print('URL: ' + str(url))
            yield SplashRequest(url, self.parse_item, args={'wait': 3},
                                endpoint='render.html')
