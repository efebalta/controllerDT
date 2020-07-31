#!/usr/bin/env python3
# 
import paramiko
import time
import numpy as np
import math
import matlab.engine
import os
from scipy import sparse
from scipy.io import loadmat
from cvxopt import matrix, solvers

# eng = matlab.engine.start_matlab()
# path = os.getcwd() + '\\src'
# eng.cd(path)
# ret = eng.um3_mpc_data()
# rall = ret
# rvec = rall[0:50]
# x0 = matlab.double([[120.0],[120.0]])
# t1 = time.time()
# r2 = eng.mpc_solve(rvec,x0)
# t2 = time.time()
# print(float(t2-t1))
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
temperature = 205
layerNum = 1
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
                    if layerNum % 2 == 0:
                        temperature += 0.1
                    layerNum += 1
            
        if "G" in line and zstart and ";" not in line:
            lineDict[zval]["lines"].append(str(line[:-1]))
            lines.append(line[:-1])
            split_line = line.split()
            if "F" in line:
                last_feed = float(split_line[1][1:])
            xword = [word for word in split_line if word[0] is "X"]
            yword = [word for word in split_line if word[0] is "Y"]
            if xword and yword:
                linesxy.append([xword[0],yword[0]])
                if "E" in line and ";" not in line:
                    idx_e = line.find("E")
                    eval = line[idx_e+1:-1]
                    mmps = last_feed/60
                    if len(linesxy) > 1:
                        x_val = float(linesxy[-2][0][1:])
                        y_val = float(linesxy[-2][1][1:])
                        x_targ = float(xword[0][1:])
                        y_targ = float(yword[0][1:])
                        line_time = math.sqrt((x_val-x_targ)**2+(y_val-y_targ)**2)/mmps
                    else:
                        line_time = math.sqrt((float(xword[0][1:]))**2+(float(yword[0][1:]))**2)/mmps
                        
                    evalDict[float(eval)] = {'line': str(line[:-1]), 'lineNr':len(lines)-1,\
                        "X":float(xword[0][1:]), "Y":float(yword[0][1:]), "F":float(last_feed),\
                        "line_time":float(line_time), "T":float(temperature)}
                
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
    # Get the controller matrices
    ret = loadmat('src/mpcdat.mat')
    N = int(ret['N'])
    Ad = np.array(ret['A']).astype(np.double)
    Bd = np.array(ret['B']).astype(np.double)
    Cd = np.array(ret['C']).astype(np.double)
    Qd = 100*sparse.eye(1)
    Rd = 0.01*sparse.eye(1)
    Qbar = matrix(np.array(ret['Qbar']).astype(np.double))
    Rbar = matrix(np.array(ret['Rbar']).astype(np.double))
    Gm = matrix(np.array(ret['G']).astype(np.double))
    Mm = matrix(np.array(ret['M']).astype(np.double))
    Parr = np.array(ret['P']).astype(np.double)
    P = matrix(Parr)
    q = matrix(np.array(ret['q']).astype(np.double))
    lb = np.array(ret['lb']).astype(np.double)
    ub = np.array(ret['ub']).astype(np.double)
    A = matrix(np.vstack((np.identity(N),-np.identity(N))))
    b = matrix(np.concatenate((ub,-lb),axis=0).astype(np.double))
    solvers.options['show_progress'] = False 
    Aeq = matrix(np.array(ret['Aeq']).astype(np.double))
    beq = matrix(np.array(ret['beq']).astype(np.double))
    dly = int(ret['dly'])
    t1 = time.time()
    res = solvers.qp(P,q,A,b)
    t2 = time.time()
    print(float(t2-t1))
    xkest = np.array([[210.],[210.]])
    Qnoise = np.array([[0.7,0.9],[0.9,1.2]])
    Rnoise = np.array([0.1])
    Pk = np.array([[1.,1.],[1.,1.]])
    Aeq = matrix(np.array(ret['Aeq']).astype(np.double))
    beq = matrix(np.array(ret['beq']).astype(np.double))

    # steady state evaluations
    A_ss = matrix(np.array(ret['A_ss']).astype(np.double))
    Q_ss = matrix(np.array(ret['Q_ss']).astype(np.double))
    A_ss_ineq = matrix(np.array(ret['A_ss_ineq']).astype(np.double))
    b_ss_ineq = matrix(np.array(ret['b_ss_ineq']).astype(np.double))
    q0 = matrix([0.,0.,0.])
    for key in evalDict:
        b_ss = matrix(np.array([[0.],[0.],[evalDict[key]['T']]]).astype(np.double))
        res = solvers.qp(Q_ss,q0,A_ss_ineq,b_ss_ineq,A_ss,b_ss)
        evalDict[key]["Xr"] = [float(res['x'][0]), float(res['x'][1])]
        evalDict[key]["Ur"] = float(res['x'][2])

    uk = 210.0
    T0_targ_val = 210
    prevTemp = 210
    uq = []
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
        opt_cycle = 0
        for i in range(2500):
            print('cycle %i' %i)
            t3 = time.time()
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
            try:
                T0_targ_idx = out_txt.find("/",T0_idx)
                at_idx = out_txt.find("@",T0_targ_idx)
                T0_targ_val = float(out_txt[T0_targ_idx+1:at_idx])
            except:
                print("Target temp not received")

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

                    # get the horizon
                    t_targ = evalDict[closest_val]["Xr"]
                    u_targ = evalDict[closest_val]["Ur"]
                    cleval = closest_val
                    rvec = []
                    uvec = []
                    while len(rvec) <= N:
                        val = math.floor(time_to_fin_line/0.5)
                        rvec.extend([t_targ for i in range(val)])
                        uvec.extend([u_targ for i in range(val)])
                        cleval = es[es.index(cleval)+1]
                        t_targ = evalDict[cleval]["Xr"]
                        u_targ = evalDict[cleval]["Ur"]
                        time_to_fin_line = evalDict[cleval]["line_time"]
                    r_ref = matrix(np.array(rvec[:N]).flatten())
                    u_ref = matrix(np.array(uvec[:N]))

                    currentTemp = float(T0_val[3:-1])
                    # xkest = matrix(np.array([[prevTemp],[currentTemp]])) 
                    xkest = Ad.dot(xkest) + Bd.dot(uk)
                    Pk = Ad.dot(Pk.dot(Ad.T)) + Qnoise
                    ytil = currentTemp - Cd.dot(xkest)
                    Sk = Cd.dot(Pk.dot(Cd.T)) + Rnoise
                    Kk = Pk.dot(Cd.T.dot(np.linalg.inv(Sk)))
                    xkest = xkest + Kk.dot(ytil)
                    Pk = (np.identity(2) - Kk.dot(Cd)).dot(Pk)
                    
                    if len(uq)>dly:
                        beq = matrix(np.array(uq[-dly:]))
                    else:
                        beq = matrix(np.array([u_targ for i in range(dly)]))

                    x0 = matrix(xkest)
                    q = Gm.T*( Qbar*( Mm*(x0) - r_ref)) - Rbar*u_ref
                    res = solvers.qp(P,q,A,b,Aeq,beq)
                    uk = float(res['x'][dly])
                    uq.append(uk)
                    # if len(uq) == dly:
                    #     beq = matrix(np.array(uq))
                    #     uk = uq.pop(0)
                    # else:
                    #     uk = float(t_targ)

                    print("MPC reference: "+ str(uk))
                    print("Estimated State: "+str(x0[0])+"; "+ str(x0[1])+"\n")
                    print("Reference: "+str(rvec[0]))
                    remote_connection.send('sendgcode M104 S%.2f\n'%float(uk))
                    # uk = float(t_targ)#
                    # uk = float(res['x'][0])

                    # set the temperature if it's not right
                    # if abs(T0_targ_val - evalDict[closest_val]["T"])>0.2:
                        # remote_connection.send('sendgcode M104 S%.2f\n'%evalDict[closest_val]["T"])


                except:
                    print('Error in gcode localization')

            # print(out_txt)
            
            time.sleep(0.32)
            t4 = time.time()
            print("Cycle time:" + str(float(t4-t3)))
        ssh.close()

    except KeyboardInterrupt:
        ssh.close()        
        print('Aborted from keyboard\n')
    except:
        print('SSH not connected \n')
        print('Is developer mode enabled? \n')
        
	
	
if __name__ == "__main__":
    discoDisco()