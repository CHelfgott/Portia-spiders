#!/bin/bash
# Script for running scrapy spiders in succession. Requires running
# docker machine. Also run cleanup.sh first.
PAPER_URLS_FILE="Paper_URLs.json"
PAPERS_INFO_FILE="Papers_Info.json"
OUTPUT_DIR="output"
mkdir $OUTPUT_DIR
cd $OUTPUT_DIR
OUTPUT_PATH=`pwd`
cd ..
PAPER_URLS_PATH="${OUTPUT_PATH}/${PAPER_URLS_FILE}"
PAPERS_INFO_PATH="${OUTPUT_PATH}/${PAPERS_INFO_FILE}"
scrapy crawl -o "${PAPER_URLS_PATH}" Paper_URLs
scrapy crawl -o "${PAPERS_INFO_PATH}" -a "${PAPER_URLS_PATH}" Papers_Info

echo "URL output is in ${OUTPUT_DIR}/${PAPER_URLS_FILE};"
echo "Paper info output is in ${OUTPUT_DIR}/${PAPERS_INFO_FILE}
