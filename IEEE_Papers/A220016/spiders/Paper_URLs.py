from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity
from scrapy.spiders import Rule
from scrapy_splash import SplashRequest

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem, IeeeXploreConferenceTableOfContentsItem


class PaperUrls(BasePortiaSpider):
    name = "Paper_URLs"
    allowed_domains = [u'ieeexplore.ieee.org']
    start_urls = [
        u'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=7373198',
        u'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=7373198&filter%3DAND%28p_IS_Number%3A7373293%29&pageNumber=2',
        u'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=7373198&filter%3DAND%28p_IS_Number%3A7373293%29&pageNumber=3',
        u'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=7373198&filter%3DAND%28p_IS_Number%3A7373293%29&pageNumber=4',
        u'http://ieeexplore.ieee.org/xpl/mostRecentIssue.jsp?punumber=7373198&filter%3DAND%28p_IS_Number%3A7373293%29&pageNumber=5']
    rules = [
        Rule(
            LinkExtractor(
                allow=(),
                deny=()),
            callback='parse_item',
            follow=True)]

    def parse_item(self, response):
      paper_selector = response.selector.css(
          '.results > li:nth-child(n) > .txt')
      for paper in paper_selector:
        paper_item = IeeeXploreConferenceTableOfContentsItem()
        title = paper.css('h3 > .art-abs-url > span *::text').extract_first()
        if not title: continue
        paper_item['Paper_Title'] = title
        paper_item['Paper_URL'] = response.urljoin(
            paper.css('h3 > .art-abs-url::attr(href)').extract_first())
        yield paper_item


    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_item, args={'wait': 3},
                                endpoint='render.html')

