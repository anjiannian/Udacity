#!/usr/bin/env python
# encoding: utf-8

"""A simple webapp2 server."""

import webapp2
import re
import jinja2
import os
import authorisation as au

from time import sleep
from google.appengine.ext import db

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

template_dir = os.path.join(os.path.dirname(__file__),'templates')
env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        return self.response.write(*a, **kw)

    def render_str(self, template, **params):
            t = env.get_template(template)
            return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

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
            self.redirect('/welcome')
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
                    self.redirect('/welcome')
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
                self.redirect('/welcome')
            else:
                self.params['error'] = 'Invalid Login!'
                self.render('login.html', **self.params)



class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        username = self.request.cookies.get('user')
        if not username:
            self.redirect('/signup')
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
        self.redirect('/signup')

application = webapp2.WSGIApplication([('/signup', SignUpHandler),
                                       ('/welcome', WelcomeHandler),
                                       ('/login', LogInHandler),
                                       ('/logout', LogOutHandler)], debug=True)

