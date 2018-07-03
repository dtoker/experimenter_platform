from detection_component import DetectionComponent
from tornado import gen
import math
from utils import *
import geometry
import time
import params
import numpy as np

# TODO figure out length_valid and length_invalid things
class EMDATComponent(DetectionComponent):

    def  __init__(self, tobii_controller, adaptation_loop, callback_time):
        #TODO: Specify which features should be calculated
        DetectionComponent.__init__(self, tobii_controller, adaptation_loop, is_periodic = True, callback_time = callback_time)
        self.pups_idx   = 0
        self.pupv_idx   = 0
        self.dist_idx   = 0
        self.fix_idx    = 0
        self.feature_select = {}

    def notify_app_state_controller(self):
        self.merge_features()
        '''
        self.app_state_controller.send_interval_features(self.select_features(self.emdat_interval_features))
        self.app_state_controller.send_task_features(self.select_features(self.emdat_task_features))
        self.app_state_controller.send_global_features(self.select_features(self.tobii_controller.emdat_global_features))
        '''

    def select_features(self, feature_source):
        features_to_send = {}
        for key, value in self.feature_select:
            if value.AOI == []:
                features_to_send[key] = feature_source[value.feature]
            else:
                features_to_send[key] = feature_source[key][value.feature]
        return features_to_send

    @gen.coroutine
    def run(self):
        start_time = time.time()
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        print("EMDAT!!!!!!!")
        # Could use any other indexing variable
        self.start = self.tobii_controller.time[self.pups_idx]
        self.end = self.tobii_controller.time[-1]
        self.length = self.end - self.start
        self.calc_validity_gaps()
        self.emdat_interval_features = {}
        self.init_emdat_task_features()
        self.length_invalid = self.get_length_invalid()

        """ calculate pupil dilation features """
        if (params.USE_PUPIL_FEATURES):
            self.calc_pupil_features()

        """ calculate distance from screen features"""
        if (params.USE_DISTANCE_FEATURES):
            self.calc_distance_features()

        """ calculate fixations, angles and path features"""
        if (params.USE_FIXATION_PATH_FEATURES):
            self.calc_fix_ang_path_features()

        self.calc_aoi_features()
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
        print("--- %s seconds ---" % (time.time() - start_time))
        #self.adaptation_loop.evaluateRules(aoi, EfixEndTime)

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
		# Path features
        self.emdat_task_features['numfixdistances'] 		= 0
        self.emdat_task_features['numabsangles'] 			= 0
        self.emdat_task_features['numrelangles'] 			= 0
        self.emdat_task_features['meanpathdistance'] 		= -1
        self.emdat_task_features['sumpathdistance'] 		= -1
        self.emdat_task_features['stddevpathdistance'] 		= -1
        self.emdat_task_features['eyemovementvelocity'] 	= -1
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
        self.emdat_task_features['sumfixationduration'] 	= -1
        self.emdat_task_features['fixationrate'] 			= -1

    def merge_features(self, part_features, accumulator_features):
        if (params.USE_PUPIL_FEATURES):
            self.merge_pupil_features(part_features, accumulator_features)
            self.merge_aoi_pupil()
        """ calculate distance from screen features"""
        if (params.USE_DISTANCE_FEATURES):
            self.merge_distance_features(part_features, accumulator_features)
            self.merge_aoi_distance()
        """ calculate fixations, angles and path features"""
        if (params.USE_FIXATION_PATH_FEATURES):
            self.merge_path_angle_features(part_features, accumulator_features)
            self.merge_fixation_features(part_features, accumulator_features)
            self.merge_aoi_fixations()


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
        distances = []
        abs_angles = []
        rel_angles = []
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
            self.emdat_interval_features['numabsangles'] = 0
            self.emdat_interval_features['numrelangles'] = 0

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
            return time[-1] - time[self.pups_idx]
        self.time_gaps = []
        dindex = self.pups_idx
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

    def calc_aoi_features(self):
        #init features
        x_y_coords                      = np.column_stack((np.array(self.tobii_controller.x), np.array(self.tobii_controller.y)))
        pup_size_vals                   = np.array(self.tobii_controller.pupilsize)
        pup_vel_vals                    = np.array(self.tobii_controller.pupilvelocity)
        dist_vals                       = np.array(self.tobii_controller.head_distance)
        fixation_vals                   = numpy.asarray(self.tobii_controller.EndFixations)

        for aoi in self.AOIS:
             self.emdat_interval_features[aoi] = {}
            ## Indices of x-y array where datapoints are inside the specified AOI
            valid_indices              = np.where(_datapoint_inside_aoi(x_y_coords, self.aoi.polyin, self.aoi.polyout))

            if params.USE_PUPIL_FEATURES:
                ## Select valid pupil sizes inside the AOI
                valid_pupil_sizes      = pup_size_vals[valid_indices]
                valid_pupil_sizes      = valid_pupil_sizes[np.where(valid_pupil_sizes > 0)]
                ## Select valid velocities inside the AOI
                valid_pupil_vel        = pup_vel_vals[valid_indices]
                valid_pupil_vel        = valid_pipil_vel[np.where(valid_pupil_vel != -1)]
                self.generate_aoi_pupil_features(aoi, this_aoi_features, valid_pipil_sizes, valid_pupil_vel, rest_pupil_size)

            if params.USE_DISTANCE_FEATURES:
                ## Select valid head distances inside the AOI
                valid_dist_vals        = dist_vals[valid_indices]
                self.generate_aoi_distance_features(aoi, this_aoi_features, valid_dist_vals)

            if (params.USE_FIXATION_PATH_FEATURES):
                valid_fixation_indices = np.where(_fixation_inside_aoi(fixation_vals, aoi))
                valid_fixation_vals    = fixation_vals[valid_fixation_indices]
                fixation_indices       = self.generate_aoi_fixation_features(aoi, this_aoi_features, datapoints, valid_fixation_vals, self.length_invalid
            if  (params.USE_TRANSITION_AOI_FEATURES):
                #self.generate_transition_features(this_aoi_features, fixation_data, fixation_indices)

    def generate_aoi_pupil_features(self, aoi, valid_pupil_data, valid_pupil_velocity, rest_pupil_size): ##datapoints, rest_pupil_size, export_pupilinfo):
        #number of valid pupil sizes

        self.emdat_interval_features[aoi]['meanpupilsize'] = -1
        self.emdat_interval_features[aoi]['stddevpupilsize'] = -1
        self.emdat_interval_features[aoi]['maxpupilsize'] = -1
        self.emdat_interval_features[aoi]['minpupilsize'] = -1
        self.emdat_interval_features[aoi]['startpupilsize'] = -1
        self.emdat_interval_features[aoi]['endpupilsize'] = -1
        self.emdat_interval_features[aoi]['meanpupilvelocity'] = -1
        self.emdat_interval_features[aoi]['stddevpupilvelocity'] = -1
        self.emdat_interval_features[aoi]['maxpupilvelocity'] = -1
        self.emdat_interval_features[aoi]['minpupilvelocity'] = -1
        self.emdat_interval_features[aoi]['numpupilsizes'] = len(valid_pupil_data)
        self.emdat_interval_features[aoi]['numpupilvelocity'] = len(valid_pupil_velocity)

        if self.emdat_interval_features[aoi]['numpupilsizes'] > 0: #check if the current segment has pupil data available

            if params.PUPIL_ADJUSTMENT == "rpscenter":
                valid_pupil_data = valid_pupil_data - rest_pupil_size
            elif params.PUPIL_ADJUSTMENT == "PCPS":
                adjvalidpupilsizes = (valid_pupil_data - rest_pupil_size) / (1.0 * rest_pupil_size)
            else:
                adjvalidpupilsizes = valid_pupil_data

            self.emdat_interval_features[aoi]['meanpupilsize'] = np.mean(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['stddevpupilsize'] = np.std(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['maxpupilsize'] = np.max(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['minpupilsize'] = np.min(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['startpupilsize'] = adjvalidpupilsizes[0]
            self.emdat_interval_features[aoi]['endpupilsize'] = adjvalidpupilsizes[-1]

            if self.emdat_interval_features[aoi]['numpupilvelocity'] > 0:
                self.emdat_interval_features[aoi]['meanpupilvelocity']      = np.mean(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['stddevpupilvelocity']    = np.std(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['maxpupilvelocity']       = np.max(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['minpupilvelocity']       = np.min(valid_pupil_velocity)


    def generate_aoi_distance_features(self, aoi, valid_distance_data):
        #number of valid pupil sizes
        self.emdat_interval_features[aoi]['numdistancedata']        = len(valid_distance_data)
        if self.emdat_interval_features[aoi]['numdistancedata'] > 0:
            self.emdat_interval_features[aoi]['meandistance']       = np.mean(valid_distance_data)
            self.emdat_interval_features[aoi]['stddevdistance']     = np.std(valid_distance_data)
            self.emdat_interval_features[aoi]['maxdistance']        = np.amax(valid_distance_data)
            self.emdat_interval_features[aoi]['mindistance']        = np.amin(valid_distance_data)
            self.emdat_interval_features[aoi]['startdistance']      = valid_distance_data[0]
            self.emdat_interval_features[aoi]['enddistance']        = valid_distance_data[-1]
        else:
            self.emdat_interval_features[aoi]['meandistance']       = -1
            self.emdat_interval_features[aoi]['stddevdistance']     = -1
            self.emdat_interval_features[aoi]['maxdistance']        = -1
            self.emdat_interval_features[aoi]['mindistance']        = -1
            self.emdat_interval_features[aoi]['startdistance']      = -1
            self.emdat_interval_features[aoi]['enddistance']        = -1

    def generate_aoi_fixation_features(self, aoi, fixation_data, sum_discarded):

        self.emdat_interval_features[aoi]['numfixations'] = 0
        self.emdat_interval_features[aoi]['longestfixation'] = -1
        self.emdat_interval_features[aoi]['meanfixationduration'] = -1
        self.emdat_interval_features[aoi]['stddevfixationduration'] = -1
        self.emdat_interval_features[aoi]['timetofirstfixation'] = -1
        self.emdat_interval_features[aoi]['timetolastfixation'] = -1
        self.emdat_interval_features[aoi]['proportionnum'] = 0
        self.emdat_interval_features[aoi]['proportiontime'] = 0
        self.emdat_interval_features[aoi]['fixationrate'] = 0
        self.emdat_interval_features[aoi]['totaltimespent'] = 0

        numfixations                                = len(fixation_data)
        self.emdat_interval_features[aoi]['numfixations']               = numfixations
        self.emdat_interval_features[aoi]['longestfixation']            = -1
        self.emdat_interval_features[aoi]['timetofirstfixation']        = -1
        self.emdat_interval_features[aoi]['timetolastfixation']         = -1
        self.emdat_interval_features[aoi]['proportionnum']              =  0
        #TODO Check that
        fixation_durations                          = fixation_data[:, 4]
        totaltimespent                              = np.sum(fixation_durations)
        self.emdat_interval_features[aoi]['totaltimespent']             = totaltimespent
        #TODO Check that
        self.emdat_interval_features[aoi]['proportiontime']             = float(totaltimespent)/(self.length - self.length_invalid)
        if numfixations > 0:
            self.emdat_interval_features[aoi]['longestfixation']        = np.max(fixation_durations)
            self.emdat_interval_features[aoi]['meanfixationduration']   = np.mean(fixation_durations)
            self.emdat_interval_features[aoi]['stddevfixationduration'] = np.stddev(fixation_durations)
            self.emdat_interval_features[aoi]['timetofirstfixation']    = fixation_data[0][3] - self.starttime
            self.emdat_interval_features[aoi]['timetolastfixation']     = fixation_data[-1][3] - self.starttime
            self.emdat_interval_features[aoi]['proportionnum']          = float(numfixations)/len(fixation_data)
            self.emdat_interval_features[aoi]['fixationrate']           = numfixations / float(totaltimespent)

    def generate_transition_features(self, aoi, fixation_data, fixation_indices):
        for aoi in self.AOIS.keys():
            aid = aoi
            self.emdat_interval_features[aoi]['numtransfrom_%s'%(aid)] = 0

        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                for aoi in active_aois:
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransfrom_%s'%(aid)
                    # ADD POLYOUT
                    if _fixation_inside_aoi((fixation_data[i-1][0], fixation_data[i-1][1]), polyin):
                        self.emdat_interval_features[aoi][key] += 1
                        sumtransfrom += 1
        for aoi in AOIs.keys():
            if sumtransfrom > 0:
                val = self.emdat_interval_features[aoi]['numtransfrom_%s'%(aoi)]
                self.emdat_interval_features[aoi]['proptransfrom_%s'%(aoi)] = float(val) / sumtransfrom
            else:
                self.emdat_interval_features[aoi]['proptransfrom_%s'%(aoi)] = 0
        self.emdat_interval_features[aoi]['total_trans_from'] = sumtransfrom

    def merge_aoi_fixations(maois, new_AOI_Stat, total_time, total_numfixations, sc_start):
        """ Merge fixation features such as
                meanfixationduration:     mean duration of fixations
                stddevfixationduration    standard deviation of duration of fixations
                sumfixationduration:      sum of durations of fixations
                fixationrate:             rate of fixation datapoints relative to all datapoints
            Args:
                main_AOI_Stat: AOI_Stat object of this Scene (must have been initialised)
                new_AOI_Stat: a new AOI_Stat object
                total_time: duration of the scene
                total_numfixations: number of fixations in the scene
                sc_start: start time (timestamp) of the scene
        """
        maois.features['numfixations'] += new_AOI_Stat.features['numfixations']
        maois.features['longestfixation'] = max(maois.features['longestfixation'],new_AOI_Stat.features['longestfixation'])
        maois.features['totaltimespent'] += new_AOI_Stat.features['totaltimespent']

        maois.features['meanfixationduration'] = maois.features['totaltimespent'] / maois.features['numfixations'] if maois.features['numfixations'] != 0 else -1

        maois.features['proportiontime'] = float(maois.features['totaltimespent'])/total_time
        maois.features['proportionnum'] = float(maois.features['numfixations'])/total_numfixations
        if maois.features['totaltimespent'] > 0:
            maois.features['fixationrate'] = float(maois.features['numfixations']) / maois.features['totaltimespent']
        else:
            maois.features['fixationrate'] = -1

        if new_AOI_Stat.features['timetofirstfixation'] != -1:
            maois.features['timetofirstfixation'] = min(maois.features['timetofirstfixation'], deepcopy(new_AOI_Stat.features['timetofirstfixation']) + new_AOI_Stat.starttime - sc_start)
        if new_AOI_Stat.features['timetolastfixation'] != -1:
            maois.features['timetolastfixation'] = max(maois.features['timetolastfixation'], deepcopy(new_AOI_Stat.features['timetolastfixation']) + new_AOI_Stat.starttime - sc_start)

    def merge_aoi_distance(maois, new_AOI_Stat):
        """ Merge distance features such as
                mean_distance:            mean of distances from the screen
                stddev_distance:          standard deviation of distances from the screen
                min_distance:             smallest distance from the screen
                max_distance:             largest distance from the screen
                start_distance:           distance from the screen in the beginning of this scene
                end_distance:             distance from the screen in the end of this scene
            Args:
                maois: AOI_Stat object of this Scene (must have been initialised)
                new_AOI_Stat: a new AOI_Stat object
        """
        if new_AOI_Stat.numdistancedata + maois.numdistancedata > 1 and new_AOI_Stat.numdistancedata > 0:
            total_distances = maois.numdistancedata + new_AOI_Stat.numdistancedata
            aggregate_mean_distance = maois.features['meandistance'] * float(maois.numdistancedata) / total_distances + new_AOI_Stat.features['meandistance'] * float(new_AOI_Stat.numdistancedata) / total_distances
            maois.features['stddevdistance'] = pow(((maois.numdistancedata - 1) * pow(maois.features['stddevdistance'], 2) + \
                                        (new_AOI_Stat.numdistancedata - 1) * pow(new_AOI_Stat.features['stddevdistance'], 2) + \
                                        maois.numdistancedata * pow(maois.features['meandistance'] - aggregate_mean_distance , 2) \
                                        + new_AOI_Stat.numdistancedata * pow(new_AOI_Stat.features['meandistance'] - aggregate_mean_distance, 2)) / (total_distances - 1), 0.5)
            maois.features['maxdistance'] = max(maois.features['maxdistance'], new_AOI_Stat.features['maxdistance'])
            maois.features['mindistance'] = min(maois.features['mindistance'], new_AOI_Stat.features['mindistance'])
            maois.features['meandistance'] = aggregate_mean_distance
            if maois.starttime > new_AOI_Stat.starttime:
                maois.features['startdistance'] = new_AOI_Stat.features['startdistance']
            if maois.endtime < new_AOI_Stat.endtime:
                maois.features['enddistance'] = new_AOI_Stat.features['enddistance']
            maois.numdistancedata += new_AOI_Stat.numdistancedata


    def merge_aoi_pupil(maois, new_AOI_Stat):
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
                maois: AOI_Stat object of this Scene (must have been initialised)
                new_AOI_Stat: a new AOI_Stat object
        """
        if new_AOI_Stat.numpupilsizes + maois.numpupilsizes > 1 and new_AOI_Stat.numpupilsizes > 0:
            total_numpupilsizes = maois.numpupilsizes + new_AOI_Stat.numpupilsizes
            aggregate_mean_pupil =  maois.features['meanpupilsize'] * float(maois.numpupilsizes) / total_numpupilsizes + new_AOI_Stat.features['meanpupilsize'] * float(new_AOI_Stat.numpupilsizes) / total_numpupilsizes
            maois.features['stddevpupilsize'] = pow(((maois.numpupilsizes - 1) * pow(maois.features['stddevpupilsize'], 2) \
                                                + (new_AOI_Stat.numpupilsizes - 1) * pow(new_AOI_Stat.features['stddevpupilsize'], 2) + \
                                                maois.numpupilsizes *  pow(maois.features['meanpupilsize'] - aggregate_mean_pupil, 2) + \
                                                new_AOI_Stat.numpupilsizes * pow(new_AOI_Stat.features['meanpupilsize'] - aggregate_mean_pupil, 2)) \
                                                / (total_numpupilsizes - 1), 0.5)
            maois.features['maxpupilsize'] = max(maois.features['maxpupilsize'], new_AOI_Stat.features['maxpupilsize'])
            maois.features['minpupilsize'] = min(maois.features['maxpupilsize'], new_AOI_Stat.features['maxpupilsize'])
            maois.features['meanpupilsize'] = aggregate_mean_pupil
            if maois.starttime > new_AOI_Stat.starttime:
                maois.features['startpupilsize'] = new_AOI_Stat.features['startpupilsize']
            if maois.endtime < new_AOI_Stat.endtime:
                maois.features['endpupilsize'] = new_AOI_Stat.features['endpupilsize']

            maois.numpupilsizes += new_AOI_Stat.numpupilsizes

    def merge_aoi_transitions(self):
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        new_AOI_Stat_transition_aois = filter(lambda x: x.startswith('numtransfrom_'), new_AOI_Stat.features.keys())
        if params.DEBUG or params.VERBOSE == "VERBOSE":
            print "Segment's transition_aois", new_AOI_Stat_transition_aois

        maois.total_trans_from += new_AOI_Stat.total_trans_from   #updating the total number of transition from this AOI
        for feat in new_AOI_Stat_transition_aois:
            if feat in maois.features:
                maois.features[feat] += new_AOI_Stat.features[feat]
            else:
                maois.features[feat] = new_AOI_Stat.features[feat]
#               sumtransfrom += maois.features[feat]
        # updating the proportion tansition features based on new transitions to and from this AOI
        maois_transition_aois = filter(lambda x: x.startswith('numtransfrom_'),maois.features.keys()) #all the transition features for this AOI should be aupdated even if they are not active for this segment
        for feat in maois_transition_aois:
            aid = feat[len('numtransfrom_'):]
            if maois.total_trans_from > 0:
                maois.features['proptransfrom_%s'%(aid)] = float(maois.features[feat]) / maois.total_trans_from
            else:
                maois.features['proptransfrom_%s'%(aid)] = 0
        ###endof transition calculation


    def get_length_invalid(self):
        """Returns the sum of the length of the invalid gaps > params.MAX_SEG_TIMEGAP

        Args:
            an integer, the length in milliseconds
        """
        length = 0
        for gap in self.time_gaps:
            length += gap[1] - gap[0]
        return length

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
