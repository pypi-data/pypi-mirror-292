from pucktrick.utils import *
import pandas as pd


def noiseCategoricalStringNewExistingValues(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  unique_values = noise_df[column].unique()
  for i, value in enumerate(extracted_list):
     while True:
        new_value=np.random.choice(unique_values)
        if new_value != noise_df.loc[i, column]:
            noise_df.loc[i, column] = new_value
            break
  return noise_df




def noiseCategoricalStringExtendedExistingValues(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseCategoricalStringNewExistingValues(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df

def noiseCategoricalStringNewFakeValues(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  unique_values = noise_df[column].unique()
  for i, value in enumerate(extracted_list):
    noise_df.loc[i, column] = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5))
  return noise_df

def noiseCategoricalStringExstendedFakeValues(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseCategoricalStringNewFakeValues(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df

def noiseCategoricalIntNewExistingValues(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  unique_values = noise_df[column].unique()
  for i, value in enumerate(extracted_list):
     while True:
        new_value=np.random.choice(unique_values)
        if new_value != noise_df.loc[i, column]:
            noise_df.loc[i, column] = new_value
            break
  return noise_df

def noiseCategoricalIntExtendedExistingValues(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseCategoricalStringNewExistingValues(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df



def noiseDiscreteExtended(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseDiscreteNew(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df


def noiseDiscreteNew(train_df,column,percentage):
    extracted_list=sampleList(percentage,len(train_df[column]))
    noise_df= train_df.copy()
    min = noise_df[column].min()
    max = noise_df[column].max()

    for i, value in enumerate(extracted_list):
       while True:
        new_value=random.randint(min,max)
        if new_value != noise_df.loc[i, column]:
            noise_df.loc[i, column] = new_value
            break
    return noise_df


def noiseBinaryNew(train_df,target,percentage):
  noise_df= train_df.copy()
  extracted_list=sampleList(percentage,len(noise_df[target])-1)
  for i, value in enumerate(extracted_list):
    if pd.isna(noise_df.loc[i, target]):
        noise_df.loc[i, target]=0
    else:
      existingValue=noise_df.loc[i, target]
      noise_df.loc[i, target]=1-existingValue
  return noise_df

def noiseBinaryExtended(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseBinaryNew(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df
def noiseContinueExtended(original_df, train_df,column,percentage):
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
    if newPercentage==0:
      return train_df
    modified_df= noiseContinueNew(new_df,column,newPercentage)
    noise_df=mergeDataframe(noise_df,modified_df)
    return noise_df


def noiseContinueNew(train_df,column,percentage):
    extracted_list=sampleList(percentage,len(train_df[column]))
    noise_df= train_df.copy()
    min = noise_df[column].min()
    max = noise_df[column].max()

    for i, value in enumerate(extracted_list):
       while True:
        new_value=random.uniform(min,max)
        if new_value != noise_df.loc[i, column]:
            noise_df.loc[i, column] = new_value
            break
    return noise_df


