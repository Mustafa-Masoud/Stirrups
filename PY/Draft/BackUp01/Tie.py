# Load the Python Standard and DesignScript Libraries
import sys
import math
import clr
from itertools import chain
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
import Autodesk
from itertools import islice


# The inputs to this node will be stored as a list in the IN variables.
dataEnteringNode = IN

#""" Global Variables"""
#b = int(input('please enter column's b length: '))
b = 3500
#h = int(input('please enter column's h length: '))
h = 400
#bp = list(range(int(input("please enter column's b side rebar number: "))))
bPoints = list(range(39))
_bPoints = bPoints[:]
#hp = list(range(int(input("please enter column's h side rebar number: "))))
hPoints = list(range(4))
_hPoints = hPoints
#sp = int(input("please enter v-spacing criteria: "))
sp = 150
#hlen = int(input("Please enter h length criteria: "))
bMin = 600

clearCover = 40
vDia = 25
hDia = 12
vCover = clearCover+hDia+(vDia/2.0)
hCover = clearCover+(hDia/2.0)

asp = (b-(2*vCover))/float(len(bPoints)-1)

#----------------------------------------------------------
""" DYNAMO-PYTHON Geometry Function """
def slc(lst): #to slice vertical rebar list into pattern.
	div = [3, 1]
	patt = (len(lst)//2)*div
	it = iter(lst)
	sliced =[list(islice(it, 0, i)) for i in patt]
	for i in sliced[::-1]:
	    if i == []:
        	sliced.remove(i)
	return sliced
# Concrete Column
basePoint = Point.ByCoordinates(0, 0, 0)

def column(basePoint, b, h):
	p1 = basePoint
	p2 = Geometry.Translate(p1, Vector.XAxis(), b)
	p3 = Geometry.Translate(p2, Vector.YAxis(), h)
	p4 = Geometry.Translate(p3, Vector.XAxis(), -b)
	lp = [p1, p2, p3, p4]
	pl = Polygon.ByPoints(lp)
	return pl, lp

# Vertical Rebar Distribution
def vRebar(basePoint, vCover, hCover, bPoints, hPoints, b, h):
	_p = Geometry.Translate(basePoint, Vector.ByCoordinates(vCover, vCover, 0))
	absp = (b-(2*vCover))/(len(bPoints)-1)
	dabsp = absp
	ahsp = (h-(2*vCover))/(len(hPoints)-1)
	dahsp = ahsp
	lbp = [_p]
	_lbp = []
	lhp = [_p]
	_lhp = []
	for nb in range(len(bPoints)-1):
		lbp.append(Geometry.Translate(_p, Vector.ByCoordinates(dabsp, 0, 0)))
		dabsp += absp
	for _nb in lbp:
		_lbp.append(Geometry.Translate(_nb, Vector.ByCoordinates(0, h-(2*vCover), 0)))
	for nh in range(len(hPoints)-1):
		lhp.append(Geometry.Translate(_p, Vector.ByCoordinates(0, dahsp, 0)))
		dahsp += ahsp
	for _nh in lhp:
		_lhp.append(Geometry.Translate(_nh, Vector.ByCoordinates(b-(2*vCover), 0, 0)))
	return lbp[1:-1], _lbp[1:-1], lhp, _lhp

# Get rebars of same position in the opposit list
def getTwin(vRebar, pureb_leftRebar, currentRebars, side):
	vRebars = vRebar(basePoint, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	vRebars_bPointsList = vRebars[1]
	vRebarshPointsList = vRebars[2]
	vRebars_hPointsList = vRebars[3]

	if len(pureb_leftRebar) == 0:
		temp1 = currentRebars[:]
		oppositRebars = []
		for i in temp1:
			if side == 'b':
				ti = vRebarsbPointsList.index(i)
				t = vRebars_bPointsList[ti]
				oppositRebars.append(t)
		return oppositRebars
	if len(pureb_leftRebar) == 1:
		temp1 = currentRebars[:]
		oppositRebars = []
		for i in temp1:
			if side == 'b':
				ti = vRebarsbPointsList.index(i)
				t = vRebars_bPointsList[ti]
				oppositRebars.append(t)
		return oppositRebars
	elif len(pureb_leftRebar) >= 2:
		temp1 = list(chain.from_iterable(currentRebars))
		temp2 = []
		n = len(currentRebars[0])
		for l in temp1:
			li = temp1.index(l)
			if side == 'b':
				ti = vRebarsbPointsList.index(l)
				t = vRebars_bPointsList[ti]
				temp2.append(t)
		oppositRebars = [temp2[i:i + n] for i in range(0, len(temp2), n)]
		return oppositRebars
	
# Getting Stirrup's curves from Pure Points:
def getCurve(stirrupPoints):
	currentPoints = stirrupPoints[0]
	twinPoints = stirrupPoints[1]
	purePoints = [currentPoints, twinPoints]

	try:
		for lst in twinPoints:
			list.reverse(lst)
		purePoints_transposed = list(map(list, zip(*purePoints)))
		flattened = []
		for i in purePoints_transposed:
			flattened.append(list(chain.from_iterable(i)))
		return flattened
	except: #for single pure rebar per one half of a side
		list.reverse(twinPoints)
		flattened = []
		#flattened.append(list(chain.from_iterable(purePoints)))
		return stirrupPoints
# Conditioning Grouping:
# Main Function:
def stirrups(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	mainTies = tie(p, vCover, hCover, bPoints, hPoints, b, h)
	sideTies = tieSide(p, vCover, hCover, bPoints, hPoints, b, h)
	curves_mainTies = getCurve(mainTies)

	if len(hPoints) <= 3:
		return curves_mainTies
	elif len(hPoints) >3:
		return curves_mainTies, sideTies

def tieSide(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	vRebars_bPointsList = vRebars[1]
	vRebarshPointsList = vRebars[2]
	vRebars_hPointsList = vRebars[3]
	hHalf = len(vRebarshPointsList)/2
	h_leftRebar = vRebarshPointsList[:hHalf]
	h_rightRebar = vRebarshPointsList[hHalf+1:][::-1]
	pureh_Rebar = vRebarshPointsList[1:-1]
	
	leftMostB = vRebarsbPointsList[0], vRebars_bPointsList[0]
	rightMostB = vRebarsbPointsList[-1], vRebars_bPointsList[-1]
	hMid = vRebarshPointsList[hHalf]
	h_vRebarTieTemp = []
	_h_vRebarTieTemp = []
	if len(vRebarshPointsList) == 4:
		h_vRebarTieTemp.append(vRebarshPointsList[1:-1])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append(vRebars_hPointsList[1:-1])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie
	elif len(vRebarshPointsList) == 5:
		h_vRebarTieTemp.append([vRebarshPointsList[2]])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append([vRebars_hPointsList[2]])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie
	elif len(vRebarshPointsList) == 6 or len(vRebarshPointsList) == 7:
		h_vRebarTieTemp.append(vRebarshPointsList[2:-2])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append(vRebars_hPointsList[2:-2])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie

def tie(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	if len(vRebars[0])%2 != 0:	#Odd Number
		return tieOdd(p, vCover, hCover, bPoints, hPoints, b, h)
	else:						#Even Number
		return tieEven(p, vCover, hCover, bPoints, hPoints, b, h)

def tieOdd(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf+1:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]
	if len(pureb_leftRebar) <= 3:
		return tieOdd1(p, vCover, hCover, bPoints, hPoints, b, h)
	else:
		return tieOdd2(p, vCover, hCover, bPoints, hPoints, b, h)

def tieEven(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]
	if len(pureb_leftRebar) <= 3:
		return tieEven1(p, vCover, hCover, bPoints, hPoints, b, h)
	else:
		return tieEven2(p, vCover, hCover, bPoints, hPoints, b, h)


def tieOdd1(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf+1:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]
		
	bMid = vRebarsbPointsList[bHalf]
	if len(pureb_leftRebar) == 0:
		b_vRebarTie = [bMid]
		_b_vRebarTie = getTwin(vRebar,pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	if len(pureb_leftRebar) == 1:
		b_vRebarTie = list((pureb_leftRebar[-1], pureb_rightRebar[-1]))
		_b_vRebarTie = getTwin(vRebar,pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	elif len(pureb_leftRebar) == 2:
		b_vRebarTie = list((pureb_leftRebar[-2:], pureb_rightRebar[-2:]))
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	elif len(pureb_leftRebar) == 3:
		b_vRebarTie = list((pureb_leftRebar[::2], pureb_rightRebar[::2]))
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie

def tieEven1(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]
		
	if len(pureb_leftRebar) == 0:
		b_vRebarTie = list((b_leftRebar[-1], b_rightRebar[-1]))
		_b_vRebarTie = getTwin(vRebar,pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	elif len(pureb_leftRebar) == 1:
		b_vRebarTie = list((b_leftRebar[-1], b_rightRebar[-1]))
		_b_vRebarTie = getTwin(vRebar,pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	elif len(pureb_leftRebar) == 2 or len(pureb_leftRebar) == 3:
		b_vRebarTie = list((pureb_leftRebar[::len(pureb_leftRebar)-1], pureb_rightRebar[::len(pureb_rightRebar)-1]))
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie

def tieOdd2(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf+1:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]

	bMid = vRebarsbPointsList[bHalf]
	aLeft = slc(pureb_leftRebar)
	aRight = slc(pureb_rightRebar)
	lenLast = len(aLeft[-1])
	lenBeforeLast = len(aLeft[-2])
	b_vRebarTie = []
	if lenLast == 1 and lenBeforeLast == 3:			#17
		for i in aLeft:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		for i in aRight:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		b_vRebarTie.append([bMid])
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	elif lenLast == 1 and lenBeforeLast == 1:		#19
		for i in aLeft:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		b_vRebarTie.append(aLeft[-1])
		b_vRebarTie[-1].append(aRight[-1][0])
		for i in aRight:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	else: 											#21 onward
		for i in aLeft:
			if len(i) == 3 or len(i) == 2:
				b_vRebarTie.append([i[0], i[-1]])
		for i in aRight:
			if len(i) == 3 or len(i) == 2:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie

def tieEven2(p, vCover, hCover, bPoints, hPoints, b, h):
	vRebars = vRebar(p, vCover, hCover, bPoints, hPoints, b, h)
	vRebarsbPointsList = vRebars[0]
	bHalf = len(vRebarsbPointsList)/2
	b_leftRebar = vRebarsbPointsList[:bHalf]
	b_rightRebar = vRebarsbPointsList[bHalf:][::-1]
	if len(hPoints) <= 3:
		pureb_leftRebar = b_leftRebar[1:]
		pureb_rightRebar = b_rightRebar[1:]
	elif len(hPoints) > 3:
		pureb_leftRebar = b_leftRebar[2:]
		pureb_rightRebar = b_rightRebar[2:]

	aLeft = slc(pureb_leftRebar)
	aRight = slc(pureb_rightRebar)
	lenLast = len(aLeft[-1])
	lenBeforeLast = len(aLeft[-2])
	b_vRebarTie = []

	if lenLast == 1 and lenBeforeLast == 3:			#17
		if len(aLeft) == 2:
			b_vRebarTie.append(aLeft[-2][0:2])
			b_vRebarTie.append(aLeft[-1])
			b_vRebarTie[-1].append(aRight[-1][0])
			b_vRebarTie.append(aRight[-2][0:2])
			_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
			return b_vRebarTie, _b_vRebarTie
		if len(aLeft) > 2:
			for i in aLeft[:-2]:
				if len(i) == 3:
					b_vRebarTie.append([i[0], i[-1]])
			b_vRebarTie.append(aLeft[-2][0:2])
			b_vRebarTie.append(aLeft[-1])
			b_vRebarTie[-1].append(aRight[-1][0])
			b_vRebarTie.append(aRight[-2][0:2])
			for i in aRight[:-2]:
				if len(i) == 3:
					b_vRebarTie.append([i[0], i[-1]])
			_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
			return b_vRebarTie, _b_vRebarTie
	elif lenLast == 1 and lenBeforeLast == 1:		#19
		for i in aLeft:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		b_vRebarTie.append(aLeft[-1])
		b_vRebarTie[-1].append(aRight[-1][0])
		for i in aRight:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
	else: 											#21 onward
		for i in aLeft:
			if len(i) == 3 or len(i) == 2:
				b_vRebarTie.append([i[0], i[-1]])
		for i in aRight:
			if len(i) == 3 or len(i) == 2:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vRebar, pureb_leftRebar, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
#----------------------------------
# TESTING
column = column(basePoint, b, h)
vRebars = vRebar(basePoint, vCover, hCover, bPoints, hPoints, b, h)
links = tie(basePoint, vCover, hCover, bPoints, hPoints, b, h)
links = stirrups(basePoint, vCover, hCover, bPoints, hPoints, b, h)

#OUT = getTwin(vRebar, 1, 3)
#OUT = getCurve(links)

OUT = links, vRebars, column
