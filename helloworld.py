import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import os.path

from pymongo import MongoClient



define("port", default=8888, help="run on the given port", type=int)



class Application(tornado.web.Application):
    def __init__(self):
        #connects url with code 
        handlers = [
            (r"/", MainHandler),
            (r"/locus", LocusHandler),
            (r"/prestudy", PreStudyHandler),
            (r"/mmd", MMDHandler),
        ]
        #connects to database
        client = MongoClient()
        self.db = client.atuav
        #"global variable" to save current UserID of session
        UserID = ''; 
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
        self.render('index.html')
        #self.render('mmd.html', "mmd=3")
        
    def post(self):
        #refers to database connected to in 'class Application'
        database = self.application.db.database
        #empty entry to insert into database in order to generate a user id
        entry = {}
        #inserts empty entry and saves it to UserID variable in 'class Application'
        self.application.UserID = database.insert_one(entry).inserted_id
        print self.application.UserID
        self.redirect('/prestudy')

class MMDHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of index.html
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
        #display contents of prestudy.html
        self.render("prestudy.html")
    def post(self):
        #get contents submitted in the form for prestudy 
        age = self.get_argument('age')
        gender = self.get_argument('gender')
        occupation = self.get_argument('occupation')
        field = self.get_argument('field')
        simple_bar = self.get_argument('simple_bar')
        complex_bar = self.get_argument('complex_bar')
        #organizes prestudy content into JSON format to save to database
        prestudy = {"age": age,
                    "gender": gender,
                    "occupation": occupation,
                    "field": field,
                    "simple_bar": simple_bar,
                    "complex_bar": complex_bar}
        #refers to database connected to in 'class Application'
        database = self.application.db.database
        #gets database entry with current sessions user id and saves prestudy content 
        database.update({"_id": self.application.UserID}, {'$set': prestudy})
        #code to print updated entry for testing 
        entry = database.find_one({"_id": self.application.UserID})
        print entry
        self.redirect('/locus')

class LocusHandler(tornado.web.RequestHandler):
    def get(self):
        #displays contents of locus.html
        self.render("locus.html")
    def post(self):
        #get system time.
        #gets content submitted in the form for locus
        question1 = self.get_argument('question1')
        question2 = self.get_argument('question2')
        question3 = self.get_argument('question3')
        question4 = self.get_argument('question4')
        question5 = self.get_argument('question5')
        question6 = self.get_argument('question6')
        question7 = self.get_argument('question7')
        question8 = self.get_argument('question8')
        question9 = self.get_argument('question9')
        question10 = self.get_argument('question10')
        question11 = self.get_argument('question11')
        question12 = self.get_argument('question12')
        question13 = self.get_argument('question13')
        question14 = self.get_argument('question14')
        question15 = self.get_argument('question15')
        question16 = self.get_argument('question16')
        question17 = self.get_argument('question17')
        question18 = self.get_argument('question18')
        question19 = self.get_argument('question19')
        question20 = self.get_argument('question20')
        question21 = self.get_argument('question21')
        question22 = self.get_argument('question22')
        question23 = self.get_argument('question23')
        question24 = self.get_argument('question24')
        question25 = self.get_argument('question25')
        question26 = self.get_argument('question26')
        question27 = self.get_argument('question27')
        question28 = self.get_argument('question28')
        question29 = self.get_argument('question29')
        #time = self.get_argument('elapsed_time')
        #organizes locus content into JSON format to save to database
        locus = {"question1": question1,
                 "question2": question2,
                 "question3": question3,
                 "question4": question4,
                 "question5": question5,
                 "question6": question6,
                 "question7": question7,
                 "question8": question8,
                 "question9": question9,
                 "question10": question10,
                 "question11": question11,
                 "question12": question12,
                 "question13": question13,
                 "question14": question14,
                 "question15": question15,
                 "question16": question16,
                 "question17": question17,
                 "question18": question18,
                 "question19": question19,
                 "question20": question20,
                 "question21": question21,
                 "question22": question22,
                 "question23": question23,
                 "question24": question24,
                 "question25": question25,
                 "question26": question26,
                 "question27": question27,
                 "question28": question28,
                 "question29": question29,}
        #refers to database connected to in 'class Application'
        database = self.application.db.database
        #gets database entry with current sessions user id and saves locus content 
        database.update({"_id": self.application.UserID}, {'$set': locus})        
        #code to print updated entry for testing 
        
        #entry = database.find_one({"_id": self.application.UserID})
        #print entry
        self.redirect('/mmd')
        

#main function is first thing to run when application starts 
def main():
    tornado.options.parse_command_line()
    #Application() refers to 'class Application'
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
    


if __name__ == "__main__":
    main()

    