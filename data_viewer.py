import os
import glob
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, callback, Input, Output, dash_table
import dash.dependencies as dd
from dash.exceptions import PreventUpdate

import utils as putils

# File loading
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
    multi=True,
    id="data-files"
)
data_load_button = html.Button(
    id='data-load-button',
    n_clicks=0,
    children='Load file(s)'
)
data_loaded_data = dcc.Store(
    id='data-loaded-data'
)
div_file_loading = html.Div([
    html.Div([html.Label("Directory: "), input_base_path]),
    html.Div([html.Label("Filename"), dropdown_files], style={"display": "inline-block", 'width': "30vw"}),
    html.Div([data_load_button]),
    data_loaded_data
])

# Graphs
data_figure = dcc.Graph(
    id='figure'
)

# Table
input_add_column = dcc.Input(
    value='',
    placeholder="Enter a column name...",
    id="input-add-column",
    style={'padding': 10}
)
button_add_column = html.Button(
    children='Add Column',
    n_clicks=0,
    id='adding-columns-button'
)
button_add_row = html.Button(
    children='Add Row',
    n_clicks=0,
    id='adding-rows-button'
)
_fixed_columns = ['file', 'x', 'y']
table_dropdown_columns = [
    dcc.Dropdown(
        options=[],
        value=None,
        id=f"table-dropdown-{col}"
    ) for col in _fixed_columns
]
_variable_columns = ['mode']
table_graph_parameters = dash_table.DataTable(
    id="table-graph-parameters",
    columns=[
        {
            "name": f"{col}",
            "id": f"{col}",
            "deletable": False,
            "renamable": False,
            "editable": True,
            "presentation": 'dropdown'
        } for col in _fixed_columns
    ] + [
        {
            "name": f"{col}",
            "id": f"{col}",
            "deletable": True,
            "renamable": True,
            "editable": True,
            "presentation": "input"
        } for col in _variable_columns
    ],
    data=pd.DataFrame(columns=_fixed_columns + _variable_columns).to_dict('records'),
    editable=True,
    row_deletable=True,
    style_cell={
        'minWidth': '100px',
        'width': '100px',
        'maxWidth': '200px',
        'whiteSpace': 'normal'
    },
    dropdown={},
    dropdown_conditional=[]
)


_div_add_column = html.Div([
    input_add_column,
    button_add_column
], style={'height': 50})

div_table = html.Div([
    _div_add_column,
    table_graph_parameters,
    button_add_row
])

# Final layout
layout = html.Div([
    html.H3("Data visualisation"),
    div_file_loading,
    data_figure,
    div_table
])


################################################################################
# FILE LOADING
################################################################################

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
    dd.State(dropdown_files, "value"),
    dd.State(data_loaded_data, "data")
)
def load_file(n_clicks, value, data_json):
    """ Loads the CSV file from the dropdown menu into memory. """
    if (value is None) or (n_clicks == 0):
        return data_json
    else:
        if data_json is None:
            data_json = "{}"

        data = putils.json_to_df(data_json)
        keys_in_data = set(list(data.keys()))
        keys_from_dropdown = set([os.path.splitext(os.path.basename(filename))[0] for filename in value])
        _to_add = keys_from_dropdown.difference(keys_in_data)
        _to_remove = keys_in_data.difference(keys_from_dropdown)

        if _to_add:
            _files = [_file for _file in value if os.path.splitext(os.path.basename(_file))[0] in _to_add]
            for _file, path in zip(_to_add, _files):
                data = {**data, **{_file: pd.read_csv(path)}}

        if _to_remove:
            for _file in _to_remove:
                del data[_file]

        return putils.dfs_dict_to_json(data)


################################################################################
# TABLE
################################################################################
@callback(
    dd.Output(table_graph_parameters, 'data'),
    Input(button_add_row, 'n_clicks'),
    dd.State(table_graph_parameters, 'data'),
    dd.State(table_graph_parameters, 'columns'))
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


@callback(
    dd.Output(table_graph_parameters, 'columns'),
    Input(button_add_column, 'n_clicks'),
    dd.State(input_add_column, 'value'),
    dd.State(table_graph_parameters, 'columns'))
def update_columns(n_clicks, value, existing_columns):
    if n_clicks > 0:
        existing_columns.append({
            'id': value, 'name': value,
            'renamable': True, 'deletable': True
        })
    return existing_columns


@callback(
    dd.Output(table_graph_parameters, "dropdown"),
    dd.Output(table_graph_parameters, "dropdown_conditional"),
    dd.Input(data_loaded_data, 'data'),
    dd.State(dropdown_files, "value"),
)
def update_table_dropdowns(data_json, value):
    """
    Updates the dropdown list of the `file`, `x` and `y` columns in the graph parameter table.
    """
    if value is None:
        return {}, []

    # keys_from_dropdown = set([os.path.splitext(os.path.basename(filename))[0] for filename in value])
    # dfs = {key: putils.json_to_df(data_json, key) for key in keys_from_dropdown}
    dfs = putils.json_to_df(data_json)

    files = dfs.keys()
    columns = {key: df.columns for key, df in dfs.items()}

    dropdown = {
        "file": {
            "options": [
                {"label": i, "value": i}
                for i in files
            ]
        }
    }
    dropdown_conditional = [
        {
            "if": {
                'column_id': table_col,
                "filter_query": "{file} eq \"%s\"" % _file
            },
            "options": [
                {"label": col, "value": col}
                for col in columns[_file]
            ]
        } for _file in files for table_col in ['x', 'y']
    ]
    return dropdown, dropdown_conditional


################################################################################
# GRAPH
################################################################################
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


@callback(
    dd.Output(data_figure, "figure"),
    dd.Input(data_loaded_data, "data")
)
def update_graph(data_json):
    if data_json:
        df = putils.json_to_df(data_json)['example_data']
    else:
        df = pd.DataFrame(data={'Date': pd.to_datetime(['2022-01-01']), 'Value': [np.nan]})

    fig = line_plot(df)
    return fig