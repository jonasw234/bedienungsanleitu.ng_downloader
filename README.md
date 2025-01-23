# bedienungsanleitu.ng_downloader
Downloads PDF files from the bedienungsanleitu.ng website

**Please use the [Selenium branch](https://github.com/jonasw234/bedienungsanleitu.ng_downloader/tree/selenium) for now.** While it is quite a bit slower, this was the easiest way to get the script working again. I was unable to properly integrate their inline CSS into the final output in this version, so text and images are separated. PRs are welcome!

## Usage
```
Usage: bedienungsanleitu.ng_downloader https://www.bedienungsanleitu.ng/bosch/serie-6-tds6080de/anleitung?p=1
```

## Installation
For the development version:
```
git clone https://github.com/jonasw234/bedienungsanleitu.ng_downloader
cd bedienungsanleitu.ng_downloader
python3 setup.py install
```
Or use [`pipx`](https://pypi.org/project/pipx/) and install with
```
pipx install git+https://github.com/jonasw234/bedienungsanleitu.ng_downloader
```
Needs [`wkhtmltopdf`](https://wkhtmltopdf.org/) installed for the PDF creation.
