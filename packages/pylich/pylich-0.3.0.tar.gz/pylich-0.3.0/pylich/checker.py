import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class LinkChecker:
    """
    A class to check for broken links in the URLs listed in a sitemap.

    Parameters
    ----------
    sitemap_url : str
        The URL of the sitemap to be checked.
    verbose : bool, optional
        Whether to print detailed information during the link checking process.
        Default is False.
    ignored_status_codes : list of int, optional
        A list of HTTP status codes that will be ignored. Default is None.
    """

    def __init__(self, sitemap_url, verbose=False, ignored_status_codes=None):
        self.sitemap_url = sitemap_url
        self.verbose = verbose
        self.ignored_status_codes = ignored_status_codes or []
        self.urls = []
        self.dead_links = []
        self.ignored_links = []

    def get_sitemap_urls(self):
        """
        Get all URLs from the sitemap.

        Returns
        -------
        list of str
            A list of URLs found in the sitemap.

        Raises
        ------
        Exception
            If the sitemap cannot be fetched.
        """
        if self.verbose:
            print(f"Fetching sitemap from: {self.sitemap_url}")
        response = requests.get(self.sitemap_url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch sitemap: {self.sitemap_url}")

        self.urls = []
        root = ET.fromstring(response.content)
        for elem in root:
            for subelem in elem:
                if "loc" in subelem.tag:
                    self.urls.append(subelem.text)

        if self.verbose:
            print(f"Found {len(self.urls)} URLs in the sitemap.")
        return self.urls

    def check_links(self, urls):
        """
        Check all links in a list of URLs for broken links.

        Parameters
        ----------
        urls : list of str
            A list of URLs to check for broken links.

        Returns
        -------
        list of tuple
            A list of tuples containing the URL of the page, the broken
            link, and the HTTP status code of the broken link.

        Notes
        -----
        Each tuple in the returned list has the form (page_url,
        broken_link, status_code).
        """
        self.dead_links = []
        self.ignored_links = []
        total_urls = len(urls)
        for idx, url in enumerate(urls):
            if self.verbose:
                print(f"Checking URL {idx + 1}/{total_urls}: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                if response.status_code in self.ignored_status_codes:
                    self.ignored_links.append((url, url, response.status_code))
                else:
                    self.dead_links.append((url, url, response.status_code))
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not href.startswith(("http://", "https://")):
                    href = urljoin(url, href)
                link_response = requests.get(href)
                if link_response.status_code != 200:
                    if link_response.status_code in self.ignored_status_codes:
                        self.ignored_links.append(
                            (url, href, link_response.status_code)
                        )
                    else:
                        self.dead_links.append(
                            (url, href, link_response.status_code)
                        )

        if self.verbose:
            print(f"Completed checking {total_urls} URLs.")

        return self.dead_links

    def print_dead_links(self):
        """
        Print the dead links found during the checking process.
        """
        if not self.dead_links:
            print("No dead links found.")
        elif not self.urls:
            print("No URLs to check.")
        else:
            print("Dead links:\n")
            for page_url, broken_link, status_code in self.dead_links:
                print(f"Page URL: {page_url}")
                print(f"Broken Link: {broken_link}")
                print(f"Status Code: {status_code}\n")

        if self.ignored_links:
            print("Ignored links:\n")
            for page_url, broken_link, status_code in self.ignored_links:
                print(f"Page URL: {page_url}")
                print(f"Ignored Link: {broken_link}")
                print(f"Status Code: {status_code}\n")
