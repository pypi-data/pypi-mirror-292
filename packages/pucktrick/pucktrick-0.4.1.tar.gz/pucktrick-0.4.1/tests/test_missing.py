import unittest
from pucktrick.missing import *
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

class Test_outlies(unittest.TestCase):
  def test_MissingAll(self):
      percentage=0.5
      num_rows = 1000
      fake_df=create_fake_table(num_rows)
      target='f3'
      null_values=fake_df[target].isna().sum()
      noise_df=missingNew(fake_df,target,percentage)
      percentage=0.7
      noise_df=missingExtended(fake_df,noise_df,target,percentage)
      new_null_values=noise_df[target].isna().sum()
      if null_values>0:
        diff=round((new_null_values-null_values)/null_values,2)
        self.assertEqual(diff, percentage)
      else:
          df_len=len(noise_df)
          rows=int(df_len*percentage)
          self.assertEqual(new_null_values, rows)


if __name__ == "__main__":
    unittest.main()
