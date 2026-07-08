# I-SEM Market Dashboard

A side project to track and analyze Irish electricity market (I-SEM) data. I built this to get a better feel for ex-ante bidding dynamics, wind generation impacts, and spark spreads for thermal units.

The pipeline pulls data from EirGrid and SEMOpx and dumps it into some clean CSVs. There's a Streamlit app to quickly visualize price trends and a Power BI dashboard for higher-level reporting.

## What's in here
- `pipeline/`: Scripts to fetch and clean the market data.
- `app/`: The Streamlit dashboard files.
- `data/`: Extracted CSV files.