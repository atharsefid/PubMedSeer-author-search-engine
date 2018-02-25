# Create your views here.
from django.http import HttpResponse
from elasticsearch import Elasticsearch  
from django.shortcuts import render_to_response
from django.core.files.storage import FileSystemStorage
from models import *
from forms import *
import os, sys
import solr
import csv
from xml.dom.minidom import parseString
import shutil
from django.template.context import RequestContext
import settings
import requests
import shutil
import zipfile
import StringIO
import traceback
import json
from elasticsearch_dsl import Search                                                                                                                                           
from elasticsearch_dsl.query import MultiMatch, Match, Q
import time

solr_disamseer = open("params","r").read().split("\n")[0].split("=")[1].strip()
client = Elasticsearch(host="heisenberg.ist.psu.edu", timeout = 1000) 
#client = Elasticsearch(host="130.203.139.36", timeout = 1000) 


ERR_QUERY_NOT_FOUND='<h1>Query not found</h1>'
ERR_DOC_NOT_AVAILABLE='The requested result can not be shown now'
ERR_BAD_REQUEST='<h1>Bad request - Try different query</h1>'
#BASEDIR='/home/qdl/qatar-pics/data/' #change BASEDIR wherver deployed


HL_PRE = '<span style="background-color: #FFFF00"><strong>'
HL_POST = '</strong></span>'
page=10

#cursor = db.cursor()

def home(request):
    if request.method == 'GET':
        q = request.GET.get('q',None)
        type=request.GET.get('type','Search')
        if q != None and len(q) > 0:
            #process the query                                                                                                                   
            if type=='Docs':
                return profile_search(request)
            else:
                return render_to_response('rsc/index.html',context_instance=RequestContext(request))
        else:
            return render_to_response('rsc/index.html',context_instance=RequestContext(request))
def export_results(request):
    start=int(request.POST.get('start',0))
    q = request.POST.get('query', None).strip()
    try:
        s = Search(using=client, index="pubmed_authors").query("match", varname=q).query("match", name=q)  
        s = s[start:s.count()]
        response = s.execute() 
        if len(response) > 0:
            return_response = HttpResponse(content_type='text/csv')
            return_response['Content-Disposition'] = 'attachment; filename="all_clusters.csv"'
            writer = csv.writer(return_response)
            for hit in response:
                name_string = hit['name']
                cid = hit['id']
                varnames = hit['varname']
                affils = hit['affil']
                meshes = None
                if hit['mesh'] is not None:
                    meshes = map(str, hit['mesh'])
                meshes_count = hit['mesh_count']
                coauthors = hit['coauthor']
                coauthors_count = hit['coauthor_count']
                coauthors_name = hit['coauthor_name']
                pmids = hit['paper']
                paper_title = hit['paper_title']
                paper_venue = hit['paper_venue']
                paper_year = hit['paper_year']
                
                coauthors_info = []
                if coauthors:
                    index = 0
                    for coauthor in coauthors:
                        coauthor_info = {}
                        coauthor_info['cid'] = coauthors[index]
                        coauthor_info['name'] = coauthors_name[index]
                        coauthor_info['count'] = coauthors_count[index]
                        coauthors_info.append(coauthor_info)
                        index +=1
                papers = []
                if pmids:
                    index=0
                    for pmid in pmids:
                        paper = {}
                        paper['pmid'] = str(pmid)
                        paper['title'] = paper_title[index]
                        paper['venue'] =  paper_venue[index]
                        paper['year'] = str(paper_year[index])
                        papers.append(paper)
                        index +=1 
                meshes_string = makeStringWithCount(meshes, meshes_count, '&emsp;')
                writer.writerow(['id:',str(cid).encode('utf-8')])
                if name_string is not None:
                    writer.writerow(['name:', name_string.encode('utf-8')])
                if affils is not None:
                    affils = [handle_none(affil).encode('utf-8') for affil in affils]
                    writer.writerow(['affiliation:']+ list(affils))
                if meshes is not None:
                    writer.writerow([])
                    meshes = [handle_none(mesh).encode('utf-8') for mesh in meshes]
                    writer.writerow(['meshes:']+meshes)
                    writer.writerow(['meshes counts:']+list(meshes_count))
                if coauthors_name is not None:
                    writer.writerow([])
                    coauthors_name = [handle_none(author).encode('utf-8')for author in coauthors_name]
                    writer.writerow(['coauthors:']+ coauthors_name)
                    writer.writerow(['coauthorship counts:']+ list(coauthors_count))
                if papers is not None:
                    writer.writerow(['papers:'])
                    writer.writerow(['author ID','pmid', 'venue', 'year','title'])  
                    for paper in papers:
                        writer.writerow([cid, paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])

                writer.writerow([])
            return return_response
        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
    	print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)

def export_results_papers(request):
    start=int(request.POST.get('start',0))
    q = request.POST.get('query', None).strip()
    try: 
        s = Search(using=client, index="pubmed_authors").query("match", varname=q).query("match", name=q)  
        s = s[start:s.count()]
        response = s.execute() 
        if len(response) > 0:
            return_response = HttpResponse(content_type='text/csv')
            return_response['Content-Disposition'] = 'attachment; filename="all_clusters.csv"'
            writer = csv.writer(return_response)
            writer.writerow(['author ID','pmid', 'venue', 'year','title'])  
            for hit in response:
                cid = hit['id']
                meshes = None
                if hit['mesh'] is not None:
                    meshes = map(str, hit['mesh'])
                pmids = hit['paper']
                paper_title = hit['paper_title']
                paper_venue = hit['paper_venue']
                paper_year = hit['paper_year']
                
                papers = []
                if pmids:
                    index=0
                    for pmid in pmids:
                        paper = {}
                        paper['pmid'] = str(pmid)
                        paper['title'] = paper_title[index]
                        paper['venue'] =  paper_venue[index]
                        paper['year'] = str(paper_year[index])
                        papers.append(paper)
                        index +=1 
                
                if papers is not None:
                    for paper in papers:
                        writer.writerow([cid, paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])

                
            return return_response
        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
    	print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)

def advanced_export_results(request):
    title = request.POST.get('title', None)
    author = request.POST.get('author', None)
    coauthor = request.POST.get('coauthor', None)
    affil = request.POST.get('affil', None)
    venue = request.POST.get('venue', None)
    keyword = request.POST.get('keyword', None)
    print('author',author)

    try: 
        s = Search(using=client, index="pubmed_authors")
        if author !='' and author is not None:
            s=s.query("match", varname=author).query("match", name=q)  
        if keyword !='' and keyword is not None:
            s=s.query("match", mesh=keyword)
        if affil !='' and affil is not None:
            s=s.query("match", affil=affil)
        if venue !='' and venue is not None:
            s=s.query("match", paper_venue=venue)
        if title !='' and title is not None:
            s=s.query("match", paper_title=title)
        if coauthor !='' and coauthor is not None:
            s=s.query("match", coauthor_name=coauthor)
        s = s[0:s.count()]
        response = s.execute() 
        if len(response) > 0:
            return_response = HttpResponse(content_type='text/csv')
            return_response['Content-Disposition'] = 'attachment; filename="all_clusters.csv"'
            writer = csv.writer(return_response)
            for hit in response:
                name_string = hit['name']
                cid = hit['id']
                varnames = hit['varname']
                affils = hit['affil']
                meshes = None
                if hit['mesh'] is not None:
                    meshes = map(str, hit['mesh'])
                meshes_count = hit['mesh_count']
                coauthors = hit['coauthor']
                coauthors_count = hit['coauthor_count']
                coauthors_name = hit['coauthor_name']
                pmids = hit['paper']
                paper_title = hit['paper_title']
                paper_venue = hit['paper_venue']
                paper_year = hit['paper_year']
                
                coauthors_info = []
                if coauthors:
                    index = 0
                    for coauthor in coauthors:
                        coauthor_info = {}
                        coauthor_info['cid'] = coauthors[index]
                        coauthor_info['name'] = coauthors_name[index]
                        coauthor_info['count'] = coauthors_count[index]
                        coauthors_info.append(coauthor_info)
                        index +=1
                papers = []
                if pmids:
                    index=0
                    for pmid in pmids:
                        paper = {}
                        paper['pmid'] = str(pmid)
                        paper['title'] = paper_title[index]
                        paper['venue'] =  paper_venue[index]
                        paper['year'] = str(paper_year[index])
                        papers.append(paper)
                        index +=1 
                meshes_string = makeStringWithCount(meshes, meshes_count, '&emsp;')
                writer.writerow(['id:',str(cid).encode('utf-8')])
                if name_string is not None:
                    writer.writerow(['name:', name_string.encode('utf-8')])
                if affils is not None:
                    affils = [handle_none(affil).encode('utf-8') for affil in affils]
                    writer.writerow(['affiliation:']+ list(affils))
                if meshes is not None:
                    writer.writerow([])
                    meshes = [handle_none(mesh).encode('utf-8') for mesh in meshes]
                    writer.writerow(['meshes:']+meshes)
                    writer.writerow(['meshes counts:']+list(meshes_count))
                if coauthors_name is not None:
                    writer.writerow([])
                    coauthors_name = [handle_none(author).encode('utf-8')for author in coauthors_name]
                    writer.writerow(['coauthors:']+ coauthors_name)
                    writer.writerow(['coauthorship counts:']+ list(coauthors_count))
                
                if papers is not None:
                    writer.writerow(['papers:'])
                    writer.writerow(['author ID','pmid', 'venue', 'year','title'])  
                    for paper in papers:
                        writer.writerow([cid, paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])

                writer.writerow([])
            return return_response
        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
    	print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)

def advanced_export_results_papers(request):
    title = request.POST.get('title', None)
    author = request.POST.get('author', None)
    coauthor = request.POST.get('coauthor', None)
    affil = request.POST.get('affil', None)
    venue = request.POST.get('venue', None)
    keyword = request.POST.get('keyword', None)

    try: 
        s = Search(using=client, index="pubmed_authors")
        if author !='' and author is not None:
            s=s.query("match", varname=author).query("match", name=q)  
        if keyword !='' and keyword is not None:
            s=s.query("match", mesh=keyword)
        if affil !='' and affil is not None:
            s=s.query("match", affil=affil)
        if venue !='' and venue is not None:
            s=s.query("match", paper_venue=venue)
        if title !='' and title is not None:
            s=s.query("match", paper_title=title)
        if coauthor !='' and coauthor is not None:
            s=s.query("match", coauthor_name=coauthor)
        s = s[0:s.count()]
        response = s.execute() 
        if len(response) > 0:
            return_response = HttpResponse(content_type='text/csv')
            return_response['Content-Disposition'] = 'attachment; filename="all_clusters.csv"'
            writer = csv.writer(return_response)
            writer.writerow(['author ID','pmid', 'venue', 'year','title'])  
            for hit in response:
                cid = hit['id']
                meshes = None
                if hit['mesh'] is not None:
                    meshes = map(str, hit['mesh'])
                pmids = hit['paper']
                paper_title = hit['paper_title']
                paper_venue = hit['paper_venue']
                paper_year = hit['paper_year']
                
                papers = []
                if pmids:
                    index=0
                    for pmid in pmids:
                        paper = {}
                        paper['pmid'] = str(pmid)
                        paper['title'] = paper_title[index]
                        paper['venue'] =  paper_venue[index]
                        paper['year'] = str(paper_year[index])
                        papers.append(paper)
                        index +=1 
                
                if papers is not None:
                    for paper in papers:
                        writer.writerow([cid, paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])

                
            return return_response
        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
    	print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)

def profile_search(request):
    start=int(request.GET.get('start',0))
    q = request.GET.get('q', None).strip()
    try: 
        s = Search(using=client, index="pubmed_authors").query("match", varname=q).query("match", name=q)
        s = s[start:start+page]
        response = s.execute()
        if len(response) > 0:
            results=[]
            for hit in response:
                name_string = hit['name']
                varnames = hit['varname']
                affils = hit['affil']
                varname_string = makeString(varnames,'&emsp;')
                affil_string = makeString(affils,'<br>')
                d = DocResult(hit['id'],name_string,varname_string,affil_string)
                results.append(d)
            return render_to_response('rsc/resultdoc.html',{'results':results,'q': request.GET.get('q', None).strip(),\
                    'searchType':'Docs', 'total':s.count(), 'i':str(start+1)\
                    , 'j':str(len(results)+start) },context_instance=RequestContext(request))

        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)

def record_search(request):
    print "record_search"
    if request.method == "POST":
	print "record_search post"
	#form = DocumentForm(request.POST, request.FILES)
	#if form.is_valid():
	#    newdoc = UploadedDoc(docfile = request.FILES('docfile'))
	#    newdoc.save()
	#    return render_to_response('rsc/viewdoc.html')
	
	if request.FILES['docfile']:
	    ord = 1
	    if request.POST.get('ord') is not None:
		try:
		    ord = int(request.POST.get('ord'))
                except:
                    ord = 1
	    myfile = request.FILES['docfile']
            fs = FileSystemStorage()
            filename = fs.save('docs/'+myfile.name, myfile)
            upload_file_url = fs.url(filename)
	    upload_file_url = upload_file_url[1:]
	    #print upload_file_url

	    files = {'file': open(upload_file_url, 'rb')}
	    r = requests.post('http://heisenberg.ist.psu.edu:8000', files=files)
	    data = json.loads(r.text)
	    if data.get('status') == 200:
		data_id = data.get('id')
		order_dict = {'order':ord}
		r = requests.get('http://127.0.0.1:8000/'+data_id, params=order_dict)
		result_data = json.loads(r.text)
		if result_data.get('result') is not None:
		    if len(result_data.get('result'))>0:
		        query_string = 'id:('
			for cur_id in result_data.get('result'):
			    query_string += cur_id + ' OR '
			query_string = query_string [:-4] + ')'
			#query_string = ''
			#for cur_id in result_data.get('result'):
			#    query_string += cur_id + ' '
			#query_string = query_string[:-1] 
			print query_string
			
    			s=solr.SolrConnection(solr_disamseer)
        		#response=s.query(query_string, highlight=True, fields="id", hl_fragsize=50000, hl_simple_pre=HL_PRE, hl_simple_post=HL_POST, start=0)
	
			try: 
    			    #query_string = '{!q.op=OR}'+query_string
			    start = 0
        		    response=s.query(query_string, highlight=True, fields="*", hl_fragsize=50000, hl_simple_pre=HL_PRE, hl_simple_post=HL_POST, start=start, op='AND')
			    #response=s.query(query_string, fields='*', start=0)
			    #print response.highlighting
			    if len(response.results) > 0:
				results=[]
				for hit in response.results:
					
				    #hit_highlight = response.highlighting.get(hit.get('id'))
				    #print "hit_highlight:", hit_highlight
				    name_string = hit.get('name')
				    varnames = hit.get('varname')
				    affils = hit.get('affil')

				    #if hit_highlight:
				    #    if hit_highlight.get('name'):
			#		    title_string = hit_highlight.get('name')[0]

				#	if hit_highlight.get('varname'):
				#	    highlightArray(varnames, hit_highlight.get('varname'))
					    
				#	if hit_highlight.get('affil'):
				#	    highlightArray(affils, hit_highlight.get('affil'))

				    varname_string = makeString(varnames,'&emsp;')
				    affil_string = makeString(affils,'<br>')
					
				    d = DocResult(hit['id'],name_string,varname_string,affil_string)
				    #if len( hit.get('desc', "") ) > 0:
				    #	 d.desc=hit['desc']
				    results.append(d)

				return render_to_response('rsc/resultdoc.html',{'results':results,'q': query_string,\
					'searchType':'Docs', 'total':response.numFound, 'i':str(start+1)\
					, 'j':str(len(results)+start) },context_instance=RequestContext(request))

			    else:
				return HttpResponse(ERR_QUERY_NOT_FOUND)
			except:
			    print '-'*60
			    traceback.print_exc(file=sys.stdout)
			    print '-'*60
			    return HttpResponse(ERR_BAD_REQUEST)
	    
            #return render_to_response('rsc/viewdoc.html')

	
    #else:
    #    form = DocumentForm()
    return render_to_response('rsc/record_search.html', {}, context_instance=RequestContext(request))

	#form = DocumentForm(request.POST, request.FILES)
        #if form.is_valid():
        #  form.save()
	#  return render_to_response('rsc/viewdoc.html')
        #else:
        #  return HttpResponse(ERR_BAD_REQUEST)
    #else:
	#form = DocumentForm()
        #return render_to_response('rsc/record_search.html')

def transfer_to_advance(request):	
    return render_to_response('rsc/advanced_search.html', {},context_instance=RequestContext(request))
def advanced_search(request):
    start=int(request.POST.get('start',0))
    title = request.POST.get('title', None)
    author = request.POST.get('author', None)
    coauthor = request.POST.get('coauthor', None)
    affil = request.POST.get('affil', None)
    venue = request.POST.get('venue', None)
    keyword = request.POST.get('keyword', None)
    q ='' 
    if author!='':
        q += 'varname:' + author 
    if keyword!='' :
        q += ' AND mesh:' + keyword
    if affil !='':
        q += ' AND affil:' + affil 
    if venue !='':
        q += ' AND paper_venue:' + venue
    if title !='':
        q += ' AND paper_title:' + title
    if coauthor !='':
        q += ' AND coauthor_name:' + coauthor
        
    if q[:4]== ' AND':
        q = q[5:]
    try: 
        s = Search(using=client, index="pubmed_authors")
        if author !='' and author is not None:
            s=s.query("match", varname=author).query("match", name=author)
        if keyword !='' and keyword is not None:
            s=s.query("match", mesh=keyword)
        if affil !='' and affil is not None:
            s=s.query("match", affil=affil)
        if venue !='' and venue is not None:
            s=s.query("match", paper_venue=venue)
        if title !='' and title is not None:
            s=s.query("match", paper_title=title)
        if coauthor !='' and coauthor is not None:
            s=s.query("match", coauthor_name=coauthor)
        s = s[start:start+page]
        response = s.execute()
        if len(response) > 0:
            results=[]
            for hit in response:
                name_string = hit['name']
                varnames = hit['varname']
                affils = hit['affil']
                varname_string = makeString(varnames,'&emsp;')
                affil_string = makeString(affils,'<br>')
                
                d = DocResult(hit['id'],name_string,varname_string,affil_string)
                results.append(d)

            return render_to_response('rsc/advance_resultdoc.html',{'results':results,'title':title, 'author':author, 'coauthor':coauthor,'q':q,\
                    'affil':affil, 'venue':venue, 'keyword':keyword, 'searchType':'Docs', 'total':s.count(), 'i':str(start+1)\
                    , 'j':str(len(results)+start) },context_instance=RequestContext(request))

        else:
            return HttpResponse(ERR_QUERY_NOT_FOUND)
    except:
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        return HttpResponse(ERR_BAD_REQUEST)
def export_papers(request):
    cid=request.POST.get('cid',None)
    if cid != None:
        s = Search(using=client, index="pubmed_authors").query("match", id=cid)
        s = s[0:s.count()]
        response = s.execute()
        if len(response) > 0:
            hit=response[0] # should be only one, id is primary key
            name_string = hit['name']
            varnames = hit['varname']
            affils = hit['affil']
            meshes = None
            if hit['mesh'] is not None:
                meshes = map(str, hit['mesh'])
            meshes_count = hit['mesh_count']
            coauthors = hit['coauthor']
            coauthors_count = hit['coauthor_count']
            coauthors_name = hit['coauthor_name']
            pmids = hit['paper']
            paper_title = hit['paper_title']
            paper_venue = hit['paper_venue']
            paper_year = hit['paper_year']
            
            coauthors_info = []
            if coauthors:
                index = 0
                for coauthor in coauthors:
                    coauthor_info = {}
                    coauthor_info['cid'] = coauthors[index]
                    coauthor_info['name'] = coauthors_name[index]
                    coauthor_info['count'] = coauthors_count[index]
                    coauthors_info.append(coauthor_info)
                    index +=1
            papers = []
            if pmids:
                index=0
                for pmid in pmids:
                    paper = {}
                    paper['pmid'] = str(pmid)
                    paper['title'] = paper_title[index]
                    paper['venue'] =  paper_venue[index]
                    paper['year'] = str(paper_year[index])
                    papers.append(paper)
                    index +=1 
            meshes_string = makeStringWithCount(meshes, meshes_count, '&emsp;')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="'+cid+'_papers.csv"'
            writer = csv.writer(response)
            print('number of papers',len(papers))
            if papers is not None:
                writer.writerow(['author ID','pmid', 'venue', 'year','title'])  
                for paper in papers:
                    writer.writerow([cid, paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])
            return response
        else:
            return HttpResponse(ERR_DOC_NOT_AVAILABLE)
    else:
        return HttpResponse(ERR_DOC_NOT_AVAILABLE)

def export_author_info(request):
    cid=request.POST.get('cid',None)
    if cid != None:
        s = Search(using=client, index="pubmed_authors").query("match", id=cid)
        s = s[0:s.count()]
        response = s.execute()
        if len(response) > 0:
            hit=response[0] # should be only one, id is primary key
            name_string = hit['name']
            varnames = hit['varname']
            affils = hit['affil']
            meshes = None
            if hit['mesh'] is not None:
                meshes = map(str, hit['mesh'])
            meshes_count = hit['mesh_count']
            coauthors = hit['coauthor']
            coauthors_count = hit['coauthor_count']
            coauthors_name = hit['coauthor_name']
            pmids = hit['paper']
            paper_title = hit['paper_title']
            paper_venue = hit['paper_venue']
            paper_year = hit['paper_year']
            
            coauthors_info = []
            if coauthors:
                index = 0
                for coauthor in coauthors:
                    coauthor_info = {}
                    coauthor_info['cid'] = coauthors[index]
                    coauthor_info['name'] = coauthors_name[index]
                    coauthor_info['count'] = coauthors_count[index]
                    coauthors_info.append(coauthor_info)
                    index +=1
            papers = []
            if pmids:
                index=0
                for pmid in pmids:
                    paper = {}
                    paper['pmid'] = str(pmid)
                    paper['title'] = paper_title[index]
                    paper['venue'] =  paper_venue[index]
                    paper['year'] = str(paper_year[index])
                    papers.append(paper)
                    index +=1 
            meshes_string = makeStringWithCount(meshes, meshes_count, '&emsp;')
            
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="'+cid+'.csv"'
            writer = csv.writer(response)
            writer.writerow(['id:',cid.encode('utf-8')])
            if name_string is not None:
                writer.writerow(['name:', name_string.encode('utf-8')])
            if affils is not None:
                affils = [handle_none(affil).encode('utf-8') for affil in affils]
                writer.writerow(['affiliation:']+ affils)
            if papers is not None:
                writer.writerow(['papers:'])
                writer.writerow(['pmid', 'venue', 'year','title'])  
                for paper in papers:
                    writer.writerow([paper['pmid'], handle_none(paper['venue']).encode('utf-8'), handle_none(paper['year']).encode('utf-8'), handle_none(paper['title']).encode('utf-8')])
            if meshes is not None:
                writer.writerow([])
                meshes = [handle_none(mesh).encode('utf-8') for mesh in meshes]
                writer.writerow(['meshes:']+meshes)
                writer.writerow(['meshes counts:']+list(meshes_count))
            if coauthors_name is not None:
                writer.writerow([])
                coauthors_name = [handle_none(author).encode('utf-8')for author in coauthors_name]
                writer.writerow(['coauthors:']+ coauthors_name)
                writer.writerow(['coauthorship counts:']+ list(coauthors_count))
            return response
        else:
            return HttpResponse(ERR_DOC_NOT_AVAILABLE)
    else:
        return HttpResponse(ERR_DOC_NOT_AVAILABLE)

def handle_none(arg):
    return arg  if arg is not None else ''
def viewdocument(request):
    cid=request.GET.get('id',None)
    hq = None
    if cid != None:
        s = Search(using=client, index="pubmed_authors").query("match", id=cid)
        s = s[0:s.count()]
        response = s.execute()
        if len(response) > 0:
            hit=response[0] # should be only one, id is primary key

            name_string = hit['name']
            varnames = hit['varname']
            affils = hit['affil']
            meshes = hit['mesh']
            meshes_count = hit['mesh_count']
            coauthors = hit['coauthor']
            coauthors_count = hit['coauthor_count']
            coauthors_name = hit['coauthor_name']
            pmids = hit['paper']
            paper_title = hit['paper_title']
            paper_venue = hit['paper_venue']
            paper_year = hit['paper_year']
            
            papers = [] 
            if pmids:
                index = 0
                for pmid in pmids:
                    paper = {}
                    paper['pmid'] = str(pmid)
                    paper['info'] = paper_title[index] + ' <i>' + paper_venue[index] + '</i> ('+str(paper_year[index])+')' 
                    papers.append(paper)
                    index +=1
            coauthors_info = []
            if coauthors:
                index = 0
                for coauthor in coauthors:
                    coauthor = {}
                    coauthor['id'] = coauthors[index]
                    coauthor['name'] = coauthors_name[index] 
                    coauthor['count'] =  coauthors_count[index]
                    coauthors_info.append(coauthor)
                    index +=1
            varnames_string = makeString(varnames,'&emsp;')
            affils_string = makeString(affils, '<br>')
            meshes_string = makeStringWithCount(meshes, meshes_count, '&emsp;')
            ten_meshes_string = makeTenStringWithCount(meshes, meshes_count, '&emsp;')
            #coauthors_string = makeArrayToString(coauthors)
            d=DocInfo(cid,name_string,varnames_string,affils_string, papers, meshes_string, ten_meshes_string, coauthors_info, hq)
            return render_to_response('rsc/viewdoc.html', {'d': d},context_instance=RequestContext(request))
        else:
            return HttpResponse(ERR_DOC_NOT_AVAILABLE)
    else:
        return HttpResponse(ERR_DOC_NOT_AVAILABLE)

def highlightArray(array, hl_array):
    for item in hl_array:
        cur_item = item.replace(HL_PRE, '')
        cur_item = cur_item.replace(HL_POST, '')
        if cur_item in array:
            array[array.index(cur_item)] = item

def makeAuthorString(authors):
    author_string = ""
    if authors:
        for author in authors:
            author_string += author + "<br>"
    if len(author_string) > 0:
        author_string = author_string[:-4]
    return author_string

def makeString(array, delim):
    result_string = ""
    if array:
        for item in array:
            result_string += item + delim
    if len(result_string) > 0:
        result_string = result_string[:-len(delim)]
    return result_string

def makeStringWithCount(array, cnt, delim):
    result_string = ""
    if array:
        length = len(array)
        for i in range(length):
            result_string += array[i] + "(" + str(cnt[i]) + ")" + delim
    if len(result_string) > 0:
        result_string = result_string[:-len(delim)]
    return result_string
def makeTenStringWithCount(array, cnt, delim):
    result_string = ""
    if array:
        length = min(10,len(array))
        for i in range(length):
            result_string += array[i] + "(" + str(cnt[i]) + ")" + delim
    if len(result_string) > 0:
        result_string = result_string[:-len(delim)]
    return result_string

def makeAuthorString2(authors, affiliations):
    author_string = ""
    if authors:
        idx = 0
        for author in authors:
            author_string += author + "("+ affiliations[idx] + ")" + ", "
            idx += 1
    if len(author_string) > 0:
        author_string = author_string[:-2]
    return author_string

def makeArrayToString(items):
    items_string = ""
    if items:
        for item in items:
            items_string += item + "&emsp;"
    if len(items_string) > 0:
        items_string = items_string[:-6]
    return items_string

'''
def zipdir(path, zip):
    for file in os.listdir(path):
        zip.write(os.path.join(path, file))

def copyandZipAllRelevantFiles(s,imageLoc):

    if (os.path.exists('imgfiles')):
        if not os.path.isfile('imgfiles'):
             shutil.rmtree('imgfiles')

    os.makedirs('imgfiles')

    a,b=os.path.split(imageLoc) #a is the directory containing final image file
    allFiles=os.listdir(a)
    for f in allFiles:
         if b[:-4] in f and os.path.isfile(os.path.join(a,f)):
            shutil.copy(os.path.join(a,f),'imgfiles')

    zipf = zipfile.ZipFile(s, 'w')
    zipdir('imgfiles', zipf)
    zipf.close()


def download(request,loc):
    actualLoc=os.path.join(BASEDIR,loc)
    s = StringIO.StringIO()
    copyandZipAllRelevantFiles(s,actualLoc)
    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % 'imgfiles.zip'
    return resp
'''
