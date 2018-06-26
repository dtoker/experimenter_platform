from detection_component import DetectionComponent
from tornado import gen
import math
from utils import *
import geometry
import time
from ... import params

class EMDATComponent(DetectionComponent):

    #TODO: Remove websocket
    def  __init__(self, tobii_controller, app_state_control, callback_time, liveWebSocket):
        #TODO: Specify which features should be calculated
        DetectionComponent.__init__(self, tobii_controller, app_state_control, is_periodic = True, callback_time = callback_time, liveWebSocket =  liveWebSocket)
        self.pups_idx = 0
        self.pupv_idx = 0
        self.dist_idx = 0
        self.fix_idx = 0

    def notify_app_state_controller(self):
        self.merge_features()
        """
        Code to send features to AppStateController
        """
    @gen.coroutine
    def run(self):
        start_time = time.time()
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        self.start = self.tobii_controller.time[0]
        self.end = self.tobii_controller.time[-1]
        self.length = self.end - self.start
        self.calc_validity_gaps()
        self.emdat_interval_features = {}
        self.init_emdat_task_features()
        self.length_invalid = self.get_length_invalid()

        """ calculate pupil dilation features """
        self.calc_pupil_features()

        """ calculate distance from screen features"""
        self.calc_distance_features()

        """ calculate fixations, angles and path features"""
        self.calc_fix_ang_path_features()

        """ calculate saccades features if available """
        #self.calc_saccade_features()

        """ calculate AOIs features """
        #self.has_aois = False
        #if aois:
        #    self.set_aois(aois, all_data, fixation_data, event_data, rest_pupil_size, export_pupilinfo)
        #    self.features['aoisequence'] = self.generate_aoi_sequence(fixation_data, aois)

        if (params.KEEP_TASK_FEATURES and params.KEEP_GLOBAL_FEATURES):
            self.merge_features(self.emdat_interval_features, self.emdat_task_features)
            self.merge_features(self.emdat_task_features, self.tobii_controller.emdat_global_features)
        elif (params.KEEP_TASK_FEATURES):
            self.merge_features(self.emdat_interval_features, self.emdat_task_features)
        elif (params.KEEP_GLOBAL_FEATURES):
            self.merge_features(self.emdat_interval_features, self.tobii_controller.emdat_global_features)
        print("EMDAT DONE")
        print("EMDAT DONE")
        print("EMDAT DONE")
        print("EMDAT DONE")
        print("EMDAT DONE")
        print("EMDAT DONE")
        print("--- %s seconds ---" % (time.time() - start_time))


    def init_emdat_task_features(self):
        self.emdat_task_features = {}
		# Pupil features
        self.emdat_task_features['numpupilsizes']    							= 0
        self.emdat_task_features['numpupilvelocity']							= 0
        self.emdat_task_features['meanpupilsize'] 			= -1
        self.emdat_task_features['stddevpupilsize'] 			= -1
        self.emdat_task_features['maxpupilsize'] 			= -1
        self.emdat_task_features['minpupilsize'] 			= -1
		#self.emdat_task_features['startpupilsize'] 			= -1
		#self.emdat_task_features['endpupilsize'] 			= -1
        self.emdat_task_features['meanpupilvelocity'] 		= -1
        self.emdat_task_features['stddevpupilvelocity'] 		= -1
        self.emdat_task_features['maxpupilvelocity'] 		= -1
        self.emdat_task_features['minpupilvelocity'] 		= -1
		# Distance features
        self.emdat_task_features['numdistancedata']							= 0
        self.emdat_task_features['meandistance'] 			= -1
        self.emdat_task_features['stddevdistance'] 			= -1
        self.emdat_task_features['maxdistance'] 				= -1
        self.emdat_task_features['mindistance'] 				= -1
		#self.emdat_task_features['startdistance'] 			= -1
		#self.emdat_task_features['enddistance'] 				= -1
		# Saccade features
        """
		self.emdat_task_features['numsaccades'] 				= 0
		self.emdat_task_features['sumsaccadedistance'] 		= -1
		self.emdat_task_features['meansaccadedistance'] 		= -1
		self.emdat_task_features['stddevsaccadedistance'] 	= -1
		self.emdat_task_features['longestsaccadedistance'] 	= -1
		self.emdat_task_features['sumsaccadeduration'] 		= -1
		self.emdat_task_features['meansaccadeduration'] 		= -1
		self.emdat_task_features['stddevsaccadeduration'] 	= -1
		self.emdat_task_features['longestsaccadeduration'] 	= -1
		self.emdat_task_features['meansaccadespeed'] 		= -1
		self.emdat_task_features['stddevsaccadespeed'] 		= -1
		self.emdat_task_features['maxsaccadespeed'] 			= -1
		self.emdat_task_features['minsaccadespeed'] 			= -1
		self.emdat_task_features['fixationsaccadetimeratio'] = -1
        """
		# Path features
        self.emdat_task_features['numfixdistances'] 							= 0
        self.emdat_task_features['numabsangles'] 								= 0
        self.emdat_task_features['numrelangles'] 								= 0
        self.emdat_task_features['meanpathdistance'] 		= -1
        self.emdat_task_features['sumpathdistance'] 			= -1
        self.emdat_task_features['stddevpathdistance'] 		= -1
        self.emdat_task_features['eyemovementvelocity'] 		= -1
        self.emdat_task_features['sumabspathangles'] 		= -1
        self.emdat_task_features['abspathanglesrate'] 		= -1
        self.emdat_task_features['meanabspathangles']		= -1
        self.emdat_task_features['stddevabspathangles']		= -1
        self.emdat_task_features['sumrelpathangles'] 		= -1
        self.emdat_task_features['relpathanglesrate'] 		= -1
        self.emdat_task_features['meanrelpathangles']		= -1
        self.emdat_task_features['stddevrelpathangles'] 		= -1
		# Fixation features
        self.emdat_task_features['numfixations'] 			= 0
        self.emdat_task_features['fixationrate'] 			= -1
        self.emdat_task_features['meanfixationduration'] 	= -1
        self.emdat_task_features['stddevfixationduration'] 	= -1
        self.emdat_task_features['sumfixationduration'] 		= -1
        self.emdat_task_features['fixationrate'] 			= -1

    def merge_features(self, part_features, accumulator_features):
        self.merge_pupil_features(part_features, accumulator_features)
        self.merge_distance_features(part_features, accumulator_features)
        self.merge_path_angle_features(part_features, accumulator_features)
        self.merge_fixation_features(part_features, accumulator_features)
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
        valid_pupil_data = []
        while(self.pups_idx < len(self.tobii_controller.pupilsize)):
            if (self.tobii_controller.pupilsize[self.pups_idx] > 0):
                valid_pupil_data.append(self.tobii_controller.pupilsize[self.pups_idx])
            self.pups_idx += 1
        #valid_pupil_data = filter(lambda pupilsize: pupilsize > 0, self.tobii_controller.pupilsize)
        #valid_pupil_velocity = filter(lambda pupilvelocity: pupilvelocity != -1, self.tobii_controller.pupilvelocity)
        valid_pupil_velocity = []
        while(self.pupv_idx < len(self.tobii_controller.pupilvelocity)):
            if (self.tobii_controller.pupilvelocity[self.pupv_idx] != -1):
                valid_pupil_velocity.append(self.tobii_controller.pupilvelocity[self.pupv_idx])
            self.pupv_idx += 1
        #number of valid pupil sizes
        self.emdat_interval_features['meanpupilsize']       = -1
        self.emdat_interval_features['stddevpupilsize']     = -1
        self.emdat_interval_features['maxpupilsize']        = -1
        self.emdat_interval_features['minpupilsize']        = -1
        self.emdat_interval_features['startpupilsize']      = -1
        self.emdat_interval_features['endpupilsize']        = -1
        self.emdat_interval_features['meanpupilvelocity']   = -1
        self.emdat_interval_features['stddevpupilvelocity'] = -1
        self.emdat_interval_features['maxpupilvelocity']    = -1
        self.emdat_interval_features['minpupilvelocity']    = -1
        self.emdat_interval_features['numpupilsizes']           = len(valid_pupil_data)
        self.emdat_interval_features['numpupilvelocity']        = len(valid_pupil_velocity)

        if self.emdat_interval_features['numpupilsizes'] > 0: #check if the current segment has pupil data available
            #if params.PUPIL_ADJUSTMENT == "rpscenter":
            #    adjvalidpupilsizes = map(lambda x: x.pupilsize - rest_pupil_size, valid_pupil_data)
            #elif params.PUPIL_ADJUSTMENT == "PCPS":
            #    adjvalidpupilsizes = map(lambda x: (x.pupilsize - rest_pupil_size) / (1.0 * rest_pupil_size), valid_pupil_data)
            #else:
            #    adjvalidpupilsizes = map(lambda x: x.pupilsize, valid_pupil_data)#valid_pupil_data
            #valid_pupil_velocity = map(lambda x: x.pupilvelocity, valid_pupil_velocity)#valid_pupil_data

            #if export_pupilinfo:
            #    self.pupilinfo_for_export = map(lambda x: [x.timestamp, x.pupilsize, rest_pupil_size], valid_pupil_data)
            self.emdat_interval_features['meanpupilsize']           = mean(valid_pupil_data)
            self.emdat_interval_features['stddevpupilsize']         = stddev(valid_pupil_data)
            self.emdat_interval_features['maxpupilsize']            = max(valid_pupil_data)
            self.emdat_interval_features['minpupilsize']            = min(valid_pupil_data)
            self.emdat_interval_features['startpupilsize']          = valid_pupil_data[0]
            self.emdat_interval_features['endpupilsize']            = valid_pupil_data[-1]

            if len(valid_pupil_velocity) > 0:
                self.emdat_interval_features['meanpupilvelocity']   = mean(valid_pupil_velocity)
                self.emdat_interval_features['stddevpupilvelocity'] = stddev(valid_pupil_velocity)
                self.emdat_interval_features['maxpupilvelocity']    = max(valid_pupil_velocity)
                self.emdat_interval_features['minpupilvelocity']    = min(valid_pupil_velocity)

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
        distances_from_screen = []
        while (self.dist_idx < len( self.tobii_controller.head_distance)):
            if (self.tobii_controller.head_distance[self.dist_idx] > 0):
                distances_from_screen.append(self.tobii_controller.head_distance[self.dist_idx])
            self.dist_idx += 1
        #number of valid distance datapoints
        numdistancedata = len(distances_from_screen)
        if numdistancedata > 0: #check if the current segment has pupil data available
            self.emdat_interval_features['meandistance']       = mean(distances_from_screen)
            self.emdat_interval_features['stddevdistance']     = stddev(distances_from_screen)
            self.emdat_interval_features['maxdistance']        = max(distances_from_screen)
            self.emdat_interval_features['mindistance']        = min(distances_from_screen)
            self.emdat_interval_features['startdistance']      = distances_from_screen[0]
            self.emdat_interval_features['enddistance']        = distances_from_screen[-1]
            self.emdat_interval_features['numdistancedata']       = numdistancedata
        else:
            self.emdat_interval_features['meandistance']       = -1
            self.emdat_interval_features['stddevdistance']     = -1
            self.emdat_interval_features['maxdistance']        = -1
            self.emdat_interval_features['mindistance']        = -1
            self.emdat_interval_features['startdistance']      = -1
            self.emdat_interval_features['enddistance']        = -1
            self.emdat_interval_features['numdistancedata']    = 0

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
        fixation_data = self.tobii_controller.EndFixations[self.fix_idx:]
        numfixations = len(fixation_data)
        self.fix_idx = len(self.tobii_controller.EndFixations)
        if numfixations > 0:
            self.emdat_interval_features['meanfixationduration'] = mean(map(lambda x: float(x[2]), fixation_data))
            self.emdat_interval_features['stddevfixationduration'] = stddev(map(lambda x: float(x[2]), fixation_data))
            self.emdat_interval_features['sumfixationduration'] = sum(map(lambda x: x[2], fixation_data))

            self.emdat_interval_features['fixationrate'] = float(numfixations) / (self.length - self.length_invalid)
            distances = self.calc_distances(fixation_data)
            abs_angles = self.calc_abs_angles(fixation_data)
            rel_angles = self.calc_rel_angles(fixation_data)
        else:
            #self.fixation_start = -1
            #self.fixation_end = -1
            self.emdat_interval_features['meanfixationduration'] = -1
            self.emdat_interval_features['stddevfixationduration'] = -1
            self.emdat_interval_features['sumfixationduration'] = -1
            self.emdat_interval_features['fixationrate'] = -1
        self.emdat_interval_features['numfixations'] = numfixations

        numfixdistances = len(distances)
        numabsangles = len(abs_angles)
        numrelangles = len(rel_angles)
        if len(distances) > 0:
            self.emdat_interval_features['meanpathdistance'] = mean(distances)
            self.emdat_interval_features['sumpathdistance'] = sum(distances)
            self.emdat_interval_features['stddevpathdistance'] = stddev(distances)
            self.emdat_interval_features['eyemovementvelocity'] = self.emdat_interval_features['sumpathdistance']/(self.length - self.length_invalid)
            self.emdat_interval_features['sumabspathangles'] = sum(abs_angles)
            self.emdat_interval_features['abspathanglesrate'] = sum(abs_angles)/(self.length - self.length_invalid)
            self.emdat_interval_features['meanabspathangles'] = mean(abs_angles)
            self.emdat_interval_features['stddevabspathangles'] = stddev(abs_angles)
            self.emdat_interval_features['sumrelpathangles'] = sum(rel_angles)
            self.emdat_interval_features['relpathanglesrate'] = sum(rel_angles)/(self.length - self.length_invalid)
            self.emdat_interval_features['meanrelpathangles'] = mean(rel_angles)
            self.emdat_interval_features['stddevrelpathangles'] = stddev(rel_angles)
            self.emdat_interval_features['numfixdistances'] = numfixdistances
            self.emdat_interval_features['numabsangles'] = numabsangles
            self.emdat_interval_features['numrelangles'] = numrelangles
        else:
            self.emdat_interval_features['meanpathdistance'] = -1
            self.emdat_interval_features['sumpathdistance'] = -1
            self.emdat_interval_features['stddevpathdistance'] = -1
            self.emdat_interval_features['eyemovementvelocity'] = -1
            self.emdat_interval_features['sumabspathangles'] = -1
            self.emdat_interval_features['abspathanglesrate'] = -1
            self.emdat_interval_features['meanabspathangles'] = -1
            self.emdat_interval_features['stddevabspathangles'] = -1
            self.emdat_interval_features['sumrelpathangles'] = -1
            self.emdat_interval_features['relpathanglesrate'] = -1
            self.emdat_interval_features['meanrelpathangles'] = -1
            self.emdat_interval_features['stddevrelpathangles'] = -1
            self.emdat_interval_features['numfixdistances'] = 0

    def merge_fixation_features(self, part_features, accumulator_features):
        """ Merge fixation features such as
                meanfixationduration:     mean duration of fixations
                stddevfixationduration    standard deviation of duration of fixations
                sumfixationduration:      sum of durations of fixations
                fixationrate:             rate of fixation datapoints relative to all datapoints
            Args:
                segments: The list of Segments for this Scene with pre-calculated features
        """
        numfixations = sumfeat(part_features, accumulator_features, "['numfixations']")
        accumulator_features['fixationrate'] = float(numfixations) / (self.length - self.length_invalid)
        if numfixations > 0:
            meanfixationduration = weightedmeanfeat(part_features, accumulator_features, "['numfixations']","['meanfixationduration']")
            accumulator_features['stddevfixationduration']  = aggregatestddevfeat(part_features, accumulator_features,
                                                      "['numfixations']", "['stddevfixationduration']", "['meanfixationduration']", meanfixationduration)
            accumulator_features['sumfixationduration']     = sumfeat(part_features, accumulator_features, "['sumfixationduration']")
            accumulator_features['fixationrate']            = float(numfixations)/(self.length - self.length_invalid)
            accumulator_features['meanfixationduration']    = meanfixationduration
        else:
            accumulator_features['meanfixationduration']    = -1
            accumulator_features['stddevfixationduration']  = -1
            accumulator_features['sumfixationduration']     = -1
            accumulator_features['fixationrate']            = -1
        accumulator_features['numfixations']                = numfixations

    def merge_path_angle_features(self, part_features, accumulator_features):
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
        numfixdistances                        = sumfeat(part_features, accumulator_features, "['numfixdistances']")
        numabsangles                           = sumfeat(part_features, accumulator_features, "['numabsangles']")
        numrelangles                           = sumfeat(part_features, accumulator_features, "['numrelangles']")

        if numfixdistances > 1:
            meanpathdistance                                = weightedmeanfeat(part_features, accumulator_features,"['numfixdistances']","['meanpathdistance']")
            accumulator_features['sumpathdistance']         = sumfeat(part_features, accumulator_features, "['sumpathdistance']")
            accumulator_features['stddevpathdistance']      = aggregatestddevfeat(part_features, accumulator_features, "['numfixdistances']",
                                                                                "['stddevpathdistance']", "['meanpathdistance']", meanpathdistance)
            accumulator_features['eyemovementvelocity']     = accumulator_features['sumpathdistance']/(self.length - self.length_invalid)
            accumulator_features['sumabspathangles']        = sumfeat(part_features, accumulator_features, "['sumabspathangles']")
            meanabspathangles                               = weightedmeanfeat(part_features, accumulator_features,"['numabsangles']","['meanabspathangles']")
            accumulator_features['abspathanglesrate']       = accumulator_features['sumabspathangles']/(self.length - self.length_invalid)
            accumulator_features['stddevabspathangles']     = aggregatestddevfeat(part_features, accumulator_features, "['numabsangles']",
                                                                "['stddevabspathangles']", "['meanabspathangles']", meanabspathangles)
            accumulator_features['sumrelpathangles']        = sumfeat(part_features, accumulator_features, "['sumrelpathangles']")
            meanrelpathangles                               = weightedmeanfeat(part_features, accumulator_features,"['numrelangles']","['meanrelpathangles']")

            accumulator_features['relpathanglesrate']       = accumulator_features['sumrelpathangles']/(self.length - self.length_invalid)
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
    """
    def merge_saccade_data(self, saccade_data, segments):
        Merge saccade features such as
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
    """
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


    t = eval('part_features'+totalfeat)
    if t > 0:
        sd = eval('part_features'+sdfeat)
        if math.isnan(sd): sd = 0
        meanobj = eval('part_features'+meanfeat)

        num += (t-1) * sd**2 + t * (meanobj-meanscene)**2
        den += t

    t = eval('accumulator_features'+totalfeat)
    if t > 0:
        sd = eval('accumulator_features'+sdfeat)
        if math.isnan(sd): sd = 0
        meanobj = eval('accumulator_features'+meanfeat)

        num += (t-1) * sd**2 + t * (meanobj-meanscene)**2
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

# TODO: Do we need this?
def mergevalues(obj_list, field):
    """a helper method that merges lists of values stored in field

    Args:

        obj_list: a list of objects

        field: name of a field that contains a list of values (string)

    Returns:
        a list formed by merging corresponding lists from collection of subjects
    """
    mergedlist = []
    for obj in obj_list:
        mergedlist.extend(eval('obj.'+ field))
    return mergedlist

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
