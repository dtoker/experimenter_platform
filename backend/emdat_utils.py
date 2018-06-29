

def merge_fixation_features(part_features, accumulator_features, length, length_invalid):
    """ Merge fixation features such as
    meanfixationduration:     mean duration of fixations
    stddevfixationduration    standard deviation of duration of fixations
    sumfixationduration:      sum of durations of fixations
    fixationrate:     rate of fixation datapoints relative to all datapoints
    Args:
    segments: The list of Segments for this Scene with pre-calculated features
    """
    numfixations = sumfeat(part_features, accumulator_features, "['numfixations']")
    accumulator_features['fixationrate'] = float(numfixations) / (length - length_invalid)
    if numfixations > 0:
        meanfixationduration = weightedmeanfeat(part_features, accumulator_features, "['numfixations']","['meanfixationduration']")
        accumulator_features['stddevfixationduration']  = aggregatestddevfeat(part_features, accumulator_features,
                      "['numfixations']", "['stddevfixationduration']", "['meanfixationduration']", meanfixationduration)
        accumulator_features['sumfixationduration']     = sumfeat(part_features, accumulator_features, "['sumfixationduration']")
        accumulator_features['fixationrate']    = float(numfixations)/(length - length_invalid)
        accumulator_features['meanfixationduration']    = meanfixationduration
    else:
        accumulator_features['meanfixationduration']    = -1
        accumulator_features['stddevfixationduration']  = -1
        accumulator_features['sumfixationduration']     = -1
        accumulator_features['fixationrate']    = -1
        accumulator_features['numfixations']    = numfixations

def merge_path_angle_features(part_features, accumulator_features, length, length_invalid):
    """ Merge path and angle features such as
        meanpathdistance:     mean of path distances
        sumpathdistance:      sum of path distances
        eyemovementvelocity:      average eye movement velocity
        sumabspathangles:     sum of absolute path angles
        abspathanglesrate:    ratio of absolute path angles relative to all datapoints
        stddevabspathangles:      standard deviation of absolute path angles
        sumrelpathangles:     sum of relative path angles
        relpathanglesrate:    ratio of relative path angles relative to all datapoints
        stddevrelpathangles:      standard deviation of relative path angles
        Args:
        segments: The list of Segments for this Scene with pre-calculated features
    """
    numfixdistances            = sumfeat(part_features, accumulator_features, "['numfixdistances']")
    numabsangles               = sumfeat(part_features, accumulator_features, "['numabsangles']")
    numrelangles               = sumfeat(part_features, accumulator_features, "['numrelangles']")

    if numfixdistances > 1:
        meanpathdistance                = weightedmeanfeat(part_features, accumulator_features,"['numfixdistances']","['meanpathdistance']")
        accumulator_features['sumpathdistance']     = sumfeat(part_features, accumulator_features, "['sumpathdistance']")
        accumulator_features['stddevpathdistance']      = aggregatestddevfeat(part_features, accumulator_features, "['numfixdistances']",
                                        "['stddevpathdistance']", "['meanpathdistance']", meanpathdistance)
        accumulator_features['eyemovementvelocity']     = accumulator_features['sumpathdistance']/(length - length_invalid)
        accumulator_features['sumabspathangles']    = sumfeat(part_features, accumulator_features, "['sumabspathangles']")
        meanabspathangles                   = weightedmeanfeat(part_features, accumulator_features,"['numabsangles']","['meanabspathangles']")
        accumulator_features['abspathanglesrate']       = accumulator_features['sumabspathangles']/(length - length_invalid)
        accumulator_features['stddevabspathangles']     = aggregatestddevfeat(part_features, accumulator_features, "['numabsangles']",
                                "['stddevabspathangles']", "['meanabspathangles']", meanabspathangles)
        accumulator_features['sumrelpathangles']    = sumfeat(part_features, accumulator_features, "['sumrelpathangles']")
        meanrelpathangles                   = weightedmeanfeat(part_features, accumulator_features,"['numrelangles']","['meanrelpathangles']")

        accumulator_features['relpathanglesrate']       = accumulator_features['sumrelpathangles']/(length - length_invalid)
        accumulator_features['stddevrelpathangles']     = aggregatestddevfeat(part_features, accumulator_features, "['numrelangles']", "['stddevrelpathangles']",
                                "['meanrelpathangles']", meanrelpathangles)

        accumulator_features['meanpathdistance']    = meanpathdistance
        accumulator_features['meanabspathangles']       = meanabspathangles
        accumulator_features['meanrelpathangles']       = meanrelpathangles
        accumulator_features['numfixdistances']     = numfixdistances
        accumulator_features['numabsangles']        = numabsangles
        accumulator_features['numrelangles']        = numrelangles
    else:
        accumulator_features['meanpathdistance']    = -1
        accumulator_features['sumpathdistance']     = -1
        accumulator_features['stddevpathdistance']      = -1
        accumulator_features['eyemovementvelocity']     = -1
        accumulator_features['sumabspathangles']    = -1
        accumulator_features['abspathanglesrate']       = -1
        accumulator_features['meanabspathangles']       = -1
        accumulator_features['stddevabspathangles']     = -1
        accumulator_features['sumrelpathangles']    = -1
        accumulator_features['relpathanglesrate']       = -1
        accumulator_features['meanrelpathangles']       = -1
        accumulator_features['stddevrelpathangles']     = -1

    def merge_pupil_features(self, part_features, accumulator_features):
    """ Merge pupil features asuch as
            mean_pupil_size:            mean of pupil sizes
            stddev_pupil_size:          standard deviation of pupil sizes
            min_pupil_size:             smallest pupil size
            max_pupil_size:             largest pupil size
            mean_pupil_velocity:        mean of pupil velocities
            stddev_pupil_velocity:      standard deviation of pupil velocities
            min_pupil_velocity:         smallest pupil velocity
            max_pupil_velocity:         largest pupil velocity
        Args:
            segments: The list of Segments for this Scene with pre-calculated features
            export_pupilinfo: True to export raw pupil data in EMDAT output (False by default).
    """
    numpupilsizes    = sumfeat(part_features, accumulator_features, "['numpupilsizes']")
    numpupilvelocity = sumfeat(part_features, accumulator_features, "['numpupilvelocity']")

    if numpupilsizes > 0: # check if scene has any pupil data
        #if export_pupilinfo:
        #    self.pupilinfo_for_export = mergevalues(part_features, accumulator_features, 'pupilinfo_for_export')
        mean_pupilsize = weightedmeanfeat(part_features, accumulator_features, "['numpupilsizes']", "['meanpupilsize']")

        accumulator_features['stddevpupilsize']    = aggregatestddevfeat(part_features, accumulator_features,
                                                                            "['numpupilsizes']", "['stddevpupilsize']",
                                                                            "['meanpupilsize']", mean_pupilsize)
        accumulator_features['maxpupilsize']       = maxfeat(part_features, accumulator_features, "['maxpupilsize']")
        accumulator_features['minpupilsize']       = minfeat(part_features, accumulator_features, "['minpupilsize']", -1)
        accumulator_features['meanpupilsize']      = mean_pupilsize
        accumulator_features['numpupilsizes']      = numpupilsizes
        #self.features['startpupilsize'] = self.firstseg.features['startpupilsize']
        #self.features['endpupilsize'] = self.endseg.features['endpupilsize']
    else:
        #self.pupilinfo_for_export = []
        accumulator_features['meanpupilsize']                  = -1
        accumulator_features['stddevpupilsize']                = -1
        accumulator_features['maxpupilsize']                   = -1
        accumulator_features['minpupilsize']                   = -1
        #self.features['startpupilsize'] = -1
        #self.features['endpupilsize'] = -1

    if numpupilvelocity > 0: # check if scene has any pupil velocity data

        mean_velocity                                           = weightedmeanfeat(part_features, accumulator_features, "['numpupilvelocity']", "['meanpupilvelocity']")
        accumulator_features['stddevpupilvelocity']             = aggregatestddevfeat(part_features, accumulator_features, "['numpupilvelocity']", "['stddevpupilvelocity']", "['meanpupilvelocity']", mean_velocity)
        accumulator_features['maxpupilvelocity']                = maxfeat(part_features, accumulator_features, "['maxpupilvelocity']")
        accumulator_features['minpupilvelocity']                = minfeat(part_features, accumulator_features, "['minpupilvelocity']", -1)
        accumulator_features['meanpupilvelocity']               = mean_velocity
        accumulator_features['numpupilvelocity']                = numpupilvelocity
    else:
        accumulator_features['meanpupilvelocity']               = -1
        accumulator_features['stddevpupilvelocity']             = -1
        accumulator_features['maxpupilvelocity']                = -1
        accumulator_features['minpupilvelocity']                = -1

def merge_distance_features(self, part_features, accumulator_features):
    """ Merge distance features such as
            mean_distance:            mean of distances from the screen
            stddev_distance:          standard deviation of distances from the screen
            min_distance:             smallest distance from the screen
            max_distance:             largest distance from the screen
            start_distance:           distance from the screen in the beginning of this scene
            end_distance:             distance from the screen in the end of this scene

        Args:
            segments: The list of Segments for this Scene with pre-calculated features
    """
    numdistancedata = sumfeat(part_features, accumulator_features,"['numdistancedata']") #Distance
    if numdistancedata > 0: # check if scene has any pupil data
        curr_mean_distance                                      = accumulator_features['meandistance']
        mean_distance                                           = weightedmeanfeat(part_features, accumulator_features, "['numdistancedata']", "['meandistance']")
        accumulator_features['stddevdistance']                  = aggregatestddevfeat(part_features, accumulator_features, "['numdistancedata']", "['stddevdistance']", "['meandistance']", curr_mean_distance)
        accumulator_features['maxdistance']                     = maxfeat(part_features, accumulator_features, "['maxdistance']")
        accumulator_features['mindistance']                     = minfeat(part_features, accumulator_features, "['mindistance']", -1)
        accumulator_features['mean_distance']                   = mean_distance
        accumulator_features['numdistancedata']                 = numdistancedata
        #self.features['startdistance'] = self.firstseg.features['startdistance']
        #self.features['enddistance'] = self.endseg.features['enddistance']
    else:
        accumulator_features['meandistance']                    = -1
        accumulator_features['stddevdistance']                  = -1
        accumulator_features['maxdistance']                     = -1
        accumulator_features['mindistance']                     = -1
        #self.features['startdistance'] = -1
        #self.features['enddistance'] = -1


def calc_distances(fixdata):
    """returns the Euclidean distances between a sequence of "Fixation"s

    Args:
        fixdata: a list of "Fixation"s
    """
    distances = []
    lastx = fixdata[0][0]
    lasty = fixdata[0][1]

    for i in xrange(1, len(fixdata)):
        x = fixdata[i][0]
        y = fixdata[i][1]
        dist = math.sqrt((x - lastx)**2 + (y - lasty)**2)
        distances.append(dist)
        lastx = x
        lasty = y

    return distances

def calc_abs_angles(fixdata):
    """returns the absolute angles between a sequence of "Fixation"s that build a scan path.

    Abosolute angle for each saccade is the angle between that saccade and the horizental axis

    Args:
        fixdata: a list of "Fixation"s

    Returns:
        a list of absolute angles for the saccades formed by the given sequence of "Fixation"s in Radiant
    """
    abs_angles = []
    lastx = fixdata[0][0]
    lasty = fixdata[0][1]

    for i in xrange(1,len(fixdata)):
        x = fixdata[i][0]
        y = fixdata[i][1]
        (dist, theta) = geometry.vector_difference((lastx,lasty), (x, y))
        abs_angles.append(abs(theta))
        lastx=x
        lasty=y

    return abs_angles

def calc_rel_angles(fixdata):
    """returns the relative angles between a sequence of "Fixation"s that build a scan path in Radiant

    Relative angle for each saccade is the angle between that saccade and the previous saccade.

    Defined as: angle = acos(v1 dot v2)  such that v1 and v2 are normalized vector2coord

    Args:
        fixdata: a list of "Fixation"s

    Returns:
        a list of relative angles for the saccades formed by the given sequence of "Fixation"s in Radiant
    """
    rel_angles = []
    lastx = fixdata[0][0]
    lasty = fixdata[0][1]

    for i in xrange(1, len(fixdata) - 1):
        x = fixdata[i][0]
        y = fixdata[i][1]
        nextx = fixdata[i + 1][0]
        nexty = fixdata[i + 1][1]
        v1 = (lastx - x, lasty - y)
        v2 = (nextx - x, nexty - y)

        if v1 != (0.0, 0.0) and v2 != (0.0, 0.0):
            v1_dot = math.sqrt(geometry.simpledotproduct(v1, v1))
            v2_dot = math.sqrt(geometry.simpledotproduct(v2, v2))
            normv1 = ((lastx - x) / v1_dot, (lasty - y) / v1_dot)
            normv2 = ((nextx - x) / v2_dot, (nexty - y) / v2_dot)
            dotproduct = geometry.simpledotproduct(normv1, normv2)
            if dotproduct < -1:
                dotproduct = -1.0
            if dotproduct > 1:
                dotproduct = 1.0
            theta = math.acos(dotproduct)
            rel_angles.append(theta)
        else:
            rel_angles.append(0.0)
        lastx = x
        lasty = y

    return rel_angles

def minfeat(part_features, accumulator_features, feat, nonevalue = None):
    """a helper method that calculates the min of a target feature over a list of objects

    Args:

        obj_list: a list of objects

        feat: a string containing the name of the target feature

        nonevalue: value to be ignored when computing the min (typically -1 in EMDAT)

    Returns:
        the min of the target feature over the given list of objects
    """
    return min(eval('part_features'+feat), eval('accumulator_features'+feat))

def maxfeat(part_features, accumulator_features, feat):
    """a helper method that calculates the max of a target feature over a list of objects

    Args:

        obj_list: a list of objects

        feat: a string containing the name of the target feature

    Returns:
        the max of the target feature over the given list of objects
    """
    return max(eval('part_features'+feat), eval('accumulator_features'+feat))

def fixation_inside_aoi(fixation, poly):
    """Determines if a point is inside a given polygon or not
        The algorithm is called "Ray Casting Method".
    Args:
        poly: is a list of (x,y) pairs defining the polgon

    Returns:
        True or False.
    """
    x,y = fixation[0], fixation[1]
    inside = False
    poly = ast.literal_eval(str(poly))

    n = len(poly)
    if n == 0:
        return False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def weightedmeanfeat(part_features, accumulator_features, totalfeat, ratefeat):
    """a helper method that calculates the weighted average of a target feature over a list of Segments

    Args:
        obj_list: a list of Segments which all have a numeric field for which the weighted average is calculated

        totalfeat: a string containing the name of the feature that has the total value of the target feature

        ratefeat: a string containing the name of the feature that has the rate value of the target feature

    Returns:
        the weighted average of the ratefeat over the Segments
    """

    num_valid = float(0)
    num = 0

    t = eval('part_features' + totalfeat)
    num_valid += t * eval('part_features' + ratefeat)
    num += t
    t = eval('accumulator_features'+totalfeat)
    num_valid += t * eval('accumulator_features' + ratefeat)
    num += t
    if num != 0:
        return num_valid / num
    return 0

def aggregatestddevfeat(part_features, accumulator_features, totalfeat, sdfeat, meanfeat, meanscene):
    """a helper method that calculates the aggregated standard deviation of a target feature over a list of Segments

    Args:
        obj_list: a list of Segments which all have a numeric field for which the stdev is calculated

        totalfeat: a string containing the name of the feature that has the total value of the target feature

        ratefeat: a string containing the name of the feature that has the rate value of the target feature

    Returns:
        the weighted average of the ratefeat over the Segments
    """
    num = float(0)
    den = float(0)


    t = eval('part_features' + totalfeat)
    if t > 0:
        sd = eval('part_features' + sdfeat)
        if math.isnan(sd): sd = 0
        meanobj = eval('part_features' + meanfeat)

        num += (t-1) * sd ** 2 + t * (meanobj - meanscene) ** 2
        den += t

    t = eval('accumulator_features'+totalfeat)
    if t > 0:
        sd = eval('accumulator_features'+sdfeat)
        if math.isnan(sd): sd = 0
        meanobj = eval('accumulator_features'+meanfeat)

        num += (t - 1) * sd ** 2 + t * (meanobj-meanscene) ** 2
        den += t
    if den > 1:
        return math.sqrt(float(num)/(den-1))
    return 0

def sumfeat(part_features, accumulator_features, feat):
    """a helper method that calculates the sum of a target feature over a list of objects

    Args:

        obj_list: a list of objects

        feat: a string containing the name of the target feature

    Returns:
        the sum of the target feature over the given list of objects
    """
    sum = 0
    sum += eval('part_features'+feat)
    sum += eval('accumulator_features'+feat)
    return sum
