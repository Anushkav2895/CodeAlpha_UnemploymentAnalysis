# CodeAlpha – Unemployment Analysis with Python

Analysis of India's unemployment data (May 2019 – Oct 2020): cleaning, exploration, visualisation, Covid-19 impact, seasonality and policy insights.

## Structure
```
data/        Unemployment_in_India.csv, Unemployment_Rate_upto_11_2020.csv
outputs/     analysis_output.txt + figures/ (13 charts)
unemployment_analysis.py
requirements.txt
```

## Run
```
pip install -r requirements.txt
python unemployment_analysis.py
```

## Method
- **Cleaning:** stripped column/text whitespace, removed blank rows, parsed dates, renamed columns, added Month/Year/Period.
- **Exploration:** distributions, correlations, state/zone/rural-urban trends.
- **Covid impact:** Jan–Feb 2020 baseline vs Apr–May 2020 lockdown window, by state.
- **Seasonality:** monthly pattern on pre-Covid months only.

## Key findings
- National average unemployment rose from ~9.2% (Jan–Feb 2020) to ~23% (Apr–May 2020), then fell to ~10.9% by June and ~8.0% by October.
- Employed people (27 states) fell ~32% in April 2020 versus Jan–Feb.
- Labour participation dropped from ~44% to ~35% in April.
- Urban unemployment (25.5%) exceeded rural (21.7%) in April 2020.
- Biggest rises: Puducherry, Jharkhand, Tamil Nadu, Bihar.
- Pre-Covid monthly rates were flat (~9–10%); only ~10 pre-Covid months exist, so seasonality is not conclusive.

## Policy takeaways
Targeted relief in hardest-hit states, urban employment/gig-worker protection, tracking participation (not just headline rate), and collecting multi-year data for seasonal planning.

## Limitations
Some state values (e.g. Puducherry, Sikkim) are extremely volatile; Sikkim has no Jan–Feb data and is excluded from the baseline comparison.
