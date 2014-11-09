#!/usr/bin/python


import sys, os, logging, time, re
import SocketServer
import BaseHTTPServer
import CGIHTTPServer
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../cfg'))
import config; config.init_log()

#class HTTPMultiThreadServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
class HTTPMultiThreadServer(BaseHTTPServer.HTTPServer):
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

    def is_executable(self, path):
        #block executing of enithing except python scripts
        return False

    def list_directory(self, path):
        #block directory view
        self.send_error(404, "No permission to list directory")

    def send_head(self):
        if self.is_cgi():
            return self.run_cgi()
        
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                self.send_error(404, "No permission to list directory")
                return StringIO()
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        fs = os.fstat(f.fileno())
        filelength = fs[6]
        
        range = self.headers.getheader("Range")
        logging.debug('1 %s'%range)
        if range:
            self.send_response(206)
            range_m = re.match('bytes=(\d+)-(\d+)?', range)
            logging.debug('2 %s'%range_m)
            if range_m:
                f_start = range_m.group(1)
                f_stop = range_m.group(2)
                if f_stop == None:
                    f_stop = filelength - 1
               
            logging.debug('3 %s %s'%(f_start, f_stop))
            self.send_header("Content-Range", "bytes %s-%s/%s"%(f_start, f_stop, str(filelength)))
            f.seek(int(f_start))
            self.read_length = int(f_stop) - int(f_start)
        else:
            self.send_response(200)
            self.read_length = filelength
            
        self.send_header("Content-type", ctype)
        self.send_header("Content-Length", str(filelength))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.send_header("Accept-Ranges", "bytes")
        
        self.end_headers()
        return f
        

    def copyfile(self, source, outputfile):
        chunk = 16*1024
        logging.error('ge: %s'%xrange(self.read_length / chunk + 1))
        for i in xrange(self.read_length / chunk + 1):
            buf = source.read(chunk)
            if not buf:
                break
            outputfile.write(buf)
        
        
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

    

