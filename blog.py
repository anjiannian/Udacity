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

class Post(db.Model):
    title = db.StringProperty(required = True)
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogHandler(Handler):
    def get(self):
        post = db.GqlQuery('select * from Post order by created desc limit 10')
        self.render('blog.html', articles=post)

class PostHandler(Handler):
    def get(self, id):
        post = Post.get_by_id(long(id))
        self.render('blog.html', articles=[post])

class CatalogHandler(Handler):
    def get(self):
        post = db.GqlQuery('select * from Post order by created desc')
        self.render('catalog.html', articles=post)

class NewPostHandler(Handler):

    def write_art(self, subject='', content='', error=''):
        self.render('newpost.html', subject=subject, content=content, error=error)

    def get(self):
        self.write_art()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            a = Post(title = subject, article = content)
            a.put()
            id = a.key().id()
            sleep(0.1)
            self.redirect('/blog/%d' % id, id)
        else:
            error = 'We need both title and article!'
            self.write_art(subject, content, error)


app = webapp2.WSGIApplication([('/blog', BlogHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/catalog', CatalogHandler),
                               (r'/blog/(\d+)', PostHandler)], debug=True)
