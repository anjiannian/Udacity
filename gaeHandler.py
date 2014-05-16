#!/usr/bin/env python
# encoding: utf-8

import os
import json
import time
import jinja2
import logging

from datastore import Post
from webapp2 import RequestHandler
from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja2_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.response.write(json_txt)

    def initialize(self, *a, **kw):
        RequestHandler.initialize(self, *a, **kw)
        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

    def get_key(self, label):
        data = memcache.get(label)
        if data:
            return data, None
        elif label == 'catalog':
            data = db.GqlQuery('select * from Post order by created desc')
            logging.info('*** Query Query Query ***')
            memcache.set(label, data)
            return data, time.time()
        elif label == 'blog':
            data = db.GqlQuery('select * from Post order by created desc limit 10')
            logging.info('*** Query Query Query ***')
            memcache.set(label, data)
            return data, time.time()
        else:
            data = Post.get_by_id(int(label))
            logging.info('*** Query Query Query ***')
            memcache.set(str(label), data)
            return data, time.time()
