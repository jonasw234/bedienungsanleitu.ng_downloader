import logging
import os
import subprocess
import sys
import time
from typing import List, Tuple

from PIL import Image
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def init_webdriver() -> webdriver.Chrome:
    """Initialize the Selenium webdriver with specified options.

    Returns
    -------
    webdriver.Chrome
        The initialized Chrome webdriver with the specified options.
    """
    logging.info("Initializing webdriver.")
    options = webdriver.ChromeOptions()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--headless=new")
    options.add_argument("--log-level=3")
    return webdriver.Chrome(options=options)


def accept_cookie_consent(driver: webdriver.Chrome) -> None:
    """Accept cookie consent on the page.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.
    """
    driver.find_element(By.CSS_SELECTOR, "button[mode=primary]").click()


def toggle_navigation(driver: webdriver.Chrome, hidden: bool) -> None:
    """Hide or reveal the navigation arrows on the page.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.
    hidden : bool
        True if the navigation should be hidden, False if it should be revealed.
    """
    display_style = 'none' if hidden else 'block'
    driver.execute_script(f"document.getElementsByClassName('glide__arrows')[0].style.display = '{display_style}'")


def take_screenshot_of_viewer(driver: webdriver.Chrome, page_number: int) -> None:
    """Take a screenshot of the viewer for the specified page number.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.
    page_number : int
        The page number to be used in the filename for the cropped image.
    """
    toggle_navigation(driver, hidden=True)

    element = driver.find_element(By.CSS_SELECTOR, "#viewer > div:nth-child(3)")
    scroll_to_element(driver, element)

    element_size = element.size
    full_image = take_screenshot(driver)
    crop_element_image(full_image, element_size, page_number)


def next_page(driver: webdriver.Chrome) -> None:
    """Navigate to the next page in the viewer.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.
    """
    toggle_navigation(driver, hidden=False)
    right_arrow = driver.find_element(By.CSS_SELECTOR, ".glide__arrow--right")
    right_arrow.click()


def scroll_to_element(driver: webdriver.Chrome, element: WebElement) -> None:
    """Scroll the specified element into view.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.
    element : WebElement
        The Selenium WebElement to scroll into view.
    """
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)  # Wait for scrolling to finish


def take_screenshot(driver: webdriver.Chrome) -> Image:
    """Take a screenshot of the full page.

    Parameters
    ----------
    driver : webdriver.Chrome
        The Selenium webdriver instance used to interact with the web page.

    Returns
    -------
    Image
        The full screenshot as a PIL Image object.
    """
    driver.save_screenshot('full_page.png')
    return Image.open('full_page.png')


def crop_element_image(full_image: Image, element_size: dict, page_number: int) -> None:
    """Crop the full image to the bounding box of the element.

    Parameters
    ----------
    full_image : Image
        The full screenshot as a PIL Image object.
    element_size : dict
        A dictionary containing the width and height of the element.
    page_number : int
        The page number to be used in the filename for the cropped image.
    """
    left, top = 232, 10
    right = left + element_size['width'] - 19  # Subtract border
    bottom = top + element_size['height'] - 19  # Subtract border
    bounding_box = (left, top, right, bottom)
    element_image = full_image.crop(bounding_box)
    element_image.save(f"page-{page_number}.png")


def create_pdf_from_images(page_number: int, url: str) -> Tuple[str, List[str]]:
    """Create a PDF file from the downloaded images.

    Parameters
    ----------
    page_number : int
        The total number of pages downloaded.
    url : str
        The URL used to derive the PDF filename.

    Returns
    -------
    tuple
        A tuple containing the path to the created PDF and a list of image filenames.
    """
    page_files = [f"page-{file}.png" for file in range(1, page_number + 1)]
    images = [Image.open(page_file) for page_file in page_files]
    pdf_path = f'{url.split("/")[3]}_{url.split("/")[4]}.pdf'
    logging.info("Creating PDF file from downloaded images.")
    images[0].save(
        pdf_path,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=images[1:]
    )
    return pdf_path, page_files


def remove_temp_files(page_files: List[str]) -> None:
    """Remove temporary image files.

    Parameters
    ----------
    page_files : List[str]
        List of filenames of the temporary image files to be removed.
    """
    logging.info("Removing temporary image files.")
    for page_file in page_files:
        os.remove(page_file)
    os.remove("full_page.png")


def ocr_pdf(pdf_path: str) -> None:
    """Perform OCR on the PDF to make it searchable.

    Parameters
    ----------
    pdf_path : str
        The path to the PDF file to be processed.

    Raises
    ------
    FileNotFoundError
        If `ocrmypdf` is not available on the system.
    """
    output_pdf_path = f"{os.path.splitext(pdf_path)[0]}_ocr.pdf"
    try:
        subprocess.run(["ocrmypdf", pdf_path, output_pdf_path], check=True)
        os.remove(pdf_path)
    except FileNotFoundError:
        logging.error(
            "Cannot OCR PDF file, most likely because `ocrmypdf` is not available."
        )


def main(url: str) -> None:
    """Main function to execute the web scraping and PDF creation process.

    Parameters
    ----------
    url : str
        The URL of the document to be processed.
    """
    driver = init_webdriver()
    try:
        driver.get(url)
        time.sleep(2)
        accept_cookie_consent(driver)

        page_number = 1
        while True:
            logging.info("Downloading page no. %d", page_number)

            take_screenshot_of_viewer(driver, page_number)

            next_page(driver)
            time.sleep(2)  # Wait for the page to load after the click

            current_url = driver.current_url
            if current_url.endswith('/anleitung') and '?' not in current_url:
                logging.info("Reached the target URL:", current_url)
                break

            page_number += 1

        pdf_path, page_files = create_pdf_from_images(page_number, url)
        remove_temp_files(page_files)
        logging.info("Trying to OCR the PDF to make it searchable (not perfect) ...")
        ocr_pdf(pdf_path)

    finally:
        driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error(
            "Usage: %s https://www.bedienungsanleitu.ng/bosch/serie-6-tds6080de/anleitung?p=1",
            os.path.basename(__file__)
        )
        sys.exit(1)
    prefix = "https://www.bedienungsanleitu.ng/"
    if not sys.argv[1].startswith(prefix):
        logging.error("URL must start with %s.", prefix)
        sys.exit(1)
    main(sys.argv[1])
