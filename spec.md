# Project 1 spec: California ZEV adoption forecast

## Question
Which California counties will reach what share of new-car sales that are ZEVs by 2030?

## Data
- CEC New ZEV Sales, county × year, 10-23–2025 (data as of 10/13/2026)
- Census ACS 5-year: median household income (B19013), population (B01003), 2015–2024
- Join key: county name / FIPS

## Method
1. Target: ZEV share = ZEV sales / total new sales, per county per year
2. Baseline: ___ (e.g. last year's share carried forward, or a linear trend per county)
3. Model A: ___   Model B: ___
4. Validation: train on years ≤ 2022, test on 2023–2025 (no random splits)

## Success metric
Mean absolute error on the test years; the best model beats the baseline by at least ___%.

## Deliverable
Streamlit app (county selector, forecast chart, key drivers) + README with results.

## Risks / open questions
- Small counties have noisy shares
- Income lags one year behind sales data