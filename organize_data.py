#!usr/bin/python

# This script takes in a JSON file which will be an array of records; each record will
# ideally be of the form
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

import json
import optparse
import re
import sys

import constants

# Script expects an JSON input file as argument.
options = Options()
parser = optparse.OptionParser(usage='%prog input.json')
options.add_to_option_parser(parser)

opts, args = parser.parse_args()
if len(args) < 1:
  parser.error('Please specify an input JSON file.')
elif len(args) > 2:
  parser.error('Too many arguments.')

in_data = []
out_data = dict()
unknown_cnt = 0
with open(sys.argv[1]) as data_file:
  in_data = json.load(data_file)
for record in in_data:
  title = record["Paper_Title"]
  conference = "Conference"
  year = "Year"
  paper_url = ""
  if "Conference" in record: conference = record["Conference"]
  if "Year" in record: year = record["Year"]
  if "Paper_PDF" in record and (record["Paper_PDF"] and
      record["Paper_PDF"] != ""):
    paper_url = record["Paper_PDF"]
  elif "Paper_URL" in record and (record["Paper_URL"] and
      record["Paper_URL"] != ""):
    paper_url = record["Paper_URL"]
  if not conference in out_data:
    out_data[conference] = dict()
  if not year in out_data[conference]:
    out_data[conference][year] = []
  for author in record["Authors"]:
    out_record = dict()
    out_record["Title"] = title
    out_record["Full Text"] = paper_url
    out_record["Author"] = author["Author"]
    out_record["Affiliation Name"] = ""
    out_record["Affiliation"] = ""
    if "Affiliation" in author and author["Affiliation"] != "":
      out_record["Affiliation Name"] = author["Affiliation"]
      found_kw = False
      for kw in constants.ACADEMIC_KWS:
        if re.search(kw, author["Affiliation"]):
          found_kw = True
          out_record["Affiliation"] = "University"
          break
      if not found_kw:
        for kw in constants.INDUSTRY_KWS:
          if re.search(kw, author["Affiliation"]):
            found_kw = True
            out_record["Affiliation"] = "Internet"
            break
      if not found_kw:
        print("Cannot classify affiliation: " + author["Affiliation"])
        out_record["Affiliation"] = "Unknown"
        unknown_cnt += 1
    out_data[conference][year].append(out_record)

print(str(unknown_cnt) + " unknown affiliations.")

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

