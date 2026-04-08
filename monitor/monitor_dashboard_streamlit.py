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

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'pin_input' not in st.session_state:
    st.session_state.pin_input = ""
if 'pin_error' not in st.session_state:
    st.session_state.pin_error = False

def pin_press(val):
    if val == 'd':
        st.session_state.pin_input = st.session_state.pin_input[:-1]
        st.session_state.pin_error = False
    elif val == 'ok':
        if st.session_state.pin_input == "5550":
            st.session_state.authenticated = True
            st.session_state.pin_input = ""
            st.session_state.pin_error = False
        else:
            st.session_state.pin_input = ""
            st.session_state.pin_error = True
    elif len(st.session_state.pin_input) < 4:
        st.session_state.pin_input += val
        st.session_state.pin_error = False

if not st.session_state.authenticated:
    pin_len = len(st.session_state.pin_input)
    dots_html = "".join([
        f'<span class="pin-dot {"filled" if i < pin_len else ""}"></span>'
        for i in range(4)
    ])
    error_html = '<div class="pin-error">Hibás PIN kód</div>' if st.session_state.pin_error else '<div class="pin-error"></div>'

    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&display=swap');

    .stApp {
        background: #0b0e14 !important;
        background-image:
            radial-gradient(ellipse 80% 60% at 50% 0%, rgba(16,85,70,0.18) 0%, transparent 70%),
            radial-gradient(circle at 80% 90%, rgba(20,40,80,0.12) 0%, transparent 50%) !important;
    }
    header[data-testid="stHeader"] { display: none; }
    footer { display: none !important; }
    #MainMenu { display: none !important; }
    section[data-testid="stMain"] > div { padding-top: 0 !important; }
    .stDeployButton, div[data-testid="stToolbar"],
    div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* A container mint kártya */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.pin-header) {
        background: linear-gradient(170deg, rgba(20,28,38,0.95), rgba(12,16,22,0.98)) !important;
        border: 1px solid rgba(56,230,180,0.12) !important;
        border-radius: 24px !important;
        padding: 40px 30px 28px !important;
        max-width: 400px !important;
        margin: 50px auto 0 !important;
        box-shadow:
            0 1px 0 0 rgba(56,230,180,0.08) inset,
            0 24px 64px rgba(0,0,0,0.6) !important;
        position: relative;
    }

    .pin-header {
        text-align: center;
        margin-bottom: 8px;
    }
    .pin-lock {
        font-size: 1.6rem;
        opacity: 0.45;
        margin-bottom: 10px;
    }
    .pin-title {
        font-family: 'Outfit', sans-serif;
        color: rgba(220,235,230,0.92);
        font-size: 0.9rem;
        font-weight: 500;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        margin-bottom: 28px;
    }
    .pin-dots {
        display: flex;
        justify-content: center;
        gap: 22px;
        margin-bottom: 10px;
    }
    .pin-dot {
        width: 16px; height: 16px;
        border-radius: 50%;
        background: rgba(56,230,180,0.06);
        border: 1.5px solid rgba(56,230,180,0.25);
        display: inline-block;
        transition: all 0.2s ease;
    }
    .pin-dot.filled {
        background: rgba(56,230,180,0.85);
        border-color: rgba(56,230,180,0.9);
        box-shadow: 0 0 12px rgba(56,230,180,0.4), 0 0 4px rgba(56,230,180,0.6);
    }
    .pin-error {
        color: #e85d5d;
        text-align: center;
        font-size: 0.85rem;
        min-height: 24px;
        padding: 4px 0 8px;
    }

    /* Gomb stílusok - globális, nincs :has() */
    div[data-testid="stButton"] > button {
        width: 86px !important;
        height: 86px !important;
        min-width: 86px !important;
        min-height: 86px !important;
        border-radius: 50% !important;
        border: 1px solid rgba(56,230,180,0.15) !important;
        background: rgba(56,230,180,0.05) !important;
        color: rgba(230,240,235,0.9) !important;
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 500 !important;
        line-height: 1 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 3px auto !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(56,230,180,0.12) !important;
        border-color: rgba(56,230,180,0.3) !important;
        box-shadow: 0 0 18px rgba(56,230,180,0.1) !important;
        color: rgba(56,230,180,1) !important;
    }
    div[data-testid="stButton"] > button:active {
        transform: scale(0.92) !important;
        background: rgba(56,230,180,0.18) !important;
    }
    div[data-testid="stButton"] > button p {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.2rem !important;
        font-weight: 500 !important;
        line-height: 1 !important;
        margin: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([1.2, 1, 1.2])
    with col_center:
        pin_container = st.container(border=True)
        with pin_container:
            st.markdown(f"""
            <div class="pin-header">
                <div class="pin-lock">&#x1F512;</div>
                <div class="pin-title">SmartBox Monitor</div>
                <div class="pin-dots">{dots_html}</div>
                {error_html}
            </div>
            """, unsafe_allow_html=True)

            for row_digits in [('1','2','3'), ('4','5','6'), ('7','8','9'), ('d','0','ok')]:
                c1, c2, c3 = st.columns([1,1,1])
                for col_btn, digit in zip([c1, c2, c3], row_digits):
                    with col_btn:
                        label = {'d': '⌫', 'ok': '✓'}.get(digit, digit)
                        if st.button(label, key=f"pin_{digit}", use_container_width=False):
                            pin_press(digit)
                            st.rerun()

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