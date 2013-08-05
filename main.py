import os
import urllib
import time
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions = ['jinja2.ext.autoescape'])

READERLIST_NAME = 'reader_list'

def readerlist_key(readerlist_name = READERLIST_NAME):
    return ndb.Key('ReaderList', readerlist_name)

# Data Structure to contain a reader's information
class Reader(ndb.Model):
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()
    email = ndb.StringProperty()
    dob = ndb.DateProperty()
    phone = ndb.StringProperty()
    loc = ndb.GeoPtProperty()

class SignUp(webapp2.RequestHandler):

    # Serves the sign up page
    def get(self):
        template_values = {
        }
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    # Helper function used to determine if location data was sent
    def is_number(self, s):
        try:
            float(s)
        except ValueError:
            return False
        return True

    # Inserts Reader entity into data table then redirects
    # to the thank you page
    def post(self):
        reader = Reader(parent = readerlist_key(READERLIST_NAME))
        reader.fname = self.request.get('fname')
        reader.lname = self.request.get('lname')
        reader.email = self.request.get('email')
        dt = time.strptime(self.request.get('dob'), "%Y-%m-%d")
        reader.dob = datetime.date(dt.tm_year, dt.tm_mon, dt.tm_mday)
        reader.phone = self.request.get('phone')
        if self.is_number(self.request.get('lat')):
            reader.loc = ndb.GeoPt(self.request.get('lat'), self.request.get('lon'))

        reader.put()
        
        self.redirect('/thanks')

class Thanks(webapp2.RequestHandler):

    # Serves the thank you page
    def get(self):
        template_values = {
        }
        
        template = JINJA_ENVIRONMENT.get_template('thanks.html')
        self.response.write(template.render(template_values))

class Action(webapp2.RequestHandler):

    # Retrieves requested Readers for batch operations
    # and serves the action choice page
    def post(self):
        ids = self.request.get('reader', allow_multiple=True)
        readers = []
        for i in ids:
            readers.append(ndb.Key(urlsafe=i).get())
        
        email = ""
        for r in readers:
            email += r.email + ', '

        template_values = {
            'emails': email,
            'readers': readers,
        }
        
        template = JINJA_ENVIRONMENT.get_template('action.html')
        self.response.write(template.render(template_values))

class Admin(webapp2.RequestHandler):

    # Retrieves all Reader data from data table and
    # serves the admin page
    def get(self):
        readers_query = Reader.query(
            ancestor = readerlist_key(READERLIST_NAME))
        readers = readers_query.fetch()

        template_values = {
            'readers': readers
        }
        
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

class Map(webapp2.RequestHandler):

    # Retrieves all Reader location data from data table
    # and displays each as a marker on Google Maps
    # serves the map page
    def get(self):
        readers_query = Reader.query(
            ancestor = readerlist_key(READERLIST_NAME))
        readers = readers_query.fetch()

        template_values = {
            'readers': readers
        }
        
        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(template_values))

    # Retrieves requested Reader location data from data table
    # and displays each as a marker on Google Maps
    # serves the map page
    def post(self):
        ids = self.request.get('reader', allow_multiple=True)
        readers = []
        for i in ids:
            readers.append(ndb.Key(urlsafe=i).get())

        template_values = {
            'readers': readers
        }
        
        template = JINJA_ENVIRONMENT.get_template('map.html')
        self.response.write(template.render(template_values))
        
# Defines application and paths
application = webapp2.WSGIApplication([
    ('/', SignUp),
    ('/thanks', Thanks),
    ('/action', Action),
    ('/admin', Admin),
    ('/map', Map),
], debug=True)
