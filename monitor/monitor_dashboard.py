import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import requests
from dash.dependencies import Input, Output, State
import datetime
import pandas as pd
import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'monitor_data.db')

# Dictionary of rack IDs, their names, tzadd values, and keys to be shown
rack_info = {
    "3o3ZcwEuKJ7aM0i5g7RY": {"name": "Akvárium Klub Csomagmegőrző", "tzadd": 2,
                             "keys": ["ps_controller_handler", "ps_firebase_main", "ps_firebaseremoteadmin", "ps_smartbox", "ps_firefox_process_count", "memory_available_rate", "sda2_usage", "git_infra_commit_behind", "git_screen_commit_behind", "git_iot_commit_behind"]},
    "L3L2BQwvrjMJfTcEdADW": {"name": "Gödöllői Városi Könyvtár", "tzadd": 2,
                             "keys": ["ps_controller_handler", "ps_firebase_main", "ps_firebaseremoteadmin", "ps_smartbox", "ps_firefox_process_count", "memory_available_rate", "sda2_usage"]},
    "U2nDDxvRaLm6BNiLhqi6": {"name": "Ford - M3", "tzadd": 2,
                             "keys": ["ps_controller_handler", "ps_firebase_main", "ps_firebaseremoteadmin", "ps_smartbox", "ps_firefox_process_count", "memory_available_rate", "sda2_usage"]},
    "bzAi1DPflIKzg75ipRF3": {"name": "David Graz Teszt HA controller", "tzadd": 2,
                             "keys": ["ps_controller_handler", "ps_firebase_main", "ps_firebaseremoteadmin", "ps_smartbox", "memory_available_rate", "sda2_usage", "git_infra_commit_behind", "git_screen_commit_behind", "git_iot_commit_behind"]},
    "LCFEL7NLIqFX4Cw6GQit": {"name": "Locker Astoria (Controller)", "tzadd": 2,
                             "keys": ["ps_controller_handler", "ps_firebase_main", "ps_firebaseremoteadmin", "ps_smartbox", "memory_available_rate", "sda2_usage"]},

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
        filtered_status = {k: v for k, v in status.items() if k in info['keys']}
        filtered_status = {
            'rack_id': f"{info['name']} ({rack_id})",
            **filtered_status,
            'memory_available_rate': float(status.get('memory_available_rate', 0)),
            'sda2_usage': 100 - float(status.get('sda2_usage', 0)),
            'git_infra_commit_behind': float(status.get('git_infra_commit_behind', -100)),
            'git_screen_commit_behind': float(status.get('git_screen_commit_behind', -100)),
            'git_iot_commit_behind': float(status.get('git_iot_commit_behind', -100))
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
                    ' && {{{column}}} < {max_bound}'
                ).format(column=column, min_bound=min_bound, max_bound=max_bound),
                'column_id': column
            },
            'background': (
                """
                    linear-gradient(90deg,
                    #53a900 0%,
                    #53a900 {max_bound_percentage}%,
                    #0020d0 {max_bound_percentage}%,
                    #0020d0 100%)
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
            'color': 'black'
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

def git_column_styles(columns):
    styles = []
    for col in columns:
        styles.append({
            'if': {
                'filter_query': '{{{}}} = 0'.format(col),
                'column_id': col
            },
            'backgroundColor': '#FFFFFF',
            'color': 'black'
        })
        styles.append({
            'if': {
                'filter_query': '{{{}}} < 0'.format(col),
                'column_id': col
            },
            'backgroundColor': 'yellow',
            'color': 'white'
        })
        styles.append({
            'if': {
                'filter_query': '{{{}}} > 0 '.format(col),
                'column_id': col
            },
            'backgroundColor': 'red',
            'color': 'black'
        })
    return styles

# Function to create conditional formatting for greyed out cells
def grey_out_styles(columns, rack_info):
    styles = []
    for col in columns:
        for rack_id, info in rack_info.items():
            if col not in info['keys']:
                styles.append({
                    'if': {
                        'filter_query': '{{rack_id}} = "{}"'.format(info['name'] + " (" + rack_id + ")"),
                        'column_id': col
                    },
                    'backgroundColor': 'grey',
                    'color': 'white'
                })
    return styles

# Function to create conditional formatting for rack_id column
def rack_id_styles():
    return [{
        'if': {
            'column_id': 'rack_id'
        },
        'backgroundColor': 'white',
        'color': 'black'
    }]


# Function to check if an SMS record exists in the sms_status table
def check_sms_flag():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM sms_status WHERE sms_sent = 1
    ''')
    result = cursor.fetchone()
    conn.close()
    return result[0] > 0

# Function to remove the SMS record from the sms_status table
def remove_sms_flag():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM sms_status WHERE sms_sent = 1
    ''')
    conn.commit()
    conn.close()

# Create Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Span("Legend: ", style={'fontWeight': 'bold'}),
            html.Span("OK ", style={'backgroundColor': '#00FF00', 'color': 'white', 'padding': '2px 5px'}),
            html.Span("NOT OK - Not running - CHECK it immediately", style={'backgroundColor': 'red', 'color': 'white', 'padding': '2px 5px'}),
            html.Span("NOT OK - Did not got monitor record - need to be checked", style={'backgroundColor': 'yellow', 'color': 'black', 'padding': '2px 5px'}),
            html.Span("OK - Non used", style={'backgroundColor': 'grey', 'color': 'white', 'padding': '2px 5px'})
        ], style={'marginBottom': '20px'})
    ]),
    html.Button('SMS Alert sent OUT - clear status', id='sms-button', n_clicks=0, disabled=not check_sms_flag()),
    dcc.Location(id='url', refresh=False),
    dcc.Interval(id='interval-component', interval=5*60*1000, n_intervals=0),
    html.Div(id='last-refresh', style={'fontSize': 20, 'marginBottom': 20}),
    html.Div(id='page-content')
])

# Define the report layout
def report_layout(data):
    columns = ['rack_id'] + [col for col in data[0].keys() if col.startswith('ps_') or col.startswith('pid_') or col.startswith('git_')] + ['memory_available_rate', 'sda2_usage']
    return html.Div([
        html.H1("Rack Process Status Report"),
        dash_table.DataTable(
            id='status-table',
            columns=[{"name": i, "id": i} for i in columns],
            data=data,
            style_data_conditional=(
                data_bars('memory_available_rate') +
                data_bars('sda2_usage') +
                git_column_styles('git_infra_commit_behind') +
                git_column_styles('git_screen_commit_behind') +
                git_column_styles('git_iot_commit_behind') +
                ps_column_styles(columns) +
                grey_out_styles(columns, rack_info) +
                rack_id_styles()
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

# Callback to handle SMS button click
@app.callback(
    Output('sms-button', 'disabled'),
    [Input('sms-button', 'n_clicks')]
)
def handle_sms_button_click(n_clicks):
    if n_clicks > 0:
        remove_sms_flag()
    return not check_sms_flag()

# Expose server for WSGI
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)