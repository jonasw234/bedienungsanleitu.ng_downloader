#!/usr/bin/env python3
"""Downloads PDF files from the bedienungsanleitu.ng website"""
import logging
import os
import subprocess
import sys

import requests
from bs4 import BeautifulSoup
from PIL import Image

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")


def main(url: str):
    """Download the files and create a (searchable PDF file as a result).

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
    while True:
        download = requests.get(
            f"https://www.bedienungsanleitu.ng/viewer/2/{viewer_id}/{page_number}/large.png"
        )
        if download.status_code == 200:
            with open(f"{page_number}.png", "wb") as page:
                page.write(download.content)
            logging.debug("Downloaded page %d", page_number)
            page_number += 1
        else:
            logging.debug("No more pages to download detected.")
            break
    page_files = [f"{file}.png" for file in range(1, page_number)]
    images = [Image.open(page_file) for page_file in page_files]
    pdf_path = f'{url.split("/")[3]}_{url.split("/")[4]}.pdf'
    logging.info("Creating PDF file from downloaded images.")
    images[0].save(
        pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
    )
    logging.debug("Removing temporary image files.")
    for page_file in page_files:
        os.remove(page_file)
    logging.info("Trying to OCR the PDF to make it searchable (not perfect) ...")
    try:
        ocrmypdf_returncode = subprocess.run(
            ["ocrmypdf", pdf_path, f"{os.path.splitext(pdf_path)[0]}_ocr.pdf"],
            check=True,
        ).returncode
        if ocrmypdf_returncode == 0:
            os.remove(pdf_path)
    except FileNotFoundError:
        logging.error(
            "Cannot OCR PDF file, most likely because `ocrmypdf` is not available."
        )


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
