import numpy as np
from manipulation.filter_numeric_columns import filter_numeric_columns
from matplotlib import pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
import pandas as pd
from sklearn.model_selection import GridSearchCV
import seaborn as sns




class data():
    def __init__(self,df) -> None:
        self.df=df
        self.ndarray=np.array(self.df)
        self.numeric_df=filter_numeric_columns(self.df)
        self.numeric_array=np.array(self.numeric_df)
        self.statistics=statistics(self.numeric_array,self.df)


class data_3d(data):
    def __init__(self,array_3d) -> None:
        super().__init__()
        self.array_3d=array_3d
        self.ndarray=self.array_3d.flatten()
        
def identify_anamolies(self,kde,i,threshold=0.01):
    densities = np.exp(kde.score_samples(self.ndarray[:, [i]]))
    anomalies = self.ndarray[densities < threshold]
    print(anomalies)

class statistics():
    def __init__(self,ndarray,df) -> None:
        self.ndarray=ndarray
        self.df=df
        self.mean=np.mean(ndarray)
        self.median=np.median(ndarray)
        self.std=np.std(ndarray)
        #self.correlation=np.corrcoef()
        #self.covariance=self.covariance()
        self.hist,self.bins=np.histogram(ndarray,bins=10) #wir müssen sagen welche variable
    def plot_hist(self,max_hists):
        for i in range(max_hists):
            plt.figure(i+1)
            hist=np.histogram(self.ndarray[:,i])
            plt.hist(hist, bins=self.bins, edgecolor='black')
        plt.xlabel('Value')
        plt.ylabel('Frequency')
        plt.title('Histogram')
        plt.grid(True)
        plt.show() 

    def plot_multiple_histograms(self,bins_list=None, title_list=None, xlabel='', ylabel='', colors=None,):
        number_columns=self.ndarray.shape[1]
        num_plots = number_columns

        if not bins_list:
            bins_list = [20] * num_plots

        if not title_list:
            title_list = [''] * num_plots

        if not colors:
            colors = ['blue'] * num_plots

        for i in range(number_columns):
            mean=np.mean(self.ndarray[:,i])
            std=np.std(self.ndarray[:,i])
            hist_range=(mean-std,mean+std)
            plt.figure(i+1)
            plt.hist(np.abs(self.ndarray[:,i]), bins=bins_list[i], color=colors[i],range=hist_range)
            print(self.ndarray[:,i])
            plt.title(self.df.columns[i])
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        
    def kde(self):
        column_names=self.df.columns
        for i in range(len(self.df)):
            data=self.ndarray[:,[i]]
            median = np.median(data)
            std = np.std(data)

            # Define the range dynamically
            range_min = median - std
            range_max = median + std

# Create a range of values
            x_d = np.linspace(range_min, range_max, 5000)[:, np.newaxis]
            bandwidths = np.linspace(0.1, 0.5, 30)

# Use GridSearchCV to find the best bandwidth
            grid = GridSearchCV(KernelDensity(kernel='gaussian'), {'bandwidth': bandwidths}, cv=5)
            grid.fit(data)
            
            # Best bandwidth
            best_bandwidth = grid.best_params_['bandwidth']
            print(f"Best bandwidth: {best_bandwidth}")
            kde = KernelDensity(kernel='gaussian', bandwidth=best_bandwidth).fit(self.ndarray[:,[i]])
            #x = np.linspace(min(self.ndarray[:,i]), max(self.ndarray[:,i]), 1000)
            #log_dens = kde.score_samples(x[:, None])

# Compute the log density
            log_dens = kde.score_samples(x_d)

            # Plot the results
            plt.figure(figsize=(8, 6))
            plt.plot(x_d[:, 0], np.exp(log_dens), label='KDE', color='blue')
            plt.hist(data, bins=30, density=True, alpha=0.5, color='gray', label='Histogram')
            plt.legend()
            plt.title(f'Kernel Density Estimation {column_names[i]}')
            plt.show()
    def corr_heatmap(self):
        columns = [f'{self.df.columns[i]}' for i in range(self.ndarray.shape[1])]
        print(self.ndarray.shape)
        df = pd.DataFrame(self.ndarray, columns=columns)
        # Compute correlation matrix
        corr_matrix = df.corr()
        
        # Create a heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', linewidths=0.5)
        plt.title('Correlation Heatmap')
        plt.show()
        









# Compute the density at specific points


# Identify anomalies (points with low density)
threshold = 0.01  # Example threshold for low density



