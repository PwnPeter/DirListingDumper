import requests
from bs4 import BeautifulSoup
import pathlib
import argparse
from concurrent.futures import ThreadPoolExecutor
import time

banned_words = ["?C=N;O=D", "?C=M;O=A", "?C=S;O=A", "?C=D;O=A"]
to_download = []
to_scrap = []
threads_list = []
download_failed = []


class bcolors:
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    GREYBG = "\33[100m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    CYELLOW = "\33[33m"
    REDBG = "\33[101m"


def crawl_directory_listing(base_url, endpoint=""):

    base_url = base_url.strip("/")
    # print(f"{base_url}/{endpoint}")
    soup = BeautifulSoup(requests.get(f"{base_url}/{endpoint}").text, "lxml")
    for link in soup.find_all("a"):
        if (not link.get("href").endswith("/")
                and not link.get("href").startswith("/")
                and link.get("href") not in banned_words):
            # download
            url_formated = format_url(
                f"{base_url}/{endpoint}/{link.get('href')}")
            to_download.append(url_formated)

        elif link.get("href").endswith(
                "/") and not link.get("href").startswith("/"):
            # scrap dans le dossier
            url_formated = format_url(
                f"{base_url}/{endpoint}/{link.get('href')}")
            to_scrap.append(url_formated)
            # Thread(target=crawl_directory_listing, args=(url_formated,)).start()
            crawl_directory_listing(url_formated)


def download_files(url):
    url_without_http = url.replace("http://", "")
    endpoints = url_without_http.split("/")
    directory_to_create_on_system = "/".join(endpoints[1:-1])
    file_name = endpoints[::-1][0]
    pathlib.Path(
        f"{system_path}/{host_directory}/{directory_to_create_on_system}"
    ).mkdir(parents=True, exist_ok=True)
    i = 0
    while i <= 4:
        try:
            response = requests.get(url)
        except Exception as e:
            i += 1
            print(
                f"{bcolors.OKBLUE}[❌]{bcolors.ENDC} {bcolors.CYELLOW}{system_path}/{host_directory}/{directory_to_create_on_system}/{bcolors.ENDC}{bcolors.BOLD}{bcolors.OKBLUE}{file_name}{bcolors.ENDC}"
                .replace("//", "/"))
            continue

        if response.status_code == 200:
            with open(
                    f"{system_path}/{host_directory}/{directory_to_create_on_system}/{file_name}",
                    "wb") as f:
                f.write(response.content)
            len_content = len(response.content)
            if len_content < 100000:
                len_str = f"{len_content/1000} KB"
            else:
                len_str = f"{len_content/1000000} MB"
            print(
                f"{bcolors.OKBLUE}[📥]{bcolors.ENDC} {bcolors.CYELLOW}{system_path}/{host_directory}/{directory_to_create_on_system}/{bcolors.ENDC}{bcolors.BOLD}{bcolors.OKBLUE}{file_name}{bcolors.ENDC} - {bcolors.OKGREEN}{len_str}{bcolors.ENDC}"
                .replace("//", "/"))
            return 0
        else:
            i += 1
            print(
                f"{bcolors.OKBLUE}[❌]{bcolors.ENDC} {bcolors.CYELLOW}{system_path}/{host_directory}/{directory_to_create_on_system}/{bcolors.ENDC}{bcolors.BOLD}{bcolors.OKBLUE}{file_name}{bcolors.ENDC}"
                .replace("//", "/"))

            continue
    download_failed.append("    - " + url)
    return 1


def format_url(url_to_format):
    url_split = url_to_format.split("http://")
    url_split[1] = url_split[1].replace("//", "/")
    url_formated = "http://".join(url_split)
    return url_formated


if __name__ == "__main__":
    without_threads_start = time.time()

    parser = argparse.ArgumentParser(
        description=
        "Dump directory listing : python3 DirListingDumper.py http://dirlisting.com /tmp/"
    )
    parser.add_argument(
        "website",
        help='URL where the directory listing is located.',
    )
    parser.add_argument("system_path",
                        help="System file where the dump is saved.")

    args = parser.parse_args()

    website = args.website
    system_path = args.system_path

    crawl_directory_listing(website)

    host_directory = website.replace("http://", "")
    
    host_directory = host_directory.split("/")[0]

    host_directory = host_directory.strip("/")

    system_path = system_path.rstrip("/")

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(download_files, url) for url in to_download]
        for future in futures:
            result = future.result()

    if len(download_failed) == 0:
        print(f"\n{bcolors.REDBG}Failed download(s): {bcolors.ENDC}\n" + \
            "   - None\n")
    else:
        print(f"\n{bcolors.REDBG}Failed download(s): {bcolors.ENDC}\n" + \
          '\n'.join(download_failed) + "\n")

    print(
        f"{bcolors.OKBLUE}[⌛]{bcolors.ENDC} Execution time: {bcolors.GREYBG}{time.time() - without_threads_start}{bcolors.ENDC} secs."
    )
