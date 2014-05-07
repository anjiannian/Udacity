#!/usr/bin/env python
# encoding: utf-8

import os
import webapp2
import jinja2

from time import sleep
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t = jinja2_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class AsciiHandler(Handler):

    def write_art(self, title='', art='', error=''):
        arts = db.GqlQuery('select * from Art order by created desc')
        self.render('ascii.html', title=title, art=art, error=error, arts=arts)

    def get(self):
        self.write_art()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')

        if title and art:
            a = Art(title = title, art = art)
            a.put()
            sleep(1)
            self.redirect('/ascii')
        else:
            error = 'We need both title and art!'
            self.write_art(title, art, error)


app = webapp2.WSGIApplication([('/ascii', AsciiHandler)], debug=True)
