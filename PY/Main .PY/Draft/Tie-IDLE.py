# Loading necessary libraries
import sys
import math
from itertools import chain
from itertools import islice
import matplotlib.pyplot as plt
from shapely import geometry, affinity

""" Global Variables"""
bLen = 1500
hLen = 600
b_total_number = 17
h_total_number = 3
bRange = list(range(b_total_number))
_bRange = bRange[:]
hRange = list(range(h_total_number))
_hRange = hRange[:]
sp = 200
bMin = 600
cc = 40
vDia = 25
hDia = 12
vCover = cc+hDia+(vDia/2)
hCover = cc+(hDia/2)
asp = (bLen-(2*vCover))/float(len(bRange)-1)
basePoint = geometry.Point(0, 0, 0)

vAttribute = {
    'basePoint': basePoint, 'clearCover': cc, 'vCover': vCover,
    'hCover': hCover, 'bRange': bRange, '_bRange': _bRange, 'hRange': hRange,
    '_hRange': _hRange, 'bLen': bLen, 'hLen': hLen, 'spacing': sp,
    'actualSpacing': asp}
info = {
    'basicCount': 0, 'basicLength': 0, 'mainCountSingle': 0,
    'mainCountClosed': 0, 'mainCountSingleLength': 0,
    'mainCountClosedLength': 0, 'sideCountSingle': 0, 'sideCountClosed': 0,
    'sideCountSingleLength': 0, 'sideCountClosedLength': 0}
# ----------------------------------------------------------

""" Basic Geometries """
# Get Coordinates of Points List for plotting preparation (SHAPELY)
# depending on point/curve criteria


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


def vRebar(attribute_Dict):  # Generate column's vertical rebars
    _p = affinity.translate(
        attribute_Dict['basePoint'], attribute_Dict['vCover'],
        attribute_Dict['vCover'], 0)
    absp = (
        attribute_Dict['bLen']-(2*attribute_Dict['vCover']))/(
            len(attribute_Dict['bRange'])-1)
    dabsp = absp
    ahsp = (
        attribute_Dict['hLen']-(2*attribute_Dict['vCover']))/(
            len(attribute_Dict['hRange'])-1)
    dahsp = ahsp
    lbp = [_p]
    _lbp = []
    lhp = [_p]
    _lhp = []
    for nb in range(len(attribute_Dict['bRange'])-1):
        lbp.append(affinity.translate(_p, dabsp, 0, 0))
        dabsp += absp
    for _nb in lbp:
        _lbp.append(affinity.translate(_nb, 0, attribute_Dict['hLen']-(
            2*attribute_Dict['vCover']), 0))
    for nh in range(len(vAttribute['hRange'])-1):
        lhp.append(affinity.translate(_p, 0, dahsp, 0))
        dahsp += ahsp
    for _nh in lhp:
        _lhp.append(affinity.translate(_nh, attribute_Dict['bLen']-(
            2*attribute_Dict['vCover']), 0, 0))
    vertical = {
        'bPoints': lbp[1:-1], '_bPoints': _lbp[1:-1], 'hPoints': lhp,
        '_hPoints': _lhp}
    return vertical


""" Basic Preparation """
# Slicing b_Side vertical rebar list into a pattern
# depending on spacing criteria


def slc(lst, attribute_Dict):
    if attribute_Dict['spacing'] <= 150:
        pattRange = 3
        div = [pattRange, 1]
    else:
        pattRange = 2
        div = [pattRange, 2]
    patt = (len(lst)//2)*div
    it = iter(lst)
    sliced = [list(islice(it, 0, i)) for i in patt]
    for i in sliced[::-1]:
        if i == []:
            sliced.remove(i)
    return sliced, pattRange


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


# Getting Stirrup's curves from Pure Points


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
    except:  # for single pure rebar per one half of a side
        list.reverse(twinPoints)
        flattened = []
        flattened.append(list(chain.from_iterable(purePoints)))
        return flattened


""" Main Conditioning Proccess """
# Main Functions


def stirrups(vertical_Dict, attribute_Dict, range_to_check):
    mainTies = tie(vertical_Dict, attribute_Dict, range_to_check)
    sideTies = tieSide(vertical_Dict, attribute_Dict)
    curves_mainTies = getCurve(mainTies)
    if len(vertical_Dict['hPoints']) <= 3:
        return curves_mainTies
    else:
        return curves_mainTies, sideTies


def tieSide(vertical_Dict, attribute_Dict):
    hHalf = len(vertical_Dict['hPoints'])//2
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


# Determine what range to look at for applying stirrups condition
# according to side rebars number


def check_range(vertical_Dict, attribute_Dict):
    bHalf = len(vertical_Dict['bPoints'])//2
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
    try:
        if end == aLeft_flat[-4]:    # End remain 3
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
    except: IndexError
    if end == aLeft_flat[-3]:    # End remain 2
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
    elif end == aLeft_flat[-2]:    # End remain 1
        for i in aLeft[0][:-2]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(vertical_Dict['bPoints']) % 2 == 0:        # Is Even?
            if attribute_Dict['spacing'] <= 150:
                b_vRebarTie.append(aLeft_flat[-4:-2])
            else:
                b_vRebarTie.append(aLeft_flat[-3:-1])
            b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
        else:                                            # Is Odd?
            b_vRebarTie.append(aLeft[0][-2][::len(aLeft[0][-2])-1])
            if attribute_Dict['spacing'] > 150:
                b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
        _b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
        for i in aRight[0][:-2]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(vertical_Dict['bPoints']) % 2 == 0:        # Is Even?
            if attribute_Dict['spacing'] <= 150:
                b_vRebarTie.append(aRight_flat[-4:-2])
            else:
                b_vRebarTie.append(aRight_flat[-3:-1])
        else:                                            # Is Odd?
            b_vRebarTie.append(aRight[0][-2][::len(aRight[0][-2])-1])
            b_vRebarTie.append([range_to_check['b_mid']])
        _b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
        return b_vRebarTie, _b_vRebarTie
    else:# end == aLeft_flat[-1]:    # End remain 0
        for i in aLeft[0]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        _b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
        for i in aRight[0]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(vertical_Dict['bPoints']) % 2 != 0:        # Is ODD?
            b_vRebarTie.append([range_to_check['b_mid']])
        _b_vRebarTie = getTwin(vertical_Dict, range_to_check, b_vRebarTie, 'b')
        return b_vRebarTie, _b_vRebarTie


#----------------------------------
""" DRIVING Complex """
vertical_rebars = vRebar(vAttribute)
column = col_conc(vAttribute)
pureRebars = check_range(vertical_rebars, vAttribute)
ties = tie(vertical_rebars, vAttribute, pureRebars)
links = stirrups(vertical_rebars, vAttribute, pureRebars)

if len(links) == 2:
    main_links = links[0]
    side_links = links[1]
else:
    main_links = links
""" Plotting """
# Inside Links
for main_link in main_links:
    if len(gc_curve(main_link)) == 2:
        m_line = geometry.LineString(gc_curve(main_link))
        plt.plot(gc_point(main_link)[0], gc_point(main_link)[1], 'm')
        info['mainCountSingle'] += 1
        info['mainCountSingleLength'] += int(m_line.length)
    else:
        m_poly = geometry.Polygon(gc_curve(main_link))
        m_curve = m_poly.exterior.xy
        plt.plot(m_curve[0], m_curve[1], 'bo-')
        info['mainCountClosed'] += 1
        info['mainCountClosedLength'] += int(m_poly.length)
if len(links) == 2:
    for side_link in side_links:
        s_poly = geometry.Polygon(gc_curve(side_link))
        s_curve = s_poly.exterior.xy
        plt.plot(s_curve[0], s_curve[1], 'bo-')
        info['sideCountClosed'] += 1
        info['sideCountClosedLength'] += int(s_poly.length)
# Column Concrete Curve
column_curves = column[0]
column_plot_curve = column_curves.exterior.xy
plt.plot(column_plot_curve[0], column_plot_curve[1], 'co-')

# Main Stirrups
basic_vertical_points = vertical_rebars['bPoints']+vertical_rebars['_hPoints']+vertical_rebars['_bPoints'][::-1]+vertical_rebars['hPoints'][::-1]
basic_vertical_poly = geometry.Polygon(gc_curve(basic_vertical_points))
basic_vertical_curve = basic_vertical_poly.exterior.xy
plt.plot(basic_vertical_curve[0], basic_vertical_curve[1], 'ro-.')
info['basicLength'] += int(basic_vertical_poly.length)

# Plotting Interface
plt.xlabel(
    '1 Main Link with length {} \n {} Closed Link, T.Length = {}, {} Single Link, T.Length = {} \n Total Links = {}, Total Length = {}'.format(info['basicLength'], info['mainCountClosed'], info['mainCountClosedLength'], info['mainCountSingle'], info['mainCountSingleLength'], info['mainCountSingle']+info['mainCountClosed']+info['sideCountSingle']+info['sideCountClosed'], info['mainCountSingleLength']+info['mainCountClosedLength']))
plt.ylabel(
    '{} Closed Side Link, T.Length = {} \n {} Single Side Link, T.Length = {}'.format(info['sideCountClosed'], info['sideCountClosedLength'], info['sideCountSingle'], info['sideCountSingleLength']))
plt.title(
    'Column \n {} x {} \n Lengths are in centimeters'.format(str(vAttribute['hLen']), str(vAttribute['bLen'])))
plt.grid(False)
plt.savefig("test.png", dpi=300)
plt.show()
