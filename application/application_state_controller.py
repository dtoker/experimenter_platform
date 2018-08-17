import sqlite3
import datetime
import os
import shutil
from tornado import gen
from tornado.ioloop import IOLoop
from StringIO import StringIO
import ast

class ApplicationStateController():

    """Class to manage the user model and application database and handling
    its relevent queries"""

    def __init__(self, task = 1):

        """Initiliazes the dynamic tables and class variables

        arguments
        task            -- first task to load into, defaults to 1

        class variables:

        currTask        -- integer, representing the current, active task id
        userStates      -- list of sqlite3.Row object, representing a set of tuples retrieved from a query result
                                - two keys are: event_name, type
                                - captures all the active user states
        eventNames      -- list, representing a list of all active user state names

        keyword arguments
        None
        """

        self.currTask = task
        self.userStates =[]
        self.eventNames = []
        self.__initializeApplication__()

    def __getDBCommands__(self):

        """Retrieves the database sql commands as a String

        arguments
        None

        keyword arguments
        None

        returns
        StringIO object  -- a dump of the sql commands for the current db connection
        """

        tempfile = StringIO()
        for line in self.conn.iterdump():
            tempfile.write('%s\n' % line)
        tempfile.seek(0)
        return tempfile

    def __readDBFromDisk__(self):

        """Initializes the db in memory by reading it from './user_model_state.db'

        arguments
        None

        keyword arguments
        None

        returns
        None
        """

        self.conn = sqlite3.connect('./user_model_state.db')
        commands = self.__getDBCommands__()
        self.conn.close()

        self.conn = sqlite3.connect(":memory:")
        self.conn.cursor().executescript(commands.read())
        self.conn.commit()
        self.conn.row_factory = sqlite3.Row
        print('read db')
        print(self.conn)

    def __writeDBToDisk__(self):

        """ Writes the current state of the db in memory back to './user_model_state.db'

        arguments
        None

        keyword arguments
        None

        returns
        None
        """
        command = self.__getDBCommands__()
        self.conn.close()

        os.remove("./user_model_state.db")
        self.conn = sqlite3.connect("./user_model_state.db")
        self.conn.cursor().executescript(command.read())
        self.conn.commit()
        self.conn.close()

    def __initializeApplication__(self):

        """ Initializes the class by:
            -setting up the db in memory
            -deleting all previous dynamic tables
            -setting the current task
            -creating the required dynamic tables

        arguments
        None

        keyword arguments
        None

        returns
        None
        """

        print "initializing application"
        self.__readDBFromDisk__()
        self.__deleteAllDynamicTables__()
        self.__updateTaskAndUserState__(self.currTask)
        self.__createDynamicTables__()

    def __updateTaskAndUserState__(self, task):

        """ Updates the current task and retrieves the relevant user states

        arguments
        task        -- integer, the task to be switched to

        keyword arguments
        None

        returns
        None
        """

        self.currTask = task
        print("CURR TASK " + str(self.currTask))
        query_results = self.conn.execute("SELECT user_state.event_name, type FROM user_state, user_state_task WHERE user_state.event_name = user_state_task.event_name and task = ?", (str(self.currTask),))
        self.userStates = query_results.fetchall()
        self.eventNames = []
        for user in self.userStates:
            self.eventNames.append(user['event_name'])

    def __createDynamicTables__(self):

        """ Creates the dynamic tables required for the current task
            -ie. one for each user state that is being tracked for the current task

        arguments
        None

        keyword arguments
        None

        returns
        None
        """

        self.conn.execute("CREATE TABLE intervention_state ( `intervention` TEXT, `active` INTEGER, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`intervention`))")
        self.conn.execute("CREATE TABLE rule_state ( `rule` TEXT, time_stamp INTEGER, occurences INTEGER, PRIMARY KEY(`rule`))")
        self.conn.commit()
        for user in self.userStates:
            table_name = user['event_name']
            print "creating table:" + table_name
            if user['type'] == 'fix':
                self.conn.execute("CREATE TABLE {} ( `id` INTEGER, `time_start` INTEGER, `time_end` INTEGER, `duration` INTEGER, PRIMARY KEY(`id`) )".format(table_name))
            elif user['type'] == 'emdat':
                self.conn.execute("CREATE TABLE {} ( `id` INTEGER, `interval_value` INTEGER, `task_value` TEXT, `runtime_value` TEXT, PRIMARY KEY(`id`) )".format(table_name))
            elif user['type'] == 'ml':
                self.conn.execute("CREATE TABLE {} ( `id` INTEGER, `time_stamp` INTEGER, `raw_prediction` REAL, `value` TEXT, PRIMARY KEY(`id`) )".format(table_name))
            else:
                raise NotImplementedError("Invalid Type: The supported types are `fix` `ml` and `emdat`")
            self.conn.commit() #commit after every creation?

    def __deleteTaskDynamicTables__(self):

        """ Deletes all the dynamic tables associated with the current task

        arguments
        None

        keyword arguments
        None

        returns
        None
        """
        self.conn.execute("DROP TABLE IF EXISTS intervention_state")
        self.conn.execute("DROP TABLE IF EXISTS rule_state")
        self.conn.commit()
        for user in self.userStates:
            table_name = user['event_name']
            self.conn.execute("DROP TABLE IF EXISTS {}".format(table_name))
        self.conn.commit()

    def __deleteAllDynamicTables__(self):

        """ Deletes all dynamic tables from every task,
            this method is called to clean-up any tables persisting in the database
            due to a premature termination (ie. crash or exception from previous run)

        arguments
        None

        keyword arguments
        None

        returns
        None
        """

        print "deleting all dynamic tables"

        self.conn.execute("DROP TABLE IF EXISTS intervention_state")
        self.conn.execute("DROP TABLE IF EXISTS rule_state")
        self.conn.commit()

        query_results = self.conn.execute('SELECT user_state.event_name FROM user_state')
        userStates = query_results.fetchall()

        for user in userStates:
            table_name = user['event_name']
            self.conn.execute("DROP TABLE IF EXISTS {}".format(table_name))
        self.conn.commit()

    def logTask(self):

        """ Creates a log file called log_for_task_x, where x is the current task
            the log file captures the current state of the database as a sql file

        arguments
        None

        keyword arguments
        None

        returns
        None
        """
        file = self.__getDBCommands__()
        #TODO: robust check of log dir
        file_name = './log/log_for_task_' + str(self.currTask) + ".sql"
        with open (file_name, 'w') as fd:
          file.seek (0)
          shutil.copyfileobj (file, fd)

    def changeTask(self, task):

        """ Changes database to reflect a new task:
            - create a log of current db state
            - deleting previous dynamic tables
            - updating class variables
            - creating new dynamic tables for the new class

        arguments
        None

        keyword arguments
        None

        returns
        None
        """
        print "Switching to task: " + str(task)
        self.logTask()
        self.__deleteTaskDynamicTables__()
        self.__updateTaskAndUserState__(task)
        self.__createDynamicTables__()


    def resetApplication(self):

        """ Prepares the application for termination, should be called at the end of execution
            - logs the current state of db
            - deletes all dynamic tables
            - writes the db from memory back to disk

        arguments
        None

        keyword arguments
        None

        returns
        None
        """

        self.logTask()
        self.__deleteAllDynamicTables__()
        self.__writeDBToDisk__()


    def getFixAoiMapping(self):

        """ Returns a mapping of the fixation user states (event name) to aoi's

        arguments
        None

        keyword arguments
        None

        returns
        Dict    -- contains a mapping of the fixation user state as keys
                to the polygon coordinates of their respective aoi's
        """
        mapping = {}
        query_results = self.conn.execute("SELECT user_state.event_name, polygon FROM aoi, user_state, user_state_task WHERE user_state.aoi = aoi.name AND aoi.task = ? AND user_state.event_name = user_state_task.event_name AND user_state_task.task = ? AND type = 'fix'", (str(self.currTask), str(self.currTask)))
        aoi_results = query_results.fetchall()
        for aoi in aoi_results:
            event_name = aoi['event_name']

            polygon = aoi['polygon']
            mapping[event_name] = ast.literal_eval(polygon)

        #print mapping
        return mapping

    def getEmdatAoiMapping(self):

        """ Returns a mapping of the emdat user states (event name) to aoi's

        arguments
        None

        keyword arguments
        None

        returns
        Dict    -- contains a mapping of the edmat user state as keys
                to the polygon coordinates of their respective aoi's
        """
        mapping = {}
        query_results = self.conn.execute("SELECT user_state.event_name, polygon FROM aoi, user_state, user_state_task WHERE user_state.aoi = aoi.name AND aoi.task = ? AND user_state.event_name = user_state_task.event_name AND user_state_task.task = ? AND type = 'emdat'", (str(self.currTask), str(self.currTask)))
        aoi_results = query_results.fetchall()
        for aoi in aoi_results:
            event_name = aoi['event_name']

            polygon = aoi['polygon']
            mapping[event_name] = ast.literal_eval(polygon)

        #print mapping
        return mapping

    def getEdmatFeatures(self):

        """ Returns a mapping of the emdat user states (event names) to its associated emdat feature

        arguments
        None

        keyword arguments
        None

        returns
        Dict    -- contains a mapping of the user state as keys
                to their respective emdat features
        """
        mapping = {}
        query_results = self.conn.execute("SELECT user_state.event_name, feature FROM user_state, user_state_task WHERE user_state.event_name = user_state_task.event_name AND user_state_task.task = ? AND type = 'emdat'", (str(self.currTask),))
        feature_results = query_results.fetchall()
        for feature in feature_results:
            event_name = feature['event_name']

            feature_value = feature['feature']
            mapping[event_name] = feature_value

        return mapping

    def getMLFeatures(self):
        """ Returns a mapping of the ML user states (event names) to associated ML features

        arguments
        None

        keyword arguments
        None

        returns
        List    -- contains a list of the user states to associate with ML predictions
        """
        mapping = {}
        query_results = self.conn.execute("SELECT user_state.event_name FROM user_state, user_state_task WHERE user_state.event_name = user_state_task.event_name AND user_state_task.task = ? AND type = 'ml'", (str(self.currTask),))
        feature_results = query_results.fetchall()
        ml_features = []
        for feature in feature_results:
            ml_features.append(feature['event_name'])

        return ml_features

    def evaluateConditional(self, query):

        """ Evalutaes an SQL conditional

        arguments
        query       -- the conditional to be evaluated, should be formed to return
                        a single colum 'result' which one row: 1 for true, 0 for false

        keyword arguments
        None

        returns
        Bool        -- 1 if the condtional evaluated true, 0 if false
        """

        query = query.replace("\n"," ") #replace new line symbols in case the sql conditional is multi-lined
        try:
            query_results = self.conn.execute(query)
            value = int(query_results.fetchone()['result'])
        except:
            raise ValueError("Malformed SQL conditional check in gaze_event_rules.db")
        #print value
        return value

    def updateFixTable(self, table, id, time_start, time_end, duration):

        """ Insert a new row into a fixation table

        arguments
        table       -- String, name of an existing dynamic fixation table
                    (ie. one of the user states)
        id          -- int, id associated with the fixation
        time_start  -- int, time_stamp of the start of the fixation in ms
        time_end    -- int, time_stamp of the end of the fixation in ms
        duration    -- int, duration of the fixation in ms

        keyword arguments
        None

        returns
        None
        """
        if not (isinstance(id, int) and isinstance(time_start, long) and isinstance(time_end, long) and isinstance(duration, int)):
            raise TypeError('Value for columns of a fixation table must be an int')
        self.conn.execute("INSERT INTO {} VALUES (?,?,?,?)".format(table), (id, time_start, time_end, duration))
        self.conn.commit()

    def updateEmdatTable(self, id, emdat_features):

        """ Insert a new row into an emdat table

        arguments

        id                   -- int, id associated with the emdat event
        edmat_features       -- dict, event_names as keys, mapped to a tuple (interval_value, task_value, runtime_value)

        keyword arguments
        None

        returns
        None
        """

        #TODO: type checking
        for event_name in emdat_features:
            self.conn.execute("INSERT INTO {} VALUES (?,?,?,?)".format(event_name), (id,) + emdat_features[event_name])
        self.conn.commit()

    def updateMlTable(self, table, id, time_stamp, raw_prediction, value):

        """ Inserts new row into a ml table

        arguments
        table           -- String, name of an existing emdat table
                        (ie. one of the user states)

        id              -- int, id associated with the emdat event
        time_stamp      -- int, time_stamp of the predictino in ms
        raw_prediction  -- float, value of raw prediction between 0 and 1
        value           -- String, value associated with prediction

        keyword arguments
        None

        returns
        None
        """
        #TODO: type checking
        self.conn.execute("INSERT INTO {} VALUES (?,?,?,?)".format(table), (id, time_stamp, raw_prediction, value))
        self.conn.commit()

    def getInterventionOccurences(self, intervention_name):

        """Get the number of times a intervention has been delivered

        arguments
        intervention_name               -- string, name of the intervention to check for rule_occurences

        keyword arguments
        None

        returns
        int                     -- number of times intervention has been delivered so far

        """
        query_results = self.conn.execute("SELECT occurences FROM intervention_state WHERE intervention = ?", (intervention_name,)).fetchone()
        if query_results is None:
            return 0
        else:
            return query_results['occurences']

    def getRuleOccurences(self, rule_name):

        """Get the number of times a rule has been delivered

        arguments
        rule_name               -- string, name of the rule to check for rule_occurences

        keyword arguments
        None

        returns
        int                     -- number of times rule has been delivered so far

        """
        query_results = self.conn.execute("SELECT occurences FROM rule_state WHERE rule = ?", (rule_name,)).fetchone()
        if query_results is None:
            return 0
        else:
            return int(query_results['occurences'])

    def setInterventionActive(self, intervention_name, rule_name, time_stamp):

        """Apply state changes in the User Model for a rule and its associated intervention
                - sets the invertention to be active
                - increments the occurences of both the rule and the intervention
                - update the time stamp of the last occurence for the rule and intervention

        arguments
        intervention_name             -- string, name of the intervention to update
        rule_name                     -- string, name of the associated rule to update
        time_stamp                    -- time stamp of triggering event

        keyword arguments
        None

        """

        #update intervention occurences
        intervention_occurences = self.conn.execute("SELECT occurences FROM intervention_state WHERE intervention = ?", (intervention_name,)).fetchone()
        if intervention_occurences is None:
            self.conn.execute("INSERT INTO intervention_state values (?, 1, ?, ?)", (intervention_name, time_stamp, 1))
        else:
            occurences = int(intervention_occurences['occurences']) + 1
            self.conn.execute("UPDATE intervention_state SET active = 1, time_stamp = ?, occurences = ? WHERE intervention = ?", (time_stamp, occurences, intervention_name))
        self.conn.commit()
        #update rule occurences
        rule_occurences = self.conn.execute("SELECT occurences FROM rule_state WHERE rule = ?", (rule_name,)).fetchone()
        if rule_occurences is None:
            self.conn.execute("INSERT INTO rule_state values (?, ?, ?)", (rule_name, time_stamp, 1))
        else:
            occurences = int(rule_occurences['occurences']) + 1
            self.conn.execute("UPDATE rule_state SET time_stamp = ?, occurences = ? WHERE rule = ?", (time_stamp, occurences, rule_name))
        self.conn.commit()

    def setInterventionInactive(self, intervention_name):

        """Sets active column on intervention to be false

        arguments
        intervention_name       -- string, name of the intervention to update

        keyword arguments
        None

        returns
        boolean                 -- true if the number of occurences so far is less than the maximum allowed repeats,
                                if max_repeats is set as NULL or a negative number, always return True
                                otherwise return false

        """

        self.conn.execute("UPDATE intervention_state SET active = 0 WHERE intervention = ?", (intervention_name,))
        self.conn.commit()

    def isInterventionActive(self, intervention_name):

        """Checks if this intervention is currently active

        arguments
        intervention_name       -- string, name of the intervention to be checked

        keyword arguments
        None

        returns
        boolean                 -- true if active column of the intervention == 1, else false

        """
        query_results = self.conn.execute("SELECT * from intervention_state where intervention = ? and active = 1", (intervention_name,)).fetchone()
        return not (query_results is None)

def main():
    app_contr = ApplicationStateController(1)
    #for testing purposes:
    table = "text_fix"
    #IOLoop.current().run_sync(lambda: app_contr.updateFixTable(table, 1, 700, 1200, 200))
    #IOLoop.current().run_sync(lambda: app_contr.updateFixTable(table, 2, 2000, 2200, 400))
    #IOLoop.current().run_sync(lambda: app_contr.changeTask(2))
    #IOLoop.current().run_sync(app_contr.resetApplication)


if __name__ == "__main__":
    main()
