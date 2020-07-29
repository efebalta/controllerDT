#!/usr/bin/env python3
# 
import paramiko
import time
import numpy as np


#output = remote_connection.recv(1000)

def discoDisco():
	try:
		ip = "141.212.180.19"
		user = "ultimaker"
		passwd = "ultimaker"
		client = paramiko.SSHClient()
		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		client.connect(ip,username=user,password=passwd)
		remote_connection = client.invoke_shell()
		time.sleep(1)
		for i in range(4):
			r = np.random.randint(255, size=(1,3))
			n = r.tolist()
			n = n[0]
			time.sleep(0.1)
			remote_connection.send("sendgcode M142 r%f g%f b%f w5 \n" % (n[0], n[1], n[2]))
			#remote_connection.send("sendgcode M142 r0 g0 b0 w10\n")
			print(n)
			time.sleep(0.1)
			if i==9: remote_connection.send("sendgcode M142 r%f g%f b%f w10 \n" % (0,0,0))
			
		time.sleep(3)
		remote_connection.send("sendgcode M142 r%f g%f b%f w10 \n" % (0,0,0))
		print("sendgcode M142 r0 g0 b0 w10\n")
		
	except:
		print('SSH not connected \n')
		print('Is developer mode enabled? \n')
		
	
	
if __name__ == "__main__":
    discoDisco()