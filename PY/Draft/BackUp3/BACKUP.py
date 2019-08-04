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
bLen = 3500
hLen = 400
bRange = list(range(IN[0]))
_bRange = bRange[:]
hRange = list(range(IN[1]))
_hRange = hRange[:]
sp = IN[2]
bMin = 600

cc = 40
vDia = 25
hDia = 12
vCover = cc+hDia+(vDia/2.0)
hCover = cc+(hDia/2.0)
asp = (bLen-(2*vCover))/float(len(bRange)-1)
basePoint = Point.ByCoordinates(0, 0, 0)
vAttribute = {'basePoint': basePoint,'clearCover': cc, 'vCover': vCover, 'hCover': hCover, 'bRange': bRange, 
'_bRange': _bRange, 'hRange': hRange, '_hRange': _hRange, 'bLen': bLen, 'hLen': hLen, 'spacing': sp, 'actualSpacing': asp}
#----------------------------------------------------------
""" DYNAMO-PYTHON Geometry Function """
def slc(lst, attribute_Dict): #to slice vertical rebar list into pattern.
	if attribute_Dict['spacing'] <= 150:
		pattRange = 3
		div = [pattRange, 1]
	else:
		pattRange = 2
		div = [pattRange, 2]
	patt = (len(lst)//2)*div
	it = iter(lst)
	sliced =[list(islice(it, 0, i)) for i in patt]
	for i in sliced[::-1]:
	    if i == []:
        	sliced.remove(i)
	return sliced, pattRange
# Concrete Column
def column(attribute_Dict):
	p1 = vAttribute['basePoint']
	p2 = Geometry.Translate(p1, Vector.XAxis(), vAttribute['bLen'])
	p3 = Geometry.Translate(p2, Vector.YAxis(), vAttribute['hLen'])
	p4 = Geometry.Translate(p3, Vector.XAxis(), -vAttribute['bLen'])
	lp = [p1, p2, p3, p4]
	pl = Polygon.ByPoints(lp)
	return pl, lp

# Vertical Rebar Distribution
def vRebar(attribute_Dict):#basePoint, vCover, hCover, bPoints, hPoints, b, h):
	_p = Geometry.Translate(vAttribute['basePoint'], Vector.ByCoordinates(vAttribute['vCover'], vAttribute['vCover'], 0))
	absp = (vAttribute['bLen']-(2*vAttribute['vCover']))/(len(vAttribute['bRange'])-1)
	dabsp = absp
	ahsp = (vAttribute['hLen']-(2*vAttribute['vCover']))/(len(vAttribute['hRange'])-1)
	dahsp = ahsp
	lbp = [_p]
	_lbp = []
	lhp = [_p]
	_lhp = []
	for nb in range(len(vAttribute['bRange'])-1):
		lbp.append(Geometry.Translate(_p, Vector.ByCoordinates(dabsp, 0, 0)))
		dabsp += absp
	for _nb in lbp:
		_lbp.append(Geometry.Translate(_nb, Vector.ByCoordinates(0, vAttribute['hLen']-(2*vAttribute['vCover']), 0)))
	for nh in range(len(vAttribute['hRange'])-1):
		lhp.append(Geometry.Translate(_p, Vector.ByCoordinates(0, dahsp, 0)))
		dahsp += ahsp
	for _nh in lhp:
		_lhp.append(Geometry.Translate(_nh, Vector.ByCoordinates(vAttribute['bLen']-(2*vAttribute['vCover']), 0, 0)))
	vertical = {'bPoints': lbp[1:-1],'_bPoints': _lbp[1:-1], 'hPoints': lhp, '_hPoints': _lhp}
	return vertical

# Get rebars of same position in the opposit list
def getTwin(vertical_Dict, range_to_check, currentRebars, side):
	if len(range_to_check['pureb_left']) == 0:
		temp1 = currentRebars[:]
		oppositRebars = []
		for i in temp1:
			if side == 'b':
				ti = vertical_Dict['bPoints'].index(i)
				t = vertical_Dict['_bPoints'][ti]
				oppositRebars.append(t)
		return oppositRebars
	if len(range_to_check['pureb_left']) == 1:
		temp1 = currentRebars[:]
		oppositRebars = []
		for i in temp1:
			if side == 'b':
				ti = vertical_Dict['bPoints'].index(i)
				t = vertical_Dict['_bPoints'][ti]
				oppositRebars.append(t)
		return oppositRebars
	elif len(range_to_check['pureb_left']) >= 2:
		temp1 = list(chain.from_iterable(currentRebars))
		temp2 = []
		n = len(currentRebars[0])
		for l in temp1:
			li = temp1.index(l)
			if side == 'b':
				ti = vertical_Dict['bPoints'].index(l)
				t = vertical_Dict['_bPoints'][ti]
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
		flattened.append(list(chain.from_iterable(purePoints)))
		return flattened
# Conditioning Grouping:
# Main Function:
def stirrups(vertical_Dict, attribute_Dict, range_to_check):
	mainTies = tie(vertical_Dict, attribute_Dict, range_to_check)
	sideTies = tieSide(vertical_Dict, attribute_Dict)
	curves_mainTies = getCurve(mainTies)
	if len(vertical_Dict['hPoints']) <= 3:
		return curves_mainTies
	else:
		return curves_mainTies, sideTies

def tieSide(vertical_Dict, attribute_Dict):
	hHalf = len(vertical_Dict['hPoints'])/2
	h_leftRebar = vertical_Dict['hPoints'][:hHalf]
	h_rightRebar = vertical_Dict['hPoints'][hHalf+1:][::-1]
	pureh_Rebar = vertical_Dict['hPoints'][1:-1]
	
	leftMostB = vertical_Dict['bPoints'][0], vertical_Dict['_bPoints'][0]
	rightMostB = vertical_Dict['bPoints'][-1], vertical_Dict['_bPoints'][-1]
	h_mid = vertical_Dict['hPoints'][hHalf]
	h_vRebarTieTemp = []
	_h_vRebarTieTemp = []
	
	if len(vertical_Dict['hPoints']) == 4:
		h_vRebarTieTemp.append(vertical_Dict['hPoints'][1:-1])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append(vertical_Dict['_hPoints'][1:-1])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie
	elif len(vertical_Dict['hPoints']) == 5:
		h_vRebarTieTemp.append([vertical_Dict['hPoints'][2]])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append([vertical_Dict['_hPoints'][2]])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie
	elif len(vertical_Dict['hPoints']) == 6 or len(vertical_Dict['hPoints']) == 7:
		h_vRebarTieTemp.append(vertical_Dict['hPoints'][2:-2])
		h_vRebarTieTemp.append(leftMostB[::-1])
		_h_vRebarTieTemp.append(vertical_Dict['_hPoints'][2:-2])
		_h_vRebarTieTemp.append(rightMostB[::-1])
		h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
		_h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
		return h_vRebarTie, _h_vRebarTie

# Determine what range to look at for applying stirrups condition according to side rebars number
def check_range(vertical_Dict, attribute_Dict):
	bHalf = len(vertical_Dict['bPoints'])/2
	b_mid = vertical_Dict['bPoints'][bHalf]
	if attribute_Dict['spacing'] <= 150:
		if len(attribute_Dict['hRange']) <= 3:
			b_first = 1
		else:
			b_first = 2
	else:
		if len(attribute_Dict['hRange']) <= 3:
			b_first = 0
		else:
			b_first = 1
	if len(vertical_Dict['bPoints'])%2 != 0:
		b_leftRebar = vertical_Dict['bPoints'][:bHalf]
		b_rightRebar = vertical_Dict['bPoints'][bHalf+1:][::-1]
	else:
		b_leftRebar = vertical_Dict['bPoints'][:bHalf]
		b_rightRebar = vertical_Dict['bPoints'][bHalf:][::-1]

	pureb_left = b_leftRebar[b_first:]
	pureb_right = b_rightRebar[b_first:]
	pure = {'pureb_left': pureb_left, 'pureb_right': pureb_right, 'b_mid': b_mid}
	return pure

def tie(vertical_Dict, attribute_Dict, range_to_check):
	aLeft = slc(range_to_check['pureb_left'], attribute_Dict)
	aLeft_flat = list(chain.from_iterable(aLeft[0]))
	aRight = slc(range_to_check['pureb_right'], attribute_Dict)
	aRight_flat = list(chain.from_iterable(aRight[0]))
	end_temp = []
	b_vRebarTie = []
	for i in aLeft[0]:
		if len(i) == aLeft[1]:
			end_temp.append(i)
	if len(aLeft_flat) >= 3:
		end = end_temp[-1][-1]
	else:
		return "numbers are lese than to be in range"
#-------------------------------------------
	try:
		if end == aLeft_flat[-4]:	# End remain 3
			for i in aLeft[0]:
				if len(i) == 3:
					b_vRebarTie.append([i[0], i[-1]])
			b_vRebarTie.append(aLeft_flat[-2:])
			_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
			for i in aRight[0]:
				if len(i) == 3:
					b_vRebarTie.append([i[0], i[-1]])
			b_vRebarTie.append(aRight_flat[-2:])
			_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
			return b_vRebarTie, _b_vRebarTie
#-------------------------------------------
	except: IndexError
	if end == aLeft_flat[-3]:	# End remain 2
		for i in aLeft[0]:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		for i in aRight[0]:
			if len(i) == 3:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
#-------------------------------------------
	elif end == aLeft_flat[-2]:	# End remain 1
		for i in aLeft[0][:-2]:
			if len(i) == aLeft[1]:
				b_vRebarTie.append([i[0], i[-1]])
		if len(vertical_Dict['bPoints']) % 2 == 0:		# Is Even?
			if attribute_Dict['spacing'] <= 150:
				b_vRebarTie.append(aLeft_flat[-4:-2])
			else:
				b_vRebarTie.append(aLeft_flat[-3:-1])
			b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
		else:											# Is Odd?
			b_vRebarTie.append(aLeft[0][-2][::len(aLeft[0][-2])-1])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		for i in aRight[0][:-2]:
			if len(i) == aLeft[1]:
				b_vRebarTie.append([i[0], i[-1]])
		if len(vertical_Dict['bPoints']) % 2 == 0:		# Is Even?
			if attribute_Dict['spacing'] <= 150:
				b_vRebarTie.append(aRight_flat[-4:-2])
			else:
				b_vRebarTie.append(aRight_flat[-3:-1])
		else:											# Is Odd?
			b_vRebarTie.append(aRight[0][-2][::len(aRight[0][-2])-1])
			b_vRebarTie.append([range_to_check['b_mid']])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie
#-------------------------------------------
	else:# end == aLeft_flat[-1]:	# End remain 0
		for i in aLeft[0]:
			if len(i) == aLeft[1]:
				b_vRebarTie.append([i[0], i[-1]])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		for i in aRight[0]:
			if len(i) == aLeft[1]:
				b_vRebarTie.append([i[0], i[-1]])
		if len(vertical_Dict['bPoints']) % 2 != 0:		# Is ODD?
			b_vRebarTie.append([range_to_check['b_mid']])
		_b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
		return b_vRebarTie, _b_vRebarTie

#----------------------------------
# TESTING
column = column(vAttribute)
vRebars = vRebar(vAttribute)
pureRebars = check_range(vRebars, vAttribute)
ties = tie(vRebars, vAttribute, pureRebars)
links = stirrups(vRebars, vAttribute, pureRebars)
#OUT = check_range(vRebars, vAttribute)
#OUT = getTwin(vRebar, 1, 3)
OUT = ties
OUT = links, column, vRebars.values(), asp
#OUT = vRebars.values()
