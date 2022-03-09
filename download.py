import os
import socket
import ssl
import sys
from urllib import request
import progressbar

import feedparser
from tqdm import tqdm
import argparse
import functools
import os
import pathlib
from multiprocessing.pool import ThreadPool

from tqdm import tqdm


def do_to_files(process_file_fn, podcasts, num_workers=6):
    if num_workers > 0:
        with ThreadPool(num_workers) as pool:
            list(tqdm(pool.imap(process_file_fn, podcasts), total=len(podcasts)))
    else:
        for f in tqdm(podcasts):
            process_file_fn(f)


class UrlRetrieveReporter():
    def __init__(self):
        self.pbar = None

    def __call__(self, block_num, block_size, total_size):
        if not self.pbar:
            self.pbar=progressbar.ProgressBar(maxval=total_size)
            self.pbar.start()

        downloaded = block_num * block_size
        if downloaded < total_size:
            self.pbar.update(downloaded)
        else:
            self.pbar.finish()


def process_listing(listing, output_dir):
    types = {
        'audio/mpeg': 'mp3',
        'audio/ogg': 'ogg',
        'audio/m4a': 'm4a',
        'audio/aac': 'aac',
    }
    socket.setdefaulttimeout(60)

    # Lots of these podcasts have cert errors, just ignore them.
    ssl._create_default_https_context = ssl._create_unverified_context

    try:
        feed = feedparser.parse(listing)
    except:
        print(f"Failed to retrieve {listing}, error: {sys.exc_info()}")
        return
    if 'feed' in feed.keys() and 'title' in feed['feed'].keys():
        title = feed['feed']['title']
    else:
        print(f"{listing} has no feed title, bailing.")
        return
    # sanitize title so it can be used for a filename.
    title = "".join(x for x in title if x.isalnum())
    if len(title) > 50:
        title = title[:50]
    castdir = os.path.join(output_dir, title)
    if os.path.exists(castdir) and len(list(os.listdir(castdir))) < 5:
        print(f"Skipping {castdir}: Already present.")
        return
    os.makedirs(castdir, exist_ok=True)
    for j, entry in enumerate(feed['entries']):
        if 'links' in entry.keys():
            found = False
            for link in entry['links']:
                if 'type' in link.keys() and link['type'] in types.keys():
                    ext = types[link['type']]
                    try:
                        request.urlretrieve(link['href'], os.path.join(castdir, f'{j}.{ext}'), UrlRetrieveReporter())
                    except:
                        href = link['href'] if 'href' in link.keys() else f'No link found {link}'
                        print(f"Failed to retrieve {href} for {title}, error: {sys.exc_info()}")
                    found = True
            if not found:
                print(f"Could not find audio file in links for {listing} {title} {j}")
        else:
            print(f"Could not extract links for {listing}, {title}")
    with open('finished_processing.txt', 'a') as fp:
        fp.write(f'{listing}\n')


if __name__ == '__main__':
    output_dir = '.'

    with open('processed_podcasts.txt', 'r') as f:
        listings = list(f.read().splitlines())
        do_to_files(functools.partial(process_listing, output_dir=output_dir), listings)
