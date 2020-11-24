# Canonical small object format representation
# Representation for CGoL objects devised by Heinrich Koenig
# Format description at http://conwaylife.com/wiki/SOF
# Further information at http://www.pentadecathlon.com/objects/definitions/definitions.php
# Determine the canonical small object format representation of the current
# pattern using the comparison rules. Special case rules for spaceships are 
# not yet implemented.
#
# By Arie Paap
# Oct. 2014
#
# Changelog
# Nov. 2020: Fixed another bug in sof_compare(). Might actually work for oscillators now.
#            Added periodicity detection with bijoscar()
# Nov. 2020: Py2/Py3 compatibility. Fixed major bug in sof_compare().

import golly as g

# Determine period of current pattern
# Part of apgsearch v1.0 by Adam P. Goucher
def bijoscar(maxsteps):
    initpop = int(g.getpop())
    initrect = g.getrect()
    if (len(initrect) == 0):
        return 0
    inithash = g.hash(initrect)
    
    for i in range(maxsteps):
        g.run(1)
        
        if (int(g.getpop()) == initpop):
            prect = g.getrect()
            phash = g.hash(prect)
            
            if (phash == inithash):
                period = i + 1
                
                if (prect == initrect):
                    return period
                else:
                    return -period

    return -1

# Obtains a canonical representation of the current pattern
# Uses algorithm by Adam P. Goucher
def sof_canonise(duration):
    sof = ''
    
    # We need to compare each phase to find the one used to determine the
    # pattern's standard form. The standard form is selected from a phase
    # with the minimum population
    minpop = int(g.getpop())
    if (duration > 1):
        for t in range(duration):
            minpop = min(minpop, int(g.getpop()))
            g.run(1)
    
    if minpop == 0:
        return '0'

    for t in range(duration):
        if int(g.getpop()) == minpop:
            rect = g.getrect()
            ox = rect[0]
            oy = rect[1]
            x_length = rect[2]
            y_breadth = rect[3]
                
            # Choose the orientation which comes first according to sof comparison rules:
            sof = sof_compare(sof, sof_representation(x_length, y_breadth, ox, oy, 1, 0, 0, 1)) # Identity
            sof = sof_compare(sof, sof_representation(x_length, y_breadth, ox+x_length-1, oy, -1, 0, 0, 1)) # flip_x
            sof = sof_compare(sof, sof_representation(x_length, y_breadth, ox, oy+y_breadth-1, 1, 0, 0, -1)) # flip_y
            sof = sof_compare(sof, sof_representation(x_length, y_breadth, ox+x_length-1, oy+y_breadth-1, -1, 0, 0, -1)) # 180
            sof = sof_compare(sof, sof_representation(y_breadth, x_length, ox, oy, 0, 1, 1, 0)) # swap_xy
            sof = sof_compare(sof, sof_representation(y_breadth, x_length, ox+x_length-1, oy, 0, -1, 1, 0)) # cw 90
            sof = sof_compare(sof, sof_representation(y_breadth, x_length, ox, oy+y_breadth-1, 0, 1, -1, 0)) # ccw 90
            sof = sof_compare(sof, sof_representation(y_breadth, x_length, ox+x_length-1, oy+y_breadth-1, 0, -1, -1, 0)) # swap_xy_flip
        
        if (duration > 1):
            g.run(1)
    
    return sof

# Determine sof for current pattern in specified orientation:
def sof_representation(length, breadth, ox, oy, a, b, c, d):
    sof = ''
    
    for v in range(breadth):
        value = 1
        run = 0
        blank = True
        if (v != 0):
            sof += '-'
        for u in range(length+1):
            x = ox + a*u + b*v
            y = oy + c*u + d*v
            
            if (g.getcell(x,y) == value):
                # Continue the run
                run += 1
            else:
                # Encode the run, unless a run of zeros reaches the boundary
                if (u < length or value == 1):
                    while (run > 78):
                        run -= 78
                        sof += '~0'
                    sof += chr(run + 48) # ord('0') = 48
                run = 1
                value = 1 - value # Toggle value
            if (value==1):
                blank = False
        if (blank == True):
            # Remove unnecessary '0'
            sof = sof[:-2] + '-'
    sof += '.'
    return sof

# Compares two sof patterns according to sof comparison rules.
def sof_compare(a, b):
    if a == b: return a
    if not a: return b
    if not b: return a
    
    alines = str.split(a, '-')
    blines = str.split(b, '-')
    aline = ''
    bline = ''
    
    # Find first line with different cell
    for line in range(0, min(len(alines), len(blines))):
        aline = alines[line]
        bline = blines[line]
        if not (aline == bline):
            break
    
    # Find first difference
    value = 1
    ii = 0
    for ii in range(0, min(len(aline), len(bline))):
        if not (aline[ii] == bline[ii]):
            break
        value = 1 - value
    
    if not aline:
        return b
    if not bline:
        return a
        
    if (value == 1):
        if aline[ii] > bline[ii]:
            return a
        else:
            return b
    else:
        if aline[ii] > bline[ii]:
            return b
        else:
            return a

# p = int(g.getstring('Enter period of pattern', '1'))
p = bijoscar(1000)
if p == -1:
    g.exit('Pattern periodicity not detected within 1000 generations.')
elif p < 0:
    g.exit('Spaceships not yet supported.')

canonPatt = sof_canonise(p)
g.setclipstr(canonPatt)
g.show('SOF representation of pattern is: ' + canonPatt + ' (copied to clipboard).')
