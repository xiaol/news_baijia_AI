__author__ = 'Gavin'

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.httpclient
from para_sim.TextRank4ZH.gist import Gist
import codecs
import json

from tornado.options import define, options
define("port", default=9999, help="run on the given port", type=int)
define("host", default="127.0.0.1", help="run on the given host", type=str)

class GistHandler(tornado.web.RequestHandler):
    def post(self):
        a = Gist().get_gist(codecs.open('/Users/Gavin/work/news_baijia_AI/para_sim/TextRank4ZH/text/01.txt', 'r', 'utf-8').read())
        gist_source = self.get_argument("gist_source", None)
        error = {}
        if not gist_source:
            error["rc"] = 404
            error["msg"] = "need gist_source"
            self.write(json.dumps(error))
            return
        gist_dict = {}
        gist_dict["gist"] = Gist().get_gist(codecs.open(gist_source, 'r', 'utf-8').read())
        gist_dict["gist_source"] = gist_source
        if a:
            gist_dict["error code"] = 0
        else:
            gist_dict["error code"] = 1

        print gist_dict

        self.set_header("Content-Type", "Application/json")
        self.write(json.dumps(gist_dict))



class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r"/news/baijia/gist", GistHandler),
        ]

        settings = {

        }

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":


    # sched = SchedulerAll()
    # sched.start()

    tornado.options.parse_command_line()
    # sockets = tornado.netutil.bind_sockets(options.port)
    # tornado.process.fork_processes(0)
    # server = tornado.httpserver.HTTPServer(Application())
    # server.add_sockets(sockets)
    # tornado.ioloop.IOLoop.instance().start()

    # app = Application()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()