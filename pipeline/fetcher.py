from datetime import date
from pandas._libs.tslibs import timedeltas
import time
import os
import requests
import pandas as pd
from datetime import timedelta
import xml.etree.ElementTree as ET
from pipeline.config import SEMOPX_DELAY_S, EIRGRID_DELAY_S

def fetch_eirgrid_metric(start_date: str, end_date: str, chart_type: str, areas: str) -> pd.DataFrame:
    headers = {'User-Agent': 'Mozilla/5.0', 'Eirgrid-Content-Request': 'Nextjs'}
    all_data = []
    current = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    field_map = {
        'demand': 'SYSTEM_DEMAND',
        'wind': 'WIND_ACTUAL',
        'solar': 'SOLAR_ACTUAL',
        'co2': 'CO2_INTENSITY',
        'interconnection': 'INTER_NET'
    }
    expected_field = field_map.get(chart_type, '')
    
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
                    if row.get('FieldName') == expected_field:
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
        
    solar = fetch_eirgrid_metric(start_date, end_date, 'solar', 'solaractual')
    if not solar.empty:
        solar = solar.rename(columns={'solar': 'SolarGeneration'})
        demand = pd.merge(demand, solar, on='Datetime', how='outer')
    else:
        demand['SolarGeneration'] = 0.0
        
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
        'page_size': 500,
        'order_by': 'DESC',
        'page': 1
    }
    r = requests.get(url, params=params, timeout=10)
    
    if r.status_code == 200:
        data = r.json()
        
        if os.getenv("ENVIRONMENT") == "DEVELOPMENT":
            length = len(data.get('items', []))
            print(f"[DEV] HTTP GET {r.url} - Response length: {length} items")
            
        if data.get('items'):
            for item in data['items']:
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
   

    if not all_data:
        raise ConnectionError(f"Could not fetch SEMO Imbalance data for {start_date} to {end_date}.")
        
    df = pd.DataFrame(all_data).drop_duplicates(subset=['Datetime'])
    # SEMO Imbalance returns naive UTC strings, so localize to UTC then convert to Dublin
    df['Datetime'] = pd.to_datetime(df['Datetime']).dt.tz_localize('UTC').dt.tz_convert('Europe/Dublin').dt.tz_localize(None)

    return df

def fetch_semopx_ea001(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching SEMOpx EA-001 data from {start_date} to {end_date}...")
    url = "https://reports.sem-o.com/api/v1/documents/static-reports"
    
    market_data = {}
    
    resource_names = {
        'DAM': 'MarketResult_SEM-DA_PWR-MRC-D',
        'IDA1': 'MarketResult_SEM-IDA1_PWR-SEM-GB-D',
        'IDA2': 'MarketResult_SEM-IDA2_PWR-SEM-GB-D_',
        'IDA3': 'MarketResult_SEM-IDA3_PWR-SEM-D_'
    }
        
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
    date_from_str = start_dt.strftime('%Y-%m-%dT00:00:00')
    date_to_str = end_dt.strftime('%Y-%m-%dT02:00:00')

    for market, res_name in resource_names.items():
        market_list = []
        params = {
            'DPuG_ID': 'EA-001',
            'ResourceName': res_name,
            'date_from': date_from_str,
            'date_to': date_to_str,
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
                doc_url = f"https://reports.sem-o.com/api/v1/documents/{doc_id}"
                doc_resp = requests.get(doc_url, timeout=10)
                if doc_resp.status_code == 200:
                    payload = doc_resp.json()
                    if isinstance(payload, dict) and 'rows' in payload:
                        for section in payload['rows']:
                            dates = None
                            prices = None
                            volumes = None
                            for i, row in enumerate(section):
                                if len(row) >= 3 and row[0] == 'Index prices' and row[2] == 'EUR':
                                    if i + 2 < len(section):
                                        dates = section[i+1]
                                        prices = section[i+2]
                                elif len(row) >= 1 and row[0] in ('Traded volume', 'Index volumes', 'Traded Volume'):
                                    if i + 2 < len(section):
                                        if not dates: 
                                            dates = section[i+1]
                                        volumes = section[i+2]
                            if dates and prices:
                                for idx, d in enumerate(dates):
                                    p = float(prices[idx]) if idx < len(prices) else None
                                    v = float(volumes[idx]) if volumes and idx < len(volumes) and volumes[idx] else 0.0
                                    if p is not None:
                                        market_list.append({
                                            'Datetime': pd.to_datetime(d), 
                                            f'{market}_Price': p,
                                            f'{market}_Volume': v
                                        })
                                break
            time.sleep(SEMOPX_DELAY_S)
        
        if market_list:
            df_m = pd.DataFrame(market_list).drop_duplicates(subset=['Datetime'])
            market_data[market] = df_m
                
    if 'DAM' not in market_data or market_data['DAM'].empty:
        raise ConnectionError(f"EA-001 DAM data not found for {start_date} to {end_date}.")

    df_final = market_data['DAM']
    for m in ['IDA1', 'IDA2', 'IDA3']:
        if m in market_data and not market_data[m].empty:
            df_final = pd.merge(df_final, market_data[m], on='Datetime', how='outer')
        else:
            df_final[f'{m}_Price'] = pd.NA
            df_final[f'{m}_Volume'] = pd.NA
            
    # SEMOpx dates have 'Z' (UTC), so to_datetime parses as tz-aware UTC. Convert to Dublin then strip tz.
    df_final['Datetime'] = pd.to_datetime(df_final['Datetime'], utc=True).dt.tz_convert('Europe/Dublin').dt.tz_localize(None)
    
    # The I-SEM Trading Day runs from 23:00 (D-1) to 22:30 (D) local time.
    start_bound = pd.to_datetime(start_date) - pd.Timedelta(days=1)
    cutoff_start = pd.to_datetime(start_bound.strftime('%Y-%m-%d') + " 23:00:00")
    cutoff_end = pd.to_datetime(end_date + " 22:30:00")
    
    df_final = df_final[(df_final['Datetime'] >= cutoff_start) & (df_final['Datetime'] <= cutoff_end)]
    
    return df_final

def fetch_nordpool_gb_da(start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Fetching Nordpool GB DA data from {start_date} to {end_date}...")
    fetched_data = []
    
    try:
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        for d in dates:
            date_str = d.strftime('%Y-%m-%d')
            url = f"https://dataportal-api.nordpoolgroup.com/api/DayAheadPrices?date={date_str}&market=N2EX_DayAhead&deliveryArea=UK&currency=EUR"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if 'multiAreaEntries' in data:
                    for entry in data['multiAreaEntries']:
                        if 'deliveryStart' in entry and 'entryPerArea' in entry and 'UK' in entry['entryPerArea']:
                            dt = pd.to_datetime(entry['deliveryStart'])
                            if dt.tzinfo is None:
                                dt = dt.tz_localize('UTC').tz_convert('Europe/Dublin').tz_localize(None)
                            else:
                                dt = dt.tz_convert('Europe/Dublin').tz_localize(None)
                            val = entry['entryPerArea']['UK']
                            fetched_data.append({'Datetime': dt, 'GB_DA_Price': float(val)})
            time.sleep(1)
    except Exception as e:
        print(f"Nordpool fetch failed: {e}.")
        
    if not fetched_data:
        print(f"Failed to retrieve valid Nordpool GB DA data for {start_date} to {end_date}. Returning empty DataFrame.")
        return pd.DataFrame()
            
    df = pd.DataFrame(fetched_data).drop_duplicates(subset=['Datetime'])
    return df

