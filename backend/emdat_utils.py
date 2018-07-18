import math
import geometry
import ast

def merge_fixation_features(part_features, accumulator_features):
    """ Merge fixation features such as
    meanfixationduration:     mean duration of fixations
    stddevfixationduration    standard deviation of duration of fixations
    sumfixationduration:      sum of durations of fixations
    fixationrate:     rate of fixation datapoints relative to all datapoints
    Args:
    segments: The list of Segments for this Scene with pre-calculated features
    """
    numfixations = sumfeat(part_features, accumulator_features, "['numfixations']")

    accumulator_features['fixationrate']                = float(numfixations) / (accumulator_features['length'] - accumulator_features['length_invalid'])
    if numfixations > 0:
        meanfixationduration                            = weightedmeanfeat(part_features, accumulator_features, "['numfixations']","['meanfixationduration']")
        accumulator_features['stddevfixationduration']  = aggregatestddevfeat(part_features, accumulator_features,
                      "['numfixations']", "['stddevfixationduration']", "['meanfixationduration']", meanfixationduration)
        accumulator_features['sumfixationduration']     = sumfeat(part_features, accumulator_features, "['sumfixationduration']")
        accumulator_features['meanfixationduration']    = meanfixationduration
    else:
        accumulator_features['meanfixationduration']    = -1
        accumulator_features['stddevfixationduration']  = -1
        accumulator_features['sumfixationduration']     = -1
        accumulator_features['fixationrate']            = -1
    accumulator_features['numfixations']            = numfixations

def merge_path_angle_features(part_features, accumulator_features):
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
        meanpathdistance                                = weightedmeanfeat(part_features, accumulator_features,"['numfixdistances']","['meanpathdistance']")
        accumulator_features['sumpathdistance']         = sumfeat(part_features, accumulator_features, "['sumpathdistance']")
        accumulator_features['stddevpathdistance']      = aggregatestddevfeat(part_features, accumulator_features, "['numfixdistances']",
                                        "['stddevpathdistance']", "['meanpathdistance']", meanpathdistance)
        accumulator_features['eyemovementvelocity']     = accumulator_features['sumpathdistance']/(accumulator_features['length'] - accumulator_features['length_invalid'])
        accumulator_features['sumabspathangles']        = sumfeat(part_features, accumulator_features, "['sumabspathangles']")
        meanabspathangles                               = weightedmeanfeat(part_features, accumulator_features,"['numabsangles']","['meanabspathangles']")
        accumulator_features['abspathanglesrate']       = accumulator_features['sumabspathangles']/(accumulator_features['length'] - accumulator_features['length_invalid'])
        accumulator_features['stddevabspathangles']     = aggregatestddevfeat(part_features, accumulator_features, "['numabsangles']",
                                "['stddevabspathangles']", "['meanabspathangles']", meanabspathangles)
        accumulator_features['sumrelpathangles']        = sumfeat(part_features, accumulator_features, "['sumrelpathangles']")
        meanrelpathangles                               = weightedmeanfeat(part_features, accumulator_features,"['numrelangles']","['meanrelpathangles']")

        accumulator_features['relpathanglesrate']       = accumulator_features['sumrelpathangles']/(accumulator_features['length'] - accumulator_features['length_invalid'])
        accumulator_features['stddevrelpathangles']     = aggregatestddevfeat(part_features, accumulator_features, "['numrelangles']", "['stddevrelpathangles']",
                                "['meanrelpathangles']", meanrelpathangles)

        accumulator_features['meanpathdistance']        = meanpathdistance
        accumulator_features['meanabspathangles']       = meanabspathangles
        accumulator_features['meanrelpathangles']       = meanrelpathangles
        accumulator_features['numfixdistances']         = numfixdistances
        accumulator_features['numabsangles']            = numabsangles
        accumulator_features['numrelangles']            = numrelangles
    else:
        accumulator_features['meanpathdistance']        = -1
        accumulator_features['sumpathdistance']         = -1
        accumulator_features['stddevpathdistance']      = -1
        accumulator_features['eyemovementvelocity']     = -1
        accumulator_features['sumabspathangles']        = -1
        accumulator_features['abspathanglesrate']       = -1
        accumulator_features['meanabspathangles']       = -1
        accumulator_features['stddevabspathangles']     = -1
        accumulator_features['sumrelpathangles']        = -1
        accumulator_features['relpathanglesrate']       = -1
        accumulator_features['meanrelpathangles']       = -1
        accumulator_features['stddevrelpathangles']     = -1

def merge_pupil_features(part_features, accumulator_features):
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
    """
    print "MERGED INTERVAL AND TASK WHOLE PUPIL FEATURES"
    print "meanpupilsize %f" % accumulator_features['meanpupilsize']
    print "stddevpupilsize %f" % accumulator_features['stddevpupilsize']
    print "maxpupilsize %f" % accumulator_features['maxpupilsize']
    print "minpupilsize %f" % accumulator_features['minpupilsize']
#    print "startpupilsize %f" % accumulator_features['startpupilsize']
#    print "endpupilsize %f" % accumulator_features['endpupilsize']
    print "meanpupilvelocity %f" % accumulator_features['meanpupilvelocity']
    print "stddevpupilvelocity %f" % accumulator_features['stddevpupilvelocity']
    print "maxpupilvelocity %f" % accumulator_features['maxpupilvelocity']
    print "minpupilvelocity %f" % accumulator_features['minpupilvelocity']
    print "numpupilsizes %f" % accumulator_features['numpupilsizes']
    print "numpupilvelocity %f" % accumulator_features['numpupilvelocity']
    print
    """
def merge_distance_features(part_features, accumulator_features):
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
        mean_distance                                           = weightedmeanfeat(part_features, accumulator_features, "['numdistancedata']", "['meandistance']")
        accumulator_features['stddevdistance']                  = aggregatestddevfeat(part_features, accumulator_features, "['numdistancedata']", "['stddevdistance']", "['meandistance']", mean_distance)
        accumulator_features['maxdistance']                     = maxfeat(part_features, accumulator_features, "['maxdistance']")

        accumulator_features['mindistance']                     = minfeat(part_features, accumulator_features, "['mindistance']", -1)
        accumulator_features['meandistance']                   = mean_distance
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
    """
    print "MERGED INTERVAL AND TASK WHOLE DISTANCE FEATURES"
    print "meandistance %f" % accumulator_features['meandistance']
    print "stddevdistance %f" % accumulator_features['stddevdistance']
    print "maxdistance %f" % accumulator_features['maxdistance']
    print "mindistance %f\n" % accumulator_features['mindistance']
    """
def merge_aoi_fixations(part_features, accumulator_features, length):
    """ Merge fixation features such as
            meanfixationduration:     mean duration of fixations
            stddevfixationduration    standard deviation of duration of fixations
            sumfixationduration:      sum of durations of fixations
            fixationrate:             rate of fixation datapoints relative to all datapoints
        Args:
            main_AOI_Stat: AOI_Stat object of this Scene (must have been initialised)
            part_features: a new AOI_Stat object
            total_numfixations: number of fixations in the scene
            sc_start: start time (timestamp) of the scene
    """
    if accumulator_features['numfixations'] == 0:
        accumulator_features['numfixations']            = part_features['numfixations']
        accumulator_features['meanfixationduration']    = part_features['meanfixationduration']
        accumulator_features['stddevfixationduration']  = part_features['stddevfixationduration']
        accumulator_features['longestfixation']         = part_features['longestfixation']
        accumulator_features['fixationrate']            = part_features['fixationrate']
        accumulator_features['totaltimespent']          = part_features['totaltimespent']
        accumulator_features['proportiontime']          = part_features['proportiontime']
        accumulator_features['proportionnum']           = part_features['proportionnum']
    else:
        if part_features['numfixations'] > 1:
            total_numfixations = accumulator_features['numfixations'] + part_features['numfixations']
            accumulator_features['longestfixation']       = max(accumulator_features['longestfixation'], part_features['longestfixation'])
            accumulator_features['totaltimespent']        += part_features['totaltimespent']
            aggregate_meanfixationduration = accumulator_features['totaltimespent'] / accumulator_features['numfixations']
            accumulator_features['stddevfixationduration']      = pow(((accumulator_features['numfixations'] - 1) * pow(accumulator_features['stddevfixationduration'], 2) + \
                                                                 (part_features['numfixations'] - 1) * pow(part_features['stddevfixationduration'], 2) + \
                                                                 accumulator_features['numfixations'] * pow(accumulator_features['meanfixationduration'] - aggregate_meanfixationduration , 2) + \
                                                                 part_features['numfixations'] * pow(part_features['meanfixationduration'] - aggregate_meanfixationduration, 2)) / (total_numfixations - 1), 0.5)
            accumulator_features['numfixations']          = total_numfixations
            accumulator_features['meanfixationduration']  = aggregate_meanfixationduration
            accumulator_features['proportiontime']        = float(accumulator_features['totaltimespent']) / length
            accumulator_features['proportionnum']         = float(accumulator_features['numfixations']) / total_numfixations

            if accumulator_features['totaltimespent'] > 0:
                accumulator_features['fixationrate']      = float(accumulator_features['numfixations']) / accumulator_features['totaltimespent']
            else:
                accumulator_features['fixationrate']      = -1
    #if part_features['timetofirstfixation'] != -1:
    #    accumulator_features['timetofirstfixation']       = min(accumulator_features['timetofirstfixation'], deepcopy(part_features['timetofirstfixation']) + part_features['starttime'] - sc_start)
    #if part_features['timetolastfixation']  != -1:
    #    accumulator_features['timetolastfixation']        = max(accumulator_features['timetolastfixation'], deepcopy(part_features['timetolastfixation']) + part_features['starttime'] - sc_start)

def merge_aoi_distance(part_features, accumulator_features):
    """ Merge distance features such as
            mean_distance:            mean of distances from the screen
            stddev_distance:          standard deviation of distances from the screen
            min_distance:             smallest distance from the screen
            max_distance:             largest distance from the screen
            start_distance:           distance from the screen in the beginning of this scene
            end_distance:             distance from the screen in the end of this scene
        Args:
            accumulator_features: AOI_Stat object of this Scene (must have been initialised)
            part_features: a new AOI_Stat object
    """
    if accumulator_features['numdistancedata'] == 0:
        accumulator_features['numdistancedata'] = part_features['numdistancedata']
        accumulator_features['meandistance'] = part_features['meandistance']
        accumulator_features['stddevdistance'] = part_features['stddevdistance']
        accumulator_features['maxdistance'] = part_features['maxdistance']
        accumulator_features['mindistance'] = part_features['mindistance']
    else:
        if part_features['numdistancedata'] + accumulator_features['numdistancedata'] > 1 and part_features['numdistancedata'] > 0:
            total_distances = accumulator_features['numdistancedata'] + part_features['numdistancedata']
            aggregate_mean_distance = accumulator_features['meandistance'] * float(accumulator_features['numdistancedata']) / total_distances + part_features['meandistance'] * float(part_features['numdistancedata']) / total_distances
            accumulator_features['stddevdistance'] = pow(((accumulator_features['numdistancedata'] - 1) * pow(accumulator_features['stddevdistance'], 2) + \
                                        (part_features['numdistancedata'] - 1) * pow(part_features['stddevdistance'], 2) + \
                                        accumulator_features['numdistancedata'] * pow(accumulator_features['meandistance'] - aggregate_mean_distance , 2) \
                                        + part_features['numdistancedata'] * pow(part_features['meandistance'] - aggregate_mean_distance, 2)) / (total_distances - 1), 0.5)
            accumulator_features['maxdistance'] = max(accumulator_features['maxdistance'], part_features['maxdistance'])
            accumulator_features['mindistance'] = min(accumulator_features['mindistance'], part_features['mindistance'])
            accumulator_features['meandistance'] = aggregate_mean_distance
            #if accumulator_features.starttime > part_features.starttime:
            #    accumulator_features['startdistance'] = part_features['startdistance']
        #    if accumulator_features.endtime < part_features.endtime:
        #        accumulator_features['enddistance'] = part_features['enddistance']
            accumulator_features['numdistancedata'] += part_features['numdistancedata']
    """
    print "MERGED INTERVAL AND TASK WHOLE DISTANCE FEATURES"
    print "meandistance %f" % accumulator_features['meandistance']
    print "stddevdistance %f" % accumulator_features['stddevdistance']
    print "maxdistance %f" % accumulator_features['maxdistance']
    print "mindistance %f\n" % accumulator_features['mindistance']
    """

def merge_aoi_pupil(part_features, accumulator_features):
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
            accumulator_features: AOI_Stat object of this Scene (must have been initialised)
            part_features: a new AOI_Stat object
        """
    #print('NUMBER OF PUPILS IN ACCUMULATOR: %d' % accumulator_features['numpupilsizes'])
    #print('NUMBER OF PUPILS IN PART: %d' % part_features['numpupilsizes'])

    if accumulator_features['numpupilsizes'] == 0:
        accumulator_features['numpupilsizes'] = part_features['numpupilsizes']
        accumulator_features['meanpupilsize'] = part_features['meanpupilsize']
        accumulator_features['stddevpupilsize'] = part_features['stddevpupilsize']
        accumulator_features['maxpupilsize'] = part_features['maxpupilsize']
        accumulator_features['minpupilsize'] = part_features['minpupilsize']
        accumulator_features['numpupilvelocity'] = part_features['numpupilvelocity']
        accumulator_features['meanpupilvelocity'] = part_features['meanpupilvelocity']
        accumulator_features['stddevpupilvelocity'] = part_features['stddevpupilvelocity']
        accumulator_features['maxpupilvelocity'] = part_features['maxpupilvelocity']
        accumulator_features['minpupilvelocity'] = part_features['minpupilvelocity']

    else:
        if part_features['numpupilsizes'] > 0:
            total_numpupilsizes = accumulator_features['numpupilsizes'] + part_features['numpupilsizes']
            aggregate_mean_pupil =  accumulator_features['meanpupilsize'] * float(accumulator_features['numpupilsizes']) / total_numpupilsizes + part_features['meanpupilsize'] * float(part_features['numpupilsizes']) / total_numpupilsizes
            accumulator_features['stddevpupilsize'] = pow(((accumulator_features['numpupilsizes'] - 1) * pow(accumulator_features['stddevpupilsize'], 2) \
                                                + (part_features['numpupilsizes'] - 1) * pow(part_features['stddevpupilsize'], 2) + \
                                                accumulator_features['numpupilsizes'] *  pow(accumulator_features['meanpupilsize'] - aggregate_mean_pupil, 2) + \
                                                part_features['numpupilsizes'] * pow(part_features['meanpupilsize'] - aggregate_mean_pupil, 2)) \
                                                / (total_numpupilsizes - 1), 0.5)
            accumulator_features['maxpupilsize'] = max(accumulator_features['maxpupilsize'], part_features['maxpupilsize'])
            accumulator_features['minpupilsize'] = min(accumulator_features['minpupilsize'], part_features['minpupilsize'])
            accumulator_features['meanpupilsize'] = aggregate_mean_pupil
            #if accumulator_features['starttime'] > part_features['starttime']:
            #    accumulator_features['startpupilsize'] = part_features['startpupilsize']
            #if accumulator_features['endtime'] < part_features['endtime']:
            #    accumulator_features['endpupilsize'] = part_features['endpupilsize']
            accumulator_features['numpupilsizes'] += part_features['numpupilsizes']

        total_numpupilvelocity = accumulator_features['numpupilvelocity'] + part_features['numpupilvelocity']
        if total_numpupilvelocity > 1 and part_features['numpupilvelocity'] > 0:
            aggregate_mean_velocity =  accumulator_features['meanpupilvelocity'] * float(accumulator_features['numpupilvelocity']) / total_numpupilvelocity + part_features['meanpupilvelocity'] * float(part_features['numpupilvelocity']) / total_numpupilvelocity
            accumulator_features['stddevpupilvelocity'] = pow(((accumulator_features['numpupilvelocity'] - 1) * pow(accumulator_features['stddevpupilvelocity'], 2) \
                                                + (part_features['numpupilvelocity'] - 1) * pow(part_features['stddevpupilvelocity'], 2) + \
                                                accumulator_features['numpupilvelocity'] *  pow(accumulator_features['meanpupilvelocity'] - aggregate_mean_velocity, 2) + \
                                                part_features['numpupilvelocity'] * pow(part_features['meanpupilvelocity'] - aggregate_mean_velocity, 2)) \
                                                / (total_numpupilvelocity - 1), 0.5)
            accumulator_features['maxpupilvelocity'] = max(accumulator_features['maxpupilvelocity'], part_features['maxpupilvelocity'])
            accumulator_features['minpupilvelocity'] = min(accumulator_features['minpupilvelocity'], part_features['minpupilvelocity'])
            accumulator_features['meanpupilvelocity'] = aggregate_mean_velocity
            accumulator_features['numpupilvelocity'] += part_features['numpupilvelocity']
    """
    print "MERGED INTERVAL AND TASK AOI PUPIL FEATURES"
    print "meanpupilsize %f" % accumulator_features['meanpupilsize']
    print "stddevpupilsize %f" % accumulator_features['stddevpupilsize']
    print "maxpupilsize %f" % accumulator_features['maxpupilsize']
    print "minpupilsize %f" % accumulator_features['minpupilsize']
    #print "startpupilsize %f" % accumulator_features['startpupilsize']
    #print "endpupilsize %f" % accumulator_features['endpupilsize']
    print "meanpupilvelocity %f" % accumulator_features['meanpupilvelocity']
    print "stddevpupilvelocity %f" % accumulator_features['stddevpupilvelocity']
    print "maxpupilvelocity %f" % accumulator_features['maxpupilvelocity']
    print "minpupilvelocity %f" % accumulator_features['minpupilvelocity']
    print "numpupilsizes %f" % accumulator_features['numpupilsizes']
    print "numpupilvelocity %f" % accumulator_features['numpupilvelocity']
    print
    """
def merge_aoi_transitions(part_features, accumulator_features):
        #calculating the transitions to and from this AOI and other active AOIs at the moment
    part_features_transition_aois = filter(lambda x: x.startswith('numtransfrom_'), part_features.keys())

    accumulator_features['total_trans_from'] += part_features['total_trans_from']   #updating the total number of transition from this AOI
    #print("Total transitions %d" % accumulator_features['total_trans_from'])

    for feat in part_features_transition_aois:
        if feat in accumulator_features:
            accumulator_features[feat] += part_features[feat]
        else:
            accumulator_features[feat] = part_features[feat]
    # updating the proportion tansition features based on new transitions to and from this AOI
    accumulator_features_transition_aois = filter(lambda x: x.startswith('numtransfrom_'), accumulator_features.keys()) #all the transition features for this AOI should be aupdated even if they are not active for this segment
    for feat in accumulator_features_transition_aois:
        aid = feat[len('numtransfrom_'):]
        if accumulator_features['total_trans_from'] > 0:
            accumulator_features['proptransfrom_%s'%(aid)] = float(accumulator_features[feat]) / accumulator_features['total_trans_from']
        else:
            accumulator_features['proptransfrom_%s'%(aid)] = 0
        #print "Proptransform from %s is %f" % (aid, accumulator_features['proptransfrom_%s'%(aid)])
    #print
    ###endof transition calculation

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
        lastx = x
        lasty = y

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
    part_feat = eval('part_features' + feat)
    acc_feat =  eval('accumulator_features' + feat)
    if (part_feat != nonevalue and acc_feat != nonevalue):
        return min(eval('part_features'+feat), eval('accumulator_features'+feat))
    elif (part_feat != nonevalue):
        return part_feat
    else:
        return nonevalue

def maxfeat(part_features, accumulator_features, feat):
    """a helper method that calculates the max of a target feature over a list of objects

    Args:

        obj_list: a list of objects

        feat: a string containing the name of the target feature

    Returns:
        the max of the target feature over the given list of objects
    """
    return max(eval('part_features'+feat), eval('accumulator_features'+feat))

def datapoint_inside_aoi(coords, poly):
    """Determines if a point is inside a given polygon or not
        The algorithm is called "Ray Casting Method".
    Args:
        poly: is a list of (x,y) pairs defining the polgon

    Returns:
        True or False.
    """
    inside = False
    x, y = coords[0], coords[1]

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
    if (eval('accumulator_features'+feat) != -1):
        sum += eval('accumulator_features'+feat)
    return sum
