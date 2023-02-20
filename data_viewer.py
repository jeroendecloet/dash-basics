from dash import dcc, html, callback, Input, Output
import dash.dependencies as dd
import pandas as pd
import plotly.graph_objects as go


load_button = html.Button(
    id='data-load-button',
    n_clicks=0,
    children='Load'
)

figure_data = dcc.Graph(
    id='figure'
)

layout = html.Div([
    html.H3("Data visualisation"),
    html.Div([load_button]),
    figure_data
])


def line_plot(df: pd.DataFrame) -> go.Figure:

    data = [{
        "x": df.index.tolist(),
        "y": df["A"].values.tolist(),
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
    dd.Output(figure_data, "figure"),
    Input(load_button, "n_clicks")
)
def update_graph(n_clicks):
    df = get_data()
    fig = line_plot(df)
    return fig
