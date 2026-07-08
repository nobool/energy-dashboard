# I-SEM Market Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://energy-dashboard-isem.streamlit.app/) 

A side project to track and analyze Irish electricity market (I-SEM) data. I built this to get a better feel for ex-ante bidding dynamics, wind generation impacts, and spark spreads for thermal units.

The pipeline pulls data from publicly available APIs and dumps it into some clean CSVs. There's a Streamlit app to quickly visualize trends.

## Live Dashboard
You can access the live version of this dashboard directly in your browser here: **[I-SEM Energy Dashboard on Streamlit](https://energy-dashboard-isem.streamlit.app/)**

**Continuous Data Updates:** A CI/CD pipeline powered by GitHub Actions runs daily and fetches the latest market data from the underlying APIs. The live Streamlit dashboard will always display a rolling **7-day trailing window** of fresh data.

## What's Included
- `pipeline/`: Python scripts designed for headless cloud execution that fetch, clean, and merge market data.
- `app/`: An interactive Streamlit dashboard for visualizing price trends and system demand.
- `data/`: Extracted and processed CSV files.

## API Sources Used
This project interacts with multiple public APIs to aggregate market conditions at 30-minute intervals:
- **SEMOpx (EA-001)**: Fetches Day-Ahead Market (DAM) and Intraday (IDA1, IDA2, IDA3) auction prices and volumes.
- **SEM-O (Imbalance)**: Fetches the 30-Minute Average Imbalance Settlement Price (ISP) to analyze the balancing market.
- **EirGrid Smart Grid Dashboard**: Fetches actual system demand, wind generation, solar generation, interconnection flows, and system CO2 intensity.
- **Nord Pool (N2EX)**: Fetches GB Day-Ahead prices to analyze interconnector price spreads since implicit market coupling ended post-Brexit.

## Quick Start (Local Setup)

I've included startup scripts to make running this project locally as frictionless as possible. These scripts will automatically create a Python virtual environment, install all dependencies, and launch the Streamlit dashboard for you. 

> [!NOTE]
> The only requirement is that you have **Python** installed on your system.

### Windows Users
Simply double-click the `start.bat` file in your file explorer, or run it from your terminal:
```cmd
.\start.bat
```

### Mac / Linux Users
Run the bash script from your terminal:
```bash
bash start.sh
```

## Pulling custom historical data
If you want to pull historical data to your local machine instead of relying on the automated cloud pipeline, you can run the pipeline script yourself. By default, it grabs the last 7 days:

```bash
# Run with default 7-day trailing window
python -m pipeline.run_pipeline
```

*Optional: You can pull specific historical date ranges by setting environment variables:*
```bash
# Windows (PowerShell)
$env:DATE_FROM="2026-07-01"; $env:DATE_TO="2026-07-07"; python -m pipeline.run_pipeline

# Mac/Linux (Bash)
DATE_FROM=2026-07-01 DATE_TO=2026-07-07 python -m pipeline.run_pipeline
```

```bash
# Launch the dashboard with new data
streamlit run app/Dashboard.py
```