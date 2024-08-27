import pandas as pd

def summarize_df(df):
    # Get column types
    column_types = df.dtypes.rename('column_type')
    
    # Get column summaries using describe()
    column_summary = df.describe().transpose()
    column_summary.rename(columns={'50%': 'median'}, inplace=True)
    
    # Merge column types and summaries into a single DataFrame
    summary_df = pd.concat([column_types, column_summary], axis=1)
    
    # Set index range from 0 to number of columns
    summary_df.reset_index(inplace=True)
    summary_df.index.name = None
    
    # Rename index and columns
    summary_df.rename(columns={'index': 'column_name'}, inplace=True)
    
    return summary_df
