# Loading necessary libraries
import sys
import math
from itertools import chain
from itertools import islice
import matplotlib.pyplot as plt
from shapely import geometry, affinity

#""" Global Variables"""
#b = int(input('please enter column's b length: '))
bLen = 1500
hLen = 600
bRange = list(range(17))
_bRange = bRange[:]
hRange = list(range(4))
_hRange = hRange[:]
sp = 150
bMin = 600

cc = 40
vDia = 25
hDia = 12
vCover = cc+hDia+(vDia/2)
hCover = cc+(hDia/2)
asp = (bLen-(2*vCover))/float(len(bRange)-1)
basePoint = geometry.Point(0, 0, 0)
vAttribute = {'basePoint': basePoint,'clearCover': cc, 'vCover': vCover, 'hCover': hCover, 'bRange': bRange, 
'_bRange': _bRange, 'hRange': hRange, '_hRange': _hRange, 'bLen': bLen, 'hLen': hLen, 'spacing': sp, 'actualSpacing': asp}
#----------------------------------------------------------
""" Basic Geometries """
# Get Coordinates of Points List for plotting preparation (SHAPELY)
def gc_curve(x):
	temp = []
	for i in x:
		temp.append((i.x, i.y))
	return temp
def gc_point(x):
	temp1 = []
	temp2 = []
	for i in x:
		temp1.append(i.x)
		temp2.append(i.y)

	return temp1, temp2

# Concrete Column
def col_conc(attribute_Dict):
	p1 = vAttribute['basePoint']
	p2 = affinity.translate(p1, vAttribute['bLen'], 0, 0)
	p3 = affinity.translate(p2, 0, vAttribute['hLen'], 0)
	p4 = affinity.translate(p3, -vAttribute['bLen'], 0, 0)
	lp = [p1, p2, p3, p4]
	p = geometry.Polygon(gc_curve(lp))
	return p, lp

# Vertical Rebar Distribution
def vRebar(attribute_Dict):#basePoint, vCover, hCover, bPoints, hPoints, b, h):
        _p = affinity.translate(attribute_Dict['basePoint'], attribute_Dict['vCover'], attribute_Dict['vCover'], 0)
        absp = (attribute_Dict['bLen']-(2*attribute_Dict['vCover']))/(len(attribute_Dict['bRange'])-1)
        dabsp = absp
        ahsp = (attribute_Dict['hLen']-(2*attribute_Dict['vCover']))/(len(attribute_Dict['hRange'])-1)
        dahsp = ahsp
        lbp = [_p]
        _lbp = []
        lhp = [_p]
        _lhp = []
        for nb in range(len(attribute_Dict['bRange'])-1):
                lbp.append(affinity.translate(_p, dabsp, 0, 0))
                dabsp += absp
        for _nb in lbp:
                _lbp.append(affinity.translate(_nb, 0, attribute_Dict['hLen']-(2*attribute_Dict['vCover']), 0))
        for nh in range(len(vAttribute['hRange'])-1):
                lhp.append(affinity.translate(_p, 0, dahsp, 0))
                dahsp += ahsp
        for _nh in lhp:
                _lhp.append(affinity.translate(_nh, attribute_Dict['bLen']-(2*attribute_Dict['vCover']), 0, 0))
        vertical = {'bPoints': lbp[1:-1],'_bPoints': _lbp[1:-1], 'hPoints': lhp, '_hPoints': _lhp}
        return vertical

""" Basic Preparation """
def slc(lst, attribute_Dict): #to slice vertical rebar list into a pattern depending on spacing criteria.
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
#----------------------------------
# DRIVING
vertical_rebars = vRebar(vAttribute)
column = col_conc(vAttribute)
p = column[0]
#print(column[1])
print(gc_point(vertical_rebars['bPoints']))

# Plotting
column_plot_curve = p.exterior.xy
for i in vertical_rebars:
        if 'Points' in i:
                v_points = gc_point(vertical_rebars[i])
                plt.plot(v_points[0], v_points[1], 'ro')

plt.plot(column_plot_curve[0], column_plot_curve[1], 'bo-')

plt.xlabel('Column B Dimension '+str(vAttribute['bLen']))
plt.ylabel('Column H Dimension '+str(vAttribute['hLen']))
plt.title('Column')
plt.grid(True)
plt.savefig("test.png", dpi=300)
plt.show()
print(asp)
