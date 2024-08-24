from pucktrick.utils import *
import pandas as pd


def duplicateAllNew(train_df,percentage):
  rowsToChange=len(train_df)*percentage
  old_duplicated=train_df.duplicated().sum()
  new_rowsToChange=rowsToChange-old_duplicated
  if new_rowsToChange<=0:    
      return train_df
  percentage=new_rowsToChange/len(train_df)
  noise_df= train_df.copy()
  df_len=len(noise_df)
  extracted_list=sampleList(percentage,df_len)
  new_lines=int(df_len*percentage)
  for i in range(new_lines):
    tmpdf=train_df.loc[generate_random_value_discrete(0,len(extracted_list))].copy()
    noise_df.loc[len(noise_df)] = tmpdf         
  return noise_df

def duplicateAllExtended(original_df, train_df,percentage):
  rowsToChange=len(original_df)*percentage
  old_duplicated=original_df.duplicated().sum()
  new_duplicated=train_df.duplicated().sum()
  diff=new_duplicated-old_duplicated
  new_rowsToChange=rowsToChange-diff
  if new_rowsToChange<=0:    
      return train_df
  new_percentage=new_rowsToChange/len(original_df)
  noise_df= train_df.copy()
  extracted_list=sampleList(new_percentage,len(original_df))
  new_lines=int(len(original_df)*new_percentage)
  for i in range(new_lines):
    tmpdf=train_df.loc[generate_random_value_discrete(0,len(extracted_list))].copy()
    noise_df.loc[len(noise_df)] = tmpdf         
  return noise_df

def duplicateClassNew(train_df,target, value,percentage):
  target_df=train_df[train_df[target] ==value]
  target_df = target_df.reset_index(drop=True)
  rowsToChange=int(len(target_df)*percentage)
  old_duplicated=target_df.duplicated().sum()
  new_rowsToChange=rowsToChange-old_duplicated
  if new_rowsToChange<=0:    
      return train_df
  percentage=new_rowsToChange/len(target_df)
  noise_df= train_df.copy()
  df_len=len(target_df)
  extracted_list=sampleList(percentage,df_len) 
  for i in range(new_rowsToChange):
    row=generate_random_value_discrete(0,len(extracted_list))
    tmpdf=target_df.loc[row].copy()
    noise_df.loc[len(noise_df)] = tmpdf         
  return noise_df

def duplicateClassExtended(original_df, train_df,target, value,percentage):
  origin_target_df=original_df[original_df[target] ==value]
  target_df=train_df[train_df[target] ==value]
  target_df = target_df.reset_index(drop=True)
  origin_target_df = origin_target_df.reset_index(drop=True)
  rowsToChange=len(origin_target_df)*percentage
  old_duplicated=origin_target_df.duplicated().sum()
  new_duplicated=target_df.duplicated().sum()
  diff=new_duplicated-old_duplicated
  new_rowsToChange=int(rowsToChange-diff)
  if new_rowsToChange<=0:    
      return train_df
  percentage=new_rowsToChange/len(origin_target_df)
  noise_df= train_df.copy()
  df_len=len(origin_target_df)
  extracted_list=sampleList(percentage,df_len) 
  for i in range(new_rowsToChange):
    row=generate_random_value_discrete(0,len(extracted_list))
    tmpdf=origin_target_df.loc[row].copy()
    noise_df.loc[len(noise_df)] = tmpdf         
  return noise_df