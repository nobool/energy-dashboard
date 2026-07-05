# I-SEM Market Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](#) 
[![Power BI Report](https://img.shields.io/badge/PowerBI-View_Report-F2C811?logo=powerbi&logoColor=black)](#)

## Overview
A dual-output analytical dashboard backed by a shared Python data pipeline. It extracts real-time and historical market data from the Single Electricity Market (I-SEM) and the EirGrid Smart Grid, providing key insights for trading optimization and risk management.


## Architecture
- **Data Pipeline:** Python (`pandas`, `requests`) fetching data from EirGrid, SEMOpx, and ENTSO-E APIs.
- **Data Storage:** Processed CSV files.
- **Front-end 1:** Streamlit application for fast, interactive technical analysis.
- **Front-end 2:** Power BI report for business stakeholder review.