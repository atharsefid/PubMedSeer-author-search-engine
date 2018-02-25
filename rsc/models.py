from django.db import models

# Create your models here.

class DocInfo:
    def __init__(self,cid,name,varnames,affils,papers,meshes, ten_meshes,coauthors, hq):
        self.cid = cid
        print(cid,'in the models .py')
        self.name=name
        self.varnames=varnames
        self.affils=affils
        self.papers=papers
        self.ten_papers = papers[:10]
        self.meshes=meshes
        self.ten_meshes=ten_meshes
        self.coauthors=coauthors
        self.ten_coauthors=coauthors[:10]
        self.hq= hq

class DocResult:
    def __init__(self,cid,name,varnames,affils):
        self.cid = cid
        self.name=name
        self.varnames=varnames
        self.affils=affils

class UploadedDoc(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m')
