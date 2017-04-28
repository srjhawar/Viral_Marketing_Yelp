import snap
FIn = snap.TFIn("am.graph")
G1 = snap.TUNGraph.Load(FIn)
G1.GetNodes()
CntV = snap.TIntPrV()
snap.GetWccSzCnt(G1, CntV)
for comp in CntV:
	print "Size: %d - Number of Components: %d" % (comp.GetVal1(), comp.GetVal2())

Components = snap.TCnComV()
snap.GetWccs(G1, Components)
for CnCom in Components:
#	print "Size of component: %d" % CnCom.Len()
	if CnCom.Len()==10636:
		comp = CnCom
f = open('comp4.txt','a+')
for item in comp:
	f.write(str(item))
	f.write("\n")

