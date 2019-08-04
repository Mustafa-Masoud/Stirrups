# Load the Python Standard and DesignScript Libraries (for DYNAMO)
import sys
import math
#import clr
#clr.AddReference('ProtoGeometry')
#from Autodesk.DesignScript.Geometry import *
#import Autodesk
# The inputs to this node will be stored as a list in the IN variables.
#dataEnteringNode = IN

""" Global Variables"""
#b = int(input('please enter column's b length: '))
b = 1500
#h = int(input('please enter column's h length: '))
h = 500
#bp = list(range(int(input("please enter column's b side rebar number: "))))
bp = list(range(12))
_bp = bp[:]
#hp = list(range(int(input("please enter column's h side rebar number: "))))
hp = list(range(4))
_hp = hp
#sp = int(input("please enter v-spacing criteria: "))
sp = 150
hlen = int(input("Please enter h length criteria: "))
#hmin = 600

cc = 40
diav = 25
diah = 12
cv = cc+diah+(diav/2)
ch = cc+(diah/2)
#----------------------------------------------------------

""" DYNAMO-PYTHON Geometry Function """
p = Point.ByCoordinates(0, 0, 0)
def column(basePoint, b, h):
        p1 = basePoint
        p2 = Geometry.Translate(p1, Vector.XAxis(), b)
        p3 = Geometry.Translate(p2, Vector.YAxis(), h)
        p4 = Geometry.Translate(p3, Vector.XAxis(), -b)
        lp = [p1, p2, p3, p4]
        pl = Polygon.ByPoints(lp)
        return pl, lp
#Driver
column = column(p, b, h)
# Vertical Rebar Distribution
def vRebar(basePoint, vCover, hCover, bPoints, hPoints, b, h):
        _p = Geometry.Translate(p, Vector.ByCoordinates(vCover, vCover, 0))
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
#Driver
vRebars = vRebar(p, cv, ch, bp, hp, b, h)


# Place your code below this line

# Assign your output to the OUT variable.
OUT = column, vRebars
