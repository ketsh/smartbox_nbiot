import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import requests
import datetime
import sqlite3
import os
from monitor_config import rack_info

db_path = os.path.join(os.path.dirname(__file__), 'monitor_data.db')
st.set_page_config(layout="wide")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'pin_input' not in st.session_state:
    st.session_state.pin_input = ""
if 'pin_error' not in st.session_state:
    st.session_state.pin_error = False

# Handle PIN button presses via query params
params = st.query_params
if 'p' in params:
    btn = params['p']
    st.query_params.clear()
    if btn == 'd':
        st.session_state.pin_input = st.session_state.pin_input[:-1]
        st.session_state.pin_error = False
    elif btn == 'ok':
        if st.session_state.pin_input == "5550":
            st.session_state.authenticated = True
            st.session_state.pin_input = ""
            st.session_state.pin_error = False
        else:
            st.session_state.pin_input = ""
            st.session_state.pin_error = True
    elif len(st.session_state.pin_input) < 4:
        st.session_state.pin_input += btn
    st.rerun()

if not st.session_state.authenticated:
    pin_len = len(st.session_state.pin_input)
    dots_html = "".join([
        f'<div class="dot {"filled" if i < pin_len else ""}"></div>'
        for i in range(4)
    ])
    error_html = '<div class="error">Hibás PIN kód</div>' if st.session_state.pin_error else '<div class="error"></div>'

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        .card {{
            background: rgba(255,255,255,0.07);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.13);
            border-radius: 32px;
            padding: 40px 36px 36px;
            width: 320px;
            box-shadow: 0 12px 48px rgba(0,0,0,0.5);
        }}
        .title {{
            color: rgba(255,255,255,0.85);
            font-size: 1rem;
            font-weight: 600;
            text-align: center;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            margin-bottom: 32px;
        }}
        .dots {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 12px;
        }}
        .dot {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: rgba(255,255,255,0.15);
            border: 2px solid rgba(255,255,255,0.35);
            transition: all 0.2s;
        }}
        .dot.filled {{
            background: #a78bfa;
            border-color: #a78bfa;
            box-shadow: 0 0 12px #a78bfa99;
        }}
        .error {{
            color: #f87171;
            text-align: center;
            font-size: 0.85rem;
            min-height: 28px;
            padding: 4px 0 16px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }}
        button {{
            width: 76px;
            height: 76px;
            border-radius: 50%;
            border: 1px solid rgba(255,255,255,0.15);
            background: rgba(255,255,255,0.08);
            color: white;
            font-size: 1.5rem;
            font-weight: 600;
            cursor: pointer;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.15s, transform 0.1s, box-shadow 0.15s;
            outline: none;
        }}
        button:hover {{
            background: rgba(167,139,250,0.25);
            box-shadow: 0 0 18px rgba(167,139,250,0.35);
        }}
        button:active {{ transform: scale(0.92); }}
        button.confirm {{
            background: linear-gradient(135deg, #7c3aed, #a78bfa);
            border: none;
            box-shadow: 0 4px 20px rgba(124,58,237,0.5);
        }}
        button.confirm:hover {{
            box-shadow: 0 4px 28px rgba(124,58,237,0.75);
        }}
        button.delete {{
            background: rgba(248,113,113,0.1);
            border-color: rgba(248,113,113,0.3);
        }}
        button.delete:hover {{
            background: rgba(248,113,113,0.25);
            box-shadow: 0 0 18px rgba(248,113,113,0.35);
        }}
    </style>
    </head>
    <body>
    <div class="card">
        <div class="title">SmartBox Monitor</div>
        <div class="dots">{dots_html}</div>
        {error_html}
        <div class="grid">
            <button onclick="press('1')">1</button>
            <button onclick="press('2')">2</button>
            <button onclick="press('3')">3</button>
            <button onclick="press('4')">4</button>
            <button onclick="press('5')">5</button>
            <button onclick="press('6')">6</button>
            <button onclick="press('7')">7</button>
            <button onclick="press('8')">8</button>
            <button onclick="press('9')">9</button>
            <button class="delete" onclick="press('d')">⌫</button>
            <button onclick="press('0')">0</button>
            <button class="confirm" onclick="press('ok')">✓</button>
        </div>
    </div>
    <script>
        function press(val) {{
            window.parent.location.href = window.parent.location.pathname + '?p=' + val;
        }}
    </script>
    </body>
    </html>
    """, height=520)

    st.stop()

# update every 5 mins
st_autorefresh(interval=1 * 60 * 1000, key="dataframerefresh")


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
#Drop placeholder record from df
df = df[df['rack_id'] != 'placeholder (placeholder)']

df = df.style.background_gradient(cmap='RdYlGn', low=0.2, high=0.2, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('memory_')]])
df = df.background_gradient(cmap='RdYlGn', low=0.2, high=0.2, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('sda')]])
styled_df = df.map(apply_styles, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('ps_')]])
styled_df = styled_df.map(apply_styles_git, subset=pd.IndexSlice[:, df.columns[df.columns.str.startswith('git_')]])

#styled_df = styled_df.apply(data_bars, column='memory_available_rate', axis=None)
#styled_df = styled_df.apply(data_bars, column='sda2_usage', axis=None)


st.dataframe(styled_df, height=400)

# Display last refresh time
st.write(f"Last Refresh: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")