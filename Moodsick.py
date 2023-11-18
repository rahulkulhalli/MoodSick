#!/usr/bin/env python
# coding: utf-8

# # DATA FETCH

# In[38]:


# Importing necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# In[39]:


# Reading the csv file for fetching data
main_data = pd.read_csv('tcc_ceds_music.csv')


# In[40]:


# Printing top 5 rows of the dataset to get the better picture 
main_data.head()


# In[41]:


# Printing all the columns of the dataset
main_data.columns


# In[42]:


# Selecting only columns with numeric values, other columns are discarded as they are of no use
desired_cols = ['genre', 'danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy']
df = pd.read_csv('tcc_ceds_music.csv', usecols = desired_cols)
print(df.head())


# In[43]:


# Plotting them to get a rough idea of relation between them
df.plot()


# # CORRELATION MATRIX AND HEATMAP

# In[44]:


# Getting a correlation matrix, which eventually helps to know how two variables are linearly related with each other.
correlation_matrix = df.corr()
print(correlation_matrix)


# In[45]:


# Representing the above correlation with the help of a Heatmap
sns.heatmap(correlation_matrix, annot = True, cmap = 'coolwarm', linewidths = .5)
plt.show()


# # HISTOGRAM PLOTS

# ## Histograms of pairs

# In[46]:


# Creating Histogram plots to show relation between pairs of numeric columns as mentioned above
plt.hist(df['danceability'], bins = 'auto', alpha = 0.7, color = 'red', label = 'danceability')
plt.hist(df['loudness'], bins = 'auto', alpha = 0.7, color = 'green', label = 'loudness')

plt.xlabel('Value')
plt.ylabel('Frequency')
plt.title('Histogram of danceability and loudness')
plt.legend()
plt.show()


# In[47]:


def multiple_hists(dataframe, columns):
    num_columns = len(columns)
    fig, axes = plt.subplots(nrows=num_columns, ncols=num_columns, figsize=(15, 15))
    
    for i in range(num_columns):
        for j in range(num_columns):
            if i != j:
                a = dataframe[columns[i]]
                b = dataframe[columns[j]]
                axes[i, j].hist2d(a, b, bins = (50,50), cmap = 'Blues', alpha = 0.7)
                axes[i, j].set_title(f'{columns[i]} vs {columns[j]}')
                axes[i, j].set_xlabel(columns[i])
                axes[i, j].set_ylabel(columns[j])
                
    plt.tight_layout()
    plt.show()


# In[48]:


columns_list = ['danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy']
multiple_hists(df, columns_list)


# In[49]:


def multiple_hists(dataframe, columns):
    num_columns = len(columns)
    fig, axes = plt.subplots(nrows=num_columns, ncols=num_columns, figsize=(20, 20))
# Running a loop to get all the pairs of the available columns in the dataset   
    for i in range(num_columns):
        for j in range(num_columns):
# Checking for the conditions where i and j are not equal to get different parameters each time
            if i != j:
                a = dataframe[columns[i]]
                b = dataframe[columns[j]]
                axes[i, j].hist2d(a, b, bins = (50,50), cmap = 'Reds', alpha = 0.7)
                axes[i, j].set_title(f'{columns[i]} vs {columns[j]}')
                axes[i, j].set_xlabel(columns[i])
                axes[i, j].set_ylabel(columns[j])
# Density plot along x-axis
                sns.kdeplot(a, ax = axes[i,j], color = 'Blue', fill = True, legend = False)
    
# Density plot along y-axis
                sns.kdeplot(b, ax = axes[i, j].twinx(), color = 'Green', fill = True, legend = False)
#             else:
#                 return print('No output')
                
    plt.tight_layout()
    plt.show()


# In[50]:


columns_list = ['danceability', 'loudness', 'acousticness', 'instrumentalness', 'valence', 'energy']
multiple_hists(df, columns_list)


# # BOXPLOTS

# In[51]:


# Boxplots give a better visualisation for comparison between numeric columns.
# We have to look for min values, max values and Inter Quartile Range and also Outliers.
sns.set(style = 'whitegrid')

plt.figure(figsize=(15, 8))
sns.boxplot(data = df[columns_list])
plt.title('Boxplots for numerical columns')
plt.show()


# In[52]:


# Analysing scatter plot of Instrumentalness
plt.scatter(df['instrumentalness'], range(len(df['instrumentalness'])))
df.transpose()
plt.title('Scatter plot of Instrumentalness')
plt.xlabel('Index')
plt.ylabel('values')
plt.show


# In[55]:


print(df.dtypes)
print(df['instrumentalness'].head())


# In[ ]:




