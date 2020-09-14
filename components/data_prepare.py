import os
import pandas as pd
from datetime import datetime

from components.constants import DATA_FILE, DATA_DIR, AND_SUBSTR


def get_data() -> pd.DataFrame():
    data_path = os.path.join(DATA_DIR, DATA_FILE)
    data = pd.read_csv(data_path)
    data['MONTH_DT'] = pd.to_datetime(data['MONTH'], format='%Y%m', errors='coerce').dropna()
    data['CLAIM_SPECIALTY'] = data['CLAIM_SPECIALTY'].str.upper().str.strip()
    for item in AND_SUBSTR:
        data['CLAIM_SPECIALTY'] = data['CLAIM_SPECIALTY'].str.replace(item, '/')
    return data


def get_column_vals(data: pd.DataFrame, column_name: str) -> list:
    return sorted(set(data[column_name].dropna().tolist()))


def filter_data(df_data, payer_value, serv_cat_value, cl_spec_value, start_date, end_date) -> pd.DataFrame():
    start_month = convert_date_to_month(start_date)
    end_month = convert_date_to_month(end_date)
    mask = (df_data['MONTH'] >= start_month) & (df_data['MONTH'] <= end_month)
    filtered_df = df_data.loc[mask]
    if payer_value:
        filtered_df = filtered_df[filtered_df['PAYER'].isin(payer_value)]
    if serv_cat_value:
        filtered_df = filtered_df[filtered_df['SERVICE_CATEGORY'].isin(serv_cat_value)]
    if cl_spec_value:
        filtered_df = filtered_df[filtered_df['CLAIM_SPECIALTY'].isin(cl_spec_value)]
    return filtered_df


def convert_month_to_date(month: int) -> str:
    return datetime.strptime(str(month), '%Y%m').strftime('%Y-%m-%d')


def convert_date_to_month(date: str) -> int:
    return int(datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m'))

