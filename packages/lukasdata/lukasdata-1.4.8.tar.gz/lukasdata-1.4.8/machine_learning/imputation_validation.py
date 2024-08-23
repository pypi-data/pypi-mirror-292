import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.metrics import mean_absolute_error
from datahandling.change_directory import chdir_sql_requests
from cleaning.drop_column_with_na import drop_nan_columns
from sklearn.preprocessing import StandardScaler

def calculate_mae_for_imputation(data,imputer,missing_rate=0.1,random_state=None,max_na=0.5):
    data = data.select_dtypes(include=[np.number,int,float])
    data=drop_nan_columns(data,max_na)
    df=data.copy()
    np.random.seed(random_state)
    data = np.array(data)
    scaler=StandardScaler().fit(data)
    data=scaler.transform(data)
    data_with_nan = data.copy()

    original_values_per_column = {}
    imputed_values_per_column = {}
    missing_indices_per_column = {}

    # Iterate over each column to introduce missing values and calculate MAE
    for col in range(data.shape[1]):
        existing_missing_mask = np.isnan(data[:, col])
        
        total_elements = data[:, col].size
        num_new_missing = int(missing_rate * total_elements)
        available_indices = np.where(~existing_missing_mask)[0]
        
        if len(available_indices) < num_new_missing:
            raise ValueError("Not enough available indices to introduce missing values at the specified rate.")
        
        # Randomly select indices for new missing values
        new_missing_indices = np.random.choice(available_indices, num_new_missing, replace=False)
        
        # Create a mask with new missing values for the current column
        data_with_nan[new_missing_indices, col] = np.nan

        # Store original and imputed values for the current column
        original_values_per_column[col] = data[new_missing_indices, col]

        missing_indices_per_column[col]=new_missing_indices

    # Apply k-NN imputation
    #imputer = KNNImputer(n_neighbors=n_neighbors)
    imputed_data = imputer.fit_transform(data_with_nan)

    mae_per_column = {}
    
    # Calculate MAE for each column
    for col in range(data.shape[1]):

        #new_missing_indices = np.where(np.isnan(data_with_nan[:, col]))[0]
        #imputed_values_per_column[col] = imputed_data[new_missing_indices, col]
        new_missing_indices=missing_indices_per_column[col]
        imputed_values_per_column[col] = imputed_data[new_missing_indices, col]
        mae = mean_absolute_error(original_values_per_column[col], imputed_values_per_column[col])
        mae_per_column[df.columns[col]] = mae

    
    return mae_per_column

def repeat_validation(df,imputer,iterations,missing_rate=0.1):
    dict_list=[]
    for i in range(iterations):
        mae_dict=calculate_mae_for_imputation(df,imputer,missing_rate)
        dict_list.append(mae_dict)
    mae_df=pd.DataFrame(dict_list)
    mae_df_agg=mae_df.agg("mean",axis=0)
    return mae_df_agg,mae_df



def return_bad_imputations(metric_df,maximum_metric):
    #metric_df_agg=metric_df.agg("mean").sort_values()
    bad_imputations=metric_df[metric_df>=maximum_metric]
    return bad_imputations

