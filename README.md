# Food Additives Scraper

This project is an automated scraper for collecting information about food additives using Selenium and Python from https://www.aditivos-alimentarios.com/. It is designed to obtain the database required for the Android app [aditivos-alimentarios-app](https://github.com/adamff-dev/aditivos-alimentarios-app), which allows users to search for food additives and consult their toxicity. The scraper automatically detects installed browsers, manages WebDrivers, and saves the results to a database.

## Features
- Automatic detection of installed browsers (Chrome, Firefox, Edge, Safari)
- Automatic installation and management of WebDrivers
- Scraping of food additives data
- Saving results to a database

## Requirements
- Python 3.8+
- A supported browser installed (Chrome, Firefox, Edge, Safari)
- Dependencies listed in `requirements.txt`

## Installation
1. Clone this repository:
   ```sh
   git clone https://github.com/adamff-dev/food-additives-scraper.git
   cd food-additives-scraper
   ```
2. Install the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
Run the main script:
```sh
python main.py
```
The script will detect the installed browser, install the required WebDriver, and start scraping food additives data from https://www.aditivos-alimentarios.com/.

## Project Structure
- `main.py`: Main execution script
- `modules/`: Auxiliary modules
  - `WebDriverInstaller.py`: WebDriver installer and manager
  - `AditivosTools.py`: Tools for scraping and saving data
  - `ProgressBar.py`, `SharedTools.py`: Additional utilities

## License
MIT
