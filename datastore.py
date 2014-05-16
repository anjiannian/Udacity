#!/usr/bin/env python
# encoding: utf-8


from google.appengine.ext import db

class Post(db.Model):
    title = db.StringProperty(required = True)
    article = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def as_dict(self):
        time_fmt = '%c'
        d = {
            'subject': self.title,
            'content': self.article,
            'created': self.created.strftime(time_fmt),
            'last_modified': self.last_modified.strftime(time_fmt)
            }
        return d

class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)

