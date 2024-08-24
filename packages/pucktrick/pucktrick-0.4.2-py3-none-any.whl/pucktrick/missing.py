from pucktrick.utils import *
from pucktrick.noisy import *
import pandas as pd
import numpy as np

def missingNew(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  for i, value in enumerate(extracted_list):
    noise_df.loc[i, column] = np.nan 
  return noise_df

def missingExtended(original_df,train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= missingNew(new_df,column,newPercentage)
    i=0
    for index in modified_df['id1']:
        if pd.isnull(modified_df[modified_df['id1']==index][column]).any() and pd.notnull(noise_df[noise_df['id1']==index][column]).any():
            i += 1
            indexer=noise_df[noise_df['id1']==index].index
            noise_df.loc[indexer,column] = np.nan   
    noise_df = noise_df.drop('id1', axis=1)
    return noise_df


