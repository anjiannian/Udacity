#!/usr/bin/env python
# encoding: utf-8

import time
import logging

from blog import Post
from google.appengine.ext import db
from google.appengine.api import memcache

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
        data = Post.get_by_id(long(id))
        logging.info('*** Query Query Query ***')
        memcache.set(label, data)
        return data, time.time()
