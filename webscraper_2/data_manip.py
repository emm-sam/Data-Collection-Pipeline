import os
import json
import pandas as pd 


class DataManipulation:
    def __init__(self):
        pass

    def open_json(self, file_path):
        '''
        Opens json file
        Args: file path
        Returns: dictionary
        '''
        with open(file_path, mode='r') as f:
            data = json.load(f)
            return data

    def dump_json(self, file_path, dict, dict_name):
        '''
        Stores dictionary as json file
        Args: 
            file_path: path to where json will be stored 
            dict: dictionary to be stored
            dict_name: name of dict, suffix with ".json"
        '''
        with open(os.path.join(file_path, dict_name), mode='w') as f:
            json.dump(dict, f)

    def list_to_dict(self, listofdicts:list) -> dict:
        '''
        Combines dictionaries in a list to the same dictionary
        Args:
            listofdicts: a list of dictionaries with the SAME keys
        Returns: one dictionary 
        '''
        new_dict = {}
        for k in listofdicts[0].keys():
            new_dict[k] = tuple(new_dict[k] for new_dict in listofdicts)
        return new_dict

    def dict_to_pd(self, dict:dict) -> pd.DataFrame:
        '''
        Transforms dictionary into a pandas dataframe
        '''
        df1 = pd.DataFrame.from_dict(dict, orient='index')
        df1 = df1.transpose()
        return df1