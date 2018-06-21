from detection_component import DetectionComponent
import math

class EMDATComponent(DetectionComponent):

    #TODO: Remove websocket
    def  __init__(self, tobii_controller, callback_time):
        #TODO: Specify which features should be calculated
        super().__init__(tobii_controller, is_periodic = True, callback_time, liveWebSocket =  None)

    def notify_app_state_controller(self):
        self.merge_features()
        """
        Code to send features to AppStateController
        """

    def run(self):

        self.start = self.tobii_controller.time[0]
        self.end = self.tobii_controller.time[-1]
        self.length = self.end - self.start
        self.calc_validity_gaps()

        self.length_invalid = self.get_length_invalid()

        """ calculate pupil dilation features """
        self.calc_pupil_features()

        """ calculate distance from screen features"""
        self.calc_distance_features()

        """ calculate fixations, angles and path features"""
        self.calc_fix_ang_path_features()

        """ calculate saccades features if available """
        self.calc_saccade_features()

        """ calculate AOIs features """
        self.has_aois = False
        if aois:
            self.set_aois(aois, all_data, fixation_data, event_data, rest_pupil_size, export_pupilinfo)
            self.features['aoisequence'] = self.generate_aoi_sequence(fixation_data, aois)

        self.merge_features()


    def merge_features(self):
        pass

    def calc_pupil_features(self):
        """ Calculates pupil features such as
                mean_pupil_size:            mean of pupil sizes
                stddev_pupil_size:          standard deviation of pupil sizes
                min_pupil_size:             smallest pupil size in this segment
                max_pupil_size:             largest pupil size in this segment
                mean_pupil_velocity:        mean of pupil velocities
                stddev_pupil_velocity:      standard deviation of pupil velocities
                min_pupil_velocity:         smallest pupil velocity in this segment
                max_pupil_velocity:         largest pupil velocity in this segment

            Args:
                all_data: The list of "Datapoint"s which make up this Segment
        """
        # check if pupil sizes are available for all missing points
        #pupil_invalid_data = filter(lambda x: x.pupilsize == -1 and x.gazepointx > 0, all_data)
        #if len(pupil_invalid_data) > 0:
        #    if params.DEBUG:
        #        raise Exception("Pupil size is unavailable for a valid data sample. \
        #                Number of missing points: " + str(len(pupil_invalid_data)))
        #    else:
        #        warn("Pupil size is unavailable for a valid data sample. Number of missing points: " + str(len(pupil_invalid_data)) )
		#get all pupil sizes (valid + invalid)
        #pupilsizes = map(lambda x: x.pupilsize, all_data)
        #get all datapoints where pupil size is available
        valid_pupil_data = filter(lambda x: x.pupilsize > 0, self.tobii_controller.pupilsize)
        valid_pupil_velocity = filter(lambda x: x.pupilvelocity != -1, self.tobii_controller.pupilvelocity)

        #number of valid pupil sizes
        self.features['meanpupilsize']       = -1
        self.features['stddevpupilsize']     = -1
        self.features['maxpupilsize']        = -1
        self.features['minpupilsize']        = -1
        self.features['startpupilsize']      = -1
        self.features['endpupilsize']        = -1
        self.features['meanpupilvelocity']   = -1
        self.features['stddevpupilvelocity'] = -1
        self.features['maxpupilvelocity']    = -1
        self.features['minpupilvelocity']    = -1
        self.numpupilsizes                   = len(valid_pupil_data)
        self.numpupilvelocity                = len(valid_pupil_velocity)

        if self.numpupilsizes > 0: #check if the current segment has pupil data available
            #if params.PUPIL_ADJUSTMENT == "rpscenter":
            #    adjvalidpupilsizes = map(lambda x: x.pupilsize - rest_pupil_size, valid_pupil_data)
            #elif params.PUPIL_ADJUSTMENT == "PCPS":
            #    adjvalidpupilsizes = map(lambda x: (x.pupilsize - rest_pupil_size) / (1.0 * rest_pupil_size), valid_pupil_data)
            #else:
            #    adjvalidpupilsizes = map(lambda x: x.pupilsize, valid_pupil_data)#valid_pupil_data
            #valid_pupil_velocity = map(lambda x: x.pupilvelocity, valid_pupil_velocity)#valid_pupil_data

            #if export_pupilinfo:
            #    self.pupilinfo_for_export = map(lambda x: [x.timestamp, x.pupilsize, rest_pupil_size], valid_pupil_data)
            self.features['meanpupilsize']           = mean(valid_pupil_data)
            self.features['stddevpupilsize']         = stddev(valid_pupil_data)
            self.features['maxpupilsize']            = max(valid_pupil_data)
            self.features['minpupilsize']            = min(valid_pupil_data)
            self.features['startpupilsize']          = valid_pupil_data[0]
            self.features['endpupilsize']            = valid_pupil_data[-1]

            if len(valid_pupil_velocity) > 0:
                self.features['meanpupilvelocity']   = mean(valid_pupil_velocity)
                self.features['stddevpupilvelocity'] = stddev(valid_pupil_velocity)
                self.features['maxpupilvelocity']    = max(valid_pupil_velocity)
                self.features['minpupilvelocity']    = min(valid_pupil_velocity)

    def calc_distance_features(self):
        """ Calculates distance features such as
                mean_distance:            mean of distances from the screen
                stddev_distance:          standard deviation of distances from the screen
                min_distance:             smallest distance from the screen in this segment
                max_distance:             largest distance from the screen in this segment
                start_distance:           distance from the screen in the beginning of this segment
                end_distance:             distance from the screen in the end of this segment

            Args:
                all_data: The list of "Datapoint"s which make up this Segment
        """
        # check if distances are available for all missing points
        #invalid_distance_data = filter(lambda x: x.distance <= 0 and x.gazepointx >= 0, all_data)
        #if len(invalid_distance_data) > 0:
        #    warn("Distance from screen is unavailable for a valid data sample. \
        #                Number of missing points: " + str(len(invalid_distance_data)))

        #get all datapoints where distance is available
        distances_from_screen = filter(lambda x: x.distance > 0, self.tobii_controller.head_distance)

        #number of valid distance datapoints
        self.numdistancedata = len(distances_from_screen)
        if self.numdistancedata > 0: #check if the current segment has pupil data available
            self.features['meandistance']       = mean(distances_from_screen)
            self.features['stddevdistance']     = stddev(distances_from_screen)
            self.features['maxdistance']        = max(distances_from_screen)
            self.features['mindistance']        = min(distances_from_screen)
            self.features['startdistance']      = distances_from_screen[0]
            self.features['enddistance']        = distances_from_screen[-1]
        else:
            self.features['meandistance']       = -1
            self.features['stddevdistance']     = -1
            self.features['maxdistance']        = -1
            self.features['mindistance']        = -1
            self.features['startdistance']      = -1
            self.features['enddistance']        = -1

    def calc_fix_ang_path_features(self):
        """ Calculates fixation, angle and path features such as
                meanfixationduration:     mean duration of fixations in the segment
                stddevfixationduration    standard deviation of duration of fixations in the segment
                sumfixationduration:      sum of durations of fixations in the segment
                fixationrate:             rate of fixation datapoints relative to all datapoints in this segment
                meanpathdistance:         mean of path distances for this segment
                sumpathdistance:          sum of path distances for this segment
                eyemovementvelocity:      average eye movement velocity for this segment
                sumabspathangles:         sum of absolute path angles for this segment
                abspathanglesrate:        ratio of absolute path angles relative to all datapoints in this segment
                stddevabspathangles:      standard deviation of absolute path angles for this segment
                sumrelpathangles:         sum of relative path angles for this segment
                relpathanglesrate:        ratio of relative path angles relative to all datapoints in this segment
                stddevrelpathangles:      standard deviation of relative path angles for this segment
        """
        fixation_data = self.tobii_controller.EndFixations
        self.numfixations = len(fixation_data)
        if self.numfixations > 0:
            self.features['meanfixationduration'] = mean(map(lambda x: float(x[2]), fixation_data))
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x[2]), fixation_data))
            self.features['sumfixationduration'] = sum(map(lambda x: x[2], fixation_data))

            self.features['fixationrate'] = float(self.numfixations) / (self.length - self.length_invalid)
            distances = self.calc_distances(fixation_data)
            abs_angles = self.calc_abs_angles(fixation_data)
            rel_angles = self.calc_rel_angles(fixation_data)
        else:
            self.fixation_start = -1
            self.fixation_end = -1
            self.features['meanfixationduration'] = -1
            self.features['stddevfixationduration'] = -1
            self.features['sumfixationduration'] = -1
            self.features['fixationrate'] = -1

        self.numfixdistances = len(distances)
        self.numabsangles = len(abs_angles)
        self.numrelangles = len(rel_angles)
        if len(distances) > 0:
            self.features['meanpathdistance'] = mean(distances)
            self.features['sumpathdistance'] = sum(distances)
            self.features['stddevpathdistance'] = stddev(distances)
            self.features['eyemovementvelocity'] = self.features['sumpathdistance']/(self.length - self.length_invalid)
            self.features['sumabspathangles'] = sum(abs_angles)
            self.features['abspathanglesrate'] = sum(abs_angles)/(self.length - self.length_invalid)
            self.features['meanabspathangles'] = mean(abs_angles)
            self.features['stddevabspathangles'] = stddev(abs_angles)
            self.features['sumrelpathangles'] = sum(rel_angles)
            self.features['relpathanglesrate'] = sum(rel_angles)/(self.length - self.length_invalid)
            self.features['meanrelpathangles'] = mean(rel_angles)
            self.features['stddevrelpathangles'] = stddev(rel_angles)
        else:
            self.features['meanpathdistance'] = -1
            self.features['sumpathdistance'] = -1
            self.features['stddevpathdistance'] = -1
            self.features['eyemovementvelocity'] = -1
            self.features['sumabspathangles'] = -1
            self.features['abspathanglesrate'] = -1
            self.features['meanabspathangles'] = -1
            self.features['stddevabspathangles'] = -1
            self.features['sumrelpathangles'] = -1
            self.features['relpathanglesrate'] = -1
            self.features['meanrelpathangles'] = -1
            self.features['stddevrelpathangles'] = -1


    def merge_fixation_features(self, segments):
        """ Merge fixation features such as
                meanfixationduration:     mean duration of fixations
                stddevfixationduration    standard deviation of duration of fixations
                sumfixationduration:      sum of durations of fixations
                fixationrate:             rate of fixation datapoints relative to all datapoints
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.numfixations = sumfeat(segments, 'numfixations')
        self.features['numfixations'] = self.numfixations
        self.features['fixationrate'] = float(self.numfixations) / (self.length - self.length_invalid)

        if self.numfixations > 0:
            self.features['meanfixationduration'] = weightedmeanfeat(segments,'numfixations',"features['meanfixationduration']")
            self.features['stddevfixationduration'] = aggregatestddevfeat(segments, 'numfixations', "features['stddevfixationduration']", "features['meanfixationduration']", self.features['meanfixationduration'])
            self.features['sumfixationduration'] = sumfeat(segments, "features['sumfixationduration']")
            self.features['fixationrate'] = float(self.numfixations)/(self.length - self.length_invalid)
        else:
            self.features['meanfixationduration'] = -1
            self.features['stddevfixationduration'] = -1
            self.features['sumfixationduration'] = -1
            self.features['fixationrate'] = -1


    def merge_path_angle_features(self, segments):
        """ Merge path and angle features such as
                meanpathdistance:         mean of path distances
                sumpathdistance:          sum of path distances
                eyemovementvelocity:      average eye movement velocity
                sumabspathangles:         sum of absolute path angles
                abspathanglesrate:        ratio of absolute path angles relative to all datapoints
                stddevabspathangles:      standard deviation of absolute path angles
                sumrelpathangles:         sum of relative path angles
                relpathanglesrate:        ratio of relative path angles relative to all datapoints
                stddevrelpathangles:      standard deviation of relative path angles
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        self.numfixdistances = sumfeat(segments, "numfixdistances")
        self.numabsangles = sumfeat(segments, "numabsangles")
        self.numrelangles = sumfeat(segments, "numrelangles")

        if self.numfixations > 1:
            self.features['meanpathdistance'] = weightedmeanfeat(segments,'numfixdistances',"features['meanpathdistance']")
            self.features['sumpathdistance'] = sumfeat(segments, "features['sumpathdistance']")
            self.features['stddevpathdistance'] = aggregatestddevfeat(segments, 'numfixdistances', "features['stddevpathdistance']", "features['meanpathdistance']", self.features['meanpathdistance'])
            self.features['eyemovementvelocity'] = self.features['sumpathdistance']/(self.length - self.length_invalid)
            self.features['sumabspathangles'] = sumfeat(segments, "features['sumabspathangles']")
            self.features['meanabspathangles'] = weightedmeanfeat(segments,'numabsangles',"features['meanabspathangles']")
            self.features['abspathanglesrate'] = self.features['sumabspathangles']/(self.length - self.length_invalid)
            self.features['stddevabspathangles'] = aggregatestddevfeat(segments, 'numabsangles', "features['stddevabspathangles']", "features['meanabspathangles']", self.features['meanabspathangles'])
            self.features['sumrelpathangles'] = sumfeat(segments, "features['sumrelpathangles']")
            self.features['meanrelpathangles'] = weightedmeanfeat(segments,'numrelangles',"features['meanrelpathangles']")
            self.features['relpathanglesrate'] = self.features['sumrelpathangles']/(self.length - self.length_invalid)
            self.features['stddevrelpathangles'] = aggregatestddevfeat(segments, 'numrelangles', "features['stddevrelpathangles']", "features['meanrelpathangles']", self.features['meanrelpathangles'])
        else:
            self.features['meanpathdistance'] = -1
            self.features['sumpathdistance'] = -1
            self.features['stddevpathdistance'] = -1
            self.features['eyemovementvelocity'] = -1
            self.features['sumabspathangles'] = -1
            self.features['abspathanglesrate'] = -1
            self.features['meanabspathangles']= -1
            self.features['stddevabspathangles']= -1
            self.features['sumrelpathangles'] = -1
            self.features['relpathanglesrate'] = -1
            self.features['meanrelpathangles']= -1
            self.features['stddevrelpathangles'] = -1


    def merge_pupil_features(self, export_pupilinfo, segments):
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
        self.numpupilsizes    = sumfeat(segments,'numpupilsizes')
        self.numpupilvelocity = sumfeat(segments,'numpupilvelocity')

        if self.numpupilsizes > 0: # check if scene has any pupil data
            if export_pupilinfo:
                self.pupilinfo_for_export = mergevalues(segments, 'pupilinfo_for_export')
            self.features['meanpupilsize'] = weightedmeanfeat(segments, 'numpupilsizes', "features['meanpupilsize']")
            self.features['stddevpupilsize'] = aggregatestddevfeat(segments, 'numpupilsizes', "features['stddevpupilsize']", "features['meanpupilsize']", self.features['meanpupilsize']) #stddev(self.adjvalidpupilsizes)
            self.features['maxpupilsize'] = maxfeat(segments, "features['maxpupilsize']")
            self.features['minpupilsize'] = minfeat(segments, "features['minpupilsize']", -1)
            self.features['startpupilsize'] = self.firstseg.features['startpupilsize']
            self.features['endpupilsize'] = self.endseg.features['endpupilsize']
        else:
            self.pupilinfo_for_export = []
            self.features['meanpupilsize'] = -1
            self.features['stddevpupilsize'] = -1
            self.features['maxpupilsize'] = -1
            self.features['minpupilsize'] = -1
            self.features['startpupilsize'] = -1
            self.features['endpupilsize'] = -1

        if self.numpupilvelocity > 0: # check if scene has any pupil velocity data
            self.features['meanpupilvelocity'] = weightedmeanfeat(segments, 'numpupilvelocity', "features['meanpupilvelocity']")
            self.features['stddevpupilvelocity'] = aggregatestddevfeat(segments, 'numpupilvelocity', "features['stddevpupilvelocity']", "features['meanpupilvelocity']", self.features['meanpupilvelocity']) #stddev(self.valid_pupil_velocity)
            self.features['maxpupilvelocity'] = maxfeat(segments, "features['maxpupilvelocity']")
            self.features['minpupilvelocity'] = minfeat(segments, "features['minpupilvelocity']", -1)
        else:
            self.features['meanpupilvelocity'] = -1
            self.features['stddevpupilvelocity'] = -1
            self.features['maxpupilvelocity'] = -1
            self.features['minpupilvelocity'] = -1


    def merge_distance_data(self, segments):
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
        self.numdistancedata = sumfeat(segments,'numdistancedata') #Distance
        if self.numdistancedata > 0: # check if scene has any pupil data
            self.features['meandistance'] = weightedmeanfeat(segments, 'numdistancedata', "features['meandistance']")
            self.features['stddevdistance'] = aggregatestddevfeat(segments, 'numdistancedata', "features['stddevdistance']", "features['meandistance']", self.features['meandistance'])
            self.features['maxdistance'] = maxfeat(segments, "features['maxdistance']")
            self.features['mindistance'] = minfeat(segments, "features['mindistance']", -1)
            self.features['startdistance'] = self.firstseg.features['startdistance']
            self.features['enddistance'] = self.endseg.features['enddistance']
        else:
            self.features['meandistance'] = -1
            self.features['stddevdistance'] = -1
            self.features['maxdistance'] = -1
            self.features['mindistance'] = -1
            self.features['startdistance'] = -1
            self.features['enddistance'] = -1


    def merge_saccade_data(self, saccade_data, segments):
        """ Merge saccade features such as
                numsaccades:              number of saccades in the segment
                sumsaccadedistance:       sum of distances during each saccade
                meansaccadedistance:      mean of distances during each saccade
                stddevsaccadedistance:    standard deviation of distances during each saccade
                longestsaccadedistance:   distance of longest saccade
                sumsaccadeduration:       total time spent on saccades in this segment
                meansaccadeduration:      average saccade duration
                stddevsaccadeduration:    standard deviation of saccade durations
                longestsaccadeduration:   longest duration of saccades in this segment
                meansaccadespeed:         average speed of saccades in this segment
                stddevsaccadespeed:       standard deviation of speed of saccades in this segment
                maxsaccadespeed:          highest saccade speed in this segment
                minsaccadespeed:          lowest saccade speed in this  segment
                fixationsaccadetimeratio: fixation to saccade time ratio for this segment
            Args:
                saccade_data: The list of saccade datapoints for this Scene
                segments: The list of Segments for this Scene with pre-calculated features
        """
        if saccade_data != None:
            self.features['numsaccades'] = sumfeat(segments,'numsaccades')
            self.features['sumsaccadedistance'] = sumfeat(segments, "features['sumsaccadedistance']")
            self.features['meansaccadedistance'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadedistance']")
            self.features['stddevsaccadedistance'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadedistance']", "features['meansaccadedistance']", self.features['meansaccadedistance'])
            self.features['longestsaccadedistance'] = maxfeat(segments, "features['longestsaccadedistance']")
            self.features['sumsaccadeduration'] = sumfeat(segments,"features['sumsaccadeduration']")
            self.features['meansaccadeduration'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadeduration']")
            self.features['stddevsaccadeduration'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadeduration']", "features['meansaccadeduration']", self.features['meansaccadeduration'])
            self.features['longestsaccadeduration'] = maxfeat(segments, "features['longestsaccadeduration']")
            self.features['meansaccadespeed'] = weightedmeanfeat(self.segments,'numsaccades',"features['meansaccadespeed']")
            self.features['stddevsaccadespeed'] = aggregatestddevfeat(segments, 'numsaccades', "features['stddevsaccadespeed']", "features['meansaccadespeed']", self.features['meansaccadespeed'])
            self.features['maxsaccadespeed'] = maxfeat(segments, "features['maxsaccadespeed']")
            self.features['minsaccadespeed'] = minfeat(segments, "features['minsaccadespeed']", -1)
            self.features['fixationsaccadetimeratio'] = sumfeat(segments, "features['fixationsaccadetimeratio']") / float(len(segments))
        else:
            self.features['numsaccades'] = 0
            self.features['sumsaccadedistance'] = -1
            self.features['meansaccadedistance'] = -1
            self.features['stddevsaccadedistance'] = -1
            self.features['longestsaccadedistance'] = -1
            self.features['sumsaccadeduration'] = -1
            self.features['meansaccadeduration'] = -1
            self.features['stddevsaccadeduration'] = -1
            self.features['longestsaccadeduration'] = -1
            self.features['meansaccadespeed'] = -1
            self.features['stddevsaccadespeed'] = -1
            self.features['maxsaccadespeed'] = -1
            self.features['minsaccadespeed'] = -1
            self.features['fixationsaccadetimeratio'] = -1

    def calc_distances(self, fixdata):
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

    def calc_abs_angles(self, fixdata):
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

    def calc_rel_angles(self, fixdata):
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

    def calc_validity_gaps(self):
        """Calculates the largest gap of invalid samples in the "Datapoint"s for this Segment.

        Args:
            all_data: The list of "Datapoint"s which make up this Segement

        Returns:
            An integer indicating the length of largest invalid gap for this Segment in milliseconds
        """
        time = self.tobii_controller.time
        fixations = self.tobii_controller.EndFixations
        validity = self.tobii_controller.validity
        if len(fixations) == 0:
            return time[-1] - time[0]
        self.time_gaps = []
        dindex = 0
        datalen = len(validity)
        while dindex < datalen:
            d = validity[dindex]
            while d is True and (dindex < datalen - 1):
                dindex += 1
                d = validity[dindex]
            if d is not True:
                gap_start = time[dindex]
                while d is not True and (dindex < datalen - 1):
                    dindex += 1
                    d = validity[dindex]
                    self.time_gaps.append((gap_start, time[dindex]))
            dindex += 1

    def get_length_invalid(self):
        """Returns the sum of the length of the invalid gaps > params.MAX_SEG_TIMEGAP

        Args:
            an integer, the length in milliseconds
        """
        length = 0
        for gap in self.time_gaps:
            length += gap[1] - gap[0]
        return length
"""
    def calc_saccade_features(self, saccade_data):
        Calculates saccade features such as
                numsaccades:              number of saccades in the segment
                sumsaccadedistance:       sum of distances during each saccade
                meansaccadedistance:      mean of distances during each saccade
                stddevsaccadedistance:    standard deviation of distances during each saccade
                longestsaccadedistance:   distance of longest saccade
                sumsaccadeduration:       total time spent on saccades in this segment
                meansaccadeduration:      average saccade duration
                stddevsaccadeduration:    standard deviation of saccade durations
                longestsaccadeduration:   longest duration of saccades in this segment
                meansaccadespeed:         average speed of saccades in this segment
                stddevsaccadespeed:       standard deviation of speed of saccades in this segment
                maxsaccadespeed:          highest saccade speed in this segment
                minsaccadespeed:          lowest saccade speed in this  segment
                fixationsaccadetimeratio: fixation to saccade time ratio for this segment
            Args:
                saccade_data: The list of saccade datapoints for this Segment

        if saccade_data != None and len(saccade_data) > 0:
            self.numsaccades = len(saccade_data)
            self.features['numsaccades'] = self.numsaccades
            self.features['sumsaccadedistance'] = sum(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['meansaccadedistance'] = mean(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['stddevsaccadedistance'] = stddev(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['longestsaccadedistance'] = max(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['sumsaccadeduration'] = sum(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['meansaccadeduration'] = mean(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['stddevsaccadeduration'] = stddev(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['longestsaccadeduration'] = max(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['meansaccadespeed'] = mean(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['stddevsaccadespeed'] = stddev(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['maxsaccadespeed'] = max(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['minsaccadespeed'] = min(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['fixationsaccadetimeratio'] = float(self.features['sumfixationduration']) / self.features['sumsaccadeduration']
        else:
            self.numsaccades = 0
            self.features['numsaccades'] = 0
            self.features['sumsaccadedistance'] = -1
            self.features['meansaccadedistance'] = -1
            self.features['stddevsaccadedistance'] = -1
            self.features['longestsaccadedistance'] = -1
            self.features['sumsaccadeduration'] = -1
            self.features['meansaccadeduration'] = -1
            self.features['stddevsaccadeduration'] = -1
            self.features['longestsaccadeduration'] = -1
            self.features['meansaccadespeed'] = -1
            self.features['stddevsaccadespeed'] = -1
            self.features['maxsaccadespeed'] = -1
            self.features['minsaccadespeed'] = -1
            self.features['fixationsaccadetimeratio'] = -1
"""
