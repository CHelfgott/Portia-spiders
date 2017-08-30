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

    def __str__(self):
        return self.msg


class ConferenceMismatch(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class SourceUnsupported(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

class PaperUrls(BasePortiaSpider):
    name = "Paper_URLs"
    allowed_domains = [u'dl.acm.org', u'portal.acm.org', u'doi.org',
                       u'dx.doi.org', u'dblp.dagstuhl.de', u'jmlr.org',
                       u'proceedings.mlr.press', u'www.aaai.org', 
                       u'papers.nips.cc']
    rules = [
        Rule(
            LinkExtractor(
                allow=(),
                deny=()),
            callback='parse_item',
            follow=True)]
    start_urls = [u'http://dblp.dagstuhl.de/db/conf/icml/index.html',
                  u'http://dblp.dagstuhl.de/db/conf/kdd/index.html',
                  u'http://dblp.dagstuhl.de/db/conf/nips/index.html']

    def parse_master(self, response):
        toc_selector = response.selector.css('a:contains("table of contents")' +
                                             '::attr(href)')
        title_selector = response.selector.css('span.title[itemprop="name"]' +
                                               '::text')
        if len(toc_selector) != len(title_selector):
          raise LengthMismatch(
              'Not every conference on ' + response.url +
              ' is matched with a Table of Contents link')

        conference = ""
        proceeding_pattern = ""
        if re.search("kdd", response.url, re.IGNORECASE):
          conference = "SIGKDD"
          # The following pattern will explicitly exclude the "Tutorial Notes"
          # accompanying the SIGKDD Proceedings in 1999 and 2001
          proc_str = "Knowledge [Dd]iscovery and [Dd]ata [Mm]ining"
          proceeding_pattern = "^Proceedings .* " + proc_str + "|"
          proceeding_pattern += "^The \w+-?\w* ACM SIGKDD [Ii]nternational "
          proceeding_pattern += "[Cc]onference [Oo]n " + proc_str
        elif re.search("icml", response.url, re.IGNORECASE):
          conference = "ICML"
          # We need to special-case ICML 1991, because the proceedings title
          # says nothing about "Machine Learning".
          proc_str = "Proceedings of the \w+-?\w* (Annual )?"
          proc_str += "International (Conference|Workshop)"
          proceeding_pattern = "^" + proc_str + " [Oo]n Machine Learning|"
          proceeding_pattern += "^Machine Learning, " + proc_str + "|ML91"
        elif re.search("nips", response.url, re.IGNORECASE):
          # Excluding co-located workshops and symposiums.
          conference = "NIPS"
          proceeding_pattern = "(?!co-located with).*Neural Information "
          proceeding_pattern += "Processing Systems.*(?!Symposium)"
        else:
          raise ConferenceMismatch(
              'The URL we requested ' + response.url + ' does not match ' +
              'any conference (SIGKDD, ICML, NIPS) that we are interested in.')

        for i in range(len(title_selector)):
          title = title_selector.extract()[i]
          self.logger.info('Checking conference title: %s', title)
          toc_url = toc_selector.extract()[i]
          if re.search(proceeding_pattern, title):
            self.logger.info('Conference matches.')
            yield Request(toc_url, self.parse_item,
                meta={
                    'splash': {
                        'args': { 'wait': 5 },
                        'endpoint': 'render.html'
                    },
                    'conference': conference
                })


    def parse_item(self, response):
        conference = response.meta['conference']
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
          paper_item["Conference"] = conference
          title = title_selector.extract_first()
          if not title: continue
          paper_item["Paper_Title"] = title
          paper_url = url_selector.extract_first()
          paper_item["Paper_URL"] = paper_url

          author_selector = paper.css('span[itemprop="author"] > a ' +
                                      '> span[itemprop="name"]::text')
          authors = []
          for author in author_selector:
            author_item = AuthorItem()
            author_item["Author"] = author.extract()
            authors.append(dict(author_item))
  
          paper_item["Authors"] = authors

          paper_item["Paper_PDF"] = ""
          secondary_src = None
          if paper_url:
            extension = paper_url.split(".")[-1]
            if extension == "pdf":
              paper_item["Paper_PDF"] = paper_url
            elif extension == "php":
              # We're looking at the AAAI Library then, very easy parse
              secondary_src = "AAAI"
            elif extension == "html":
              # We're looking at the JMLR website, don't even need to parse
              # except for latest year.
              if re.search("jmlr\.org", paper_url) and year != "2017":
                paper_item["Paper_PDF"] = re.sub(
                    "jmlr\.org/proceedings/papers(.*)\.html",
                    "proceedings.mlr.press\\1.pdf",
                    paper_url)
              else:
                secondary_src = "JMLR"
            elif conference == "NIPS":
              # NIPS is very easy.
              paper_item["Paper_PDF"] = paper_url + ".pdf"
            # Otherwise it's probably an ACM Digital Library paper, skip it.
            # (ACM is very anti-scraping.)

          if secondary_src:
            yield Request(paper_url, self.parse_pdf,
                meta={
                    'splash': {
                        'args': { 'wait': 5 },
                        'endpoint': 'render.html'
                    },
                    'secondary_source': secondary_src,
                    'paper_item': paper_item
                })
          else:
            yield paper_item


    def parse_pdf(self, response):
        secondary_src = response.meta['secondary_source']
        paper_item = response.meta['paper_item']
        if secondary_src == "AAAI":
          paper_item["Paper_PDF"] = response.urljoin(response.selector.css(
              'h1 > a::attr(href)').extract_first())
        elif secondary_src == "JMLR":
          paper_item["Paper_PDF"] = response.urljoin(response.selector.css(
              'meta[name="citation_pdf_url"]::attr(content)').extract_first())
        elif secondary_src == "NIPS":
          paper_item["Paper_PDF"] = response.urljoin(response.selector.css(
              'a:contains("[PDF]")::attr(href)').extract_first())
        else:
          raise SourceUnsupported('%s is not supported as a secondary scraping '
              + 'source.', secondary_src)
        yield paper_item


    def start_requests(self):
        for url in self.start_urls:
          yield SplashRequest(url, self.parse_master,
                              args={'wait': 5}, endpoint='render.html')

