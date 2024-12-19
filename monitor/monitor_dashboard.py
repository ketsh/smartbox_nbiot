import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import requests
from dash.dependencies import Input, Output, State

# Dictionary of rack IDs and their names
rack_info = {
    "bzAi1DPflIKzg75ipRF3": "David Graz Teszt HA controller",
    "LCFEL7NLIqFX4Cw6GQit": "Locker Astoria (Controller)",
    "U2nDDxvRaLm6BNiLhqi6": "Ford - M3",
    "3o3ZcwEuKJ7aM0i5g7RY": "Akvárium Klub Csomagmegőrző"
}

# Function to get process status for a given rack ID
def get_process_status(rack_id):
    url = f"http://report.mehter.hu:81/api/process_status"
    params = {'rack_id': rack_id}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# Fetch process status for all rack IDs
data = []
for rack_id, name in rack_info.items():
    status = get_process_status(rack_id)
    status['rack_id'] = f"{name} ({rack_id})"
    data.append(status)

# Create Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Define the report layout
report_layout = html.Div([
    html.H1("Rack Process Status Report"),
    dash_table.DataTable(
        id='status-table',
        columns=[{"name": i, "id": i} for i in data[0].keys()],
        data=data,
        style_data_conditional=[
            {
                'if': {
                    'filter_query': '{' + col + '} = "OK"',
                    'column_id': col
                },
                'backgroundColor': 'green',
                'color': 'white'
            } for col in data[0].keys() if col != 'rack_id'
        ] + [
            {
                'if': {
                    'filter_query': '{' + col + '} = "NO"',
                    'column_id': col
                },
                'backgroundColor': 'red',
                'color': 'white'
            } for col in data[0].keys() if col != 'rack_id'
        ]
    )
])

# Define the access denied layout
access_denied_layout = html.Div([
    html.H1("Access Denied")
])

# Update the page content based on the URL
@app.callback(Output('page-content', 'children'),
              [Input('url', 'search')])
def display_page(search):
    from urllib.parse import parse_qs
    query_params = parse_qs(search[1:])
    api_key = query_params.get('api_key', [None])[0]
    if api_key == "J7r4Z2j1JvJj4Z5DQ0bM":
        return report_layout
    else:
        return access_denied_layout

# Expose server for WSGI
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)