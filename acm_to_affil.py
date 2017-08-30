#!/usr/bin/python

# Pull and Parse ACM Digital Library pages to get author affiliation.
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

import utils


def output_data(out_data):
  for conference in out_data:
    for year in out_data[conference]:
      filename = "acm-" + conference + "-" + year + ".csv"
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
  for record in in_data:
#    if record_cnt >= 15: break
    title = record["Paper_Title"]
    conference = "Conference"
    year = "Year"
    paper_url = ""
    pdf_url = ""
    if "Conference" in record: conference = record["Conference"]
    if "Year" in record: year = record["Year"]
    if "Paper_PDF" in record and (record["Paper_PDF"] and
        record["Paper_PDF"] != ""):
      continue
    elif "Paper_URL" in record and (record["Paper_URL"] and
        record["Paper_URL"] != ""):
      paper_url = record["Paper_URL"]
    if not re.search('acm\.|doi\.', paper_url): continue
    if not conference in out_data:
      out_data[conference] = dict()
    if not year in out_data[conference]:
      out_data[conference][year] = []
    if conference == "ICML" and year == "2010":
      # Paper links are incorrect
      paper_url = ""
      pdf_url = ""


