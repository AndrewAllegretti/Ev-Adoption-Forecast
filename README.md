# CA EV Adoption Forecast

Forecasts the share of new-car sales that are zero-emission vehicles (ZEVs) in each California county through 2030, using public sales and Census data. *(In progress.)*

## Project structure

- `data/raw/`: downloaded source files (not committed; see below)
- `data/processed/`: cleaned outputs written by `src/`
- `notebooks/`: exploration and modeling
- `src/`: download and cleaning scripts

## Getting the data

Raw data isn't stored in this repo. To reproduce it, save these files to `data/raw/`:

1. **ZEV sales by county**: California Energy Commission [New ZEV Sales dashboard](https://www.energy.ca.gov/zevstats). Use the *download data* link below the dashboard.
2. **Median household income and population by county**: U.S. Census ACS 5-year estimates, tables B19013 and B01003, all California counties, 2015 onward ([data.census.gov](https://data.census.gov)).

## Setup

Use Python 3.15.2 (the current environment is validated with this version).

    py -3.15 -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt