#!/usr/bin/env python3
"""Downloads PDF files from the bedienungsanleitu.ng website"""
import logging
import os
import sys

import requests
from bs4 import BeautifulSoup
import pdfkit

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main(url: str):
    """Download the files and create a (searchable) PDF file as a result.

    Params
    ------
    url : str
        The URL to download the manual from
    """
    logging.info("Starting download for %s.", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    viewer_id = list(soup.find_all("link", href=lambda x: x and "/viewer/" in x))
    if not viewer_id:
        logging.error("Cannot determine viewer id!")
        return
    viewer_id = viewer_id[0].attrs["href"].split("/")[2]
    logging.debug("Viewer id detected as %d", viewer_id)
    page_number = 1
    temp_image_files = set()
    while True:
        download = requests.get(
            f"https://www.bedienungsanleitu.ng/viewer/{viewer_id}/{page_number}/page-{page_number}.page"
        )
        if download.status_code == 200:
            with open(f"{page_number}.html", "w", encoding="latin1", errors="ignore") as page:
                page.write(download.text)
            subsoup = BeautifulSoup(download.text, features="html.parser")
            images = subsoup.find_all("img")
            for image in images:
                # Download the images
                download = requests.get(f"https://www.bedienungsanleitu.ng/viewer/{viewer_id}/{page_number}/{image.attrs['src']}")
                if download.status_code == 200:
                    image_path = image.attrs["src"].split("/")[-1]
                    with open(image_path, "wb") as image:
                        image.write(download.content)
                        temp_image_files.add(image_path)
                else:
                    logging.warning("Could not download image %s", image.attrs["src"])
            logging.debug("Downloaded page %d", page_number)
            page_number += 1
        else:
            logging.debug("No more pages to download detected.")
            break
    page_files = [f"{file}.html" for file in range(1, page_number)]
    pdf_path = f'{url.split("/")[3]}_{url.split("/")[4]}.pdf'
    logging.info("Creating PDF file from downloaded files.")
    pdfkit.from_file(page_files, pdf_path, options={"enable-local-file-access": True})
    logging.debug("Removing temporary files.")
    for page_file in page_files:
        os.remove(page_file)
    for image_file in temp_image_files:
        os.remove(image_file)
    logging.info("Done.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error(
            "Usage: %s https://www.bedienungsanleitu.ng/bosch/serie-6-tds6080de/anleitung?p=1",
            os.path.basename(__file__),
        )
        sys.exit(1)
    prefix = "https://www.bedienungsanleitu.ng/"
    if prefix != sys.argv[1][: len(prefix)]:
        logging.error("URL must start with %s.", prefix)
        sys.exit(1)
    main(sys.argv[1])
