from pucktrick.utils import *
from pucktrick.noisy import *

def wrongLabelsBinaryExtended(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseBinaryNew(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    noise_df[column] = noise_df[column].fillna(0)
    return noise_df

def wrongLabelsBinaryNew(train_df,target,percentage):
    noise_df=noiseBinaryNew(train_df,target,percentage)
    return noise_df

def  wrongLabelsCategoricalNew(train_df,target,percentage):
    noise_df=noiseCategoricalIntNewExistingValues(train_df,target,percentage)
    return noise_df

def wrongLabelsCategoryExtended(train_df,target,percentage):
    noise_df=noiseCategoricalIntExtendedExistingValues(train_df,target,percentage)
    return noise_df



