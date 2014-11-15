#!/usr/bin/python


import sys, os, logging, time, re
import SocketServer
import BaseHTTPServer
import CGIHTTPServer
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config; config.init_log()

class HTTPMultiThreadServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

class HTTPRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):

    web_user = None

    @staticmethod
    def web_user_id():
        if HTTPRequestHandler.web_user:
            return HTTPRequestHandler.web_user
        try:
            import pwd
            HTTPRequestHandler.web_user = pwd.getpwnam(config.web_user)[2]
        except ImportError, KeyError:
            HTTPRequestHandler.web_user = -1
        return HTTPRequestHandler.web_user

    def log_error(self, *args):
        msg = args[0]%args[1:]
        logging.error("HTTP: %s - %s"%(self.address_string(), msg))

    def log_message(self, format, *args):
        msg = format%args
        logging.info("HTTP: %s - %s"%(self.address_string(), msg))

CGIHTTPServer.nobody_uid = HTTPRequestHandler.web_user_id


def serve_forever():
    while(1):
        httpd = None
        try:
            logging.info( '*** Start http_serv ***' )
            server_address = (config.web_address, config.web_port)
            httpd = HTTPMultiThreadServer(server_address, HTTPRequestHandler)
            httpd.serve_forever()
        except Exception, e:
            logging.error( 'Unhandled exception in http_serv: %s'%str(e) )
            if httpd != None:
                del httpd
            time.sleep(30)


def run_deamon():
    pid = os.fork()
    if pid != 0:
        ' Parent '
        return
    else:
        ' Child '
        sys.stdin.close()
        sys.stdout.close()
        sys.stderr.close()

        serve_forever()



def run_sync():
    serve_forever()


if len(sys.argv) > 1 and sys.argv[1] == 'sync':
    run_sync()
else:
    run_deamon()



