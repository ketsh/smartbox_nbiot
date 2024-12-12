
from machine import  ADC, Pin
from os import stat

def getBattery():
    pin_vp = ADC(Pin(36, Pin.IN))
    pin_vp.atten(ADC.ATTN_6DB)
    pin_vp.width(ADC.WIDTH_12BIT)
    vp = pin_vp.read()
    pin_vn = ADC(Pin(35, Pin.IN))
    pin_vn.atten(ADC.ATTN_6DB)
    pin_vn.width(ADC.WIDTH_12BIT)
    vn = pin_vn.read()
    return  (vp, vn)

def file_exists(filename):
    try:
        stat(filename)
        return True
    except :
        return False

def step_firmware_update():
    # Read the reboot count from the file
    try:
        with open("reboot_count.txt", "r") as file:
            reboot_count = int(file.read())
    except OSError:
        # If the file doesn't exist or cannot be read, set reboot_count to 0
        reboot_count = 0

    # Increment the reboot count by 1
    reboot_count += 1

    # Write the incremented reboot count back to the file
    with open("reboot_count.txt", "w") as file:
        file.write(str(reboot_count))

def check_firmware_update():
    reboot_count = 0
    try:
        with open("reboot_count.txt", "r") as file:
            reboot_count = int(file.read())
    except OSError:
        # If the file doesn't exist or cannot be read, set reboot_count to 0
        reboot_count = 0


    # Check if reboot_count is greater than or equal to 3
    if reboot_count >= 3:
        return True
    else:
        return False

def reset_firmware_update():
    with open("reboot_count.txt", "w") as file:
        file.write("0")
