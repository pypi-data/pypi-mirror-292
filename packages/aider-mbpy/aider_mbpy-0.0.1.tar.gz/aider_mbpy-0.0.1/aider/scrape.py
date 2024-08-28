#!/usr/bin/env python

import re
import sys

import pypandoc

from aider import __version__, urls
from aider.dump import dump  # noqa: F401

aider_user_agent = f"Aider/{__version__} +{urls.website}"


class Scraper:
    pandoc_available = None

    # Public API...
    def __init__(self, print_error=None, verify_ssl=True):
        """
        `print_error` - a function to call to print error/debug info.
        `verify_ssl` - if False, disable SSL certificate verification when scraping.
        """
        if print_error:
            self.print_error = print_error
        else:
            self.print_error = print

        self.verify_ssl = verify_ssl

    def scrape(self, url):
        """
        Scrape a url and turn it into readable markdown.

        `url` - the URLto scrape.
        """

        content = self.scrape_with_httpx(url)

        if not content:
            self.print_error(f"Failed to retrieve content from {url}")
            return None

        self.try_pandoc()

        content = self.html_to_markdown(content)

        return content

    # Internals...
    def scrape_with_httpx(self, url):
        import httpx

        headers = {"User-Agent": f"Mozilla./5.0 ({aider_user_agent})"}
        try:
            with httpx.Client(headers=headers, verify=self.verify_ssl) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as http_err:
            self.print_error(f"HTTP error occurred: {http_err}")
        except Exception as err:
            self.print_error(f"An error occurred: {err}")
        return None

    def try_pandoc(self):
        if self.pandoc_available:
            return

        try:
            pypandoc.get_pandoc_version()
            self.pandoc_available = True
            return
        except OSError:
            pass

        try:
            pypandoc.download_pandoc(delete_installer=True)
        except Exception as err:
            self.print_error(f"Unable to install pandoc: {err}")
            return

        self.pandoc_available = True

    def html_to_markdown(self, page_source):
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(page_source, "html.parser")
        soup = slimdown_html(soup)
        page_source = str(soup)

        if not self.pandoc_available:
            return page_source

        md = pypandoc.convert_text(page_source, "markdown", format="html")

        md = re.sub(r"</div>", "      ", md)
        md = re.sub(r"<div>", "     ", md)

        md = re.sub(r"\n\s*\n", "\n\n", md)

        return md


def slimdown_html(soup):
    for svg in soup.find_all("svg"):
        svg.decompose()

    if soup.img:
        soup.img.decompose()

    for tag in soup.find_all(href=lambda x: x and x.startswith("data:")):
        tag.decompose()

    for tag in soup.find_all(src=lambda x: x and x.startswith("data:")):
        tag.decompose()

    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr != "href":
                tag.attrs.pop(attr, None)

    return soup


def main(url):
    scraper = Scraper()
    content = scraper.scrape(url)
    print(content)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python playw.py <URL>")
        sys.exit(1)
    main(sys.argv[1])
