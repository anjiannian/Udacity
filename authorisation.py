#!/usr/bin/env python
# encoding: utf-8


import random
import string
import hashlib

Sfile = open('secret')
SECRET = Sfile.readline()
SECRET = SECRET.strip('\n')
Sfile.close()

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

# Implement the function valid_pw() that returns True if a user's password
# matches its hash. You will need to modify make_pw_hash.

def make_pw_hash(name, pw, secret=SECRET, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + SECRET + salt).hexdigest()
    return '%s|%s%s' % (h, salt, secret)

def valid_pw(name, pw, h, secret=SECRET):
    salt = h.split('|')[1]
    return make_pw_hash(name, pw, secret, salt) == h


#h = make_pw_hash('spez', 'hunter2')
#print valid_pw('spez', 'hunter2', h)

