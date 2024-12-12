
# Firmware

esp32-20220618-v1.19.1.bin

# Upload files
```
Makeverse_RV3028.py
esp32log.py
frequency.cfg
hx711.py
hx711_gpio.py
hxdouble.cfg  - in case of double scaler
led.py
main.py
oled.py
qmp6988.py
sht20.py
sim7080.py
smbus.py
ssd1206.py
udpserver.py
version.cfg
pixel_dict_kg.json
```

# First use

send AT+CGREG=2
to enable localtime

on 1nce, test Device integration, enter the ICCID and start a send process to have the device as activated

OR/AND
set the time

sim.send('AT+CCLK="23/04/09,12:07:55"', retType='o')



***Note***
On NB-IOT network, we got CCLK back, on CAT-M, maybe, but not sure.

