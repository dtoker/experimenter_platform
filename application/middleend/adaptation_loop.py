import sqlite3
import json
from StringIO import StringIO

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

class AdaptationLoop():

    """Class to evaluate user defined rules and dispatch interventions as neccesary"""

    def __init__(self, app_state_controller, liveWebSocket = []):

        """Initiliazes the class variables

        arguments
        ApplicationStateController      -- instance of ApplicationStateController
                                        for interfacing with the user model database
        liveWebSocket                   -- a list of Websockets for dispatching messages to the front-end

        class variables:

        controller                      -- ApplicationStateController, instance of the ApplicationStateController
        liveWebSocket                   -- list of tornado.websocket.WebSocketHandler, websockets for dispatching
                                        messages to the front-end

        keyword arguments
        None
        """
        self.app_state_controller = app_state_controller
        self.liveWebSocket = liveWebSocket
        self.__readDBFromDisk__()

    def __readDBFromDisk__(self):

        """Reads the rules / intervention database from disk and stores it in memory
            - also sets the row_factory attribute of the db connection to return a dictionary
            - read from ./gaze_event_rules.db

        arguments
        None

        keyword arguments
        None

        """
        # db read from ./gaze_event_rules.db
        self.conn = sqlite3.connect('./gaze_event_rules.db')

        #copy the db from disk into a buffer
        db = StringIO()
        for line in self.conn.iterdump():
            db.write('%s\n' % line)
        db.seek(0)
        self.conn.close()

        #one shot the buffered sql commands into a db running in memory
        self.conn = sqlite3.connect(":memory:")
        self.conn.cursor().executescript(db.read())
        self.conn.commit()
        self.conn.row_factory = dict_factory

    def __removeExpiredInterventions__(self, event_name, task):

        """Removes all the required interventions
            - gets all the rules which have this event as a removal trigger
            - if the corresponding intervention is currently active and the removal condition is met
            remove the intervention

        arguments
        event_name      -- string, name of the user (state) event triggering this rule check
        task            -- int, current task id

        keyword arguments
        None

        """

        # get all rules and interventions which have a trigger event that matches event_name
        query_results = self.conn.execute("SELECT name, removal_sql_condition, intervention FROM rule, rule_task WHERE rule.name = rule_task.rule_name and rule_task.task = ? and rule.removal_trigger_event = ?", (task, event_name))
        triggered_removals = query_results.fetchall()

        to_remove = []
        #for each intervention, if it is currently active and if it's removal condition is met
        #update its status in the application state. ie. set active = 0
        for removal in triggered_removals:

            intervention_name = removal['intervention']
            removal_condition = removal['removal_sql_condition']

            if self.app_state_controller.isInterventionActive(intervention_name):
                if self.app_state_controller.evaluateConditional(removal_condition):
                    self.app_state_controller.setInterventionInactive(intervention_name)
                    to_remove.append(intervention_name)
                    print("removing: " + intervention_name)

        #dispatch a call to remove all the interventions from the UI
        #TODO: Whether or not liveWebSocket should be an array
        if to_remove:
            to_remove = json.dumps({'remove': to_remove})
            print to_remove
            for ws in self.liveWebSocket:
                ws.write_message(to_remove)

    def __ruleRepeatsAllowed__(self, rule_name):

        """Checks if this rule has not exceeded its maximum number of repeats

        arguments
        rule_name       -- string, name of the rule to be checked against

        keyword arguments
        None

        returns
        boolean                 -- true if the number of occurences so far is less than the maximum allowed repeats,
                                if max_repeats is set as NULL or a negative number, always return True
                                otherwise return false

        """

        max_repeat = self.conn.execute("SELECT max_repeat FROM rule where name = ?", (rule_name,)).fetchone()
        if max_repeat is None or max_repeat['max_repeat'] < 0:
            return True
        occurences = self.app_state_controller.getRuleOccurences(rule_name)
        return occurences < max_repeat['max_repeat']

    def __interventionRepeatsAllowed__(self, intervention_name):

        """Checks if this intervention has not exceeded its maximum number of repeats

        arguments
        intervention_name       -- string, name of the intervention to be checked against

        keyword arguments
        None

        returns
        boolean                 -- true if the number of occurences so far is less than the maximum allowed repeats,
                                if max_repeats is set as NULL or a negative number, always return True
                                otherwise return false

        """

        max_repeat = self.conn.execute("SELECT max_repeat FROM intervention where name = ?", (intervention_name,)).fetchone()
        if max_repeat is None or max_repeat['max_repeat'] < 0:
            return True
        occurences = self.app_state_controller.getInterventionOccurences(intervention_name)
        return occurences < max_repeat['max_repeat']

    def __deliverNewInterventions__(self, event_name, task, time_stamp):

        """Dispacthes new interventions which are triggered
            - gets all the rules which have this event as a delivery trigger
            - if the delivery trigger on the rule is met, dispatch it's corresponding invervention

        arguments
        event_name         -- string, name of the user (state) event triggering this rule check
        task               -- int, current task id
        time_stamp         -- long, time stamp of user event

        keyword arguments
        None

        """

        #get all the rules/interventions which have event_name as the delivery_trigger
        query_results = self.conn.execute("SELECT name, delivery_sql_condition, intervention, active_retrigger FROM rule, rule_task WHERE rule.name = rule_task.rule_name and rule_task.task = ? and rule.delivery_trigger_event = ?", (task, event_name))
        triggered_rules = query_results.fetchall()

        #filter the triggered rules to rules to deliver based on their delivery sql conditional
        #if the delivery condtional is satisfied, update the application state ie. active = 1
        to_deliver_rules = []
        for rule in triggered_rules:
            rule_name = rule['name']
            intervention_name = rule['intervention']
            active_retrigger = rule['active_retrigger']
            #check the rule if it is not currently active or if active_retrigger = 1
            if active_retrigger == 1 or not self.app_state_controller.isInterventionActive(intervention_name):
                #if both the rule and intervention has not exceeded max repeats
                if self.__ruleRepeatsAllowed__(rule_name) and self.__interventionRepeatsAllowed__(intervention_name):
                    #check the delivery conditional
                    if self.app_state_controller.evaluateConditional(rule['delivery_sql_condition']):
                        results = self.conn.execute("SELECT * FROM intervention WHERE intervention.name = ?", (intervention_name,))
                        intervention_params = results.fetchone()
                        to_deliver_rules.append(intervention_params)
                        self.app_state_controller.setInterventionActive(intervention_name, rule_name, time_stamp)
                        #print("triggered: " + rule_name + " deliverying: " + intervention_name)

        #TODO: whether or not liveWebSocket should be an array
        if to_deliver_rules:
            to_deliver_rules = json.dumps({'deliver': to_deliver_rules})
            print to_deliver_rules
            for ws in self.liveWebSocket:
                ws.write_message(to_deliver_rules)

    def evaluateRules(self, event_name, time_stamp):

        """Evaluates all rules based that are triggered by the event with event_name

        arguments
        event_name       -- string, name of the user state event causing this trigger
                        must be one of the user state events that is active for this task

        time_stamp      -- long, time stamp of when the event occured

        keyword arguments
        None

        returns
        """
        #if the triggering event is not one of the active user states for this task, an error has occured
        print("CHECKING RULES")
        if event_name not in self.app_state_controller.eventNames:
            raise ValueError("Event name received is not one of the user states active for this task")
        task = self.app_state_controller.currTask

        #remove all interventions that have this event as a removal_triggger
        self.__removeExpiredInterventions__(event_name, task)

        #deliver new interventions for all interventions that have this event as deliver_trigger
        self.__deliverNewInterventions__(event_name, task, time_stamp)

    def test(self):
        # for testing purposes:
        table = "text_fix"
        self.app_state_controller.updateFixTable(table, 1, long(700), long(1200), 200)
        self.app_state_controller.updateFixTable(table, 2, long(700), long(1200), 200)
        #self.app_state_controller.setInterventionInactive("intervention_1")
        #self.app_state_controller.setInterventionActive("intervention_1", "rule_1", 2000)
        #self.app_state_controller.setInterventionActive("intervention_1", "rule_2", 3000)
        #self.app_state_controller.setInterventionInactive("intervention_1")

        print self.app_state_controller.getFixAoiMapping()
        print self.app_state_controller.getEmdatAoiMapping()
        print self.app_state_controller.getEdmatFeatures()
        print("new fix")
        self.evaluateRules('text_fix', 3000)
        #self.evaluateRules('vis_fix', 4000)
        #self.evaluateRules('vis_fix', 5000)
        print("new fix")
        self.evaluateRules('text_fix', 6000)
        print("new fix")
        self.evaluateRules('text_fix', 6000)
        print("new fix")
        self.evaluateRules('text_fix', 3000)
        print("new fix")
        #self.evaluateRules('vis_fix', 4000)
        #self.evaluateRules('vis_fix', 5000)
        self.evaluateRules('text_fix', 6000)
        print("new fix")
        self.evaluateRules('text_fix', 6000)
        self.app_state_controller.resetApplication()

def main():
    print "main"
    #app_contr = ApplicationStateController()
    #loop = AdaptationLoop(app_contr)
    #loop.test()

if __name__ == "__main__":
    main()
