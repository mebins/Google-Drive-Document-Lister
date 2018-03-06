#!/usr/bin/env python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Joe Gregorio - Template
import httplib2
import logging
import os
import pickle

from googleapiclient import discovery
from oauth2client import client
from oauth2client.contrib import appengine
from google.appengine.api import memcache

import webapp2
import jinja2


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
http = httplib2.Http(memcache)

decorator = appengine.oauth2decorator_from_clientsecrets(
    CLIENT_SECRETS,
    scope='https://www.googleapis.com/auth/drive.readonly')

class MainHandler(webapp2.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    variables = {
        'url': decorator.authorize_url(),
        'has_credentials': decorator.has_credentials()
        }
    template = JINJA_ENVIRONMENT.get_template('grant.html')
    self.response.write(template.render(variables))


class AboutHandler(webapp2.RequestHandler):

  @decorator.oauth_required
  def get(self):
    try:
      http = decorator.http()
      service = discovery.build("drive", "v2", http=http)
      files = service.files().list(q= 'mimeType = "application/vnd.google-apps.document"', maxResults = 1000000).execute().get('items', [])
      text = "Google Document Files:,"
      for f in files:
          text = text+ f['title']+","

      template = JINJA_ENVIRONMENT.get_template('welcome.html')
      self.response.write(template.render({'text': text }))
    except client.AccessTokenRefreshError:
      self.redirect('/')


app = webapp2.WSGIApplication(
    [
     ('/', MainHandler),
     ('/about', AboutHandler),
     (decorator.callback_path, decorator.callback_handler()),
    ],
debug=True)
