This Scrapy project is designed to scrape a single year of conference paper data from the IEEE website.  To do so, go to A220016, and change the start_urls parameter to the list of index pages for that conference*.  Then run "cleanup.sh" followed by "run.sh". This will create an "output" directory, run the Paper_URLs spider, and then run the Papers_Info spider.  The first grabs [Paper Title, Paper URL] and sticks it in Paper_URLs.json in that directory, the second goes to each paper URL and grabs [Paper Title, Author, Author Affiliation, IEEE Keywords, Author Keywords] (as a nested json structure) and stores it in Papers_Info.json.

Caveat: Some papers do not have an "HTML" field in the conference listing.  This will cause them to be missing the Paper_URL field in the Paper_URLs output, and will cause them not to get scraped by the followup Papers_Info spider. To avoid this, instead of running run.sh, type in each line from that file individually, and after the first "scrapy crawl", do some QA on the Paper_URLs output.  Then run the second "scrapy crawl" on the modified file.


*In theory, Scrapy supports following next arrow links.  In practice, this can be a pain, and it may just be easier to list them by hand.


