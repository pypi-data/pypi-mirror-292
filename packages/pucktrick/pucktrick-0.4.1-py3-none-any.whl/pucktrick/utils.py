import random
import pandas as pd
import numpy as np

def create_fake_table(num_rows=1000):
  # Generate data for each column
  f1 = np.random.uniform(-100, 100, num_rows)  # Continuous values between -100 and 100
  f2 = np.random.randint(-100, 101, num_rows)  # Discrete values between -100 and 100
  f3 = np.random.choice(['apple', 'banana', 'cherry'], num_rows)  # String values
  f4 = np.random.choice(['apple', 'banana', 'cherry'], num_rows)  # String values
  f5 = np.random.choice([0, 1], num_rows)  # Binary values (0 or 1)
  target = np.random.choice([0, 1], num_rows)  # Binary target (0 or 1)

  # Create the DataFrame
  df = pd.DataFrame({
    'f1': f1,
    'f2': f2,
    'f3': f3,
    'f4': f4,
    'f5': f5,
    'target': target
  })
  return df

def sampleList(percentage, maxValueList ):
    values = int(maxValueList * (percentage))
    extracted_List= random.sample(range(1, maxValueList), values)
    return extracted_List

def generateSubdf(original_df, train_df,column,percentage ):
    rowsToChange=len(original_df[column])*percentage
    dif = original_df[column] != train_df[column]
    diff_number = dif.sum()
    new_rowsToChange=rowsToChange-diff_number
    if new_rowsToChange<=0:
      newPercentage=0
      return train_df,newPercentage
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    or_df=original_df.copy()
    or_df['id1'] = range(len(or_df))
    mask = or_df[column] == noise_df[column]
    new_df = noise_df[mask]
    new_df = new_df.reset_index(drop=True)
    newPercentage=new_rowsToChange/len(new_df)
    return new_df,newPercentage

def mergeDataframe(noise_df,modified_df):

    merged_df = noise_df.merge(modified_df, on='id1', how='left', suffixes=('_df1', '_df2'))
    new_array = [string for string in noise_df.columns if string != 'id1']
    for col in new_array:
      noise_df[col] = merged_df[col + '_df2'].fillna(merged_df[col + '_df1'])
    noise_df = noise_df.drop('id1', axis=1)
    return noise_df

def generate_random_value(lower, upper):
        return np.random.uniform(lower, upper)

def generate_random_value_discrete(lower, upper):
        return np.random.randint(lower, upper)
