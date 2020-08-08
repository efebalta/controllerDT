#!/usr/bin/env python3
# 

import shutil
import tempfile
import urllib.request
import time
import datetime
import json
import requests
import os.path
import msvcrt as m
import ast

t = time.time()
ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H-%M-%S')
#path = os.path.join(r'Z:\13_AM_Repository\UM3_TempListener',ts+'.txt')
path = "misc/flowListen/"+ts+'.txt'

def mainListener():
    isPrint = 0
    printerIP = '192.168.0.102'
    apiurl = 'http://'+printerIP+'/api/v1/'
    # Get the printer state form the API
    # r = requests.get(apiurl+'v1/print_job/state')
    # print(r.json())

    # if r.json() == 'printing':  # Add pre_print here for transient response
    #     f = open(path,'w')

    f = open(path,'w')
    header_added = 0
    last_time_stamp = 0.0
    #while r.json() == 'printing':
    while True:
        try:
            # Get the temperature data response from the machine
            with urllib.request.urlopen(
                apiurl+'printer/diagnostics/temperature_flow/5?csv=0') as response:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    shutil.copyfileobj(response, tmp_file)
                    
            # Get the appropriate piece of data and write it in the output
            with open(tmp_file.name) as resp:
                for line in resp.readlines():
                    list_resp = ast.literal_eval(line)
 
                    if not header_added:
                        f.write(";".join(list_resp[0])+"\n")
                        header_added = 1
                    else:
                        for wrl in list_resp[1:]:
                            if last_time_stamp < wrl[0]:
                                wrl_write = ['%.3f'% ix for ix in wrl]
                                f.write(";".join(wrl_write)+"\n")
                                last_time_stamp = wrl[0]
                            else:
                                break
                    
            # r = requests.get(apiurl+'print_job/state')           
        
        except KeyboardInterrupt:
            f.close()        
            break
        time.sleep(0.05)
    # f is only created if the printer is printing
    try:
        f.close()
    except:
        return
    
if __name__ == "__main__":
    mainListener()
