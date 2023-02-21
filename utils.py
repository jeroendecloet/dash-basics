import os
import json
import pandas as pd
from typing import Union


def load_csv_to_json(filename: str, **kwargs) -> dict:
    """ Loads a CSV file and converts it to a JSON format. """
    df = pd.read_csv(filename, **kwargs).to_json(orient='split')
    name = os.path.splitext(os.path.basename(filename))[0]
    return {name: df}


def json_to_df(json_data: Union[str, bytes], key: str, columns: list = None) -> pd.DataFrame:
    """ Converts a DataFrame stored as JSON format back to a DataFrame object. """
    if (json_data is not None) and (key in json_data):
        return pd.read_json(json.loads(json_data)[key], orient='split')
    else:
        return pd.DataFrame(columns=columns)
