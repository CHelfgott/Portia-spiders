import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile

from fuzzywuzzy import fuzz, process
from lxml import etree as ET
from xml.sax.saxutils import quoteattr

import constants

FUZZY_MATCH_CUTOFF = 50
MAX_AFFIL_LINES = 5
MIN_AFFIL_CHARS = 50
CLEANUP = True


def clean_string(input_string):
  tmp_string = input_string.decode("utf-8", "replace")
  # Clean up whitespace and linebreaks.
  cleaned = re.sub('[\s\n]+', ' ', tmp_string.encode("ascii", "ignore"))
  # Fix broken email addresses
  return re.sub('\s*@\s*', '@', cleaned)


def parse_etree_for_affs(etree_nodes, author_set):
  affs = dict()
  for author in author_set:
    affs[author] = ""
  last_font = "-1"
  collected_str = ""
  matching_authors = []
  num_author_chars = 0
  num_lines = 0
  # Overall logic: We expect title to be in font "0", author to be in
  # font "1", and affiliation to be in font "2".  So we collect all text
  # in a contiguous font; if it is font "1", try to match it to author
  # names.  If it is font "2", immediately after font "1", grab the first N
  # lines as affiliation.  If font "1" is overly long, assume the affiliation
  # was written in the same font as the author names; if the text in any font 
  # is very short (<4 characters), assume it is a missed OCR and do not change
  # font state.  If we hit "Abstract", we've gone too far.
  for node in etree_nodes:
    font = node.get("font")
    if not font: continue
    current_str = ET.tostring(node, method="text", encoding="utf-8")
    if re.search("^Abstract", current_str): break
    # Sometimes the string is just a bunch of punctuation or digits.
    # Leave that out.
    if re.search("^[0-9\s,\+\?\*&\[\]\(\)]*$", current_str):
      continue
    # We sometimes have issues where e.g. an author's middle initial is
    # OCRed as being in a different font from the rest of the name.
    # Since we do not expect any discrete piece of author / affiliation
    # information to be less than 4 characters, this should handle that
    # case without causing further issues (N.B. Things like "MIT"
    # generally get OCRed with a space before or after, and usually a comma.)
    if len(current_str) < 4:
      collected_str += current_str
      continue
    if font == last_font:
      collected_str += current_str
      cleaned_str = clean_string(collected_str)
      num_lines += 1
      # Affiliation font size, hopefully
      if font == "2" and len(matching_authors) > 0:
        if num_lines == MAX_AFFIL_LINES:
          for author in matching_authors:
            affs[author] = cleaned_str
          matching_authors = []
          num_author_chars = 0
    else:
      cleaned_str = clean_string(collected_str)
      if last_font == "1":   # Author font size
        results = process.extract(cleaned_str, author_set)
        for match in results:
          if match[1] > FUZZY_MATCH_CUTOFF:
            matching_authors.append(match[0])
            author_set.discard(match[0])
            num_author_chars += len(match[0]) + 1
        # It's possible that the affiliation is in the same font as the author
        # name (or at least that the two fonts have OCR'ed the same). If so,
        # we can hope that the number of characters in that font is more
        # than the length of the authors names + the constant we've set.
        if len(cleaned_str) >= (num_author_chars + MIN_AFFIL_CHARS):
          for author in matching_authors:
            affs[author] = cleaned_str
          matching_authors = []
          num_author_chars = 0
      elif last_font == "2":
        for author in matching_authors:
          affs[author] = cleaned_str
        matching_authors = []
        num_author_chars = 0
      collected_str = current_str
      num_lines = 1
    last_font = font

  for author in matching_authors:
    affs[author] = clean_string(collected_str)

  return affs


def scrape_pdf_for_affs(author_set, pdf_url):
  # Default cases
  if len(author_set) == 0: return dict()
  author_affs = dict()
  for author in author_set:
    author_affs[author] = ""
  if not pdf_url or pdf_url == "":
    return author_affs

  # Download the PDF and convert to XML and parse.
  tmpdir = tempfile.mkdtemp(prefix='pdf2xml-')
  pdfname = pdf_url.split("/")[-1]
  pdf_path = os.path.join(tmpdir, pdfname)
  if not os.path.exists(pdf_path):
    r = requests.get(pdf_url)
    if r.status_code != 200:
      print("Error " + str(r.status_code) + ": PDF not found at " + pdf_url)
      return author_affs
    with open(pdf_path, "wb") as pdf_file:
      pdf_file.write(r.content)
  try:
    xml_path = os.path.join(tmpdir, 'output')
    cmd = "pdftohtml -c -i -l 1 -hidden -noframes -xml " + pdf_path + " " + xml_path
    subprocess.check_call(cmd, shell=True)

    xml_file = xml_path + ".xml"
    tree = ET.parse(xml_file)
    root = tree.getroot()
    if root.tag != "pdf2xml":
      raise Error('Expected a pdf2xml document, got %s' % root.tag)
      return author_affs

    page = tree.find('page')
    text_nodes = page.findall('text')

    author_affs = parse_etree_for_affs(text_nodes, author_set)

  finally:
    if CLEANUP: shutil.rmtree(tmpdir)
    return author_affs


def scrape_acmdl_for_affs(author_set, paper_url):
  # Default cases
  if len(author_set) == 0: return dict()
  author_affs = dict()
  for author in author_set:
    author_affs[author] = ""
  if not paper_url or paper_url == "":
    return author_affs

  # Pull out the DOI reference number.
  doi_ref = re.search('(\d+\.\d+)$', paper_url)
  if not doi_ref: return author_affs
  acm_url = "http://dl.acm.org/citation.cfm?id={0}&preflayout=flat".format(
      doi_ref.group(1))

  tmpdir = tempfile.mkdtemp(prefix='acm_dl-')
  htmlname = doi_ref.group(1) + ".html"
  html_path = os.path.join(tmpdir, htmlname)
  if not os.path.exists(html_path):
    try:
      with open(html_path, "wb") as html_file:
        r = requests.get(acm_url, headers=constants.HEADERS)
        if r.status_code != 200:
          print("Error " + str(r.status_code) + ": page not accessible at "
                + acm_url)
        html_file.write(r.content)
    except:
      print("Could not get " + acm_url)
  try:
    with open(html_path, "r") as html_file:
      parser= ET.HTMLParser()
      tree = ET.parse(html_file, parser)
      root = tree.getroot()

      table_nodes = root.findall(".//table[@class='medium-text']")
      cnt = 0
      for table_node in table_nodes:
        cnt += 1
        table_name_node = table_node.xpath("tr/td")
        if len(table_name_node) == 0: continue
        if not re.search("Authors?:",
            ET.tostring(table_name_node[0], method="text", encoding="utf-8")):
          continue
        current_author = ""
        link_nodes = table_node.findall('.//a[@title]')
        for link_node in link_nodes:
          if link_node.get("title") == "Author Profile Page":
            current_author = clean_string(ET.tostring(link_node, method="text",
                encoding="utf-8"))
          if (link_node.get("title") == "Institutional Profile Page" and
              current_author != ""):
            affiliation = clean_string(ET.tostring(link_node, method="text",
                encoding="utf-8"))
            results = process.extract(current_author, author_set)
            for match in results:
              if match[1] > FUZZY_MATCH_CUTOFF:
                author_set.discard(match[0])
                author_affs[match[0]] = affiliation
          if len(author_set) == 0: break
        if len(author_set) == 0: break

  finally:
    if CLEANUP: shutil.rmtree(tmpdir)
    return author_affs      


def classify_affiliation(affiliation):
  if affiliation == "" or not affiliation:
    return "Unknown"
  affils = ["Unknown", "University", "Internet", "Both"]
  aff_idx = 0
  for kw in constants.ACADEMIC_KWS:
    if re.search(kw, affiliation): aff_idx |= 1
  for kw in constants.INDUSTRY_KWS:
    if re.search(kw, affiliation): aff_idx |= 2
  if aff_idx == 0:
    print("Cannot classify affiliation: " + affiliation)
  return affils[aff_idx]


