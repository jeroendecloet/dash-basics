import os
import json
import pandas as pd
from typing import Union

DEFAULT_DATAFRAME_NAME = 'df'


def load_csv_to_json(filename: str, **kwargs) -> dict:
    """ Loads a CSV file and converts it to a JSON format. """
    df = pd.read_csv(filename, **kwargs).to_json(orient='split')
    name = os.path.splitext(os.path.basename(filename))[0]
    return {name: df}


def json_to_df_with_key(json_data: Union[str, bytes], key: str, columns: list = None) -> pd.DataFrame:
    """ Converts a DataFrame stored as JSON format back to a DataFrame object. """
    if (json_data is not None) and (key in json_data):
        return pd.read_json(json.loads(json_data)[key], orient='split')
    else:
        return pd.DataFrame(columns=columns)


def json_to_df(json_data: Union[str, bytes], columns: list = None) -> dict[str, pd.DataFrame]:
    """ Converts a serialized JSON object with multiple DataFrames back to a dictionary. """
    if json_data is not None:
        json_dict = json.loads(json_data)
        print(json_dict)
        return {key: pd.read_json(df_str, orient='split') for key, df_str in json_dict.items()}
    else:
        return {DEFAULT_DATAFRAME_NAME: pd.DataFrame(columns=columns)}


def dfs_dict_to_json(dfs: dict[str, pd.DataFrame]) -> str:
    return json.dumps({
        key: df.to_json(orient='split') for key, df in dfs.items()
    })


