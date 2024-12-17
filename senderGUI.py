from tkinter import *
import tkinter as tk
from tkinter import ttk
from sendPackage import UDPSender

from google.cloud.bigquery import Client
from google.oauth2 import service_account
import time

project_id = "beescaled-dev"

# FOR TESTING, UNCOMMENT IT
credentials = service_account.Credentials.from_service_account_file(
    "./key/beescaled-dev-8c00249da18e.json", scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
client = Client(credentials=credentials, project=project_id)

def commandSend():
    print(device_var.get())
    print(commands_var.get())
    print(inputvar_var.get())
    udp.send(commands_var.get(), inputvar_var.get())
    time.sleep(3)
    refreshBQ()

def refreshBQ():
    sql = """
        select * from (select * from (SELECT timestamp, 
SAFE_CONVERT_BYTES_TO_STRING(FROM_BASE64(REPLACE(JSON_EXTRACT(data, '$.payload.value'), "\\"", ""))) PAYLOAD,
REPLACE(JSON_EXTRACT(data, '$.device.iccid'), "\\"", "") ICCID
 FROM `beescaled-dev.firestore_export.nbiotMessages_raw_changelog` )
)
where iccid in ('{}')
order by timestamp desc LIMIT 1
    """.format(device_var.get())
    df = client.query(sql).to_dataframe()
    T.delete('1.0', tk.END)
    T.insert('1.0', df.PAYLOAD[0])
    lastTime()

def lastTime():
    sql = """
select max(timestamp) ts from (select * from (SELECT timestamp, 
REPLACE(JSON_EXTRACT(data, '$.device.iccid'), "\\"", "") ICCID
 FROM `beescaled-dev.firestore_export.nbiotMessages_raw_changelog` )
)
where iccid in ('{}')""".format(device_var.get())
    df = client.query(sql).to_dataframe()
    time_var.set(df.ts[0])


def openConnection():
    udp.open(device_var.get())
    print("Opened")

def closeConnection():
    udp.close()
    print("Closed")

udp = UDPSender()
root = Tk()
root.geometry("820x250")
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="UDP sender for Mehter!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)

ttk.Label(frm, text="Select Device (ICCID)").grid(column=0, row=1)
device_var = StringVar()
device = ttk.Combobox(frm, values=["8988228066602756535", "8988228066603096577", "8988228066603096578", "8988228066603096579", "8988228066603096581",
                                   "8988228066603096580", "8988228066603096583"], textvariable=device_var).grid(column=1, row=1)

ttk.Label(frm, text="Select Command").grid(column=0, row=2)
commands_var = StringVar()
commands = ttk.Combobox(frm, values=["Open Door", "Get Signal strength", "Get Clock", "Get Version", "Get Frequency",  "Break", "Set High Frequency", "Set Medium Frequency", "Set Low Frequency", "Read ESP32 Log", "Read ESP32 Last 10"], textvariable=commands_var).grid(column=1, row=2)


ttk.Button(frm, text="Open Connection", command=openConnection).grid(column=0, row=3)
ttk.Button(frm, text="Close Connection", command=closeConnection).grid(column=0, row=4)
ttk.Button(frm, text="Send Command", command=commandSend).grid(column=0, row=5)

ttk.Label(frm, text="Input var 1").grid(column=0, row=6)
inputvar_var = StringVar()
ttk.Entry(frm, text="Input1", textvariable=inputvar_var).grid(column=1, row=6)

time_var = StringVar()
ttk.Label(frm, text="Last Time").grid(column=0, row=7)
ttk.Label(frm, text="xxx", textvariable=time_var).grid(column=1, row=7)

ttk.Button(frm, text="Refresh", command=refreshBQ).grid(column=0, row=8)
T = Text(root, height=10, width=60)
T.grid(column=3, row=0)

#T.grid(column=0, row=8).insert(1, "valai")

root.mainloop()