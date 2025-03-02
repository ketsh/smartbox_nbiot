import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import requests
import datetime
import sqlite3
import os
from monitor_config import rack_info

db_path = os.path.join(os.path.dirname(__file__), 'monitor_data.db')
st.set_page_config(layout="wide")
# update every 5 mins
st_autorefresh(interval=5 * 60 * 1000, key="dataframerefresh")


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
        }
        if 'memory_available_rate' in info['keys']:
            filtered_status['memory_available_rate'] = int(status.get('memory_available_rate', 0))
        else:
            filtered_status['memory_available_rate'] = -1

        if 'sda2_usage' in info['keys']:
            filtered_status['sda2_usage'] = 100 - int(status.get('sda2_usage', 0))
        else:
            filtered_status['sda2_usage'] = -1

        if 'git_infra_commit_behind' in info['keys']:
            filtered_status['git_infra_commit_behind'] = int(status.get('git_infra_commit_behind', -100))
        else:
            filtered_status['git_infra_commit_behind'] = -1

        if 'git_screen_commit_behind' in info['keys']:
            filtered_status['git_screen_commit_behind'] = int(status.get('git_screen_commit_behind', -100))
        else:
            filtered_status['git_screen_commit_behind'] = -1

        if 'git_iot_commit_behind' in info['keys']:
            filtered_status['git_iot_commit_behind'] = int(status.get('git_iot_commit_behind', -100))
        else:
            filtered_status['git_iot_commit_behind'] = -1

        data.append(filtered_status)
    return data

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

# Streamlit layout
st.title("Rack Process Status Report")

# Display legend
st.markdown("""
**Legend:**
- **OK**: Process is running
- **NOT OK - Not running - CHECK it immediately**: Process is not running
- **NOT OK - Did not get monitor record - need to be checked**: No monitor record received
- **OK - Non used**: Not used
""")

# SMS button
if st.button('SMS Alert sent OUT - clear status', disabled=not check_sms_flag()):
    remove_sms_flag()

# Fetch and display data
data = fetch_data()
df = pd.DataFrame(data)

# Apply conditional formatting
def apply_styles(val):
    color = 'white'
    if val == "OK":
        bgcolor = 'green'
    elif val == "NO":
        bgcolor = 'red'
    elif val == "":
        bgcolor = 'yellow'
    else:
        bgcolor = 'grey'
        color = 'white'
    return f'background-color: {bgcolor}; color: {color}'

def apply_styles_git(val):
    if val == 0:
        bgcolor = 'green'
        color = 'white'
    elif val > 0:
        bgcolor = 'yellow'
        color = 'black'
    else:
        bgcolor = 'grey'
        color = 'grey'
    return f'background-color: {bgcolor}; color: {color}'

def data_bars(df, column):
    try:
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        n_bins = 100
        bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
        for i in range(1, len(bounds)):
            min_bound = (i - 1) * (100 / n_bins)
            max_bound = i * (100 / n_bins)
            max_bound_percentage = bounds[i] * 100
            styles.loc[(df[column] >= min_bound) & (df[column] < max_bound), column] = (
                f'background: linear-gradient(90deg, #53a900 0%, #53a900 {max_bound_percentage}%, #0020d0 {max_bound_percentage}%, #0020d0 100%); padding-bottom: 2px; padding-top: 2px;'
            )
        return styles
    except Exception as e:
        styles = pd.DataFrame("", index=df.index, columns=df.columns)
        return styles

df = df.style.background_gradient(cmap='RdYlGn', low=0.2, high=0.2, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('memory_')]])
df = df.background_gradient(cmap='RdYlGn', low=0.2, high=0.2, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('sda')]])
styled_df = df.applymap(apply_styles, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('ps_')]])
styled_df = styled_df.applymap(apply_styles_git, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('git_')]])

#styled_df = styled_df.apply(data_bars, column='memory_available_rate', axis=None)
#styled_df = styled_df.apply(data_bars, column='sda2_usage', axis=None)


st.dataframe(styled_df, height=400)

# Display last refresh time
st.write(f"Last Refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")