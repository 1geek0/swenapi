import time

import os

import json

import tornado.httpserver
import pycurl
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
import json

define('last', 0, type=int)

client = HODClient("e7edaa72-d0b8-4335-89bc-1b07696dbb17", version="v2")

try:
    # python 3
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode


class TopHandler(RequestHandler):
    def get(self):
        self.write({[1, 2, 3, 4, 5]})


class ArticleHandler(RequestHandler):
    def get(self, ref):
        query = client.get_request({'text': 'story', 'indexes': 'swendex'}, HODApps.QUERY_TEXT_INDEX, async=False)[
            'documents']
        return_dict = {
            "title": query[int(ref)]['title'],
            "type": "story"
        }
        self.write(return_dict)

    def post(self):
        request_body = dict(tornado.escape.json_decode(self.request.body))
        url = request_body['url']
        req_title = request_body['title']
        sentiment = client.get_request({'url': url}, HODApps.ANALYZE_SENTIMENT, async=False)
        if sentiment['aggregate']['sentiment'] == "positive":
            c = pycurl.Curl()
            c.setopt(c.URL, 'https://api.havenondemand.com/1/api/sync/addtotextindex/v1')
            item_dict = {
                "apikey": "e7edaa72-d0b8-4335-89bc-1b07696dbb17",
                "url": url,
                "index": "swendex",
                "additional_metadata": {
                    "title": req_title,
                    "type": 'story',
                    "reference": options.last + 1,
                    "sentiment_score": sentiment['aggregate']['score']
                }
            }
            apikey = {

            }
            print(item_dict)
            # postFields = urlencode(json.dumps(item_dict))
            c.setopt(c.POSTFIELDS, json.dumps(item_dict))
            c.setopt(c.POSTFIELDS, json.dumps(apikey))
            c.perform()
            c.close()


def onResponse(response, error, **kwargs):
    print(response)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=[
            (r"/top.json", TopHandler),
            (r"/article/([0-9]+)", ArticleHandler)
        ],
    )
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(80)
    tornado.ioloop.IOLoop.instance().start()
