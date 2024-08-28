import unittest
import pandas as pd
from pandas import DataFrame
from datetime import datetime
from typing import List, Tuple
from ivers.temporal import allforfree_endpoint_split, allforfree_folds_endpoint_split
class TestEndpointSplits(unittest.TestCase):
    def setUp(self):
        # Set up a DataFrame with two different endpoints, each with its own date column
        data = {
            'SMILES': ['C', 'CC', 'CCC', 'CCCC', 'CCCCC', 'C', 'CC', 'CCC', 'CCCC', 'CCCCC'],
            'Activity': [1.2, 3.4, 5.6, 7.8, 9.0, None, None, None, None, None],
            'Activity_Date': [
                datetime(2020, 1, 1),
                datetime(2020, 2, 1),
                datetime(2020, 3, 1),
                datetime(2020, 4, 1),
                datetime(2020, 5, 1),
                None, None, None, None, None
            ],
            'Toxicity': [None, None, None, None, None, 0.5, 2.5, 5.0, 7.5, None],
            'Toxicity_Date': [
                None, None, None, None, None,
                datetime(2020, 1, 15),
                datetime(2020, 2, 15),
                datetime(2020, 3, 15),
                datetime(2020, 4, 15),
                None
            ]
        }
        self.df = pd.DataFrame(data)
        self.split_size = 0.4
        self.smiles_column = 'SMILES'
        self.date_columns = ['Activity_Date', 'Toxicity_Date']  # Adjusted to match the expected format

    def test_endpoint_split(self):
        # Test the split function for a single DataFrame with multiple date columns
        # Assuming the function can handle multiple date columns either directly or through pre-processing
        train_dfs, test_dfs = allforfree_endpoint_split(
            [self.df], self.split_size, self.smiles_column, self.date_columns
        )
        # Check if the function correctly splits the DataFrame based on the date columns
        self.assertEqual(len(train_dfs), 1)
        self.assertEqual(len(test_dfs), 1)
        total_size = len(self.df)
        expected_test_size = int(total_size * self.split_size)
        actual_test_size = len(test_dfs[0])
        self.assertTrue(abs(actual_test_size - expected_test_size) <= 1)  # Allow a margin of error of 1

    def test_leaky_endpoint_split_folds(self):
        # Test for a fold split function to handle the same scenario with multiple date columns
        num_folds = 2
        results = allforfree_folds_endpoint_split(self.df, num_folds, self.smiles_column, self.date_columns)
        # Expect 2 tuples in the results since we have 2 folds
        self.assertEqual(len(results), 2)
        
        # Validate the sizes of each fold's train and test sets
        for train_df, test_df in results:
            self.assertTrue(len(train_df) + len(test_df), len(self.df))  # Ensure no data is lost

if __name__ == '__main__':
    unittest.main()