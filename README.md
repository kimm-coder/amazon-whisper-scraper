# Amazon Store Product Scraper

A Playwright-based scraper for collecting product data from Amazon store pages, with a React dashboard for visualization.

![Dashboard Preview](screenshot.png)

## Features

- Scrapes product name, ASIN, price, rating, review count, sales rank, and images
- React + TypeScript dashboard with search and sorting
- Exports data to CSV

## Quick Start

### Scraper
```bash
source .venv/bin/activate
python scraper.py
```

### Dashboard
```bash
cd dashboard
npm install
npm run dev
```

## Live Demo

[View Dashboard](https://kimm-coder.github.io/amazon-whisper-scraper/)
