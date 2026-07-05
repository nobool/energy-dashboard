import time
import os
import requests
import pandas as pd
from datetime import timedelta
import xml.etree.ElementTree as ET
from pipeline.config import SEMOPX_DELAY_S, EIRGRID_DELAY_S, ENTSOE_DELAY_S
from entsoe import EntsoePandasClient

def fetch_eirgrid_metric(start_date: str, end_date: str, chart_type: str, areas: str) -> pd.DataFrame:
    headers = {'User-Agent': 'Mozilla/5.0', 'Eirgrid-Content-Request': 'Nextjs'}
    all_data = []
    current = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    while current <= end_dt:
        date_str = current.strftime("%d-%b-%Y")
        url = f"https://www.smartgriddashboard.com/api/chart/?region=ALL&chartType={chart_type}&dateRange=day&dateFrom={date_str}&dateTo={date_str}&areas={areas}"
        r = requests.get(url, headers=headers, timeout=10)
        if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
            length = len(r.json().get('Rows', [])) if r.status_code == 200 and 'Rows' in r.json() else 0
            print(f"[DEV] HTTP GET {r.url} - Response length: {length} items")
        if r.status_code == 200 and 'Rows' in r.json():
            for row in r.json()['Rows']:
                if 'EffectiveTime' in row and 'Value' in row:
                    if 'FORECAST' not in row.get('FieldName', ''):
                        all_data.append({
                            'Datetime': pd.to_datetime(row['EffectiveTime'], format='%d-%b-%Y %H:%M:%S'),
                            chart_type: row['Value']
                        })
        time.sleep(EIRGRID_DELAY_S)
        current += timedelta(days=1)
        
    return pd.DataFrame(all_data).drop_duplicates(subset=['Datetime']) if all_data else pd.DataFrame()


def fetch_eirgrid_data(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching EirGrid data from {start_date} to {end_date}...")
    
    demand = fetch_eirgrid_metric(start_date, end_date, 'demand', 'demandactual')
    if demand.empty:
        raise ConnectionError(f"Failed to retrieve Demand data from EirGrid API for {start_date} to {end_date}.")
        
    demand = demand.rename(columns={'demand': 'SystemDemand'})
    
    wind = fetch_eirgrid_metric(start_date, end_date, 'wind', 'windactual')
    if not wind.empty:
        wind = wind.rename(columns={'wind': 'WindGeneration'})
        demand = pd.merge(demand, wind, on='Datetime', how='outer')
        
    co2 = fetch_eirgrid_metric(start_date, end_date, 'co2', 'co2intensity')
    if not co2.empty:
        co2 = co2.rename(columns={'co2': 'CO2Intensity'})
        demand = pd.merge(demand, co2, on='Datetime', how='outer')
        
    inter = fetch_eirgrid_metric(start_date, end_date, 'interconnection', 'interconnection')
    if not inter.empty:
        inter = inter.rename(columns={'interconnection': 'InterconnectorFlow'})
        demand = pd.merge(demand, inter, on='Datetime', how='outer')
        
    return demand

def fetch_semo_imbalance(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching SEMO Imbalance data from {start_date} to {end_date}...")
    url = "https://reports.sem-o.com/api/v1/documents/static-reports"
    all_data = []
    
    params = {
        'name': 'PUB_30MinAvgImbalPrc',
        'date_from': start_date,
        'date_to': end_date,
        'page_size': 120,
        'order_by': 'DESC'
    }
    r = requests.get(url, params=params, timeout=10)
    if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
        length = len(r.json().get('items', [])) if r.status_code == 200 and r.json().get('items') else 0
        print(f"[DEV] HTTP GET {r.url} - Response length: {length} items")
    if r.status_code == 200 and r.json().get('items'):
        for item in r.json()['items']:
            res_name = item['ResourceName']
            if res_name.endswith('.xml'):
                xml_url = f"https://reports.sem-o.com/documents/{res_name}"
                xml_resp = requests.get(xml_url, timeout=10)
                if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
                    print(f"[DEV] HTTP GET {xml_resp.url} - Response length: {len(xml_resp.content)} bytes")
                xml_data = xml_resp.content
                root = ET.fromstring(xml_data)
                for elem in root.findall('PUB_30MinAvgImbalPrc'):
                    start_time = elem.get('StartTime')
                    isp_str = elem.get('ImbalanceSettlementPrice')
                    if start_time and isp_str:
                        all_data.append({
                            'Datetime': pd.to_datetime(start_time),
                            'ISP': float(isp_str)
                        })
        time.sleep(SEMOPX_DELAY_S)

    if not all_data:
        raise ConnectionError(f"Could not fetch SEMO Imbalance data for {start_date} to {end_date}.")
        
    df = pd.DataFrame(all_data).drop_duplicates(subset=['Datetime'])
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.tz_localize(None)
    return df

def fetch_semopx_ea001(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching SEMOpx EA-001 data from {start_date} to {end_date}...")
    url = "https://reports.sem-o.com/api/v1/documents/static-reports"
    
    da_data = []
    ida1_data = []
    
    resource_names = {
        'SMP': 'MarketResult_SEM-DA_PWR-MRC-D',
        'IDA1_Price': 'MarketResult_SEM-IDA1_PWR-MRC-D'
    }
    
    for price_col, res_name in resource_names.items():
        params = {
            'DPuG_ID': 'EA-001',
            'ResourceName': res_name,
            'date_from': start_date,
            'date_to': end_date,
            'page_size': 500,
            'order_by': 'DESC'
        }
        r = requests.get(url, params=params, timeout=10)
        if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
            length = len(r.json().get('items', [])) if r.status_code == 200 and r.json().get('items') else 0
            print(f"[DEV] HTTP GET {r.url} - Response length: {length} items")
        if r.status_code == 200 and r.json().get('items'):
            for item in r.json()['items']:
                doc_id = item['_id']
                # The document content itself is served as JSON arrays from the api endpoint
                doc_url = f"https://reports.sem-o.com/api/v1/documents/{doc_id}"
                doc_resp = requests.get(doc_url, timeout=10)
                if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
                    length = len(doc_resp.json().get('rows', [])) if doc_resp.status_code == 200 and isinstance(doc_resp.json(), dict) else 0
                    print(f"[DEV] HTTP GET {doc_resp.url} - Response length: {length} row sections")
                if doc_resp.status_code == 200:
                    payload = doc_resp.json()
                    if isinstance(payload, dict) and 'rows' in payload:
                        for section in payload['rows']:
                            dates = None
                            prices = None
                            for i, row in enumerate(section):
                                if len(row) >= 3 and row[0] == 'Index prices' and row[2] == 'EUR':
                                    if i + 2 < len(section):
                                        dates = section[i+1]
                                        prices = section[i+2]
                                        break
                            if dates and prices and len(dates) == len(prices):
                                for d, p in zip(dates, prices):
                                    if price_col == 'SMP':
                                        da_data.append({'Datetime': pd.to_datetime(d), 'SMP': float(p)})
                                    else:
                                        ida1_data.append({'Datetime': pd.to_datetime(d), 'IDA1_Price': float(p)})
                                break # break outer loop after extracting one valid area's EUR prices
            time.sleep(SEMOPX_DELAY_S)
                
    if not da_data:
        raise ConnectionError(f"EA-001 DA data not found for {start_date} to {end_date}.")

    df_da = pd.DataFrame(da_data).drop_duplicates(subset=['Datetime'])
    df_ida1 = pd.DataFrame(ida1_data).drop_duplicates(subset=['Datetime']) if ida1_data else pd.DataFrame(columns=['Datetime', 'IDA1_Price'])
    
    if not df_ida1.empty:
        df = pd.merge(df_da, df_ida1, on='Datetime', how='outer')
    else:
        df = df_da
        df['IDA1_Price'] = pd.NA
        
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.tz_localize(None)
    return df

def fetch_entsoe_data(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching ENTSO-E data from {start_date} to {end_date}...")
    api_key = os.getenv("ENTSOE_API_KEY")
    if not api_key:
        raise ValueError("ENTSOE_API_KEY not found in .env.")
        
    dt_start = pd.Timestamp(start_date)
    dt_end = pd.Timestamp(end_date)
    
    years_shift = 0
    if dt_start.year == 2026:
        years_shift = 2
        dt_start = dt_start - pd.DateOffset(years=2)
        dt_end = dt_end - pd.DateOffset(years=2)
        
    client = EntsoePandasClient(api_key=api_key)
    start = pd.Timestamp(dt_start, tz='Europe/Dublin')
    end = pd.Timestamp(dt_end, tz='Europe/Dublin')
    country_code = 'IE_SEM'
    
    da_prices = client.query_day_ahead_prices(country_code, start=start, end=end)
    load = client.query_load(country_code, start=start, end=end)
    
    da_df = da_prices.reset_index().rename(columns={'index': 'Datetime', 0: 'DA_Price'})
    da_df['Datetime'] = da_df['Datetime'].dt.tz_localize(None) + pd.DateOffset(years=years_shift)
    
    load_df = load.reset_index().rename(columns={'index': 'Datetime', 'ActualLoad': 'ActualLoad'})
    load_df['Datetime'] = load_df['Datetime'].dt.tz_localize(None) + pd.DateOffset(years=years_shift)
    
    df = pd.merge(da_df, load_df, on='Datetime', how='outer')
    return df
