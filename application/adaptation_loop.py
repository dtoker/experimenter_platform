import sqlite3
import json
from StringIO import StringIO

from application_state_controller import ApplicationStateController
from tornado.web import RequestHandler

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
        self.conn.row_factory = dict_factory

    def evaluateRules(self, event_name):
        #if the triggering event is not of the active user states for this task, an error has occured
        print self.controller.eventNames
        print event_name
        if event_name not in self.controller.eventNames:
            raise ValueError("Event name received is not one of the user staes active for this task")
        task = self.controller.currTask

        #query for all the rules which get triggered by this event
        query_results = self.conn.execute('SELECT name, delivery_sql_condition, intervention FROM rule, rule_task WHERE rule.name = rule_task.rule_name and rule_task.task = ?', str(task))
        triggered_rules = query_results.fetchall()
        #print "triggered rules:" + json.dumps(triggered_rules)

        #filter the triggered rules to rules to deliver based on their delivery sql conditional
        to_deliver_rules = []
        for rule in triggered_rules:
            if self.controller.evaluateConditional(rule['delivery_sql_condition']):
                intervention_name = rule['intervention']
                print "reached here"
                print intervention_name
                results = self.conn.execute("SELECT * FROM intervention WHERE intervention.name = ?", (intervention_name,))
                intervention = results.fetchone()
                print intervention
                to_deliver_rules.append(intervention)

        to_deliver_rules = json.dumps({'message': to_deliver_rules})
        print to_deliver_rules

    def executeQueries(self):
        queryResults = self.conn.execute('SELECT * from rule')
        print queryResults.fetchone()

def main():
    app_contr = ApplicationStateController()
    table = "text_fix"
    app_contr.updateFixTable(table, 1, 700, 1200, 200)
    app_contr.updateFixTable(table, 2, 700, 1200, 200)
    loop = AdaptationLoop(app_contr)
    loop.evaluateRules('text_fix')

if __name__ == "__main__":
    main()
