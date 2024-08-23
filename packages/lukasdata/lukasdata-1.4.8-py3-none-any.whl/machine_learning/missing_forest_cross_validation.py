from sklearn.model_selection import train_test_split
import pandas as pd
from missing_forest import MissForestImputer
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
#from missingpy import MissForest
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error
from datahandling.change_directory import chdir_sql_requests



# Load your dataset with missing values
# Example: Replace this with your actual data loading process
chdir_sql_requests()
df = pd.read_csv('financialsbvd_ama.csv')



# Arrays to store the errors

def kfold_mse(data,n_splits = 5,missing_forest_iterations=10,missing_proportion=0.1):
    #imputer = MissForest(random_state=42)
    data=filter_numeric_columns(data)
    scaler = StandardScaler()
    data_standardized = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)
    
    mse_scores = []
    mae_scores = []
    column_mse_sum=pd.DataFrame(columns=data.columns)

    column_mse_list=[]
    for train_index, test_index in kf.split(data_standardized):
        train_data = data_standardized.iloc[train_index].copy()
        test_data = data_standardized.iloc[test_index].copy()

        # Artificially introduce missing values in the testing set
        test_data_missing = test_data.copy()
        mask = np.random.rand(*test_data.shape) < missing_proportion
        test_data_missing[mask] = np.nan
        model=MissForestImputer(max_iter=missing_forest_iterations)
        model.run_miss_forest(test_data_missing,insert_id=False)
        test_data_imputed=model.X
        # Fit the imputer on the training data
        #train_data_imputed = imputer.fit_transform(train_data)

        # Transform the artificially missing testing data
        #test_data_imputed = imputer.transform(test_data_missing)

        # Calculate the mask for the artificially missing values in the test set
        # This ensures we only consider the artificially introduced missing values and not the originally missing values
        artificial_mask = mask & ~test_data.isna()
    
    # Create dataframes for the true and imputed values
        true_values_df = test_data.copy()
        imputed_values_df = pd.DataFrame(test_data_imputed, columns=test_data.columns)

        # Extract the values to compare only for the artificially introduced missing values
        difference = (true_values_df - imputed_values_df) ** 2
        column_mse=difference[artificial_mask].sum()/artificial_mask.sum()
        mse = difference[artificial_mask].sum().sum() / artificial_mask.sum().sum()

        # Calculate Mean Absolute Error
        absolute_difference = np.abs(true_values_df - imputed_values_df)
        mae = absolute_difference[artificial_mask].sum().sum() / artificial_mask.sum().sum()

            # Calculate the errors for the imputed values in the test set
        mse_scores.append(mse)
        mae_scores.append(mae)
        column_mse_list.append(column_mse)
    length=len(column_mse_list)
    for index,column in enumerate(column_mse_list):
        if index==0:
            column_sum=column
        else:
            column_sum+=column
    column_mse=column_sum/length
    
        

    return mse_scores,column_mse
    # Store the errors
    

mse_scores,column_mse=kfold_mse(df,missing_forest_iterations=3)
print(column_mse)
from my_logs import build_logger

kfc_validation=build_logger("kfc_validation")

def compare_n_iterations(df,max_range=11,missing_proportion=0.1):
    kfc_validation.log_parameters({"max_range":max_range,"missing_proportion":missing_proportion})
    mse_dict={}
    range_object=range(1,max_range)
    for i in range_object:
        print(f"{i}/{range_object[-1]}")
        mse_scores=kfold_mse(df,missing_forest_iterations=i,missing_proportion=missing_proportion)
        mean_mse = np.mean(mse_scores)
        mse_dict[f"{i} Iterations"]=mean_mse
    kfc_validation.log_performance(mse_dict)
    return mse_dict
 

#iterations_dict=compare_n_iterations(df,missing_proportion=0.2)

#variations with how much we allow in terms of percentage









