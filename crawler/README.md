# Know Yourself India Crawler

## How to Use

1. Run crawler.py. This generates a list of all the list names that are associated with Igbo. It does this by recursively requesting all the lists and subcategories inside the page "Category:Igbo" and then does the same thing to all subcategories within that page and so on and so forth.

The output of crawler.py is saved within ```database.json```.

2. Run loader.py.

This script downloads all the mentioned pages in ```database.json``` in sections, so that we can easily isolate and remove useless sections as well as get the critical information, like the tables or lists easily.

Note: this program tends to crash and it has almost never gotten all the URLs saved. 

The output of loader.py is saved in ```tables.json```, so named because primarily we want tables with information saved here.

3. Run cleanse.py

This script just goes through every record saved inside ```table.json``` and cleans it up.

It removes References links, edit boxes, citation superscripts, and fixes most (if not all) links so they point to Wikipedia correctly.
