# Importing Libraries
import serial
import time
import re
from datetime import datetime
import os
import configparser
from gpiozero import LED
from gpiozero import Button
from progress.bar import Bar

def read_tmf():
    serial.write("r\n".encode())
    time.sleep(0.5)
    data = serial.readline()
    return data


def parse_tmf_response(match):

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

    # prepare the message file
    with open(settings['template_file_name'], "rt") as fp:
        template_content = fp.read()
        template_content = template_content.replace('{device_id}', device_id)

        if temp_0 < 0:
            template_content = template_content.replace(
                '{temp_0}', "minusz {}".format(abs(temp_0)))
        else:
            template_content = template_content.replace(
                '{temp_0}', str(temp_0))

        if temp_05 < 0:
            template_content = template_content.replace(
                '{temp_05}', "minusz {}".format(abs(temp_05)))
        else:
            template_content = template_content.replace(
                '{temp_05}', str(temp_05))

        if temp_2 < 0:
            template_content = template_content.replace(
                '{temp_2}', "minusz {}".format(abs(temp_2)))
        else:
            template_content = template_content.replace(
                '{temp_2}', str(temp_2))

        template_content = template_content.replace(
            '{pressure}', str(pressure))
        template_content = template_content.replace(
            '{humidity}', str(humidity))
        template_content = template_content.replace(
            '{hour}', str(datetime.now().hour))
        template_content = template_content.replace(
            '{minute}', str(datetime.now().minute))

        with open(settings['message_file_name'], "wt") as out_file:
            out_file.write(template_content)
            
        relay.on()
        time.sleep(0.2)
        
        command_result = os.system(settings['speak_command'])
        print('Command result {}'.format(command_result))
        
        relay.off()

def do_readout():
    value = read_tmf().decode()
    print("Raw data: {}".format(value))  # printing the value
    test_str = "|;0036+0400-0410-0420+0900+0100*0000*0000|"
    
    #value = test_str
    
    match = pattern.search(value)
    
    if match:
        parse_tmf_response(match)
    else:
        print("TMF data cannot be parsed - is the device connected/powered?")    


configparser = configparser.ConfigParser()
configparser.read('config.ini')
settings = configparser['DEFAULT']

serial = serial.Serial(port=settings['serial_port'], baudrate=115200, timeout=.1)
regex = r"(?P<id>\d{4})(?P<temp_0>(-|\+)\d{4})(?P<temp_05>(-|\+)\d{4})(?P<temp_2>(-|\+)\d{4})(?P<press>(-|\+)\d{4})(?P<hum>(-|\+)\d{4})"
pattern = re.compile(regex)
read_tmf() # initialize the port - no data will be returned for the first attempt
button = Button(6, pull_up=False)
relay = LED(5)
read_time_interval = int(settings['read_interval_minutes']) * 60

remaining_time = read_time_interval


while True:
    if  button.is_pressed:
        do_readout()
        remaining_time = read_time_interval
    
    if remaining_time==0:
        do_readout()
        remaining_time = read_time_interval
    else:
        remaining_time = remaining_time - 1
        time.sleep(1)
        os.system('clear')
        with Bar('Waiting for next readout', max=read_time_interval, width=100) as bar:
            bar.next(remaining_time)



