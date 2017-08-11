from __future__ import absolute_import

import re

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule
from scrapy_splash import SplashRequest

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem, ConferenceTableOfContentsItem, AuthorItem


class LengthMismatch(Exception):
    def __init__(self, msg):
        self.msg = msg


    def __str__(self)
        return self.msg


class PaperUrls(BasePortiaSpider):
    name = "Paper_URLs"
    allowed_domains = [u'dl.acm.org', u'portal.acm.org', u'doi.org',
                       u'dx.doi.org', u'dblp.dagstuhl.de']
    rules = [
        Rule(
            LinkExtractor(
                allow=(),
                deny=()),
            callback='parse_item',
            follow=True)]
    start_urls = [u'http://dblp.dagstuhl.de/db/conf/icml/index.html']#,
#                  u'http://dblp.dagstuhl.de/db/conf/kdd/index.html']

    def parse_master(self, response):
        toc_selector = response.selector.css('a:contains("table of contents")' +
                                             '::attr(href)')
        title_selector = response.selector.css('span.title[itemprop="name"]' +
                                               '::text')
        if len(toc_selector) != len(title_selector):
          raise LengthMismatch(
              'Not every conference on ' + response.url +
              ' is matched with a Table of Contents link')
        proceeding_str = "Proceedings of the \w+-?\w* (Annual )?"
        proceeding_str += "International (Conference|Workshop)"
        pattern = "^" + proceeding_str + " [Oo]n Machine Learning|"
        pattern += "^Machine Learning, " + proceeding_str
        for i in range(len(title_selector)):
          title = title_selector.extract()[i]
          toc_url = toc_selector.extract()[i]
          if re.search(pattern, title):
            yield SplashRequest(toc_url, self.parse_item, args={'wait': 5},
                                endpoint='render.html')
  
  
    def parse_item(self, response):
        date_selector = response.selector.css('header.headline > h1::text')
        date = date_selector.extract_first()
        year = ""
        if date:
          date_match = re.search("\D(\d{4})\D", date)
          if date_match:
            year = date_match.group(1)
        paper_selector = response.selector.css('li.inproceedings')
        for paper in paper_selector:
          title_selector = paper.css('span.title[itemprop="name"]::text')
          url_selector = paper.css('a:contains("electronic edition")' +
                                   '::attr(href)')
          paper_item = ConferenceTableOfContentsItem()
          paper_item["Year"] = year
          title = title_selector.extract_first()
          if not title: continue
          paper_item["Paper_Title"] = title
          paper_item["Paper_URL"] = url_selector.extract_first()
  
          author_selector = paper.css('span[itemprop="author"] > a ' +
                                      '> span[itemprop="name"]::text')
          authors = []
          for author in author_selector:
            author_item = AuthorItem()
            author_item["Author"] = author.extract()
            authors.append(dict(author_item))
  
          paper_item["Authors"] = authors
          yield paper_item


    def start_requests(self):
        for url in self.start_urls:
          yield SplashRequest(url, self.parse_master,
                              args={'wait': 5}, endpoint='render.html')

