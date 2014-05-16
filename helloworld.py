#!/usr/bin/env python
# encoding: utf-8

"""A simple webapp2 server."""

import webapp2

class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        ip = self.request.remote_addr
        self.response.write('Hello, World! %s' % ip)


application = webapp2.WSGIApplication([
    ('/hello', MainPage),
], debug=True)

