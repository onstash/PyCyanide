"""Script to download Cyanide & Happiness comics."""
__author__ = "Santosh Venkatraman<santosh.venk@gmail.com>"
from os import path, getcwd, mkdir, makedirs
import sys
import time
import logging
from PIL import Image
from StringIO import StringIO
from argparse import ArgumentParser

from dateutil.parser import parse as date_parse
from lxml.etree import HTML
from requests import get
from requests.exceptions import ReadTimeout, ConnectionError, \
    ConnectTimeout


COMICS_DIR = path.join(getcwd(), "comics")
if not path.exists(COMICS_DIR):
    try:
        mkdir(COMICS_DIR)
    except BaseException:
        makedirs(COMICS_DIR)


def get_tree(url):
    """Helper method to get Tree of the url provided."""
    try:
        return HTML(get(url, timeout=3).content)
    except (ReadTimeout, ConnectTimeout, ConnectionError) as error:        
        logging.error(error)


def fetch_data(url):
    """Helper method to fetch data from url."""
    page_tree = get_tree(url)
    if page_tree is None:
        return
    image_link = page_tree.xpath("//img[@id='main-comic']/@src")[0]
    image_link = "http:{}".format(image_link) \
        if image_link.startswith("//") else \
        image_link
    permalink = page_tree.xpath("//input[@id='permalink']/@value")[0]
    date = \
        page_tree.xpath("//div[@class='meta-data']/div/h3/a/text()")[0]
    date = date_parse(date)
    author = page_tree.xpath(
        "//small[@class='author-credit-name']/text()"
    )[0].strip("by ")
    comic_number = permalink.strip("/").split("/")[-1]
    return {
        "number": comic_number,
        "image": image_link,
        "permalink": permalink,
        "metadata": {
            "date": (date.year, date.month, date.day),
            "author": author
        }
    }


def generate_comic_link(number):
    """Helper method to generate comic link based on number."""
    return "http://explosm.net/comics/{number}".format(**locals())


def process_comic(url):
    download_comic(fetch_data(url))


def download_comic(data):
    """Helper method to download comic from source to destination."""
    if not data:
        return
    date = data.get("metadata").get("date")
    destination = path.join(COMICS_DIR,
                            str(date[0]),
                            str(date[1]),
                            str(date[2]))
    if not path.exists(destination):
        makedirs(destination)
    destination = \
        path.join(destination, "{}.png".format(data.get("number")))
    if path.exists(destination):
        print("Already downloaded comic - {destination}".format(
            **locals())
        )
        return
    response = get(data.get("image"), stream=True)
    Image.open(StringIO(response.content)).save(destination)
    print("Downloaded comic - {destination}".format(**locals()))


def fetch_latest_comic():
    """Helper method to fetch latest comic id."""
    base_url = "http://explosm.net/comics/latest"
    root_page = fetch_data(base_url)
    if not root_page:
        sys.exit("Internet connection is ded!")
    return int(root_page.get("number"))


def generate_limits(arguments):
    """Helper method to generate limits based on arguments."""
    return arguments.start or fetch_latest_comic(), arguments.end or 0


def process_all_links(links):
    """Helper method to process links."""
    error_links = []
    for url in comic_links:
        try:
            process_comic(url)
        except KeyboardInterrupt:
            sys.exit()
        except BaseException:
            error_links.append(url)

    if error_links:
        process_all_links(error_links)


if __name__ == '__main__':
    argument_parser = ArgumentParser()
    argument_parser.add_argument("-s", "--start", type=int,
        help="Indicate starting comic number for crawling")
    argument_parser.add_argument("-e", "--end", type=int,
        help="Indicate ending comic number for crawling")
    arguments = argument_parser.parse_args()
    start, stop = generate_limits(arguments)
    comic_links = map(generate_comic_link, xrange(start, stop, -1))
    process_all_links(comic_links)
