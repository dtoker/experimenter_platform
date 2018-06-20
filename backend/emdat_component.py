
from detection_component import DetectionComponent


class EMDATComponent(DetectionComponent):

    #TODO: Remove websocket
    def  __init__(self, tobii_controller, is_periodic, callback_time, liveWebSocket):
        #TODO: Specify which features should be calculated
        super().__init__(tobii_controller, is_periodic, callback_time, liveWebSocket)

    def notify_app_state_controller(self):
        self.merge_features()
        """
        Code to send features to AppStateController
        """

    def run(self):
        """ calculate pupil dilation features """
        self.calc_pupil_features()

        """ calculate distance from screen features"""
        self.calc_distance_features(all_data)

        """ calculate fixations, angles and path features"""
        self.calc_fix_ang_path_features(fixation_data)

        """ calculate saccades features if available """
        self.calc_saccade_features(saccade_data)

        """ calculate AOIs features """
        self.has_aois = False
        if aois:
            self.set_aois(aois, all_data, fixation_data, event_data, rest_pupil_size, export_pupilinfo)
            self.features['aoisequence'] = self.generate_aoi_sequence(fixation_data, aois)

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

    def calc_fix_ang_path_features(self, fixation_data):
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
            Args:
                saccade_data: The list of saccade datapoints for this Segment
        """
        if self.numfixations > 0:
            self.fixation_start = fixation_data[0].timestamp
            self.fixation_end = fixation_data[-1].timestamp
            self.features['meanfixationduration'] = mean(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['sumfixationduration'] = sum(map(lambda x: x.fixationduration, fixation_data))
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

    def merge_features():
        pass

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
