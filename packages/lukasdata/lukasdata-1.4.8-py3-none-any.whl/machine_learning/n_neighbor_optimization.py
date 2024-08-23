import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
import seaborn as sns
import matplotlib.pyplot as plt
from imputation_validation import repeat_validation

def optimize_n_neighnors(df,neighbor_interval,repititions=5):
    df_list=[]
    for i in range(neighbor_interval[0],neighbor_interval[1]):
        imputer=KNNImputer(n_neighbors=i)
        mae_df_agg,mae_df=repeat_validation(df,imputer,repititions)
        df_list.append(mae_df_agg)
    df=pd.concat(df_list,axis=1).T
    df.index=range(neighbor_interval[0],neighbor_interval[1])
    return df

def plot_n_neighbor_optimization(df):
    df.index.name="neighbors"
    df.reset_index(inplace=True)
    df_melted = df.melt(id_vars='neighbors', var_name='feature', value_name='mae')
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_melted, x='neighbors', y='mae', hue='feature', marker='o')
    plt.xlabel('Number of Neighbors')
    plt.ylabel('MAE')
    plt.title('MAE vs. Number of Neighbors for Each Feature')
    plt.grid(True)
    plt.show()