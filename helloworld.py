import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os.path

import sqlite3
import datetime



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
            (r"/Qurstionnaire", QuestionnaireHandler),

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
        self.render('mmd.html', mmd="3")

        #self.render('MMDIntervention.html', mmd="3")
        #self.render('questionnaire.html', mmd="3")

    def post(self):

        ##### TODO ######

        # 1)generate userid
        # 2)login with old userid

        self.application.end_time = str(datetime.datetime.now().time())
        task_data = (self.application.cur_user, self.application.cur_mmd, self.application.start_time, self.application.end_time,"")
        self.application.conn.execute('INSERT INTO MMD_tasks VALUES (?,?,?,?,?)', task_data)
        self.application.conn.commit()

        self.redirect('/prestudy')

		 
class QuestionnaireHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
        self.application.start_time = str(datetime.datetime.now().time())
        self.render('questionnaire.html', mmd="30")

    def post(self):
        #refers to database connected to in 'class Application'
        #database = self.application.db.database
        #empty entry to insert into database in order to generate a user id
        #entry = {}
        #inserts empty entry and saves it to UserID variable in 'class Application'
        #self.application.UserID = database.insert_one(entry).inserted_id
        #print self.application.UserID
        self.redirect('/prestudy')

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
        self.write("Hello, world")

        
#main function is first thing to run when application starts
def main():
    tornado.options.parse_command_line()
    #Application() refers to 'class Application'
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()



if __name__ == "__main__":
    main()
