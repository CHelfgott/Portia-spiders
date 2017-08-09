from __future__ import absolute_import

from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.spiders import Rule
from scrapy_splash import SplashRequest

from ..utils.spiders import BasePortiaSpider
from ..utils.starturls import FeedGenerator, FragmentGenerator
from ..utils.processors import Item, Field, Text, Number, Price, Date, Url, Image, Regex
from ..items import PortiaItem, AuditingBlackBoxModelsForIndirectInfluenceItem, AuthorItem


class PapersInfo(BasePortiaSpider):
    name = "Papers_Info"
    allowed_domains = [u'ieeexplore.ieee.org']
    start_urls = [u'http://ieeexplore.ieee.org/document/7837824/keywords',
        		  u'http://ieeexplore.ieee.org/document/7837825/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837826/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837827/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837828/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837829/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837830/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837831/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837832/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837833/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837834/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837835/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837836/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837837/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837838/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837839/keywords', 	   
        		  u'http://ieeexplore.ieee.org/document/7837840/keywords', 	   
		          u'http://ieeexplore.ieee.org/document/7837841/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837842/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837843/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837844/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837845/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837846/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837847/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837848/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837849/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837850/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837851/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837852/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837853/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837854/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837855/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837856/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837857/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837858/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837859/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837860/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837861/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837862/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837863/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837864/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837865/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837866/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837867/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837868/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837869/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837870/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837871/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837872/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837873/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837874/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837875/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837876/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837877/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837878/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837879/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837880/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837881/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837882/keywords', 	
              u'http://ieeexplore.ieee.org/document/7837883/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837884/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837885/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837886/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837887/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837888/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837889/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837890/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837891/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837892/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837893/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837894/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837895/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837896/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837897/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837898/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837899/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837900/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837901/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837902/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837903/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837904/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837905/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837906/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837907/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837908/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837909/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837910/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837911/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837912/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837913/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837914/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837915/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837916/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837917/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837918/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837919/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837920/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837921/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837922/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837923/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837924/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837925/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837926/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837927/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837928/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837929/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837930/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837931/keywords', 
              u'http://ieeexplore.ieee.org/document/7837932/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837933/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837934/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837935/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837936/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837937/keywords', 	   
              u'http://ieeexplore.ieee.org/document/7837938/keywords']
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

    def parse_item(self, response):
        paper = AuditingBlackBoxModelsForIndirectInfluenceItem()

        paper["Title"] = response.css('h1.document-title > span[ng-bind-html="vm.displayDocTitle"]::text').extract_first()
            
        kw_selector = response.selector.css('.doc-keywords-list')
        IEEE_KW_CSS = '.doc-keywords-list-item:nth-child(1)'
        AUTHOR_KW_CSS = '.doc-keywords-list-item:nth-child(4)'
        ieee_kw_selector = kw_selector.css(IEEE_KW_CSS).css('a.stats-keywords-list-item::text')
        author_kw_selector = kw_selector.css(AUTHOR_KW_CSS).css('a.stats-keywords-list-item::text')

        paper["IEEE Keywords"] = ieee_kw_selector.extract()
        paper["Author Keywords"] = author_kw_selector.extract()

        author_selector = response.selector.css('div.authors-info-container')
        author_selector = author_selector.css('span[ng-if="::author.affiliation"]')
        authors = []
        for author in author_selector:
          author_item = AuthorItem()
          author_item["Author"] = author.css('a > span[ng-bind-html="::author.name"]::text').extract_first()
          author_item["Affiliation"] = author.css('a::attr(qtip-text)').extract_first()
          authors.append(dict(author_item))

        paper["Authors"] = authors

        yield paper


    def start_requests(self):
        for url in self.start_urls:
            print('URL: ' + str(url))
            yield SplashRequest(url, self.parse_item, args={'wait': 3}, endpoint='render.html')
