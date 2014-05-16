#!/usr/bin/env python
# encoding: utf-8

import re
import time
import webapp2
import authorisation as au

from time import sleep
from gaeHandler import Handler
from datastore import User, Post
from google.appengine.api import memcache

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


st = {}

class BlogHandler(Handler):
    def get(self):
        post, btime = self.get_key('blog')
        if self.format == 'html':
            if btime:
                st['t'] = btime
            oldtime = time.time() - st['t']
            self.render('blog.html', articles=post, ttime=int(oldtime))
        else:
            self.render_json([p.as_dict() for p in post])

class PostHandler(Handler):
    def get(self, id):
        post, ptime = self.get_key(str(id))
        if not post:
            self.error(404)
            return
        elif self.format == 'json':
            self.render_json(post.as_dict())
        elif ptime:
            st['p'] = ptime
        oldtime = time.time() - st['p']
        self.render('blog.html', articles=[post], ttime=int(oldtime))

class CatalogHandler(Handler):
    def get(self):
        post, catime = self.get_key('catalog')
        if catime:
            st['c'] = catime
        ttime = time.time() - st['c']
        self.render('catalog.html', articles=post, ttime=int(ttime))

class NewPostHandler(Handler):

    def write_art(self, subject='', content='', error=''):
        self.render('newpost.html', subject=subject, content=content, error=error)

    def get(self):
        #self.request.
        self.write_art()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            a = Post(title = subject, article = content)
            a.put()
            id = a.key().id()
            sleep(0.1)
            memcache.set(str(id), a)
            st['p'] = time.time()
            self.redirect('/blog/%d' % id, id)
        else:
            error = 'We need both title and article!'
            self.write_art(subject, content, error)

class SignUpHandler(Handler):
    params = dict(username =  '',
                  password =  '',
                  verify =  '',
                  email =  '',
                  username_error =  '',
                  password_error =  '',
                  email_error =  '',
                  verify_error =  '')

    def valid_username(self, username):
        return USER_RE.match(username)
    def valid_password(self, password):
        return PASSWORD_RE.match(password)
    def valid_email(self, email):
        if email == '' or EMAIL_RE.match(email):
            return True
        else:
            return False

    def get(self):
        self.render('signup.html', **self.params)

    def post(self):
        username = self.request.get('username')
        self.params['username'] = username
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        self.params['email'] = email
        user = User.all()
        user.filter('username =', username)
        invalid_user = False
        for q in user:
            if q.username:
                invalid_user = True
            else:
                invalid_user = False


        if not self.valid_username(username):
            self.params['username_error'] = 'That is not a valid username'
        elif invalid_user:
            self.params['username_error'] = 'This name has been taken'
        else:
            self.params['username_error'] = ''

        if self.valid_password(password):
            self.params['password_error'] = ''
        else:
            self.params['password_error'] = 'That is not a valid password!'

        if verify == password:
            self.params['verify_error'] = ''
        else:
            self.params['verify_error'] = 'Your passwords did not match!'

        if self.valid_email(email):
            self.params['email_error'] = ''
        else:
            self.params['email_error'] = 'That is not a valid email!'

        if not invalid_user and self.valid_username(username) \
            and self.valid_password(password) and self.valid_email(email) \
            and verify == password:

            pwhash = au.make_pw_hash(username, password)
            new = User(username=username, password=pwhash, email=email)
            new.put()
            self.response.headers.add_header('Set-Cookie', 'user=%s; Path=/' % str(username))
            self.response.headers.add_header('Set-Cookie', 'pw=%s; Path=/' % str(pwhash))
            sleep(0.5)
            self.redirect('/blog/welcome')
        else:
            self.render('signup.html', **self.params)

class LogInHandler(Handler):
    params = dict(username =  '',
                  password =  '',
                  error = '')
    def get(self):
        username = self.request.cookies.get('user')
        if not username:
            self.render('login.html', **self.params)
        else:
            password = self.request.cookies.get('pw')

            user = User.all()
            user.filter('username =', username)
            for u in user:
                if password == u.password:
                    self.redirect('/blog/welcome')
                else:
                    self.params['error'] = '逗逼再见!'
                    self.render('login.html', **self.params)

    def post(self):
        username = self.request.get('username')
        self.params['username'] = username
        password = self.request.get('password')
        user = User.all()
        user.filter('username =', username)
        for u in user:
            if au.valid_pw(username, password, u.password):
                self.response.headers.add_header('Set-Cookie', 'user=%s; Path=/' % str(username))
                self.response.headers.add_header('Set-Cookie', 'pw=%s; Path=/' % str(u.password))
                sleep(0.5)
                self.redirect('/blog/welcome')
            else:
                self.params['error'] = 'Invalid Login!'
                self.render('login.html', **self.params)

class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.cookies.get('user')
        if not username:
            self.redirect('/blog/signup')
        else:
            password = self.request.cookies.get('pw')

            user = User.all()
            user.filter('username =', username)
            for u in user:
                if password == u.password:
                    self.response.out.write('Welcome, %s' % username)
                else:
                    self.response.write('逗逼再见!')

class LogOutHandler(Handler):
    def get(self):
        self.response.delete_cookie('user')
        self.redirect('/blog/signup')

class Flush(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect('/blog')

app = webapp2.WSGIApplication([('/blog/signup', SignUpHandler),
                               ('/blog/login', LogInHandler),
                               ('/blog/welcome', WelcomeHandler),
                               ('/blog/logout', LogOutHandler),
                               ('/blog/newpost', NewPostHandler),
                               ('/blog/catalog', CatalogHandler),
                               ('/blog/flush', Flush),
                               (r'/blog/(\d+)(?:.json)?', PostHandler),
                               (r'/blog/?(?:.json)?', BlogHandler)], debug=True)
