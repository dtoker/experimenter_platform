from detection_component import DetectionComponent
from tornado import gen
import math
from utils import *
import geometry
import time
import params
import numpy as np
from emdat_utils import *
import ast

class EMDATComponent(DetectionComponent):

    def  __init__(self, tobii_controller, adaptation_loop, callback_time):
        DetectionComponent.__init__(self, tobii_controller, adaptation_loop, is_periodic = True, callback_time = callback_time)
        self.pups_idx   = 0
        self.pupv_idx   = 0
        self.dist_idx   = 0
        self.fix_idx    = 0
        self.x_y_idx    = 0
        self.id = 1
        self.AOIS = self.application_state_controller.getEmdatAoiMapping()
        print(self.AOIS)
        print("NUMBER OF AOIS %d" % len(self.AOIS))
        self.init_emdat_task_features()
        self.tobii_controller.update_aoi_storage(self.AOIS)
        self.feature_select = self.application_state_controller.getEdmatFeatures()
        self.execfile = open('newfile.txt', 'w')

    def notify_app_state_controller(self):
        self.merge_features()
        '''
        self.app_state_controller.send_interval_features(self.select_features(self.emdat_interval_features))
        self.app_state_controller.send_task_features(self.select_features(self.emdat_task_features))
        self.app_state_controller.send_global_features(self.select_features(self.tobii_controller.emdat_global_features))
        '''

    def select_features(self):
        features_to_send = {}
        for event_name, feature_name in self.feature_select.iteritems():
            #print("adding feature for event: " + event_name)
            #print(self.AOIS)
            if self.AOIS[event_name] == []:
                features_to_send[event_name] = (self.emdat_interval_features[feature_name],
                                                self.emdat_task_features[feature_name],
                                                self.tobii_controller.emdat_global_features[feature_name])
            else:
                print event_name
                print feature_name
                print("interval feature: %f" % self.emdat_interval_features[event_name][feature_name])
                print ("task feature: %f" % self.emdat_task_features[event_name][feature_name])
                print ("global feature: %f" % self.tobii_controller.emdat_global_features[event_name][feature_name])
                print
                features_to_send[event_name] = (self.emdat_interval_features[event_name][feature_name],
                                                self.emdat_task_features[event_name][feature_name],
                                                self.tobii_controller.emdat_global_features[event_name][feature_name])
        return features_to_send

    @gen.coroutine
    def run(self):
        start_time = time.time()
        # Could use any other indexing variable
        self.start = self.tobii_controller.time[self.pups_idx]
        self.end = self.tobii_controller.time[-1]
        #print "TIME IS %f" % (self.end - self.start)
        self.length = self.end - self.start
        self.calc_validity_gaps()
        self.emdat_interval_features = {}
        self.length_invalid = self.get_length_invalid()
        self.emdat_interval_features['length'] = self.length
        self.emdat_interval_features['length_invalid'] = self.length_invalid

        """ calculate pupil dilation features """
        pupil_start_time = time.time()
        #print("\n\n\n============ START calculating features for whole screen ============")
        if (params.USE_PUPIL_FEATURES):
            self.calc_pupil_features()
        #print("Calculating PUPIL features for WHOLE screen: --- %s seconds ---" % (time.time() - pupil_start_time))
        """ calculate distance from screen features"""
        distance_start_time = time.time()
        if (params.USE_DISTANCE_FEATURES):
            self.calc_distance_features()
        #print("Calculating DISTANCE features for WHOLE screen: --- %s seconds ---" % (time.time() - distance_start_time))

        """ calculate fixations, angles and path features"""
        fix_angle_start_time = time.time()
        if (params.USE_FIXATION_PATH_FEATURES):
            self.calc_fix_ang_path_features()
        #print("Calculating FIXATION ANGLE features for WHOLE screen: --- %s seconds ---" % (time.time() - fix_angle_start_time))
        #print("============ FINISH calculating features for whole screen ============\n\n\n\n\n")

        all_aoi_time = time.time()
        #print(all_aoi_time)
        """ calculate AOIs features """
        #print("============ START calculating features for AOIS ============\n\n")

        self.calc_aoi_features()# rest_pupil_size, export_pupilinfo)
        #print("============ FINISH calculating features for AOIS ============\n\n\n\n\n")
        #print(time.time())
        #print(time.time() - all_aoi_time)
        #print("Calculating ALL AOI: --- %s seconds ---" % (time.time() - all_aoi_time))
        all_merging_time = time.time()
        if (params.KEEP_TASK_FEATURES and params.KEEP_GLOBAL_FEATURES):
            self.merge_features(self.emdat_interval_features, self.emdat_task_features)
            self.merge_features(self.emdat_interval_features, self.tobii_controller.emdat_global_features)
        elif (params.KEEP_TASK_FEATURES):
            self.merge_features(self.emdat_interval_features, self.emdat_task_features)
        elif (params.KEEP_GLOBAL_FEATURES):
            self.merge_features(self.emdat_interval_features, self.tobii_controller.emdat_global_features)
        #print("Merging ALL features: --- %s seconds ---" % (time.time() - all_merging_time))
        print("Complete EMDAT execution --- %.12f seconds --- \n\n\n" % (time.time() - start_time))
        self.execfile.write("%.5f\n" % (time.time() - start_time))
        print self.id
        self.id += 1
        self.application_state_controller.updateEmdatTable(self.id, self.select_features())

    def init_emdat_task_features(self):
        self.emdat_task_features = {}
        self.emdat_task_features['length'] = 0
        self.emdat_task_features['length_invalid'] = 0
		# Pupil features
        self.emdat_task_features['numpupilsizes']    	    = 0
        self.emdat_task_features['numpupilvelocity']		= 0
        self.emdat_task_features['meanpupilsize'] 			= -1
        self.emdat_task_features['stddevpupilsize'] 		= -1
        self.emdat_task_features['maxpupilsize'] 			= -1
        self.emdat_task_features['minpupilsize'] 			= -1
		#self.emdat_task_features['startpupilsize'] 			= -1
		#self.emdat_task_features['endpupilsize'] 			= -1
        self.emdat_task_features['meanpupilvelocity'] 		= -1
        self.emdat_task_features['stddevpupilvelocity'] 	= -1
        self.emdat_task_features['maxpupilvelocity'] 		= -1
        self.emdat_task_features['minpupilvelocity'] 		= -1
		# Distance features
        self.emdat_task_features['numdistancedata']			= 0
        self.emdat_task_features['meandistance'] 			= -1
        self.emdat_task_features['stddevdistance'] 			= -1
        self.emdat_task_features['maxdistance'] 			= -1
        self.emdat_task_features['mindistance'] 			= -1
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
        self.emdat_task_features['stddevrelpathangles']     = -1
		# Fixation features
        self.emdat_task_features['numfixations'] 			= 0
        self.emdat_task_features['fixationrate'] 			= -1
        self.emdat_task_features['meanfixationduration'] 	= -1
        self.emdat_task_features['stddevfixationduration'] 	= -1
        self.emdat_task_features['sumfixationduration'] 	= -1
        self.emdat_task_features['fixationrate'] 			= -1
        for aoi in self.AOIS.keys():
            self.emdat_task_features[aoi] = {}
            self.emdat_task_features[aoi]['numfixations'] 			    = 0
            self.emdat_task_features[aoi]['longestfixation']            = -1
            self.emdat_task_features[aoi]['meanfixationduration']       = -1
            self.emdat_task_features[aoi]['stddevfixationduration']     = -1
            self.emdat_task_features[aoi]['timetofirstfixation']        = -1
            self.emdat_task_features[aoi]['timetolastfixation']         = -1
            self.emdat_task_features[aoi]['proportionnum']              = 0
            self.emdat_task_features[aoi]['proportiontime']             = 0
            self.emdat_task_features[aoi]['fixationrate']               = 0
            self.emdat_task_features[aoi]['totaltimespent']             = 0
            self.emdat_task_features[aoi]['meanpupilsize']              = -1
            self.emdat_task_features[aoi]['stddevpupilsize']            = -1
            self.emdat_task_features[aoi]['maxpupilsize']               = -1
            self.emdat_task_features[aoi]['minpupilsize']               = -1
            #self.emdat_task_features[aoi]['startpupilsize']             = -1
            #self.emdat_task_features[aoi]['endpupilsize']               = -1
            self.emdat_task_features[aoi]['meanpupilvelocity']          = -1
            self.emdat_task_features[aoi]['stddevpupilvelocity']        = -1
            self.emdat_task_features[aoi]['maxpupilvelocity']           = -1
            self.emdat_task_features[aoi]['minpupilvelocity']           = -1
            self.emdat_task_features[aoi]['numpupilsizes']              = 0
            self.emdat_task_features[aoi]['numpupilvelocity']           = 0
            self.emdat_task_features[aoi]['numdistancedata']            = 0
            self.emdat_task_features[aoi]['numdistancedata']            = 0
            self.emdat_task_features[aoi]['meandistance']               = -1
            self.emdat_task_features[aoi]['stddevdistance']             = -1
            self.emdat_task_features[aoi]['maxdistance']                = -1
            self.emdat_task_features[aoi]['mindistance']                = -1
            #self.emdat_interval_features[aoi]['startdistance']      = valid_distance_data[0]
            #self.emdat_interval_features[aoi]['enddistance']        = valid_distance_data[-1]
            self.emdat_task_features[aoi]['total_trans_from'] = 0

            for cur_aoi in self.AOIS.keys():
                self.emdat_task_features[aoi]['numtransfrom_%s'%(cur_aoi)] = 0
                self.emdat_task_features[aoi]['proptransfrom_%s'%(cur_aoi)] = -1

    def merge_features(self, part_features, accumulator_features):
        accumulator_features['length'] = sumfeat(part_features, accumulator_features, "['length']")
        accumulator_features['length_invalid'] = sumfeat(part_features, accumulator_features, "['length_invalid']")

        if (params.USE_PUPIL_FEATURES):
            merge_pupil_features(part_features, accumulator_features)
            for aoi in self.AOIS.keys():
                if (len(self.tobii_controller.aoi_ids[aoi]) > 0):
                    #print('merging pupils for %s aoi' % aoi)
                    merge_aoi_pupil(part_features[aoi], accumulator_features[aoi])
        """ calculate distance from screen features"""
        if (params.USE_DISTANCE_FEATURES):
            merge_distance_features(part_features, accumulator_features)
            for aoi in self.AOIS.keys():
                if (len(self.tobii_controller.aoi_ids[aoi]) > 0):
                    #print('merging distances for %s aoi' % aoi)
                    merge_aoi_distance(part_features[aoi], accumulator_features[aoi])

        """ calculate fixations, angles and path features"""
        if (params.USE_FIXATION_PATH_FEATURES):
            merge_path_angle_features(part_features, accumulator_features)
            merge_fixation_features(part_features, accumulator_features)
            for aoi in self.AOIS.keys():
                if (len(self.tobii_controller.aoi_ids[aoi]) > 0):
                    merge_aoi_fixations(part_features[aoi], accumulator_features[aoi], accumulator_features['length'])
                    #print('merging transitions for %s aoi' % aoi)
                    if (params.USE_TRANSITION_AOI_FEATURES):
                        if (len(self.tobii_controller.aoi_ids[aoi]) > 0):
                            merge_aoi_transitions(part_features[aoi], accumulator_features[aoi])

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
        valid_pupil_data = []
        while(self.pups_idx < len(self.tobii_controller.pupilsize)):
            if (self.tobii_controller.pupilsize[self.pups_idx] > 0):
                valid_pupil_data.append(self.tobii_controller.pupilsize[self.pups_idx])
            self.pups_idx += 1
        valid_pupil_velocity = []
        while(self.pupv_idx < len(self.tobii_controller.pupilvelocity)):
            if (self.tobii_controller.pupilvelocity[self.pupv_idx] != -1):
                valid_pupil_velocity.append(self.tobii_controller.pupilvelocity[self.pupv_idx])
            self.pupv_idx += 1
        #number of valid pupil sizes
        self.emdat_interval_features['meanpupilsize']           = -1
        self.emdat_interval_features['stddevpupilsize']         = -1
        self.emdat_interval_features['maxpupilsize']            = -1
        self.emdat_interval_features['minpupilsize']            = -1
        #self.emdat_interval_features['startpupilsize']         = -1
        #self.emdat_interval_features['endpupilsize']           = -1
        self.emdat_interval_features['meanpupilvelocity']       = -1
        self.emdat_interval_features['stddevpupilvelocity']     = -1
        self.emdat_interval_features['maxpupilvelocity']        = -1
        self.emdat_interval_features['minpupilvelocity']        = -1

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
            self.emdat_interval_features['meanpupilsize']           = mean(valid_pupil_data)
            self.emdat_interval_features['stddevpupilsize']         = stddev(valid_pupil_data)
            self.emdat_interval_features['maxpupilsize']            = max(valid_pupil_data)
            self.emdat_interval_features['minpupilsize']            = min(valid_pupil_data)
            #self.emdat_interval_features['startpupilsize']          = valid_pupil_data[0]
            #self.emdat_interval_features['endpupilsize']            = valid_pupil_data[-1]

            if len(valid_pupil_velocity) > 0:
                self.emdat_interval_features['meanpupilvelocity']   = mean(valid_pupil_velocity)
                self.emdat_interval_features['stddevpupilvelocity'] = stddev(valid_pupil_velocity)
                self.emdat_interval_features['maxpupilvelocity']    = max(valid_pupil_velocity)
                self.emdat_interval_features['minpupilvelocity']    = min(valid_pupil_velocity)
        """
        print("\n \t Computed PUPIL features WHOLE screen:")
        print "mean pupilsize %f" % self.emdat_interval_features['meanpupilsize']
        print "std pupilsize %f" %self.emdat_interval_features['stddevpupilsize']
        print "max pupilsize %f" %self.emdat_interval_features['maxpupilsize']
        print "min pupilsize %f" %self.emdat_interval_features['minpupilsize']
        print "num pupilsize %f" %self.emdat_interval_features['numpupilsizes']
        print "num pupilvelocity %f" % self.emdat_interval_features['numpupilvelocity']
        print "mean velocity %f" % self.emdat_interval_features['meanpupilvelocity']
        print "std velocity %f" %self.emdat_interval_features['stddevpupilvelocity']
        print "max velocity %f" %self.emdat_interval_features['maxpupilvelocity']
        print "min velocity %f" %self.emdat_interval_features['minpupilvelocity']
        """
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
            """
        print("\n\n \t Computed DISTANCE features WHOLE screen")
        print "mean distance %f" % self.emdat_interval_features['meandistance']
        print "std distance %f" %self.emdat_interval_features['stddevdistance']
        print "min distance %f" %self.emdat_interval_features['mindistance']
        print "max distance %f" %self.emdat_interval_features['maxdistance']
        print "num distance %f" %self.emdat_interval_features['numdistancedata']
        """
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
        distances = []
        abs_angles = []
        rel_angles = []
        if numfixations > 0:
            self.emdat_interval_features['meanfixationduration'] = mean(map(lambda x: float(x[2]), fixation_data))
            self.emdat_interval_features['stddevfixationduration'] = stddev(map(lambda x: float(x[2]), fixation_data))
            self.emdat_interval_features['sumfixationduration'] = sum(map(lambda x: x[2], fixation_data))

            self.emdat_interval_features['fixationrate'] = float(numfixations) / (self.length - self.length_invalid)
            distances = calc_distances(fixation_data)
            abs_angles = calc_abs_angles(fixation_data)
            rel_angles = calc_rel_angles(fixation_data)
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
            self.emdat_interval_features['eyemovementvelocity'] = self.emdat_interval_features['sumpathdistance'] / (self.length - self.length_invalid)
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
            """
        print("\n\n \t Computed PATH FIXATION features WHOLE screen")
        print "mean fixatiom duration %f" % self.emdat_interval_features['meanfixationduration']
        print "stddevfixationduration %f" % self.emdat_interval_features['stddevfixationduration']
        print "sumfixationduration %f" % self.emdat_interval_features['sumfixationduration']
        print "fixationrate %f" % self.emdat_interval_features['fixationrate']
        print "numfixations %f" % self.emdat_interval_features['numfixations']
        print "meanpathdistance %f" % self.emdat_interval_features['meanpathdistance']
        print "sumpathdistance %f" % self.emdat_interval_features['sumpathdistance']
        print "stddevpathdistance %f" % self.emdat_interval_features['stddevpathdistance']
        print "eyemovementvelocity %f" % self.emdat_interval_features['eyemovementvelocity']
        print "sumabspathangles %f" % self.emdat_interval_features['sumabspathangles']
        print "abspathanglesrate %f" % self.emdat_interval_features['abspathanglesrate']
        print "meanabspathangles %f" % self.emdat_interval_features['meanabspathangles']
        print "stddevabspathangles %f" % self.emdat_interval_features['stddevabspathangles']
        print "sumrelpathangles %f" % self.emdat_interval_features['sumrelpathangles']
        print "relpathanglesrate %f" % self.emdat_interval_features['relpathanglesrate']
        print "meanrelpathangles %f" % self.emdat_interval_features['meanrelpathangles']
        print "stddevrelpathangles %f" % self.emdat_interval_features['stddevrelpathangles']
        print "numfixdistances %f" % self.emdat_interval_features['numfixdistances']
        print "numabsangles %f" %self.emdat_interval_features['numabsangles']
        print "numrelangles %f" %self.emdat_interval_features['numrelangles']
        print
        """
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
        self.time_gaps = []
        #TODO: CHECK THAT
        if len(fixations) == 0:
            return time[-1] - time[self.pups_idx]
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
                if time[dindex] - gap_start > params.MAX_SEG_TIMEGAP:
                    self.time_gaps.append((gap_start, time[dindex]))
            dindex += 1

    def calc_aoi_features(self):
        start_constructing_numpy        = time.time()
        x_y_coords                      = np.column_stack((np.array(self.tobii_controller.x[self.x_y_idx:]), np.array(self.tobii_controller.y[self.x_y_idx:])))
        pup_size_vals                   = np.array(self.tobii_controller.pupilsize[self.x_y_idx:])
        pup_vel_vals                    = np.array(self.tobii_controller.pupilvelocity[self.x_y_idx:])
        dist_vals                       = np.array(self.tobii_controller.head_distance[self.x_y_idx:])
        fixation_vals                   = np.asarray(self.tobii_controller.EndFixations[self.fix_idx:])
        #print("Constructing numpy arrays for AOIS --- %s seconds ---" % (time.time() - start_constructing_numpy))

        for aoi in self.AOIS:
            start_computing_features = time.time()

            self.emdat_interval_features[aoi] = {}
            ## Indices of x-y array where datapoints are inside the specified AOI
            aoi_dpt_indices = np.array(self.tobii_controller.aoi_ids[aoi])
            aoi_dpt_indices = aoi_dpt_indices[aoi_dpt_indices >= self.x_y_idx]
            valid_indices = aoi_dpt_indices - self.x_y_idx
            #print('NUMBER OF VALID INDICES: %d' % len(valid_indices))
            no_dpts_available = (len(valid_indices) == 0)
            if no_dpts_available:
                self.set_empty_values(aoi)
                continue
            if params.USE_PUPIL_FEATURES:
                ## Select valid pupil sizes inside the AOI
                valid_pupil_sizes      = pup_size_vals[valid_indices]
                valid_pupil_sizes      = valid_pupil_sizes[valid_pupil_sizes > 0]
                    ## Select valid velocities inside the AOI
                valid_pupil_vel        = pup_vel_vals[valid_indices]
                valid_pupil_vel        = valid_pupil_vel[valid_pupil_vel != -1]
                self.generate_aoi_pupil_features(aoi, valid_pupil_sizes, valid_pupil_vel) #rest_pupil_size)
            if params.USE_DISTANCE_FEATURES:
                ## Select valid head distances inside the AOI
                valid_dist_vals        = dist_vals[valid_indices]
                self.generate_aoi_distance_features(aoi, valid_dist_vals)
            if (len(fixation_vals) == 0):
                self.set_empty_values(aoi, fixations_only = True)
                continue
            if (params.USE_FIXATION_PATH_FEATURES or params.USE_TRANSITION_AOI_FEATURES):
                valid_fixation_indices = np.where(np.apply_along_axis(datapoint_inside_aoi, 1, fixation_vals[:, :2], poly = self.AOIS[aoi]))
            if (params.USE_FIXATION_PATH_FEATURES):
                valid_fixation_vals    = fixation_vals[valid_fixation_indices]
                self.generate_aoi_fixation_features(aoi, valid_fixation_vals, self.length_invalid, len(fixation_vals))
            if (params.USE_TRANSITION_AOI_FEATURES):
                self.generate_transition_features(aoi, fixation_vals, valid_fixation_indices[0])
            #print("Computing features for %s AOI --- %s seconds ---" % (aoi, time.time() - start_constructing_numpy))
        self.x_y_idx = len(self.tobii_controller.x)
        self.fix_idx = len(self.tobii_controller.EndFixations)

    def set_empty_values(self, aoi, fixations_only = False):

        if not fixations_only:
            self.emdat_interval_features[aoi]['meanpupilsize']           = -1
            self.emdat_interval_features[aoi]['stddevpupilsize']         = -1
            self.emdat_interval_features[aoi]['maxpupilsize']            = -1
            self.emdat_interval_features[aoi]['minpupilsize']            = -1
            self.emdat_interval_features[aoi]['numpupilsizes']          = 0
            self.emdat_interval_features[aoi]['numpupilvelocity']       = 0
            self.emdat_interval_features[aoi]['numdistancedata']        = 0
            self.emdat_interval_features[aoi]['numfixations']               = 0
            self.emdat_interval_features[aoi]['meanpupilvelocity']      = -1
            self.emdat_interval_features[aoi]['stddevpupilvelocity']    = -1
            self.emdat_interval_features[aoi]['maxpupilvelocity']       = -1
            self.emdat_interval_features[aoi]['minpupilvelocity']       = -1
            self.emdat_interval_features[aoi]['meandistance']           = -1
            self.emdat_interval_features[aoi]['stddevdistance']         = -1
            self.emdat_interval_features[aoi]['maxdistance']            = -1
            self.emdat_interval_features[aoi]['mindistance']            = -1
            self.emdat_interval_features[aoi]['startdistance']          = -1
            self.emdat_interval_features[aoi]['enddistance']            = -1
        self.emdat_interval_features[aoi]['longestfixation']            = -1
        self.emdat_interval_features[aoi]['meanfixationduration']       = -1
        self.emdat_interval_features[aoi]['stddevfixationduration']     = -1
        self.emdat_interval_features[aoi]['timetofirstfixation']        = -1
        self.emdat_interval_features[aoi]['timetolastfixation']         = -1
        self.emdat_interval_features[aoi]['proportionnum']              = 0
        self.emdat_interval_features[aoi]['proportiontime']             = 0
        self.emdat_interval_features[aoi]['fixationrate']               = 0
        self.emdat_interval_features[aoi]['totaltimespent']             = 0
        self.emdat_interval_features[aoi]['total_trans_from'] = 0
        for cur_aoi in self.AOIS.keys():
            self.emdat_interval_features[aoi]['numtransfrom_%s'%(cur_aoi)] = 0
            self.emdat_interval_features[aoi]['proptransfrom_%s'%(cur_aoi)] = 0

    def generate_aoi_pupil_features(self, aoi, valid_pupil_data, valid_pupil_velocity): # rest_pupil_size): ##datapoints, rest_pupil_size, export_pupilinfo):
        #number of valid pupil sizes
        #self.emdat_interval_features[aoi]['startpupilsize']         = -1
        #self.emdat_interval_features[aoi]['endpupilsize']           = -1
        self.emdat_interval_features[aoi]['meanpupilsize']           = -1
        self.emdat_interval_features[aoi]['stddevpupilsize']         = -1
        self.emdat_interval_features[aoi]['maxpupilsize']            = -1
        self.emdat_interval_features[aoi]['minpupilsize']            = -1


        self.emdat_interval_features[aoi]['meanpupilvelocity']      = -1
        self.emdat_interval_features[aoi]['stddevpupilvelocity']    = -1
        self.emdat_interval_features[aoi]['maxpupilvelocity']       = -1
        self.emdat_interval_features[aoi]['minpupilvelocity']       = -1
        valid_pupil_data = valid_pupil_data[valid_pupil_data > 0]
        valid_pupil_velocity = valid_pupil_velocity[valid_pupil_velocity != -1]

        self.emdat_interval_features[aoi]['numpupilsizes']          = len(valid_pupil_data)
        self.emdat_interval_features[aoi]['numpupilvelocity']       = len(valid_pupil_velocity)

        if self.emdat_interval_features[aoi]['numpupilsizes'] > 0: #check if the current segment has pupil data available

            #if params.PUPIL_ADJUSTMENT == "rpscenter":
            #    valid_pupil_data        = valid_pupil_data - rest_pupil_size
            #elif params.PUPIL_ADJUSTMENT == "PCPS":
            #    adjvalidpupilsizes      = (valid_pupil_data - rest_pupil_size) / (1.0 * rest_pupil_size)
            #else:
            adjvalidpupilsizes      = valid_pupil_data
            self.emdat_interval_features[aoi]['meanpupilsize']              = np.mean(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['stddevpupilsize']            = calc_aoi_std_feature(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['maxpupilsize']               = np.max(adjvalidpupilsizes)
            self.emdat_interval_features[aoi]['minpupilsize']               = np.min(adjvalidpupilsizes)
            #self.emdat_interval_features[aoi]['startpupilsize']             = adjvalidpupilsizes[0]
            #self.emdat_interval_features[aoi]['endpupilsize']               = adjvalidpupilsizes[-1]

            if self.emdat_interval_features[aoi]['numpupilvelocity'] > 0:
                self.emdat_interval_features[aoi]['meanpupilvelocity']      = np.mean(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['stddevpupilvelocity']    = calc_aoi_std_feature(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['maxpupilvelocity']       = np.max(valid_pupil_velocity)
                self.emdat_interval_features[aoi]['minpupilvelocity']       = np.min(valid_pupil_velocity)
                """
        print "\n\n\tComputing %s AOI pupil features" % aoi
        print "meanpupilsize %f" % self.emdat_interval_features[aoi]['meanpupilsize']
        print "stddevpupilsize %f" % self.emdat_interval_features[aoi]['stddevpupilsize']
        print "maxpupilsize %f" % self.emdat_interval_features[aoi]['maxpupilsize']
        print "minpupilsize %f" % self.emdat_interval_features[aoi]['minpupilsize']
        #print "startpupilsize %f" % self.emdat_interval_features[aoi]['startpupilsize']
        #print "endpupilsize %f" % self.emdat_interval_features[aoi]['endpupilsize']
        print "meanpupilvelocity %f" % self.emdat_interval_features[aoi]['meanpupilvelocity']
        print "stddevpupilvelocity %f" % self.emdat_interval_features[aoi]['stddevpupilvelocity']
        print "maxpupilvelocity %f" % self.emdat_interval_features[aoi]['maxpupilvelocity']
        print "minpupilvelocity %f" % self.emdat_interval_features[aoi]['minpupilvelocity']
        print "numpupilsizes %f" % self.emdat_interval_features[aoi]['numpupilsizes']
        print "numpupilvelocity %f" % self.emdat_interval_features[aoi]['numpupilvelocity']
        print "\n\n\n"
        """
    def generate_aoi_distance_features(self, aoi, valid_distance_data):
        #number of valid pupil sizes
        valid_distance_data = valid_distance_data[valid_distance_data > 0]
        self.emdat_interval_features[aoi]['numdistancedata']        = len(valid_distance_data)
        if self.emdat_interval_features[aoi]['numdistancedata'] > 0:
            self.emdat_interval_features[aoi]['meandistance']       = np.mean(valid_distance_data)
            self.emdat_interval_features[aoi]['stddevdistance']     = calc_aoi_std_feature(valid_distance_data)
            self.emdat_interval_features[aoi]['maxdistance']        = np.max(valid_distance_data)
            self.emdat_interval_features[aoi]['mindistance']        = np.min(valid_distance_data)
            self.emdat_interval_features[aoi]['startdistance']      = valid_distance_data[0]
            self.emdat_interval_features[aoi]['enddistance']        = valid_distance_data[-1]
        else:
            self.emdat_interval_features[aoi]['meandistance']       = -1
            self.emdat_interval_features[aoi]['stddevdistance']     = -1
            self.emdat_interval_features[aoi]['maxdistance']        = -1
            self.emdat_interval_features[aoi]['mindistance']        = -1
            self.emdat_interval_features[aoi]['startdistance']      = -1
            self.emdat_interval_features[aoi]['enddistance']        = -1
        """
        print "\tComputing %s AOI distance features" % aoi
        print "numdistancedata %f" % self.emdat_interval_features[aoi]['numdistancedata']
        print "meandistance %f" % self.emdat_interval_features[aoi]['meandistance']
        print "stddevdistance %f" % self.emdat_interval_features[aoi]['stddevdistance']
        print "maxdistance %f" % self.emdat_interval_features[aoi]['maxdistance']
        print "mindistance %f" % self.emdat_interval_features[aoi]['mindistance']
        print "startdistance %f" % self.emdat_interval_features[aoi]['startdistance']
        print "enddistance %f" % self.emdat_interval_features[aoi]['enddistance']
        print "\n\n\n"
        """
    def generate_aoi_fixation_features(self, aoi, fixation_data, sum_discarded, num_all_fixations):

        self.emdat_interval_features[aoi]['longestfixation']            = -1
        self.emdat_interval_features[aoi]['meanfixationduration']       = -1
        self.emdat_interval_features[aoi]['stddevfixationduration']     = -1
        self.emdat_interval_features[aoi]['timetofirstfixation']        = -1
        self.emdat_interval_features[aoi]['timetolastfixation']         = -1
        self.emdat_interval_features[aoi]['proportionnum']              = 0
        self.emdat_interval_features[aoi]['proportiontime']             = 0
        self.emdat_interval_features[aoi]['fixationrate']               = 0
        self.emdat_interval_features[aoi]['totaltimespent']             = 0

        numfixations                                                    = len(fixation_data)
        self.emdat_interval_features[aoi]['numfixations']               = numfixations
        fixation_durations                                              = fixation_data[:, 2]
        totaltimespent                                                  = np.sum(fixation_durations)
        self.emdat_interval_features[aoi]['totaltimespent']             = totaltimespent
        self.emdat_interval_features[aoi]['proportiontime']             = float(totaltimespent) / (self.length - self.length_invalid)
        if numfixations > 0:
            self.emdat_interval_features[aoi]['longestfixation']        = np.max(fixation_durations)
            self.emdat_interval_features[aoi]['meanfixationduration']   = np.mean(fixation_durations)
            self.emdat_interval_features[aoi]['stddevfixationduration'] = calc_aoi_std_feature(fixation_durations)
            #self.emdat_interval_features[aoi]['timetofirstfixation']    = fixation_data[0][3] - self.starttime
            #self.emdat_interval_features[aoi]['timetolastfixation']     = fixation_data[-1][3] - self.starttime
            self.emdat_interval_features[aoi]['proportionnum']          = float(numfixations)/num_all_fixations
            self.emdat_interval_features[aoi]['fixationrate']           = numfixations / float(totaltimespent)
        """
        print "\tComputing %s AOI fixation features" % aoi
        print "longestfixation %f" % self.emdat_interval_features[aoi]['longestfixation']
        print "meanfixationduration %f" % self.emdat_interval_features[aoi]['meanfixationduration']
        print "stddevfixationduration %f" % self.emdat_interval_features[aoi]['stddevfixationduration']
        #print "timetofirstfixation %f" % self.emdat_interval_features[aoi]['timetofirstfixation']
        #print "timetolastfixation %f" % self.emdat_interval_features[aoi]['timetolastfixation']
        print "proportionnum %f" % self.emdat_interval_features[aoi]['proportionnum']
        print "proportiontime %f" % self.emdat_interval_features[aoi]['proportiontime']
        print "totaltimespent %d" % self.emdat_interval_features[aoi]['totaltimespent']

        print "fixationrate %f" % self.emdat_interval_features[aoi]['fixationrate']
        """
    def generate_transition_features(self, cur_aoi, fixation_data, fixation_indices):
        #print "GENERATING TRANSITION FEATURES FOR %s AOI" % cur_aoi
        for aoi in self.AOIS.keys():
            self.emdat_interval_features[cur_aoi]['numtransfrom_%s'%(aoi)] = 0

        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                # Find the number
                for aoi in self.AOIS:
                    # TODO: Add  polyout
                    #polyout = aoi.polyout
                    key = 'numtransfrom_%s'%(aoi)
                    if datapoint_inside_aoi((fixation_data[i-1][0], fixation_data[i-1][1]), self.AOIS[aoi]):
                        self.emdat_interval_features[cur_aoi][key] += 1
                        sumtransfrom += 1
        for aoi in self.AOIS.keys():
            if sumtransfrom > 0:
                val = self.emdat_interval_features[cur_aoi]['numtransfrom_%s'%(aoi)]
                self.emdat_interval_features[cur_aoi]['proptransfrom_%s'%(aoi)] = float(val) / sumtransfrom
            else:
                self.emdat_interval_features[cur_aoi]['proptransfrom_%s'%(aoi)] = 0
            #print "Proptransform from %s to %s is %f" % (aoi, cur_aoi, self.emdat_interval_features[cur_aoi]['proptransfrom_%s'%(aoi)])
        self.emdat_interval_features[cur_aoi]['total_trans_from']               = sumtransfrom
        #print("Total transitions %d" % sumtransfrom)

    def get_length_invalid(self):
        """Returns the sum of the length of the invalid gaps > params.MAX_SEG_TIMEGAP
        Args:
            an integer, the length in milliseconds
        """
        time = self.tobii_controller.time
        length = 0
        if isinstance(self.time_gaps, list):
            for gap in self.time_gaps:
                length += gap[1] - gap[0]
        else:
            length = time[-1] - time[self.pups_idx]
        return length

def calc_aoi_std_feature(data):
    if (len(data) > 1):
        return np.std(data, ddof = 1)
    else:
        return -1

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
