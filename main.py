import webapp2
import jinja2
from google.appengine.api import users
from google.appengine.ext import ndb
import os
import urllib
import logging
import json

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class User(ndb.Model):
	email = ndb.StringProperty(indexed=True)
	first_name = ndb.StringProperty(indexed=True)
	last_name = ndb.StringProperty(indexed=True)
	phone_number = ndb.StringProperty(indexed=True)
	date = ndb.DateTimeProperty(auto_now_add=True)

class Thesis(ndb.Model):
    year = ndb.IntegerProperty(indexed=True)
    title = ndb.StringProperty(indexed=True)
    abstract = ndb.StringProperty(indexed=True)
    adviser = ndb.StringProperty(indexed=True)
    section = ndb.IntegerProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPageHandler(webapp2.RequestHandler):
	 def get(self):
		self.redirect('/login')
		user = users.get_current_user()
		
		login_url = users.create_login_url('/login')
		
		if user:
			logout_url = users.create_logout_url('/login')
			template_values = {
				'logout_url' : logout_url
			}
			
			template = JINJA_ENVIRONMENT.get_template('main.html')
			self.response.write(template.render(template_values))
		
		else:
			template_values = {
				'login_url' : login_url
			}
			template = JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render())
			self.response.write(users.create_login_url(self.request.uri))
			self.response.write(template.render(template_values))
			# url = users.create_logout_url(self.request.uri)
			# url_linktext = 'Logout'

			# template_data = {
				# 'user': user,
				# 'url': url,
				# 'url_linktext': url_linktext
			# }
			# if user:
				# template = JINJA_ENVIRONMENT.get_template('main.html')
				# self.response.write(template.render(template_data))
			# else:
				# self.redirect(users.create_login_url(self.request.uri))

class LoginPageHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			logout_url = users.create_logout_url('/login')
			template_values = {
				'logout_url' : logout_url
			}
			template = JINJA_ENVIRONMENT.get_template('main.html')
			self.response.write(template.render(template_values))
		else:
			login_url = users.create_login_url(self.request.uri)
			template_values = {
				'login_url' : login_url
			}
			template = JINJA_ENVIRONMENT.get_template('login.html')
			self.response.write(template.render(template_values))
		
class RegisterPageHandler(webapp2.RequestHandler):
	def get(self):
		# template = JINJA_ENVIRONMENT.get_template('main.html')
		# self.response.write(template.render(template_values))
		pass
	def post(self):
		logging.info(self.request.get('first_name'))
		logging.info(self.request.get('last_name'))

		loggedin_user = users.get_current_user()
		user = User()
		user.id = loggedin_user.user_id()
		user.email = loggedin_user.email()
		user.first_name = self.request.get('first_name')
		user.last_name = self.request.get('last_name')

		user.put()

		self.redirect('/home')
		
class APIThesisHandler(webapp2.RequestHandler):
    def get(self):
        thesiss = Thesis.query().order(-Thesis.date).fetch()
        thesis_list = []

        for thesis in thesiss:
            thesis_list.append({
                'id': thesis.key.urlsafe(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section
                });
            
        response = {
             'result' : 'OK',
             'data' : thesis_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        thesis = Thesis()
        thesis.year = int(self.request.get('year'))
        thesis.title = self.request.get('title')
        thesis.abstract = self.request.get('abstract')
        thesis.adviser = self.request.get('adviser')
        thesis.section = int(self.request.get('section'))
        thesis.key = thesis.put()
        thesis.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
            'id': thesis.key.urlsafe(),
                'year' : thesis.year,
                'title' : thesis.title,
                'abstract' : thesis.abstract,
                'adviser' : thesis.adviser,
                'section' : thesis.section
        }
        }
        self.response.out.write(json.dumps(response))
		
class APIRegisterHandler(webapp2.RequestHandler):
    def get(self):
        users = User.query().order(-User.date).fetch()
        user_list = []

        for user in users:
            user_list.append({
                'id': user.key.urlsafe(),
                'email' : user.email,
                'first_name' : user.first_name,
                'last_name' : user.last_name
                });
            
        response = {
             'result' : 'OK',
             'data' : user_list
        }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(response))

    def post(self):
        user = User()
        user.first_name = self.request.get('first_name')
        user.last_name = self.request.get('last_name')
        user.key = user.put()
        user.put()

        self.response.headers['Content-Type'] = 'application/json'
        response = {
        'result' : 'OK',
        'data':{
            'id': user.key.urlsafe(),
                'email' : user.email,
                'first_name' : user.first_name,
                'last_name' : user.abstract
        }
        }
        self.response.out.write(json.dumps(response))

app = webapp2.WSGIApplication([
    ('/api/thesis', APIThesisHandler),
    ('/home', MainPageHandler),
    ('/', MainPageHandler),
	('/login', LoginPageHandler),
	('/registerPage', RegisterPageHandler),
	('/api/registerPage', APIRegisterHandler)
], debug=True)