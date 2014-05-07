#!/usr/bin/env python
# encoding: utf-8

import webapp2
import cgi

title = '''
<head>
    <title> ROT13 Translator </title>
</head>
'''

form = '''
<p> ROT13 Applicaiton
</p>
<textarea rows='4' cols='50' form='rot13' name='text' autofoucs>
%(txt)s
</textarea>
<br>
<form method='post' action='/rot13' id='rot13'>
    <input type='submit'>
</form>
<p> Go back to the <a href='/'>MainPage</a></p>
'''

class RotHandler(webapp2.RequestHandler):

    def write_form(self, text='Hello, type something here'):
        self.response.out.write(form % {'txt':text})

    def get(self):
        self.response.out.write(title)
        self.write_form()

    def post(self):
        user_text = self.request.get('text')
        rot13 = self.rot13(user_text)
        rot13 = cgi.escape(rot13, quote=None)
        self.write_form(rot13)

    def rot13(self,string):
        new_string = ''
        for char in string:
            if char >= 'a' and char <= 'z':
                new_string += chr(97 + ((ord(char) - 97) + 13)%26)  # 97 is the number of 'a' acsii
            elif char >= 'A' and char <= 'Z':
                new_string += chr(65 + ((ord(char) - 65) + 13)%26)  # 65 is the number of 'A' acsii
            else:
                new_string += char
        return new_string

app = webapp2.WSGIApplication([('/rot13', RotHandler)
                                ], debug=True)


