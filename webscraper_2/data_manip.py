import os
import json
import pandas as pd 


class DataManipulation:
    def __init__(self):
        pass

    def _open_json(self, file_path):
        '''
        Opens json file
        Args: file path
        Returns: dictionary
        '''
        with open(file_path, mode='r') as f:
            data = json.load(f)
            return data

    def _dump_json(self, file_path, dict, dict_name):
        '''
        Stores dictionary as json file
        Args: 
            file_path: path to where json will be stored 
            dict: dictionary to be stored
            dict_name: name of dict, suffix with ".json"
        '''
        with open(os.path.join(file_path, dict_name), mode='w') as f:
            json.dump(dict, f)

    def _list_to_dict(self, listofdicts:list) -> dict:
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

    def _dict_to_pd(self, dict:dict) -> pd.DataFrame:
        '''
        Transforms dictionary into a pandas dataframe
        Args:
            dict: dictionary to be converted
        Returns: pandas dataframe
        '''
        df1 = pd.DataFrame.from_dict(dict, orient='index')
        df1 = df1.transpose()
        return df1



# [{'name': 'Neroli Mediterraneo', 'price': '£130.00', 'sample': '£85.00, 50 ml EdP', 'token': '£5.00, 1 ml EdP', 'concentration': '£130.00, 100 ml EdP', 'brand': 'Perris Monte Carlo', 'description': ['', '', ''], 'flavours': ['citrusy', 'green'], 'top_notes': ['bergamot', None, 'bigarade', None, 'mandarin', None], 'heart_notes': ['black pepper', None, 'geranium', None, 'ginger', None, 'neroli', None, 'orange blossom', None, 'petitgrain', None], 'base_notes': ['cedarwood', None, 'musk', None, 'orris (iris root)', None], 'related_perfumes': ['Orangers en Fleurs', "Fleur d'Oranger", 'Lacura', 'Run of the River', 'Rayon Vert', 'Pure Azure'], 'url': 'https://bloomperfume.co.uk/products/neroli-mediterraneo', 'href': 'neroli-mediterraneo'}, {'name': 'Nimitr', 'price': '£160.00', 'sample': '£7.00, 1 ml Extrait de Parfum', 'token': '11 tokens, 10 ml Extrait de Parfum', 'concentration': '£160.00, 30 ml Extrait de Parfum', 'brand': 'Parfum Prissana', 'description': [''], 'flavours': ['spicy', 'vintage/old school', 'woody'], 'top_notes': ['aldehydes', None, 'bay', None, 'birch tar', None, 'cade', None, 'castoreum', None, 'cinnamon', None, 'civet', None, 'clary sage', None, 'costus', None, 'galbanum', None, 'gardenia', None, 'haiti vetiver', None, 'hyacinth', None, 'incense', None, 'jasmine', None, 'labdanum', None, 'lavender', None, 'leather', None, 'lemon', None, 'mandarin', None, 'musk', None, 'nutmeg', None, 'oakmoss', None, 'opoponax', None, 'patchouli', None, 'plum', None, 'sandalwood', None, 'styrax', None, 'tobacco', None, 'vanilla', None, 'vetiver', None], 'heart_notes': ['sexy', None], 'base_notes': ['for him', None], 'related_perfumes': ['Ultrahot', 'Rhinoceros (2020) Version II', 'Giardinodiercole', 'Coeur de Noir', 'Ma Nishtana', 'Evernia'], 'url': 'https://bloomperfume.co.uk/products/nimitr', 'href': 'nimitr'}, {'name': 'Ayutthaya (อยุธยา)', 'price': '£160.00', 'sample': '£7.00, 1 ml Extrait de Parfum', 'token': '11 tokens, 10 ml Extrait de Parfum', 'concentration': '£160.00, 30 ml Extrait de Parfum', 'brand': 'Parfum Prissana', 'description': ['', ''], 'flavours': ['green', 'unconventional', 'woody'], 'top_notes': ['aldehydes', None, 'amber', None, 'benzoin', None, 'black tea', None, 'camphor', None, 'champaca', None, 'cinnamon', None, 'coriander', None, 'cumin', None, 'ebony', None, 'gun powder', None, 'incense', None, 'jasmine', None, 'moss', None, 'myrrh', None, 'nutmeg', None, 'opoponax', None, 'papyrus', None, 'patchouli', None, 'sandalwood', None, 'styrax', None, 'teak wood', None, 'vetiver', None], 'heart_notes': ['fresh', None], 'base_notes': ['unisex', None], 'related_perfumes': ['Spice Must Flow', 'Mohragot', 'Santal du Pacifique', 'X Oud', 'Nanban', 'Vi et Armis'], 'url': 'https://bloomperfume.co.uk/products/ayutthaya', 'href': 'ayutthaya'}]
