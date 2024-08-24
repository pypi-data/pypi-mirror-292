import unittest
from pucktrick.noisy import *
from pucktrick.utils import * 
import pandas as pd
from pandas.testing import assert_frame_equal
class TestCategorical(unittest.TestCase):
    def test_saluta(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table()
        column='f2'
        noise_df=noiseCategoricalStringNewFakeValues(fake_df,column,percentage)
        print(noise_df)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        noise_df=noiseCategoricalStringExstendedFakeValues(fake_df,noise_df,column,percentage)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
    
        # Verifica che il numero di modifiche sia corretto
        self.assertEqual(diff_p, percentage)
    


if __name__ == "__main__":
    unittest.main()
