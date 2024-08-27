#!/usr/bin/python3
# -*- coding: utf-8 -*-
from socket import *
from iptools import IpRange
import sys
import os
def portScanner(host,port):
    try:
        s = socket(AF_INET,SOCK_STREAM)
        host = str(host)
        port = int(port)
        s.connect((host,port))
        print('%s[+] %d open--------------------------------------' % (host,port))
        results.append(host+"-"+str(port)+" is open!\n")
        s.close()
    except:
        pass
        print('%s[-] %d close' % (host,port))
        #results.append(host+"-"+str(port)+"is closed!")
def main(argv):
    global results
    results=[]
    string_ip = "".join(argv[1])
    ports=[]
    string_port = "".join(argv[2])
    string_port=string_port.replace("[","").replace("]","")
    for i in string_port.split(","):
        if "-" in i:
            init_a=int(i.split("-")[0])
            while init_a<=int(i.split("-")[1]):
                ports.append(init_a)
                init_a=init_a+1
        else:
            ports.append(int(i))
    setdefaulttimeout(0.1)

    ip_list = IpRange(string_ip)
    for ip in ip_list:
        for p in ports:
            #if str(ip).split('.')[3] in ['1','10','100','200']:
            #    print(str(ip) + ':' + str(p) +' is scanning')
            portScanner(ip,p)
    log_name = "scan.log"
    if os.path.exists(log_name):
        os.remove(log_name)
    f = open(log_name,'w')
    f.close() 
    with open(log_name,"a") as f:
        for i in results:
            f.writelines(i)

        

if __name__ == '__main__':
    main(sys.argv)
