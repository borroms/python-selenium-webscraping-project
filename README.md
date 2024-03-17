# Product Details Scraper

This project automates the process of scraping product data from the Frontline Hobbies website. It extracts information such as product name, price, availability, and reviews for all products under the Kyosho brand.

## Overview

The script utilizes Python along with the following libraries:

- `pandas` for data manipulation.
- `selenium` for web scraping.
- `psycopg2` for connecting to a PostgreSQL database.

## Workflow

1. **Web Scraping**: The script navigates through the Frontline Hobbies website, specifically targeting the Kyosho brand's products. It collects product details, including name, price, availability, and reviews, for each product.

2. **Data Processing**: Extracted data is processed and transformed into a structured format using `pandas`. Duplicate entries are removed, and necessary transformations are applied to columns.

3. **Database Insertion**: The processed data is inserted into a PostgreSQL database. Each row represents a unique product, containing relevant information such as scrape date, company name, product name, SKU, price, rating, availability, and reviews.

4. **CSV Export**: Additionally, the script generates a CSV file, containing the scraped data.

## Setup

### Prerequisites

- Python 3.x
- Google Chrome browser
- Chrome WebDriver

### Installation

1. Install Python dependencies:

```bash
pip install pandas selenium psycopg2
```

2. Download the Chrome WebDriver and specify its path in the script (`chrome_driver_path` variable).

3. Set up a PostgreSQL database named `frontlinehobbies` with appropriate permissions.

4. Update the database connection parameters (`db_params`) in the script with your PostgreSQL credentials.

### Execution

Run the script in your preferred Python environment:

```bash
python frontline_hobbies_scraper.py
```

## Notes

- Ensure proper internet connectivity during script execution to access the website.
- Adjustments may be required in case of website layout changes.
