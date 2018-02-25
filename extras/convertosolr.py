#expects a directory as input, searches for all ".txt" files 
#in that directory, converts it to a solr complient xml.
#xml structure: <figid> </figid> <desc> </desc>

import os,sys
import fnmatch
from lxml import etree
import codecs

def listAllfiles(inpDir,extFilter):
	matches = []
	for root, dirnames, filenames in os.walk(inpDir):
		for filename in fnmatch.filter(filenames, '*mod.'+extFilter):
			matches.append(os.path.join(root, filename))
	return matches

def convertToSolrXML(content,fileName,counter):
	c='<add><doc>\n\t<field name="id">'
	c=c+str(counter)
	c=c+'</field>\n\t<field name="figloc">'
	if os.path.exists(os.path.abspath(fileName)[:-8]+".jpg"):
		c=c+os.path.abspath(fileName)[:-8]+".jpg"
	else:
		return None
	c=c+'</field>\n\t<field name="desc">'
	c=c+content
	c=c+'</field>\n</doc></add>'
	#sanitizing the xml before returning
	#print c
	try:
		parser = etree.XMLParser(recover=True) # recover from bad characters.
		root = etree.fromstring(c, parser=parser)
		return etree.tostring(root, encoding='unicode')
	except:
		print "couldn't sanitize",os.path.abspath(fileName)
		return None

def main():
	inpDir=sys.argv[1]
	print "file searching started"
	files=listAllfiles(inpDir,'txt')
	for index,item in enumerate(files):
		print index,os.path.abspath(item)[:-8]+".xml","out of",len(files),"being processed"
		f = codecs.open(item, encoding='utf-8')
		con= f.read()
		c=convertToSolrXML(con,item,index+1)
		#print con,c
		if c:
			print os.path.abspath(item)[:-8]+".xml"
			with open(os.path.abspath(item)[:-8]+".xml","w") as f:
				f.write(c.encode("utf-8"))
		else:
			print "problem finding image file"

if __name__ == "__main__":
	main()	
	
		
