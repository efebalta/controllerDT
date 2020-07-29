#!/usr/bin/env python3
# 
import paramiko
import time
import numpy as np
import math


#output = remote_connection.recv(1000)
file_name = "misc/UM3_hourglass3.gcode"

lines = []
linesxy = []
lineDict = {}
evalDict = {}
lineNum = 0
lastZ = 0.0
zval = 0
zstart = 0
last_feed = 0
with open(file_name) as fp:
    while True:
        lineNum += 1
        line = fp.readline()
        if "Z" in line and ";" not in line:
            idx = line.find("Z")
            zval = line[idx:-1]
            if not zstart:
                zstart = 1 if "Z0.27" in line else 0

            if zstart:
                if float(zval[1:]) > lastZ:
                    lineDict[zval] = {"lines":[str(line[:-1])], "Z":str(zval[1:]), "lineNr": lineNum}
                    lastZ = float(zval[1:])
                    lines.append(line[:-1])
            
        if "G" in line and zstart and ";" not in line:
            lineDict[zval]["lines"].append(str(line[:-1]))
            lines.append(line[:-1])
            split_line = line.split()
            if "F" in line:
                last_feed = float(split_line[1][1:])
            xword = [word for word in split_line if word[0] is "X"]
            yword = [word for word in split_line if word[0] is "Y"]
            if xword and yword:
                linesxy.append([xword[0]+" "+yword[0]])
                if "E" in line and ";" not in line:
                    idx_e = line.find("E")
                    eval = line[idx_e+1:-1]
                    evalDict[float(eval)] = {'line': str(line[:-1]), 'lineNr':len(lines)-1,\
                        "X":float(xword[0][1:]), "Y":float(yword[0][1:]), "F":float(last_feed)}
                
        if not line:
            break
es = list(evalDict.keys())
t1 = time.time()
testval = 126.548
l1_norm = lambda list_val : abs(testval - list_val)
closest_val = min(es, key=l1_norm)
t2 = time.time()
print(float(t2-t1))
a = 3

def discoDisco():
    try:
        host = '192.168.0.100'
        user = 'ultimaker'
        passwd = 'ultimaker'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host,username=user,password=passwd)
        remote_connection = ssh.invoke_shell()
        time.sleep(1)
        out = remote_connection.recv(2000)
        for i in range(500):
            print('cycle %i' %i)
            # remote_connection.send('sendgcode M104 S70\n')
            remote_connection.send('sendgcode M105\n')
            # time.sleep(0.1)
            # out = remote_connection.recv(1000)
            # out_txt = out.decode('ascii')
            # print(out_txt)
            remote_connection.send('sendgcode M114\n')
            time.sleep(0.15)
            out = remote_connection.recv(2000)
            out_txt = out.decode('ascii')
            T0_idx = out_txt.find("T0:")
            T0_val = out_txt[T0_idx:T0_idx+8]
            
            x_idx = out_txt.find("X")
            if x_idx == -1:
                continue
            else:
                t1 = time.time()
                y_idx = out_txt.find("Y")
                z_idx = out_txt.find("Z")
                e_idx = out_txt.find("E", x_idx+1)
                c_idx = out_txt.find("c", e_idx+1)

                x_val = float(out_txt[x_idx+2:y_idx-1])
                y_val = float(out_txt[y_idx+2:z_idx-1])
                e_val = float(out_txt[e_idx+2:c_idx-1])
                try:
                    
                    l1_norm = lambda list_val : abs(e_val - list_val)
                    closest_val = min(es, key=l1_norm)
                    t2 = time.time()
                    print("localization time: "+ str(float(t2-t1))+"")
                    print("current line: "+ str(evalDict[closest_val]["lineNr"])+"")
                    if closest_val > float(e_val):
                        next_e_lineNr = evalDict[closest_val]["lineNr"]
                        x_targ = evalDict[closest_val]["X"]
                        y_targ = evalDict[closest_val]["Y"]
                        fr = evalDict[closest_val]["F"]/60
                        time_to_fin_line = math.sqrt((x_val-x_targ)**2+(y_val-y_targ)**2)/fr
                    else:
                        next_line_e_val = es[es.index(closest_val)+1]
                        next_e_lineNr = evalDict[next_line_e_val]["lineNr"]
                        x_targ = evalDict[next_line_e_val]["X"]
                        y_targ = evalDict[next_line_e_val]["Y"]
                        fr = evalDict[closest_val]["F"]/60
                        time_to_fin_line = math.sqrt((x_val-x_targ)**2+(y_val-y_targ)**2)/fr
                    print("Time to fin line "+str(next_e_lineNr)+" is :"+str(time_to_fin_line)+"\n")

                except:
                    print('Error in gcode localization')

            # print(out_txt)
            
            time.sleep(0.15)
        ssh.close()
		
    except:
        print('SSH not connected \n')
        print('Is developer mode enabled? \n')
		
	
	
if __name__ == "__main__":
    discoDisco()