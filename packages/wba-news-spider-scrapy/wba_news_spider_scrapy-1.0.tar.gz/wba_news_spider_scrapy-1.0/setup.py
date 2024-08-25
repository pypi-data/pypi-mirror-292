# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'wba-news-spider-scrapy',
    version      = '1.0',
    description  = 'A web scraping tool using Scrapy to gather news data.',
    author       = 'Michel Padron',
    author_email = 'michel@padmora.com',
    packages     = find_packages(),
    entry_points = {'scrapy': ['settings = newsspider.settings']},
)
