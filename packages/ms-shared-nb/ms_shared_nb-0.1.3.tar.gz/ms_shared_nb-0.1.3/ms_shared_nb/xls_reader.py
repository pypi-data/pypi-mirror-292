import pandas as pd


def read_table_from_xls(file_path: str, sheet_nama: str) -> pd.DataFrame:
    return pd.read_excel(file_path, sheet_name=sheet_name)

