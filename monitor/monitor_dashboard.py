import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import requests

# List of rack IDs to monitor
rack_ids = ["bzAi1DPflIKzg75ipRF3", "LCFEL7NLIqFX4Cw6GQit",  "U2nDDxvRaLm6BNiLhqi6", "3o3ZcwEuKJ7aM0i5g7RY"]

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
for rack_id in rack_ids:
    status = get_process_status(rack_id)
    status['rack_id'] = rack_id
    data.append(status)

# Create Dash application
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
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

if __name__ == '__main__':
    app.run_server(debug=True)