import time

import os

import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.escape
from pymongo import MongoClient
import string, random
from smtplib import SMTP

from tornado.options import define, options
from tornado.web import RequestHandler

from havenondemand.hodclient import *

client = HODClient("e7edaa72-d0b8-4335-89bc-1b07696dbb17", version="v2")


class TopHandler(RequestHandler):
    def get(self):
        pass


class ArticleHandler(RequestHandler):
    def post(self):
        request_body = dict(tornado.escape.json_decode(self.request.body))
        url = request_body['url']
        sentiment = client.get_request({'url': url}, HODApps.ANALYZE_SENTIMENT, async=False)
        if sentiment['aggregate']['sentiment'] == "positive":
            print(sentiment['aggregate']['score'])


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/top.json", TopHandler),
            (r"/article", ArticleHandler)
        ],
    )
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()
