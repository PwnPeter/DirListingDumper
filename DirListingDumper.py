from ast import arg
from email.mime import base
import requests
from bs4 import BeautifulSoup
from threading import Thread
import pathlib
import argparse

url = "http://104.210.219.69"

PATH_TO_DOWNLOAD = "/tmp/"

banned_words = ["?C=N;O=D", "?C=M;O=A", "?C=S;O=A", "?C=D;O=A"]

to_download = []
to_scrap = []

r = requests.get(url)

soup = BeautifulSoup(r.text, "lxml")


def crawl_directory_listing(base_url, endpoint=""):

    base_url = base_url.strip("/")
    # print(f"{base_url}/{endpoint}")
    soup = BeautifulSoup(requests.get(f"{base_url}/{endpoint}").text, "lxml")
    for link in soup.find_all("a"):
        if (
            not link.get("href").endswith("/")
            and not link.get("href").startswith("/")
            and link.get("href") not in banned_words
        ):
            # download
            url_formated = format_url(f"{base_url}/{endpoint}/{link.get('href')}")
            to_download.append(url_formated)

        elif link.get("href").endswith("/") and not link.get("href").startswith("/"):
            # scrap dans le dossier
            url_formated = format_url(f"{base_url}/{endpoint}/{link.get('href')}")
            to_scrap.append(url_formated)
            # Thread(target=crawl_directory_listing, args=(url_formated,)).start()
            crawl_directory_listing(url_formated)


def format_url(url_to_format):
    url_split = url_to_format.split("http://")
    url_split[1] = url_split[1].replace("//", "/")
    url_formated = "http://".join(url_split)
    return url_formated


crawl_directory_listing(url)

host_directory = url.replace("http://", "")

host_directory = host_directory.strip("/")
PATH_TO_DOWNLOAD = PATH_TO_DOWNLOAD.rstrip("/")

for url in to_download:
    url_without_http = url.replace("http://", "")
    endpoints = url_without_http.split("/")
    directory_to_create_on_system = "/".join(endpoints[1:-1])
    file_name = endpoints[::-1][0]
    pathlib.Path(f"{PATH_TO_DOWNLOAD}/{host_directory}/{directory_to_create_on_system}").mkdir(parents=True, exist_ok=True)
    response = requests.get(url)
    print(len(response.content))
    with open(f"{PATH_TO_DOWNLOAD}/{host_directory}/{directory_to_create_on_system}/{file_name}", "wb") as f:
        f.write(response.content)
    print(
        f"{PATH_TO_DOWNLOAD}/{host_directory}/{directory_to_create_on_system}",
        file_name,
    )
