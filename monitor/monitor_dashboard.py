import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import requests
from dash.dependencies import Input, Output, State
import datetime
import pandas as pd

# Dictionary of rack IDs, their names, and tzadd values
rack_info = {
    "bzAi1DPflIKzg75ipRF3": {"name": "David Graz Teszt HA controller", "tzadd": 1},
    "LCFEL7NLIqFX4Cw6GQit": {"name": "Locker Astoria (Controller)", "tzadd": 2},
    "U2nDDxvRaLm6BNiLhqi6": {"name": "Ford - M3", "tzadd": 2},
    "3o3ZcwEuKJ7aM0i5g7RY": {"name": "Akvárium Klub Csomagmegőrző", "tzadd": 2},
    "L3L2BQwvrjMJfTcEdADW": {"name": "Gödöllői Városi Könyvtár", "tzadd": 2}
}

# Function to get process status for a given rack ID
def get_process_status(rack_id, tzadd):
    url = f"http://report.mehter.hu:81/api/process_status"
    params = {'rack_id': rack_id, 'tzadd': tzadd}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# Fetch process status for all rack IDs
def fetch_data():
    data = []
    for rack_id, info in rack_info.items():
        status = get_process_status(rack_id, info['tzadd'])
        filtered_status = {k: v for k, v in status.items() if k.startswith('ps_')}
        filtered_status = {
            'rack_id': f"{info['name']} ({rack_id})",
            **filtered_status,
            'memory_available_rate': float(status.get('memory_available_rate', 0)),
            'sda2_usage': 100-float(status.get('sda2_usage', 0))
        }
        data.append(filtered_status)
    return data

# Function to create data bars
def data_bars(column):
    n_bins = 100
    bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
    styles = []
    for i in range(1, len(bounds)):
        min_bound = (i - 1) * (100 / n_bins)
        max_bound = i * (100 / n_bins)
        max_bound_percentage = bounds[i] * 100
        styles.append({
            'if': {
                'filter_query': (
                    '{{{column}}} >= {min_bound}' +
                    (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #00FF00 0%,
                    #00FF00 {max_bound_percentage}%,
                    #FF0000 {max_bound_percentage}%,
                    #FF0000 100%)
                """.format(max_bound_percentage=max_bound_percentage)
            ),
            'paddingBottom': 2,
            'paddingTop': 2
        })

    return styles

# Function to create conditional formatting for ps_% columns
def ps_column_styles(columns):
    styles = []
    for col in columns:
        styles.append({
            'if': {
                'filter_query': '{{{}}} = "OK"'.format(col),
                'column_id': col
            },
            'backgroundColor': '#00FF00',
            'color': 'white'
        })
        styles.append({
            'if': {
                'filter_query': '{{{}}} = "NO"'.format(col),
                'column_id': col
            },
            'backgroundColor': 'red',
            'color': 'white'
        })
        styles.append({
            'if': {
                'filter_query': '{{{}}} = ""'.format(col),
                'column_id': col
            },
            'backgroundColor': 'yellow',
            'color': 'black'
        })
    return styles

# Create Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0),
    html.Div(id='last-refresh', style={'fontSize': 20, 'marginBottom': 20}),
    html.Div(id='page-content')
])

# Define the report layout
def report_layout(data):
    columns = [col for col in data[0].keys() if col.startswith('ps_')]
    return html.Div([
        html.H1("Rack Process Status Report"),
        dash_table.DataTable(
            id='status-table',
            columns=[{"name": i, "id": i} for i in data[0].keys()],
            data=data,
            style_data_conditional=(
                data_bars('memory_available_rate') +
                data_bars('sda2_usage') +
                ps_column_styles(columns)
            )
        )
    ])

# Define the access denied layout
access_denied_layout = html.Div([
    html.H1("Access Denied")
])

# Update the page content based on the URL and interval
@app.callback(
    [Output('page-content', 'children'), Output('last-refresh', 'children')],
    [Input('url', 'search'), Input('interval-component', 'n_intervals')]
)
def display_page(search, n_intervals):
    from urllib.parse import parse_qs
    query_params = parse_qs(search[1:])
    api_key = query_params.get('api_key', [None])[0]
    if api_key == "J7r4Z2j1JvJj4Z5DQ0bM":
        data = fetch_data()
        last_refresh = f"Last Refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return report_layout(data), last_refresh
    else:
        return access_denied_layout, ""

# Expose server for WSGI
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)