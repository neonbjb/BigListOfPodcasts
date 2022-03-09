# BigListOfPodcasts
A list of podcast URLs scraped from the Apple podcast database in late 2021, including a script for downloading those podcasts.

I've included a script that will download all these podcasts, which is basically impossible because they would consume somewhere around 1PB of data. Instead, you can download the podcasts in chunks, and process those chunks individually (as I have done).

Usage:

1.  Edit download.py, change `num_workers=6` to however many concurrent downloads you want to use. There is pretty much no upper bound other than your connection speed.
2.  Change `output_dir=` to wherever you want to download the podcasts to.
3.  `python download.py` and watch your disk fill up.

Enjoy!
