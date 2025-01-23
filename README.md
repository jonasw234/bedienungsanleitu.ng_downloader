# bedienungsanleitu.ng_downloader
Downloads PDF files from the bedienungsanleitu.ng website

## Usage
```
Usage: bedienungsanleitu.ng_downloader https://www.bedienungsanleitu.ng/bosch/serie-6-tds6080de/anleitung?p=1
```

## Installation
For the development version:
```
git clone https://github.com/jonasw234/bedienungsanleitu.ng_downloader
cd bedienungsanleitu.ng_downloader
git checkout selenium
python3 setup.py install
```
Or use [`pipx`](https://pypi.org/project/pipx/) and install with
```
pipx install git+https://github.com/jonasw234/bedienungsanleitu.ng_downloader@selenium
```
To OCR your PDF files, install the [`ocrmypdf`](https://ocrmypdf.readthedocs.io/en/latest/installation.html) Python package and the [`tesseract`](https://tesseract-ocr.github.io/tessdoc/Installation.html) binary.

Using Selenium makes the whole download process *a lot* slower, but it works reliably at least. PRs welcome for the other version so that all the CSS is applied correctly.
