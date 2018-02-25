import sys,os

posdir=sys.argv[1]
a,b=os.path.split(posdir)
print a,b
f=open(os.path.join(a,b+"-allpositions"),"w")
for posFile in os.listdir(posdir):
	positions=open(os.path.join(posdir,posFile),"r").read().split("\n")
	
	xs=[]
	ys=[]
	for it in positions:
		if it:
			xs.append(int(it.split(",")[0]))
			ys.append(int(it.split(",")[1]))
	if xs and ys:	
		f.write(str(min(xs))+","+str(min(ys))+","+str(max(xs))+","+str(max(ys))+"\n")

f.close()
		
		
	
