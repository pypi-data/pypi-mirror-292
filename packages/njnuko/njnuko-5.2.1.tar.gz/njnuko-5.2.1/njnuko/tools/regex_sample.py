#/usr/bin/python
# -*- coding: utf-8 -*-
import re,os
def readfile(x):
    out = open(x+"---output.temp",'a')
    with open(x,'r',encoding='utf8') as f:
        cc=f.read()
        print("===============begin find_tel")
        find_tel(cc,out)
        print("===============begin find mail")
        find_mail(cc,out)
        print("===============begin find thunder")
        find_thunder(cc,out)
    out.close()


def find_tel(a,out):
    tel=re.compile(r'''((\d{3}||\(\d{3}\))?(\s|\.|-)?(\d{3})(\s|\.|-)(\d{4})(\s*(ext|x|ext.)\s*(\d{2,5}))?)''',re.VERBOSE)
    tel1=re.compile(r'''(1\d{10}\D)''',re.VERBOSE)

    tels=[]
    out.write("Telephone List:\n")
    c=tel.findall(a)
    for i in c:        
        try:
            ac=re.compile('(\d)+')
            tels.append('-'.join([i[1],i[3],i[5]])+' ext. '+str(ac.search(i[6]).group(0)))
            out.write('-'.join([i[1],i[3],i[5]])+' ext. '+str(ac.search(i[6]).group(0)))
            out.write('\n')
        except AttributeError:
            tels.append('-'.join([i[1],i[3],i[5]]))
    c1=tel1.findall(a)
    for i in c1:        
        tels.append(i)
        print(i)
        out.write(i)
        out.write('\n')


def find_mail(a,out):
    email1 = re.compile(r'[\w\.-_]+@[\w.-_]+\.[\w]+',re.I)
    #email=re.compile(r'''(([a-zA-Z0-9_.%+-]+)+@([a-zA-Z0-9.-]+)(\.[a-zA-Z]{2,4}))''',re.I)
    mails=[]
    c=email1.findall(a)
    out.write("Email List:\n")
    for i in c:
        print(i)
        mails.append(i)
        out.write(i)
        out.write('\n')

def find_thunder(a,out):
    thunders=[]
    thu = re.compile("\'(thunder\:\/\/\S+)\'")
    cc = thu.findall(a)
    out.write("Thunder List:\n")
    for dd in cc:
        print(dd)
        thunders.append(dd)
        out.write(dd)
        out.write('\n')
