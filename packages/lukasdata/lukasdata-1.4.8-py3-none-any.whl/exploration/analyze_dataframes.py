from count_nans import count_nan
import pandas as pd
from datahandling.change_directory import chdir_sql_requests


def analyze_dataframes(*dfs):
    for i,df in enumerate(dfs):
        print(f"shape of Dataframe {i}: {df.shape}")
    for df in dfs:
        df_nans=count_nan(df)
        print(df_nans)

chdir_sql_requests()
treatments_financials=pd.read_csv("treatmentfinancialsbvd_ama.csv")
financials=pd.read_csv("financialsbvd_ama.csv")

analyze_dataframes(treatments_financials,financials)

    



