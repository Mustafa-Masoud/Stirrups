# Loading necessary libraries
import sys
import math
from itertools import chain
from itertools import islice
import matplotlib.pyplot as plt
from shapely import geometry, affinity


""" Global Variables"""
b_length = 1500
h_length = 600
b_total_number = 25
h_total_number = 5
b_range = list(range(b_total_number))
_b_range = b_range[:]
h_range = list(range(h_total_number))
_hRange = h_range[:]
req_spacing = 150
b_length_min = 600
clear_cover = 40
vertical_diameter = 25
horizontal_diameter = 12
vertical_cover = clear_cover+horizontal_diameter+(vertical_diameter/2)
horizontal_cover = clear_cover+(horizontal_diameter/2)
actual_spacing = (b_length-(2*vertical_cover))/float(len(b_range)-1)
base_point = geometry.Point(0, 0, 0)

data = {
    'basePoint': base_point, 'clearCover': clear_cover, 'vCover': vertical_cover,
    'hCover': horizontal_cover, 'bRange': b_range, '_bRange': _b_range, 'hRange': h_range,
    '_hRange': _hRange, 'bLen': b_length, 'hLen': h_length, 'rSpacing': req_spacing,
    'actualSpacing': actual_spacing}
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


def col_conc(data_dict):
    p1 = data['basePoint']
    p2 = affinity.translate(p1, data['bLen'], 0, 0)
    p3 = affinity.translate(p2, 0, data['hLen'], 0)
    p4 = affinity.translate(p3, -data['bLen'], 0, 0)
    lp = [p1, p2, p3, p4]
    p = geometry.Polygon(gc_curve(lp))
    return p, lp


# Vertical Rebar Distribution


def v_rebars(data_dict):  # Generate column's vertical rebars
    _p = affinity.translate(
        data_dict['basePoint'], data_dict['vCover'],
        data_dict['vCover'], 0)
    absp = (
        data_dict['bLen']-(2*data_dict['vCover']))/(
            len(data_dict['bRange'])-1)
    dabsp = absp
    ahsp = (
        data_dict['hLen']-(2*data_dict['vCover']))/(
            len(data_dict['hRange'])-1)
    dahsp = ahsp
    lbp = [_p]
    _lbp = []
    lhp = [_p]
    _lhp = []
    for nb in range(len(data_dict['bRange'])-1):
        lbp.append(affinity.translate(_p, dabsp, 0, 0))
        dabsp += absp
    for _nb in lbp:
        _lbp.append(affinity.translate(_nb, 0, data_dict['hLen']-(
            2*data_dict['vCover']), 0))
    for nh in range(len(data['hRange'])-1):
        lhp.append(affinity.translate(_p, 0, dahsp, 0))
        dahsp += ahsp
    for _nh in lhp:
        _lhp.append(affinity.translate(_nh, data_dict['bLen']-(
            2*data_dict['vCover']), 0, 0))
    vertical = {
        'bPoints': lbp[1:-1], '_bPoints': _lbp[1:-1], 'hPoints': lhp,
        '_hPoints': _lhp}
    return vertical


""" Basic Preparation """
# to be called from "main tie"; slicing the primary range rebars
# into a required pattern depending on the required spacing criteria


def slice_patt(lst, data_dict):
    if data_dict['rSpacing'] <= 150:
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


# to be called from "main tie"; getting the same main ties indices rebars
# from the opposite side rebar list


def get_opposite_rebars(v_rebars_dict, primary_range_dict, currentRebars, side):
    if len(primary_range_dict['pureb_left']) == 0:
        temp1 = currentRebars[:]
        oppositRebars = []
        for i in temp1:
            if side == 'b':
                ti = v_rebars_dict['bPoints'].index(i)
                t = v_rebars_dict['_bPoints'][ti]
                oppositRebars.append(t)
        return oppositRebars
    if len(primary_range_dict['pureb_left']) == 1:
        temp1 = currentRebars[:]
        oppositRebars = []
        for i in temp1:
            if side == 'b':
                ti = v_rebars_dict['bPoints'].index(i)
                t = v_rebars_dict['_bPoints'][ti]
                oppositRebars.append(t)
        return oppositRebars
    elif len(primary_range_dict['pureb_left']) >= 2:
        temp1 = list(chain.from_iterable(currentRebars))
        temp2 = []
        n = len(currentRebars[0])
        for l in temp1:
            li = temp1.index(l)
            if side == 'b':
                ti = v_rebars_dict['bPoints'].index(l)
                t = v_rebars_dict['_bPoints'][ti]
                temp2.append(t)
        oppositRebars = [temp2[i:i + n] for i in range(0, len(temp2), n)]
        return oppositRebars


# getting the output from "all tie" merge each tie lists together into
# one flat sequenced list to be ready for making curves


def merge_tie_lists(all_tie_lists):
    filtered_ties = all_tie_lists[0]
    opposite_ties = all_tie_lists[1]
    all_ties = [filtered_ties, opposite_ties]
    try:
        for lst in opposite_ties:
            list.reverse(lst)
        purePoints_transposed = list(map(list, zip(*all_ties)))
        flat_lists = []
        for i in purePoints_transposed:
            flat_lists.append(list(chain.from_iterable(i)))
        return flat_lists
    except:  # for single pure rebar per one half of a side
        list.reverse(opposite_ties)
        flat_lists = []
        flat_lists.append(list(chain.from_iterable(all_ties)))
        return flat_lists


""" Main Conditioning Proccess """
# The head Function, to call both main and side tie functions


def all_tie(v_rebars_dict, data_dict, primary_range_dict):
    m_tie = main_tie(v_rebars_dict, data_dict, primary_range_dict)
    s_tie = side_tie(v_rebars_dict, data_dict)
    m_tie_curves = merge_tie_lists(m_tie)
    if len(v_rebars_dict['hPoints']) <= 3:
        return m_tie_curves
    else:
        return m_tie_curves, s_tie


def side_tie(v_rebars_dict, data_dict):
    hHalf = len(v_rebars_dict['hPoints'])//2
    h_leftRebar = v_rebars_dict['hPoints'][:hHalf]
    h_rightRebar = v_rebars_dict['hPoints'][hHalf+1:][::-1]
    pureh_Rebar = v_rebars_dict['hPoints'][1:-1]

    leftMostB = v_rebars_dict['bPoints'][0], v_rebars_dict['_bPoints'][0]
    rightMostB = v_rebars_dict['bPoints'][-1], v_rebars_dict['_bPoints'][-1]
    h_mid = v_rebars_dict['hPoints'][hHalf]
    h_vRebarTieTemp = []
    _h_vRebarTieTemp = []

    if len(v_rebars_dict['hPoints']) == 4:
        h_vRebarTieTemp.append(v_rebars_dict['hPoints'][1:-1])
        h_vRebarTieTemp.append(leftMostB[::-1])
        _h_vRebarTieTemp.append(v_rebars_dict['_hPoints'][1:-1])
        _h_vRebarTieTemp.append(rightMostB[::-1])
        h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
        _h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
        return h_vRebarTie, _h_vRebarTie
    elif len(v_rebars_dict['hPoints']) == 5:
        h_vRebarTieTemp.append([v_rebars_dict['hPoints'][2]])
        h_vRebarTieTemp.append(leftMostB[::-1])
        _h_vRebarTieTemp.append([v_rebars_dict['_hPoints'][2]])
        _h_vRebarTieTemp.append(rightMostB[::-1])
        h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
        _h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
        return h_vRebarTie, _h_vRebarTie
    elif len(v_rebars_dict['hPoints']) == 6 or len(v_rebars_dict['hPoints']) == 7:
        h_vRebarTieTemp.append(v_rebars_dict['hPoints'][2:-2])
        h_vRebarTieTemp.append(leftMostB[::-1])
        _h_vRebarTieTemp.append(v_rebars_dict['_hPoints'][2:-2])
        _h_vRebarTieTemp.append(rightMostB[::-1])
        h_vRebarTie = [item for sublist in h_vRebarTieTemp for item in sublist]
        _h_vRebarTie = [item for sublist in _h_vRebarTieTemp for item in sublist]
        return h_vRebarTie, _h_vRebarTie


# Determine what range to look at for applying main_tie check
# according to side ties existance


def primary_tie_range(v_rebars_dict, data_dict):
    bHalf = len(v_rebars_dict['bPoints'])//2
    b_mid = v_rebars_dict['bPoints'][bHalf]
    if data_dict['rSpacing'] <= 150:
        if len(data_dict['hRange']) <= 3:
            b_first = 1
        else:
            b_first = 2
    else:
        if len(data_dict['hRange']) <= 3:
            b_first = 0
        else:
            b_first = 1
    if len(v_rebars_dict['bPoints']) % 2 != 0:
        b_leftRebar = v_rebars_dict['bPoints'][:bHalf]
        b_rightRebar = v_rebars_dict['bPoints'][bHalf+1:][::-1]
    else:
        b_leftRebar = v_rebars_dict['bPoints'][:bHalf]
        b_rightRebar = v_rebars_dict['bPoints'][bHalf:][::-1]

    pureb_left = b_leftRebar[b_first:]
    pureb_right = b_rightRebar[b_first:]
    primary_range = {'pureb_left': pureb_left, 'pureb_right': pureb_right, 'b_mid': b_mid}
    return primary_range


# picking the required vertical rebar points
# which will be linked together


def main_tie(v_rebars_dict, data_dict, primary_range_dict):
    aLeft = slice_patt(primary_range_dict['pureb_left'], data_dict)
    aLeft_flat = list(chain.from_iterable(aLeft[0]))
    aRight = slice_patt(primary_range_dict['pureb_right'], data_dict)
    aRight_flat = list(chain.from_iterable(aRight[0]))
    end_temp = []
    b_vRebarTie = []
    for i in aLeft[0]:
        if len(i) == aLeft[1]:
            end_temp.append(i)
    if len(aLeft_flat) >= 3:
        end = end_temp[-1][-1]
    else:
        return "numbers are lese than the required range"
    try:
        if end == aLeft_flat[-4]:       # End remain 3
            for i in aLeft[0]:
                if len(i) == 3:
                    b_vRebarTie.append([i[0], i[-1]])
            b_vRebarTie.append(aLeft_flat[-2:])
            _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
            for i in aRight[0]:
                if len(i) == 3:
                    b_vRebarTie.append([i[0], i[-1]])
            b_vRebarTie.append(aRight_flat[-2:])
            _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
            return b_vRebarTie, _b_vRebarTie
    except: IndexError
    if end == aLeft_flat[-3]:           # End remain 2
        for i in aLeft[0]:
            if len(i) == 3:
                b_vRebarTie.append([i[0], i[-1]])
        b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        for i in aRight[0]:
            if len(i) == 3:
                b_vRebarTie.append([i[0], i[-1]])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        return b_vRebarTie, _b_vRebarTie
    elif end == aLeft_flat[-2]:         # End remain 1
        for i in aLeft[0][:-2]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(v_rebars_dict['bPoints']) % 2 == 0:          # Is Even?
            if data_dict['rSpacing'] <= 150:
                b_vRebarTie.append(aLeft_flat[-4:-2])
            else:
                b_vRebarTie.append(aLeft_flat[-3:-1])
            b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
        else:                                               # Is Odd?
            b_vRebarTie.append(aLeft[0][-2][::len(aLeft[0][-2])-1])
            if data_dict['rSpacing'] > 150:
                b_vRebarTie.append([aLeft_flat[-1], aRight_flat[-1]])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        for i in aRight[0][:-2]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(v_rebars_dict['bPoints']) % 2 == 0:          # Is Even?
            if data_dict['rSpacing'] <= 150:
                b_vRebarTie.append(aRight_flat[-4:-2])
            else:
                b_vRebarTie.append(aRight_flat[-3:-1])
        else:                                               # Is Odd?
            b_vRebarTie.append(aRight[0][-2][::len(aRight[0][-2])-1])
            b_vRebarTie.append([primary_range_dict['b_mid']])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        return b_vRebarTie, _b_vRebarTie
    else:  # end == aLeft_flat[-1]:     # End remain 0
        for i in aLeft[0]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        for i in aRight[0]:
            if len(i) == aLeft[1]:
                b_vRebarTie.append([i[0], i[-1]])
        if len(v_rebars_dict['bPoints']) % 2 != 0:          # Is ODD?
            b_vRebarTie.append([primary_range_dict['b_mid']])
        _b_vRebarTie = get_opposite_rebars(v_rebars_dict, primary_range_dict, b_vRebarTie, 'b')
        return b_vRebarTie, _b_vRebarTie


# ----------------------------------
""" DRIVING CODE """
vertical_rebars = v_rebars(data)
column = col_conc(data)
rebare_range = primary_tie_range(vertical_rebars, data)
#ties = main_tie(vertical_rebars, data, rebare_range)
links = all_tie(vertical_rebars, data, rebare_range)

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
    '(Output Sample) \n Column \n {} x {} \n Lengths are in centimeters'.format(str(data['hLen']), str(data['bLen'])))
plt.grid(False)
plt.savefig("test.png", dpi=300)
plt.show()
