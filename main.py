from selectorlib import Extractor
import requests
import random
import numpy as np
import pprint
import time
import datetime
from pushover import Client

client = Client("ubppd94ysjtc6ess4jyh87wanreu9n", api_token="a2vg3r6ck5ewfobadgwxo6jwozd36z")

random.seed()

#Nvidia URLs
nvidia_url = 'https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/'
nvidia_yml = Extractor.from_yaml_file('NvidiaChecker.yml')

#Newegg URLs
newegg_url = 'https://www.newegg.com/p/pl?d=rtx+3080&N=100007709&isdeptsrh=1'
newegg_yml = Extractor.from_yaml_file('NeweggChecker.yml')


def nvidia_html_check():
    nvidia_html = requests.get(nvidia_url)
    t = 1
    if nvidia_html.status_code != 200:
        while nvidia_html.status_code != 200:
            print(f"Nvidia HTML request failed. Retrying in {t} s")
            time.sleep(t)
            t = t + 1
            nvidia_html = requests.get(nvidia_url)
    return nvidia_html

def newegg_html_check():
    newegg_html = requests.get(newegg_url)
    t = 1
    if (newegg_html.status_code != 200):
        while newegg_html.status_code != 200:
            print(f"Newegg HTML request failed. Retrying in {t} s")
            time.sleep(t)
            t = t + 1
            newegg_html = requests.get(newegg_url)
    return newegg_html

def newegg_data_check():
    newegg_html = newegg_html_check()
    newegg_data = newegg_yml.extract(newegg_html.text)
    if newegg_data["Availability"] is None:
        while newegg_data["Availability"] is None:
            newegg_html = newegg_html_check()
            newegg_data = newegg_yml.extract(newegg_html.text)
    return newegg_data


#Nividia Sizer
nvidia_alert = 0

#Newegg Sizer
newegg_data = newegg_data_check()
newegg_alert = [0] * len(newegg_data["Availability"])


cycles = 0

while 1:
    #NVIDIA CHECK----------------------------------------------------------------------------------------
    #Retrieve HTML
    nvidia_html = nvidia_html_check()

    #Extract HTML
    nvidia_data = nvidia_yml.extract(nvidia_html.text)

    #Check for Stock and Alert
    if nvidia_data["OOSMarker"] != "Out Of Stock":
        if nvidia_alert == 0:
            client.send_message(f"https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080/", title=f"NVIDIA: RTX 3080 FE", priority=1)
            nvidia_alert = 1
            time.sleep(2)


    #NEWEGG CHECK------------------------------------------------------------------------------------------
    #Retrieve and Extract HTML
    newegg_data = newegg_data_check()

    #Check for Stock and Alert
    for n, avail_string in enumerate(newegg_data["Availability"]):
        if avail_string != "OUT OF STOCK":
            if newegg_alert[n] == 0:
                client.send_message(f"{(newegg_data['Link'][n])}", title=f"{(newegg_data['ProductName'][n])[0:60]}", priority=1)
                newegg_alert[n] = 1
                time.sleep(2)


    #Cycle Checker
    if cycles == 1000:
        client.send_message(f"Completed at {datetime.datetime.now()}", title=f"1000 Check Cycles Completed", priority=-1)
        cycles = 0
    cycles = cycles + 1

    #Time Randomness
    random_time = 1 + (random.random() * random.randrange(1, 5))
    time.sleep(random_time)




