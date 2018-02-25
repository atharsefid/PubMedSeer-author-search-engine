import os, sys 
import solr
import csv 
from xml.dom.minidom import parseString
import shutil
import settings
import settings
import shutil
import zipfile
import StringIO
import time
import traceback
HL_PRE = '<span style="background-color: #FFFF00"><strong>'
HL_POST = '</strong></span>'
solr_disamseer = open("params","r").read().split("\n")[0].split("=")[1].strip()
s=solr.SolrConnection(solr_disamseer)
#start=int(request.GET.get('start',0))
times =[]
for char in 'abcdefghijklmnopqrstuvwxyz':
    q = '{!q.op=AND}'+ char
    start_time = time.time()
    response=s.query(q, highlight=True, fields="*", hl_fragsize=50000, hl_simple_pre=HL_PRE, hl_simple_post=HL_POST) #, start=start, op='AND')
    t = time.time()-start_time
    times.append(t)
    '''if len(response.results) > 0:
        for hit in response.results:
            print(hit.get('name'))
    '''
print(times)
print('average time: ', sum(times)/len(times))
