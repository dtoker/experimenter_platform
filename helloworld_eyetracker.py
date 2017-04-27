import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import time
from tornado.options import define, options
import os.path

import sqlite3
import datetime
import json
import random

import eye_tracker
from eye_tracker import TobiiController

import csv 




define("port", default=8888, help="run on the given port", type=int)



class Application(tornado.web.Application):
    def __init__(self):
        #connects url with code
        handlers = [
            (r"/", MainHandler),
            (r"/locus", LocusHandler),
            (r"/prestudy", PreStudyHandler),
            (r"/fixation", FixationHandler),
            (r"/mmd", MMDHandler),
            (r"/MMDIntervention", MMDInterventionHandler),
            (r"/questionnaire", QuestionnaireHandler),
            (r"/websocket", EchoWebSocketHandler),

        ]
        #connects to database
        self.conn = sqlite3.connect('database.db')
        #"global variable" to save current UserID of session
        UserID = -1;
        #global variable to track start and end times
        start_time = '';
        end_time = '';
        #where to look for the html files
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
        )
        #initializes web app
        tornado.web.Application.__init__(self, handlers, **settings)

#each ____Handler is associated with a url
#def get is for when a http get request is made to the url
#def post is for when a http post request is made to the url(ex: form is submitted)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        #self.render('index.html')
        self.application.start_time = str(datetime.datetime.now().time())
        self.application.cur_mmd = 3
        self.application.cur_user = 100
        print 'hello'
        mmdQuestions = self.loadMMDQuestions()

        self.render('mmd.html', mmd="3")

        #self.render('MMDIntervention.html', mmd="3")
        #self.render('questionnaire.html', mmd="3", questions = mmdQuestions)


    def post(self):

        ##### TODO ######

        # 1)generate userid
        # 2)login with old userid
        self.application.cur_user = random.randint(0, 1000)  #random number for now
        self.application.end_time = str(datetime.datetime.now().time())
        task_data = (self.application.cur_user, self.application.cur_mmd, self.application.start_time, self.application.end_time,"")
        self.application.conn.execute('INSERT INTO MMD_tasks VALUES (?,?,?,?,?)', task_data)
        self.application.conn.commit()

        self.redirect('/questionnaire')

        #self.redirect('/prestudy')

    def loadMMDQuestions (self):
        conn = sqlite3.connect('database.db')
        query_results = conn.execute('select * from MMDQuestions')

        return json.dumps(query_results.fetchall())
        # query_results
        # OR

        # query_results.fetchone()





class QuestionnaireHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        print 'questionnaire handler'
        self.application.start_time = str(datetime.datetime.now().time())
        mmdQuestions = self.loadMMDQuestions()
        self.render('questionnaire.html', mmd="3", questions = mmdQuestions)



    def post(self):
        print 'post'
        answers = self.get_argument('answers')
        print answers

        answers = json.loads(answers)

        print answers

        self.application.end_time = str(datetime.datetime.now().time())
        questionnaire_data = [
        self.application.cur_user, self.application.cur_mmd, self.application.start_time, self.application.end_time]


        for a in answers:
            questionnaire_data.append(a)

        print tuple(questionnaire_data)

        self.application.conn.execute('INSERT INTO MMD_tasks VALUES (?,?,?,?,?)', questionnaire_data)
        #self.application.conn.commit()

        #refers to database connected to in 'class Application'
        #database = self.application.db.database
        #empty entry to insert into database in order to generate a user id
        #entry = {}
        #inserts empty entry and saves it to UserID variable in 'class Application'
        #self.application.UserID = database.insert_one(entry).inserted_id
        #print self.application.UserID
        self.redirect('/prestudy')

    def loadMMDQuestions (self):
        conn = sqlite3.connect('database.db')
        query_results = conn.execute('select * from MMDQuestions')

        return json.dumps(query_results.fetchall())

    #
    # def saveMMDQuestions(self):
    #     self.application.end_time = str(datetime.datetime.now().time())
    #     task_data = (
    #     self.application.cur_user, self.application.cur_mmd, self.application.start_time, self.application.end_time, "")
    #     self.application.conn.execute('INSERT INTO MMD_tasks VALUES (?,?,?,?,?)', task_data)
    #     self.application.conn.commit()

class MMDInterventionHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        self.application.start_time = str(datetime.datetime.now().time())
        self.render('MMDIntervention.html', mmd="30")

    def post(self):
        #refers to database connected to in 'class Application'
        #database = self.application.db.database
        #empty entry to insert into database in order to generate a user id
        #entry = {}
        #inserts empty entry and saves it to UserID variable in 'class Application'
        #self.application.UserID = database.insert_one(entry).inserted_id
        #print self.application.UserID
        self.redirect('/prestudy')

class MMDHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        self.application.start_time = str(datetime.datetime.now().time())
        self.render('mmd.html', mmd="30")

    def post(self):
        #refers to database connected to in 'class Application'
        #database = self.application.db.database
        #empty entry to insert into database in order to generate a user id
        #entry = {}
        #inserts empty entry and saves it to UserID variable in 'class Application'
        #self.application.UserID = database.insert_one(entry).inserted_id
        #print self.application.UserID
        self.redirect('/prestudy')

class PreStudyHandler(tornado.web.RequestHandler):
    def get(self):
        #gets time upon entering form
        self.application.start_time = str(datetime.datetime.now().time())
        #display contents of prestudy.html
        self.render("prestudy.html", userid = self.application.UserID)
    def post(self):
        #gets time upon completing form
        self.application.end_time = str(datetime.datetime.now().time())
        #get contents submitted in the form for prestudy
        age = self.get_argument('age')
        gender = self.get_argument('gender')
        occupation = self.get_argument('occupation')
        field = self.get_argument('field')
        simple_bar = self.get_argument('simple_bar')
        complex_bar = self.get_argument('complex_bar')

        #currently that number value is just a dummy user id
        #organizes data to insert into table into a tuple
        prestudy = (7, age, gender, occupation, field, simple_bar, complex_bar, self.application.start_time, self.application.end_time)
        self.application.conn.execute('INSERT INTO prestudy VALUES (?,?,?,?,?,?,?,?,?)', prestudy)
        self.application.conn.commit()

        #####TODO######

        #get database entry with current sessions user id and saves prestudy content
            #database.update({"_id": self.application.UserID}, {'$set': prestudy})
        self.redirect('/locus')

class LocusHandler(tornado.web.RequestHandler):
    def get(self):
        #get time upon entering form
        self.application.start_time = str(datetime.datetime.now().time())
        #displays contents of locus.html
        self.render("locus.html", userid = self.application.UserID)
    def post(self):
        #get time upon leaving form
        self.application.end_time = str(datetime.datetime.now().time())
        #gets content submitted in the form for locus
        q1 = self.get_argument('question1')
        q2 = self.get_argument('question2')
        q3 = self.get_argument('question3')
        q4 = self.get_argument('question4')
        q5 = self.get_argument('question5')
        q6 = self.get_argument('question6')
        q7 = self.get_argument('question7')
        q8 = self.get_argument('question8')
        q9 = self.get_argument('question9')
        q10 = self.get_argument('question10')
        q11 = self.get_argument('question11')
        q12 = self.get_argument('question12')
        q13 = self.get_argument('question13')
        q14 = self.get_argument('question14')
        q15 = self.get_argument('question15')
        q16 = self.get_argument('question16')
        q17 = self.get_argument('question17')
        q18 = self.get_argument('question18')
        q19 = self.get_argument('question19')
        q20 = self.get_argument('question20')
        q21 = self.get_argument('question21')
        q22 = self.get_argument('question22')
        q23 = self.get_argument('question23')
        q24 = self.get_argument('question24')
        q25 = self.get_argument('question25')
        q26 = self.get_argument('question26')
        q27 = self.get_argument('question27')
        q28 = self.get_argument('question28')
        q29 = self.get_argument('question29')
        #time = self.get_argument('elapsed_time')

        #####TODO#####

        #gets database entry with current sessions user id and saves locus content
            #database.update({"_id": self.application.UserID}, {'$set': locus})

        #organizes data to be inserted into table as a tuple
        locus = (2, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10,
                 q11, q12, q13, q14, q15, q16, q17, q18, q19, q20,
                 q21, q22, q23, q24, q25, q26, q27, q28, q29,
                 self.application.start_time, self.application.end_time)
        self.application.conn.execute('INSERT INTO locus VALUES (?,?,?,?,?,?,?,?,?,?,' +
                                                                '?,?,?,?,?,?,?,?,?,?,' +
                                                                '?,?,?,?,?,?,?,?,?,?,?)', locus)
        self.application.conn.commit()

        self.redirect('/mmd')


class FixationHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("fixations.html")
        '''
        eb = TobiiController()
        eb.waitForFindEyeTracker()
        print eb.eyetrackers
        eb.activate(eb.eyetrackers.keys()[0])

        eb.startTracking()
        time.sleep(10)
        eb.stopTracking()

        eb.destroy()
        '''

class EchoWebSocketHandler(tornado.websocket.WebSocketHandler):

    def updateSquare1(self, eb):
        while(1):
            time.sleep(.06)
            #print fixation_detection(eb.leftxarray, eb.leftyarray, eb.timearray, 19.88, 60)
            #print eb.leftxarray;
            #eb.leftxarray = []
            #eb.leftyarray = []
            #eb.timearray = []
        
            self.write_message('{"x":"%d", "y":"%d"}' % (eb.leftx * 1440,eb.lefty * 900))

    def updateSquare(self, x, y):
        self.write_message('{"x":"%d", "y":"%d"}' % (x * 1440,y * 900))
    
    def open(self):
        eb = TobiiController()
        eb.liveWebSocket.add(self)
        print "eb created"
        eb.waitForFindEyeTracker()
        print eb.eyetrackers
        eb.activate(eb.eyetrackers.keys()[0])

        var = 1
        eb.startTracking()
        
        #Returns online fixations and loads them onto a file 
        myOnlineFixations =  eb.onlinefix()
        fl = open('myOnlineFixations.csv', 'w')
        writer = csv.writer(fl)
        writer.writerow(['start_time', 'end_time', 'duration', 'end_x', 'end_Y'])
        for values in myOnlineFixations:
            writer.writerow(values[0])
        fl.close()


        #thread.start_new_thread(eb.onlinefix())
        #thread.start_new_thread(self.updateSquare1(eb))

        #t1 = Thread(target = eb.onlinefix())
        #t2 = Thread(target = self.updateSquare(eb))

        #t2.start()
        #t1.start()
        
        

        
        

        #time.sleep(5)
        #while var == 1:
            #print eb.leftxarray;
        #print fixation_detection(eb.leftxarray, eb.leftyarray, eb.timearray, 19.88, 60)
        
        
        


        
            


        
        
        '''
        var = 1
        x = 0
        y = 0
        while var == 1: 
            #self.write_message(u"Time Stamp: " + str(time.time()))
            if (x < 500 and y == 0): 
                x = x + 1
            if (x == 500 and y < 500):
                y = y + 1
            if (y == 500 and x > 0):
                x = x - 1
            if (y <= 500 and x == 0):
                y = y - 1

            self.write_message('{"x":"%d", "y":"%d"}' % (x,y))
            time.sleep(.01)
            print("in loop")
        '''
        

        '''
        eb = TobiiController()
        print "view works"
        eb.waitForFindEyeTracker()
        print eb.eyetrackers
        eb.activate(eb.eyetrackers.keys()[0])
        eb.startTracking()
        time.sleep(10)
        print "Stop Tracking"
        eb.stopTracking()
        eb.destroy()
        '''
        print("WebSocket opened")


    def on_message(self, message):
        self.write_message(u"Time Stamp: " + str(time.time()))
        print("sending message from server")

    def on_close(self):
        print("WebSocket closed")

        
#main function is first thing to run when application starts
def main():
    tornado.options.parse_command_line()
    #Application() refers to 'class Application'
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()



if __name__ == "__main__":
    main()
