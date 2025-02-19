# Tebra_scraping
# Tebra Scraping & MySQL Data Storage

## Overview
This project is a web scraper for extracting healthcare provider details from [Tebra](https://www.tebra.com). The extracted data is stored in a MySQL database for further analysis.

## Features
- Scrapes provider details including name, company, locations, phone number, and website.
- Stores extracted data in a structured JSON file (`providers_data.json`).
- Inserts data into a MySQL database (`tebra_data`).
- Uses `httpx` for async web requests and `selectolax` for HTML parsing.

## Technologies Used
- Python
- `httpx` (Asynchronous HTTP requests)
- `selectolax` (HTML parsing)
- MySQL (Database storage)
- `mysql-connector-python` (Database connection)
- GitHub (Version control)

## Setup & Installation

### Prerequisites
- Python 3.8+
- MySQL Server (Workbench recommended)
- Git (For version control)

### 1. Clone the Repository
```sh
git clone https://github.com/Pradeep-Oaksol/Tebra_scraping.git
cd Tebra_scraping
```

### 2. Install Dependencies
```sh
pip install httpx selectolax mysql-connector-python
```

### 3. Configure MySQL Database
Create a MySQL database named `tebra_data` and a table named `providers`:
```sql
CREATE DATABASE tebra_data;
USE tebra_data;

CREATE TABLE providers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider_name VARCHAR(255),
    company_name VARCHAR(255),
    num_locations INT,
    location_addresses TEXT,
    phone_number TEXT,
    website_link VARCHAR(500)
);
```

### 4. Run the Scraper
```sh
python scraping_tebra.py
```

This will scrape the provider data and store it in `providers_data.json`.

### 5. Insert Data into MySQL
```sh
python data.py
```

This will insert the extracted data into your MySQL database.

## Usage
- Modify `scraping_tebra.py` to change the search query or add new data fields.
- Schedule the script using **cron jobs** (Linux) or **Task Scheduler** (Windows) for automation.
- Use `SELECT * FROM providers;` in MySQL to verify stored data.


