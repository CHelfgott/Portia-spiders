#!/usr/bin/python

import glob
import io
import os
import re

import utils

def main():

  for csvfile in glob.glob("*.csv"):
    record_holder = dict()
    old_file = os.path.join("./tmp_output/", csvfile)
    output_file = os.path.join("./merged_output/", csvfile)
    with open(output_file, "w") as output_handle:
      with io.open(old_file, "r", encoding="utf-8") as input_handle:
        for record in input_handle:
          parsed_record = record.split("|")
          if parsed_record[0] == "Title":
            output_handle.write(record.encode('utf-8'))
            continue
          title = parsed_record[0]
          author = parsed_record[1]
          if not title in record_holder:
            record_holder[title] = dict()
          record_holder[title][author] = parsed_record
      with io.open(csvfile, "r", encoding="utf-8") as input_handle:
        for record in input_handle:
          parsed_record = record.split("|")
          if parsed_record[0] == "Title":
            continue
          if len(parsed_record) > 9:
            print("Extra |s: " + record)
          title = parsed_record[0]
          author = parsed_record[1]
          if title in record_holder and author in record_holder[title]:
            old_record = record_holder[title][author]
            new_affil = parsed_record[3]
            new_aff_type = parsed_record[2]
            if new_aff_type == "Unknown":
              if old_record[2] != "Unknown":
                parsed_record[3] = old_record[3]
                parsed_record[2] = utils.classify_affiliation(old_record[3])
              elif len(new_affil) < 5 and len(old_record[3]) >= 5:
                parsed_record[3] = old_record[3]
                parsed_record[2] = utils.classify_affiliation(old_record[3])
            else:
              parsed_record[2] = utils.classify_affiliation(new_affil)
          else:
            affil = parsed_record[3]
            parsed_record[2] = utils.classify_affiliation(affil)
          reprocessed_record = u'|'.join(parsed_record)
          output_handle.write(reprocessed_record.encode('utf-8'))



if __name__ == '__main__':
    main()
