import sqlite3
from StringIO import StringIO

from application_state_controller import ApplicationStateController
from tornado.web import RequestHandler

class AdaptationLoop():

    def __init__(self, ApplicationStateController, RequestHandler = None):
        self.controller = ApplicationStateController
        self.handler = RequestHandler
        self.readDBFromDisk()
        print "intialization"

    def readDBFromDisk(self):
        # db read from ../gaze_event_rules.db
        self.conn = sqlite3.connect('../gaze_event_rules.db')

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
        self.conn.row_factory = sqlite3.Row

    def evaluateRules(self, event_name):
        #if the triggering event is not of the active user states for this task, an error has occured
        if event_name not in this.controller.userStates:
            raise ValueError("Event name received is not one of the user staes active for this task")
        task = this.controller.currTask

        #query for all the rules which get triggered by this event
        query_results = this.conn.execute('SELECT name, delivery_sql_conditional, intervention FROM rule, rule_task WHERE rule.name = rule_task.rule_name and rule_task.task = ?', task)
        triggered_rules = query_results.fetchall()
        print "triggered rules:" + triggered_rules

        #filter the triggered rules to rules to deliver based on their delivery sql conditional
        to_deliver_rules = []
        for rule in triggered_rules:
            if this.controller.evaluateConditional(rule['delivery_sql_conditional']):
                intervention_name = rule['intervention']
                results = this.conn.execute('SELECT function, delivery_delay, transition_in, transition_out, arguments FROM intervention WHERE name = ?', intervention_name)
                intervention = json.loads(results.fetchone())
                print intervention
                to_deliver_rules.append(intervention)

        to_deliver_rules = json.loads(to_deliver_rules)
        print to_deliver_rules

    def executeQueries(self):
        queryResults = self.conn.execute('SELECT * from rule')
        print queryResults.fetchone()

def main():
    app_contr = ApplicationStateController()
    loop = AdaptationLoop(app_contr)
    loop.executeQueries()

if __name__ == "__main__":
    main()
