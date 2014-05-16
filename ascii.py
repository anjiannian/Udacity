#!/usr/bin/env python
# encoding: utf-8

import webapp2
import urllib2

from gaeHandler import Handler
from xml.dom import minidom
from time import sleep
from google.appengine.ext import db


GMAPS_URL =  "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
def gmaps_img(points):
  markers = '&'.join('markers=%s,%s' % (p.lat,  p.lon) for p in points)
  return GMAPS_URL + markers

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    position = db.GeoPtProperty()



class AsciiHandler(Handler):

    def get_position(self):
        ip = repr(self.request.remote_addr)
        hostip = 'http://api.hostip.info/?ip=%s' % ip
        page = urllib2.urlopen(hostip).read()
        ele = minidom.parseString(page).getElementsByTagName('gml:coordinates')
        if ele and ele[0].childNodes[0].nodeValue:
            lon, lat =  ele[0].childNodes[0].nodeValue.split(',')
            return db.GeoPt(lat, lon)

    def write_art(self, title='', art='', error=''):
        arts = db.GqlQuery('select * from Art order by created desc')

        img_url = None
        points = filter(None, (a.position for a in arts))
        if points:
            img_url = gmaps_img(points)
        self.render('ascii.html', title=title, art=art, error=error, arts=arts, img_url=img_url)

    def get(self):
       self.write_art()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        position = self.get_position()

        if title and art:
            a = Art(title=title, art=art, position=position)
            a.put()
            sleep(0.1)
            self.redirect('/ascii')
        else:
            error = 'We need both title and art!'
            self.write_art(title, art, error)


app = webapp2.WSGIApplication([
    ('/ascii', AsciiHandler)], debug=True)
