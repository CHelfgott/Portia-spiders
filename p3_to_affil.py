#!/usr/bin/python

# Pull and Parse PDFs to get author affiliation.
# Takes in paper information in JSON format, ideally of the form
# { "Paper_Title": <title>,
#   "Paper_PDF": <url of paper>,
#   "Authors": [ { "Author": <name>,
#                  "Affiliation": <institution> },
#                { "Author": <>, "Affiliation": <> }, ...],
#   "Conference": <conference>,
#   "Year": <year> }

# It will output a sequence of CSV files, one for each (conference, year).
# The CSV files will have header (Title, Author, Affiliation,
#   Affiliation Name, Dataset, Data Type, Topic, Topic Type, Full Text);
# most of these fields will not be filled in; Full Text refers to the PDF url.

import io
import json
import optparse
import os
import re
import sys
import time

import utils

def output_data(out_data):
  for conference in out_data:
    for year in out_data[conference]:
      filename = "organized-" + conference + "-" + year + ".csv"
      print("Output file = " + filename)
      with open(filename, "w") as output_file:
        output_file.write("Title|Author|Affiliation|Affiliation Name|" +
            "Dataset|Data Type|Topic|Topic Type|Full Text\n".encode('utf-8'))
        for out_record in out_data[conference][year]:
          output_file.write(u'|'.join((out_record["Title"], 
              out_record["Author"], out_record["Affiliation"], 
              out_record["Affiliation Name"], "\"\"", "\"\"", "\"\"", "\"\"",
              out_record["Full Text"])).encode('utf-8'))
          output_file.write("\n".encode('utf-8'))


def main():
  parser = optparse.OptionParser(usage='%prog input.json')

  opts, args = parser.parse_args()
  if len(args) < 1:
    parser.error('Please specify an input JSON file.')
  elif len(args) > 2:
    parser.error('Too many arguments.')

  in_data = []
  out_data = dict()
  with io.open(args[0], "r", encoding="utf-8") as data_file:
    in_data = json.load(data_file)

  record_cnt = 0
  acm_cnt = 0
  for record in in_data:
#    if record_cnt >= 50: break
    title = record["Paper_Title"]
    conference = "Conference"
    year = "Year"
    paper_url = ""
    pdf_url = ""
    if "Conference" in record: conference = record["Conference"]
    if "Year" in record: year = record["Year"]
    if conference == "ICML" and (year == "Year" or len(year) < 4):
      year = "1991"
    if conference == "NIPS" and (year == "Year" or len(year) < 4):
      continue
    if "Paper_PDF" in record and (record["Paper_PDF"] and
        record["Paper_PDF"] != ""):
      pdf_url = record["Paper_PDF"]
      paper_url = pdf_url
    elif "Paper_URL" in record and (record["Paper_URL"] and
        record["Paper_URL"] != ""):
      paper_url = record["Paper_URL"]
    if not conference in out_data:
      out_data[conference] = dict()
    if not year in out_data[conference]:
      out_data[conference][year] = []
    if conference == "ICML" and year == "2010":
      # Paper links are incorrect
      paper_url = ""
      pdf_url = ""

    # Now to the tricky bit.
    authors_without_affs = set()
    author_affiliation = dict()
    for entry in record["Authors"]:
      author = entry["Author"].encode("ascii", "ignore")
      if "Affiliation" in entry and entry["Affiliation"] != "":
        author_affiliation[author] = entry["Affiliation"]
      else:
        authors_without_affs.add(author)
    if pdf_url != "":
#      if len(authors_without_affs) > 0: record_cnt += 1
      author_affiliation.update(
          utils.scrape_pdf_for_affs(authors_without_affs, pdf_url))
    elif paper_url != "" and re.search("acm\.|doi\.", paper_url):
      if len(authors_without_affs) > 0: record_cnt += 1
      author_affiliation.update(
          utils.scrape_acmdl_for_affs(authors_without_affs, paper_url))
      time.sleep(0.2)
      acm_cnt += 1
      print("ACM Count: " + str(acm_cnt))
      sys.stdout.flush()
    else:
      for author in authors_without_affs:
        author_affiliation[author] = ""

    for author in author_affiliation:
      out_record = dict()
      out_record["Title"] = title.encode("ascii", "ignore")
      out_record["Full Text"] = paper_url.encode("ascii")
      out_record["Author"] = author
      out_record["Affiliation Name"] = author_affiliation[author].encode(
          'ascii', 'ignore')
      out_record["Affiliation"] = utils.classify_affiliation(
          out_record["Affiliation Name"])
      out_data[conference][year].append(out_record)

  output_data(out_data)
 
       
if __name__ == '__main__':
    main()
