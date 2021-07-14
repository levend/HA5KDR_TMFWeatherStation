# Importing Libraries
import serial
import time
import re
from datetime import datetime

arduino = serial.Serial(port='/dev/cu.usbserial-142230', baudrate=115200, timeout=.1)
regex = r"(?P<id>\d{4})(?P<temp_0>(-|\+)\d{4})(?P<temp_05>(-|\+)\d{4})(?P<temp_2>(-|\+)\d{4})(?P<press>(-|\+)\d{4})(?P<hum>(-|\+)\d{4})"
pattern = re.compile(regex);

def read_tmf():
    arduino.write("r\n".encode())
    time.sleep(0.5)
    data = arduino.readline()
    return data

while True:
    input("Press ENTER to read the TMF") # Taking input from user
    value = read_tmf().decode()
    print("Raw data: {}".format(value)) # printing the value
    test_str = "|;0036+0400-0410-0420+0900+0100*0000*0000|"
    match = pattern.search(test_str)
    
    device_id = match.group("id")
    temp_0_s = match.group("temp_0")
    temp_05_s = match.group("temp_05")
    temp_2_s = match.group("temp_2")
    pressure_s = match.group("press")
    humidity_s = match.group("hum")
    
    temp_0 = int(temp_0_s) / 10.0
    temp_05 = int(temp_05_s) / 10.0
    temp_2 = int(temp_2_s) / 10.0

    pressure = int(pressure_s)
    humidity = int(humidity_s) / 10.0

    print("Állomás szám {}".format(device_id))
    print("Talajmenti hőmérséklet {} celsius fok".format(temp_0))
    print("Fél méteren a hőmérséklet {} celsius fok".format(temp_05))
    print("2 méteren a hőmérséklet {} celsius fok".format(temp_2))
    print("A légnyomás {} milibar".format(pressure))
    print("Relatív páratartalom {} %".format(humidity))

    #prepare the message file
    with open("message_template.txt", "rt") as fp:
        template_content = fp.read()
        template_content = template_content.replace('{device_id}', device_id)
        template_content = template_content.replace('{temp_0}', str(temp_0))
        template_content = template_content.replace('{temp_05}', str(temp_05))
        template_content = template_content.replace('{temp_2}', str(temp_2))
        template_content = template_content.replace('{pressure}', str(pressure))
        template_content = template_content.replace('{humidity}', str(humidity))
        template_content = template_content.replace('{hour}', str(datetime.now().hour))
        template_content = template_content.replace('{minute}', str(datetime.now().minute))

        with open("message.txt","wt") as out_file:
            out_file.write(template_content)
        







