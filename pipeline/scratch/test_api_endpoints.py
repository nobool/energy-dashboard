import requests
import pandas as pd
from datetime import timedelta

# Test SNSP
date_str = "2026-06-25"
headers = {'User-Agent': 'Mozilla/5.0'}
url_snsp = f"https://www.smartgriddashboard.com/api/chart/?region=ALL&chartType=snsp&dateRange=day&dateFrom={date_str}&dateTo={date_str}&areas=snsp"
r_snsp = requests.get(url_snsp, headers=headers)
print("SNSP Status:", r_snsp.status_code)
if r_snsp.status_code == 200 and 'Rows' in r_snsp.json():
    rows = r_snsp.json()['Rows']
    print(f"SNSP Rows: {len(rows)}, First row: {rows[0] if rows else 'None'}")
else:
    print("SNSP failed or no rows")

# Test IDA1
url_semo = "https://reports.sem-o.com/api/v1/documents/static-reports"
params_ida = {
    'DPuG_ID': 'EA-001',
    'ResourceName': 'MarketResult_SEM-IDA1_PWR-SEM-D',
    'date_from': "2026-06-22",
    'date_to': "2026-06-29",
    'page_size': 5
}
r_ida = requests.get(url_semo, params=params_ida)
print("IDA1 Status:", r_ida.status_code)
if r_ida.status_code == 200 and r_ida.json().get('items'):
    items = r_ida.json()['items']
    print(f"IDA1 Items: {len(items)}, First item ResourceName: {items[0]['ResourceName']}")
else:
    print("IDA1 failed or no items")
