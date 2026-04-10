# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Amazon product scraper for the Whisper Ear Care store with a React dashboard to display scraped products.

## Commands

### Python Scraper
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the scraper (outputs to amazon_whisper_store_products.csv)
python scraper.py

# Run debug script to test dashboard locally
python debug.py
```

### Dashboard (React + Vite + TypeScript)
```bash
cd dashboard

# Install dependencies
npm install

# Development server
npm run dev

# Build for production
npm run build

# Lint
npm run lint
```

## Architecture

### Scraper (`scraper.py`)
Playwright-based Amazon scraper that:
1. Navigates to the Whisper Ear Care Amazon store page
2. Scrolls to load all products and collects product links
3. Visits each product page to extract: name, ASIN, price, rating, review count, sales rank, main image
4. Outputs data to CSV

Key functions:
- `scrape_store_product_links()` - Collects product URLs from store page
- `scrape_product()` - Extracts data from individual product pages
- `extract_*()` functions - Handle specific data extraction with multiple selector fallbacks

### Dashboard (`dashboard/`)
React 18 + TypeScript + Vite + Tailwind CSS application:
- `src/App.tsx` - Main component with product grid, search, and sorting
- `src/types/Product.ts` - TypeScript interface matching scraper output
- `src/data/products.json` - Static product data (manually updated from scraper CSV)

The dashboard reads from a static JSON file. To update products:
1. Run the scraper to generate new CSV
2. Convert CSV to JSON and replace `dashboard/src/data/products.json`
