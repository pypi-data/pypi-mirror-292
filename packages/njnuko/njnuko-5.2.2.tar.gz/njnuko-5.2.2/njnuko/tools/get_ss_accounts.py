import os
import bs4
import lxml
import urllib.request
import re
#get the contents of website
con = urllib.request.urlopen('http://www.ishadowsocks.net/')
soup = bs4.BeautifulSoup(con.read(),'lxml')
#print(soup.prettify())

servers = soup.select('#free > div > div:nth-of-type(2) > div')
a=[]


for i in servers:
#    print(ko.search(str(i.to_text)))
#    print(i.contents[1].string)
#    print(i.contents[1].string.index(':'))
    a.append({'server':i.contents[1].string[i.contents[1].string.index(':')+1:],
              'port':i.contents[3].string[i.contents[3].string.index(':')+1:],
              'password':i.contents[5].string[i.contents[5].string.index(':')+1:],
              'encrypt':i.contents[7].string[i.contents[7].string.index(':')+1:]
              })

                     
con.close()
