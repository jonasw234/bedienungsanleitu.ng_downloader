import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bedienungsanleitu.ng_downloader",
    version="0.0.1",
    author="Jonas A. Wendorf",
    description="Downloads PDF files from the bedienungsanleitu.ng website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jonasw234/bedienungsanleitu.ng_downloader",
    packages=setuptools.find_packages(),
    install_requires=["requests", "beautifulsoup4", "pdfkit", "wkhtmltopdf"],
    include_package_data=True,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Natural Language :: English",
        "OSI Approved :: GNU General Public License v3 or later (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": ["bedienungsanleitu.ng_downloader=bedienungsanleitu.ng_downloader.bedienungsanleitu.ng_downloader:main"],
    },
)
