from pucktrick.utils import *
from pucktrick.noisy import *
import pandas as pd

def outlierContinuosNew3Sigma(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  mean = np.mean(noise_df[column])
  std_dev = np.std(noise_df[column])
  upper_bound=mean + 3 * std_dev
  lower_bound=mean -3 * std_dev
  new_lower_limit = mean - 4 * std_dev
  new_upper_limit = mean + 4 * std_dev

  for i, value in enumerate(extracted_list):
     if np.random.rand() > 0.5:
        noise_df.loc[i, column] = generate_random_value(upper_bound, new_upper_limit)
     else:
        noise_df.loc[i, column] = generate_random_value(new_lower_limit, lower_bound)
        
  return noise_df

def outlierContinuosExtended3Sigma(original_df, train_df,column,percentage):
  noise_df= train_df.copy()
  noise_df['id1'] = range(len(noise_df))
  new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
  if newPercentage==0:
      return train_df
  modified_df= outlierContinuosNew3Sigma(new_df,column,newPercentage)
  noise_df=mergeDataframe(noise_df,modified_df)
  return noise_df

def outlierDiscreteNew3Sigma(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  mean = np.mean(noise_df[column])
  std_dev = np.std(noise_df[column])
  upper_bound=mean + 3 * std_dev
  lower_bound=mean -3 * std_dev
  new_upper_limit = mean + 4 * std_dev
  new_lower_limit = mean - 4 * std_dev
  if upper_bound==0:
     upper_bound=1
  if new_upper_limit==upper_bound:
     new_upper_limit=5*upper_bound
  
  if lower_bound==0:
     lower_bound=-1
  if new_lower_limit==lower_bound and lower_bound<0:
     new_lower_limit=5*lower_bound
  elif lower_bound>0:
     new_lower_limit=-5*lower_bound
  if upper_bound>new_upper_limit:
      tmp=new_upper_limit
      new_upper_limit=upper_bound
      upper_bound=tmp
  if new_lower_limit>lower_bound:
     tmp=lower_bound
     lower_bound=new_lower_limit
     new_lower_limit=tmp
  for i, value in enumerate(extracted_list):
     if np.random.rand() > 0.5:
        noise_df.loc[i, column] = generate_random_value_discrete(upper_bound, new_upper_limit)
     else:
        noise_df.loc[i, column] = generate_random_value_discrete(new_lower_limit, lower_bound)
        
  return noise_df

def outlierDiscreteExtended3Sigma(original_df, train_df,column,percentage):
  noise_df= train_df.copy()
  noise_df['id1'] = range(len(noise_df))
  new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
  if newPercentage==0:
      return train_df
  modified_df= outlierDiscreteNew3Sigma(new_df,column,newPercentage)
  noise_df=mergeDataframe(noise_df,modified_df)
  return noise_df

def outlierCategoricalIntegerNew(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  max_value = noise_df[column].max()
  min_value=noise_df[column].min()
  if min_value==0:
      min_value=-1
      new_minValue=-5
  elif min_value<0:
      new_minValue=5*min_value
  else:
      new_minValue=-5+min_value
  if max_value==0:
      max_value=1
      new_maxValue=5
  else:
      new_maxValue=2*max_value
  for i, value in enumerate(extracted_list):
     if np.random.rand() > 0.5:
      noise_df.loc[i, column] = np.random.randint(max_value, new_maxValue)
     else:
      noise_df.loc[i, column] = np.random.randint(new_minValue, min_value)
        
  return noise_df

def outliercategoricalIntegerExtended(original_df, train_df,column,percentage):
  noise_df= train_df.copy()
  noise_df['id1'] = range(len(noise_df))
  new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
  if newPercentage==0:
      return train_df
  modified_df= outlierCategoricalIntegerNew(new_df,column,newPercentage)
  noise_df=mergeDataframe(noise_df,modified_df)
  return noise_df

def outlierCategoricalStringNew(train_df,column,percentage):
  extracted_list=sampleList(percentage,len(train_df[column]))
  noise_df= train_df.copy()
  for i, value in enumerate(extracted_list):
    noise_df.loc[i, column] = "puck was here"
  return noise_df

def outliercategoricalStringExtended(original_df, train_df,column,percentage):
  noise_df= train_df.copy()
  noise_df['id1'] = range(len(noise_df))
  new_df,newPercentage=generateSubdf(original_df, noise_df,column,percentage)
  if newPercentage==0:
      return train_df
  modified_df= outlierCategoricalStringNew(new_df,column,newPercentage)
  noise_df=mergeDataframe(noise_df,modified_df)
  return noise_df
