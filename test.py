#!/usr/bin/python

import json
import optparse

import utils


def main():
  parser = optparse.OptionParser(usage='%prog <JSON list of authors> <PDF URL>')

  opts, args = parser.parse_args()
  if len(args) < 2:
    parser.error('Please specify a list of authors and a PDF.')
  elif len(args) > 3:
    parser.error('Too many arguments.')

  author_list = json.loads(args[0])
  author_set = set()
  for author in author_list: author_set.add(author)

  pdf_url = args[1]

  author_affs = dict()
  author_affs = utils.parse_pdf_for_affs(author_set, pdf_url)
  print json.dumps(author_affs, sort_keys=True, indent=4, separators=(',', ': '))

       
if __name__ == '__main__':
    main()
