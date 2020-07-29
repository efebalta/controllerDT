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

t = time.time()
ts = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d_%H-%M-%S')
ts = ts + '_position'
#path = os.path.join(r'Z:\13_AM_Repository\UM3_TempListener',ts+'.txt')
path = ts+'.txt'

def mainListener():
    isPrint = 0
    printerIP = '141.212.180.19'

    # Get the printer state form the API
    r = requests.get('http://141.212.180.19/api/v1/print_job/state')
    print(r.json())

    if r.json() == 'printing' or 'wait_cleanup' or 'pre_print':  # Add pre_print here for transient response
        f = open(path,'w')

    last_time_stamp = 0.0
    while r.json() == 'printing' or 'pre_print':
    #while True:
        try:
            # Get the temperature data response from the machine
            with urllib.request.urlopen(
                'http://141.212.180.19/api/v1/printer/diagnostics/temperature_flow/20?csv=1') as response:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                    shutil.copyfileobj(response, tmp_file)
            posResponse = requests.get('http://141.212.180.19/api/v1/printer/heads/0/position')
            pos = posResponse.json()

            with urllib.request.urlopen(
                'http://141.212.180.19/api/v1/printer/heads/0/extruders/0/active_material/length_remaining') as materialLength:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file2:
                    shutil.copyfileobj(materialLength, tmp_file2)
            with open(tmp_file2.name) as matInf:
                length = matInf.readlines()

            with urllib.request.urlopen(
                'http://141.212.180.19/api/v1/printer/heads/0/extruders/1/active_material/length_remaining') as materialLength2:
                with tempfile.NamedTemporaryFile(delete=False) as tmp_file3:
                    shutil.copyfileobj(materialLength2, tmp_file3)
            with open(tmp_file3.name) as matInf:
                length2 = matInf.readlines()
                
					
            # Get the appropriate piece of data and write it in the output
            with open(tmp_file.name) as csv:
                for line in csv.readlines():
                    a = line.split(';');

                    # Dealing with the header line
                    if a[0] == '# Time':
                        continue        
                    
                    # Add the values to the csv based on the timestamp
                    if last_time_stamp < float(a[0]):
                        ll = [line[:-1], length[0], length2[0], pos['x'], pos['y'], ''.join([str(pos['z']),'\n'])]
                        #print(';'.join(str(e) for e in ll))
                        f.write(';'.join(str(e) for e in ll))
                        last_time_stamp = float(a[0]);
                    else:
                        break
                    
            r = requests.get('http://141.212.180.19/api/v1/print_job/state')           
        
        except KeyboardInterrupt:
            f.close()        
            break
        
    # f is only created if the printer is printing
    try:
        f.close()
    except:
        return
    
if __name__ == "__main__":
    mainListener()
