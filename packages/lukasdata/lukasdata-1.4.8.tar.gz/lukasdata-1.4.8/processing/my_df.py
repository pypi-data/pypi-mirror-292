import pandas as pd
from datahandling.change_directory import chdir_sql_requests

#building a df subclass?

class mydf(pd.DataFrame):
    def __init__(self) -> None:
        super().__init__()
        self.dropped_columns=None
    def filter_numeric_columns(self,inplace=False):
        columns=self.columns
        new_df=mydf()
        dropped_columns=[]
        for column_name in columns:
            column=self[column_name]
            try:
                pd.to_numeric(column)
                if inplace==False:
                    new_df[column_name]=column
                if inplace==True:
                    self[column_name]=column
            except ValueError:
                dropped_columns.append(column_name)
        if inplace==False:
            new_df.dropped_columns=dropped_columns
            return new_df
        if inplace==True:
            self.dropped_columns=dropped_columns
    def drop_nan_columns(self,max_allowed_na: float=1,inplace=False):
        na_bool=self.isna()
        for column_name in self.columns:
            na_percentage=na_bool[column_name].sum()/len(na_bool)
            if na_percentage > max_allowed_na:
                if inplace==False:
                    df=df.drop(columns=column_name,axis=1)
                if inplace==True:
                    self.drop(columns=column_name,axis=1,inplace=True)
        if inplace==False:
            return df


def concat_dfs(dataframes):
    concat_frames=[dataframe.reset_index(drop=True, inplace=True) for dataframe in dataframes]
    df=pd.concat(concat_frames,ignore_index=True)
    df.reset_index(drop=True,inplace=True)
    return df

def filter_numeric_columns(df):
    columns=df.columns
    new_df=pd.DataFrame()
    dropped_columns=[]
    for column_name in columns:
        column=df[column_name]
        try:
            pd.to_numeric(column)
            new_df[column_name]=column
            print(column_name)
        except ValueError:
            dropped_columns.append(column_name)
            print(f"{column_name} can't be converted to numeric")
    return new_df,dropped_columns

def drop_observations(dataframe_path,column,min_count,output_name):
    chdir_sql_requests()
    df=pd.read_csv(dataframe_path)
    company_counts = df[column].value_counts()
    companies_to_keep = company_counts[company_counts >= min_count].index
    df_filtered = df[df[column].isin(companies_to_keep)]
    df_filtered.to_csv(output_name)
    return df_filtered

def drop_nan_columns(df : pd.DataFrame,max_allowed_na: float=1):
    #should I copy here?
    #bool_df=df.notna()
    na_bool=df.isna()
    for column_name in df.columns:
        na_percentage=na_bool[column_name].sum()/len(na_bool)
        if na_percentage > max_allowed_na:
            df=df.drop(columns=column_name,axis=1)
            #print(f"dropped {column_name}")
    return df

def na_counts(df : pd.DataFrame):
    na_df=pd.isna(df)
    counts=na_df.sum()
    true_rows=counts[counts>=1]
    return true_rows