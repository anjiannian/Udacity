#!/usr/bin/env python
# encoding: utf-8

"""A simple webapp2 server."""

import webapp2
import re

html = '''
<html>
<head>
    <title> SignUp </title>
    <style type='text/css'>
    body {font:12px/19px Arial, Helvetica, sans-serif; color:#666;}
    input.inputbox{border:#999 1px solid; height:16px; width:120px;}
    label{text-align:right; width:100px; float:left;}
    </style>
</head>
<body>
    <h1 style='color:gray'> SignUp </h1>
<br>
</form>

<form method='post' action='/signup'>
    <p><label>Username:</label>
    <input name='username' class='inputbox' value='%(username)s'>
    <span style='color:red'> %(username_error)s</span>
    </p>
    <p><label>Password:</label>
    <input name='password' type='password' class='inputbox' value='%(password)s'>
    <span style='color:red'> %(password_error)s</span>
    </p>
    <p><label>Verify Password:</label>
    <input name='verify' type='paaswod' class='inputbox' value='%(verify)s'>
    <span style='color:red'> %(verify_error)s</span>
    </p>
    <p><label>Email(Optional):</label>
    <input name='email' class='inputbox' value='%(email)s'>
    <span style='color:red'> %(email_error)s</span>
    </p>
    <input type='submit'>
</form>
<p> Go back to the <a href='/'>MainPage</a></p>
</body>
</html>
'''

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class MainHandler(webapp2.RequestHandler):

    def write_html(self, username='', password='', verify='', email='',
            username_error='', password_error='', verify_error='', email_error=''):
        self.response.write(html % {'username':username,
                                        'password':password,
                                        'verify':verify,
                                        'email':email,
                                        'username_error':username_error,
                                        'password_error':password_error,
                                        'email_error':email_error,
                                        'verify_error':verify_error})

    def valid_username(self, username):
        return USER_RE.match(username)
    def valid_password(self, password):
        return PASSWORD_RE.match(password)
    def valid_email(self, email):
        return EMAIL_RE.match(email)

    def getname(self):
        return self.request.get('username')

    def get(self):
        self.write_html()

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not self.valid_username(username):
            username_error = 'That is not a valid username'
        else:
            username_error = ''

        if not self.valid_password(password):
            password_error = 'That is not a valid password!'
        else:
            password_error = ''

        if verify != password:
            verify_error = 'Your passwords did not match!'
        else:
            verify_error = ''

        if email != '' and self.valid_email(email):
            email_error = ''
        else:
            email_error = 'That is not a valid email!'

        if self.valid_username(username) and self.valid_password(password) and self.valid_email(email) and verify == password:
            self.redirect('/welcome' + '?username=%s' % username)
        else:
            self.write_html(username,password,verify,email,username_error,password_error,verify_error,email_error)


class WelcomeHandler(webapp2.RequestHandler):


    def get(self):
        username = self.request.get('username')
        self.response.out.write('Welcome, %s' % username)
    #    self.response.out.write("Welcom")


application = webapp2.WSGIApplication([('/signup', MainHandler),
                                       ('/welcome', WelcomeHandler)], debug=True)

