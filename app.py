from dash import Dash, dcc, html, Input, Output, callback

import data_viewer

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

url_bar_and_content_div = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


layout_index = html.Div([
    dcc.Link("Navigate to \"data_viewer\"", href="/data_viewer")
])

# index layout
app.layout = url_bar_and_content_div


@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/data_viewer':
        return data_viewer.layout
    else:
        return layout_index


if __name__ == '__main__':
    app.run_server(debug=True)
