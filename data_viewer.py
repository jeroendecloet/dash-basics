import os
import glob

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output
import dash.dependencies as dd
from dash.exceptions import PreventUpdate


input_base_path = dcc.Input(
    placeholder="Enter a data path...",
    type="text",
    value='',
    id="data-base-path",
    style={"width": "30vw"}
)
dropdown_files = dcc.Dropdown(
    options=[],
    value=None,
    id="data-files"
)

data_load_button = html.Button(
    id='data-load-button',
    n_clicks=0,
    children='Load'
)

data_figure = dcc.Graph(
    id='figure'
)

data_loaded_data = dcc.Store(
    id='data-loaded-data'
)


layout = html.Div([
    html.H3("Data visualisation"),
    html.Div([
        html.Div([html.Label("Directory: "), input_base_path]),
        html.Div([html.Label("Filename"), dropdown_files], style={"display": "inline-block", 'width': "30vw"}),
        html.Div([data_load_button])
    ]),
    data_figure,
    data_loaded_data
])


def line_plot(df: pd.DataFrame) -> go.Figure:

    data = [{
        "x": df["Date"],
        "y": df["Value"],
        "mode": "lines"
    }]

    _layout = {"title": "Some plot"}

    fig = go.Figure({
        "data": data,
        "layout": _layout
    })

    return fig


def get_data() -> pd.DataFrame:
    df = pd.DataFrame(
        index=pd.DatetimeIndex(pd.date_range("2020-01-01", freq='D', periods=10), name='Date'),
        data={"A": range(10)}
    )
    return df


@callback(
    Output(dropdown_files, "options"),
    Input(input_base_path, "value")
)
def update_dropdown_files(value):
    if not os.path.isdir(value):
        raise PreventUpdate("File path invalid!")
    else:
        return glob.glob(os.path.join(value, '*.csv'))


@callback(
    dd.Output(data_loaded_data, "data"),
    Input(data_load_button, "n_clicks"),
    dd.State(dropdown_files, "value")
)
def load_file(n_clicks, value):
    """ Loads the CSV file from the dropdown menu into memory. """
    if value is None:
        return None
    else:
        df = pd.read_csv(value)
        return df.to_json(date_format="iso", orient="split")


@callback(
    dd.Output(data_figure, "figure"),
    dd.Input(data_loaded_data, "data")
)
def update_graph(data_json):
    if data_json:
        df = pd.read_json(data_json, orient='split')
    else:
        df = pd.DataFrame(data={'Date': pd.to_datetime(['2022-01-01']), 'Value': [np.nan]})

    fig = line_plot(df)
    return fig
