import unittest
from pucktrick.outliers import *
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

class Test_outlies(unittest.TestCase):
  

  def test_outliersCategoricalString(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table(num_rows)
        column='f3'
        noise_df=outlierCategoricalStringNew(fake_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        percentage=0.7
        noise_df=outliercategoricalStringExtended(fake_df,noise_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
        self.assertEqual(diff_p, percentage)
  
  def test_outliersCategoricalInt(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table(num_rows)
        column='f2'
        noise_df=outlierCategoricalIntegerNew(fake_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        percentage=0.7
        noise_df=outliercategoricalIntegerExtended(fake_df,noise_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
        self.assertEqual(diff_p, percentage)
  
  def test_outliersdiscrete(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table(num_rows)
        column='f2'
        noise_df=outlierDiscreteNew3Sigma(fake_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        percentage=0.7
        noise_df=outlierDiscreteExtended3Sigma(fake_df,noise_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
        # Verifica che il numero di modifiche sia corretto
        self.assertEqual(diff_p, percentage)

  def test_outlierscontinous(self):
        percentage=0.5
        num_r = 1000
        fake_df=create_fake_table(num_r)
        #fake_df=pd.read_csv("age_predictions_cleaned-3.csv", sep=";")
        num_rows=len(fake_df)
        column='f1'
        noise_df=outlierContinuosNew3Sigma(fake_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = float(dif.sum())
        percentage=0.7
        noise_df=outlierContinuosExtended3Sigma(fake_df,noise_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=round(diff_number/num_rows,2)
        test="target"
        # Verifica che il numero di modifiche sia corretto
        self.assertEqual(diff_p,percentage)

    


if __name__ == "__main__":
    unittest.main()
