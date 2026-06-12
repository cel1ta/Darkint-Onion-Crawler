# Darkint-Onion-Crawler
Crawler for discovering .onion services through Tor and filtering URLs using user-defined keywords.

## Description

This project implements a crawler designed to discover new .onion services through the Tor network. Starting from a set of seed URLs, the crawler visits each page, extracts links, and recursively explores newly discovered onion services.

Additionally, the tool allows users to search for a specific keyword within discovered URLs, making it easier to locate services related to a particular topic.

## Features

* Crawling through the Tor network using a SOCKS5 proxy.
* Discovery of new .onion services.
* URL keyword filtering.
* Multi-threaded crawling.
* Duplicate avoidance using a persistent URL database.
* Configurable crawling depth.

## Files

* "seed.txt": initial URLs used as starting points.
* "seen.txt": URLs already visited.
* "results.txt": URLs containing the keyword provided by the user.

## Requirements

* Python 3
* requests

Install dependencies:
pip install requests

## Usage

Run the crawler:
python crawler.py

The program will request a keyword and begin exploring the URLs stored in "seed.txt".

## Disclaimer

This software was developed for academic and research purposes. Users are responsible for complying with all applicable laws and regulations.

