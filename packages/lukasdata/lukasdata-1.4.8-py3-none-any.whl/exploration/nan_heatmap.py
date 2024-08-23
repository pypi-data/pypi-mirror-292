import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datahandling.change_directory import chdir_sql_requests
from cleaning.drop_column_with_na import drop_nan_columns
def nan_heatmap(df,title="NaN Values"):

    plt.figure(figsize=(20, 10))

    # Create a heatmap to visualize NaNs
    sns.heatmap(df.isna(), cbar=False, cmap='viridis', yticklabels=False)

    # Show the plot
    plt.title(title)
    plt.xlabel('Columns')
    plt.ylabel('Rows')
    plt.show()


chdir_sql_requests()
df=pd.read_csv("financialsbvd_ama.csv")
df=drop_nan_columns(df,0.2)
print(df.columns)

nan_heatmap(df)
