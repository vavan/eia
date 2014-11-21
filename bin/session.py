import logging, sys
import string
import random

class Session:
    CHARS=string.letters+string.digits

    def __init__(self, is_admin = False):
        self.is_admin = is_admin
        self.timeout = 30*60

    
    def generate_sid(self):
        newid = ''.join([ random.choice(Session.CHARS) for i in range(24) ])
        return newid


    def get_form_cred(self, form):
        if (form.has_key("login") and form.has_key("passwd")):
            return (form.getvalue("login"), form.getvalue("passwd"))
        else:
            return (None, None)

    def get_form_sid(self, form):
        if form.has_key("session"):
            return form.getvalue("session")
        else:
            return None
            
    def create_session_http(self, sessionid):
        return '<input type="hidden" name="session" value="%s">'%sessionid
        
    def create_session_link(self, sessionid):
        return 'session=%s'%sessionid       

    def inject(self, r, sessionid):
        r.session = self.create_session_http(sessionid)
        r.session_link = self.create_session_link(sessionid)

    def validate(self, db, form, ip):
        uid = None
        sid = ''
        db.expire_session(self.timeout)
        if (form.has_key("onLogin")):
            login, passwd = self.get_form_cred(form)
            uid = db.authorize_admin(login, passwd, ip)
            if uid:
                sid = self.generate_sid()
                db.insert_session(sid, ip, uid)
            else:
                logging.error( "Can not authorize '%s'-'%s' from %s"%(login, passwd, ip))
        else:
            sid = self.get_form_sid(form)
            uid = db.get_session(sid, ip, self.timeout)
            if uid:
                db.update_sesion(sid)
        return uid, sid

