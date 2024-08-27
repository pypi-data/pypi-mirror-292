import pandas as pd
import numpy as np
import re

from collections import defaultdict


def columns_by_type(df):
    columns_by_type_dict = defaultdict(list)

    def try_convert(column, type_to_try):
        try:
            if type_to_try == 'numeric':
                df[column] = pd.to_numeric(df[column])
            elif type_to_try == 'datetime':
                df[column] = pd.to_datetime(df[column])
            elif type_to_try == 'categorical':
                df[column] = df[column].astype('category')
            return True
        except (ValueError, TypeError):
            return False

    for col in df.columns:
        # if column has no values it will be nan
        col_dtype = df[col].dtype
        if  pd.api.types.is_datetime64_any_dtype(df[col]):
            columns_by_type_dict["datetime"].append(col)
        elif pd.api.types.is_numeric_dtype(df[col]):
            columns_by_type_dict["numeric"].append(col)
        elif df[col].isnull().all():
            columns_by_type_dict["nan"].append(col)
        elif try_convert(col, 'numeric'):
            columns_by_type_dict["numeric"].append(col)
        elif try_convert(col, 'datetime'):
            columns_by_type_dict["datetime"].append(col)
        else:
            columns_by_type_dict["object"].append(col)

    return columns_by_type_dict


def find_correlated_columns(df, min_threshold=-0.9, max_threshold=0.9):
    corr_matrix = df.corr().abs()
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    return [
        col
        for col in upper_tri.columns
        if any(upper_tri[col] > max_threshold)
        or any(upper_tri[col] < min_threshold)
    ]

def find_columns_with_missing_values(df, missing_threshold=0.5):
    missing_cols = [col for col in df.columns if (df[col].isnull().sum() / len(df)) > missing_threshold]
    for col in missing_cols:
        try:
            df[col] = df[col].fillna(df[col].median())
        except TypeError:
            df[col] = df[col].fillna(df[col].mode()[0])
    return missing_cols


def filter_df_by_date_filter(df, filter_string, index_is_date=True, date_col=None):
    """
    Filters a DataFrame based on a date filter string.

    The function assumes that the DataFrame's index or a specific column contains datetime data and will filter the DataFrame based on the provided filter_string.

    Args:
    filter_string (str): The date filter string. The filter string can have the following formats:
        'yYY' or 'yYYYY': Filters the DataFrame to include only data from a specific year. 
                          For example, 'y21' or 'y2021' would include only data from 2021.
        'mMM': Filters the DataFrame to include only data from a specific month of the current year. 
                For example, 'm08' would include only data from August of the current year.
        'ymYYYYMM': Filters the DataFrame to include only data from a specific month and year. 
                     For example, 'ym202108' would include only data from August 2021.
        'rangeYYYYMMDD-YYYYMMDD': Filters the DataFrame to include only data within a specific date range.
                                   For example, 'range20210801-20210831' would include only data from August 1, 2021, through August 31, 2021.
    index_is_date (bool, optional): If True, the function will use the DataFrame's index for filtering. 
                                     If False, it will use the specified date column. Default is True.
    """
    # Ensure date column or index is in datetime format
    if index_is_date:
        df.index = pd.to_datetime(df.index)
        date_series = df.index.to_series()
    else:
        if date_col is None or date_col not in df.columns:
            raise ValueError("date_col must be specified if index_is_date is False.")
        
        df[date_col] = pd.to_datetime(df[date_col])
        date_series = df[date_col]

    if re.search(r'y\d{2,4}', filter_string):  # format: yYY or yYYYY
        if len(filter_string) == 3:  # format: yYY
            year = int('20' + filter_string[1:])
            return df[date_series.dt.year == year]
        elif len(filter_string) == 5:  # format: yYYYY
            year = int(filter_string[1:])
            return df[date_series.dt.year == year]

    elif filter_string.startswith('m'):  # format: mMM
        if len(filter_string) == 3:
            month = int(filter_string[1:])
            return df[(date_series.dt.month == month) & (date_series.dt.year == pd.to_datetime('today').year)]

    elif filter_string.startswith('ym'):  # format: ymYYYYMM
        if len(filter_string) == 8:
            year = int(filter_string[2:6])
            month = int(filter_string[6:])
            print(year, month)
            return df[(date_series.dt.year == year) & (date_series.dt.month == month)]
            
    elif filter_string.startswith('range'):  # format: rangeYYYYMMDD-YYYYMMDD
        dates = filter_string[5:].split('-')
        start_date, end_date = pd.to_datetime(dates[0]), pd.to_datetime(dates[1])
        return df[(date_series >= start_date) & (date_series <= end_date)]

    else:
        raise ValueError("Invalid filter string.")
    
    return df


def filter_df_by_filter_type(df, filter_type, filter_value, index_is_date=True, date_col=None):
    """
    args:
        filter_type: str
            one of ['column_regex', 'column_type', 'date_string']
        filter_value: str
            value to filter by
    """    
    if filter_type == 'column_regex':
        return df.filter(regex=filter_value)
    elif filter_type == 'column_type':
        columns_by_type_dict = columns_by_type(df)
        col_types = filter_value.split(',')
        cols = []
        for _col_type in col_types:
            cols.extend(columns_by_type_dict[_col_type])
        return df[cols]
    elif filter_type == 'date_string':
        return filter_df_by_date_filter(df, filter_value, index_is_date=index_is_date, date_col=date_col)
    else:
        raise ValueError("Invalid filter type. Must be one of ['column_regex', 'column_type', 'date_string']")

