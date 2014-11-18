#!/usr/bin/env python
import sys, os, re
import datetime
import logging
import cgi
import cgitb; cgitb.enable()
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../cfg'))
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
import config
import sql_db
from session import Session
from text import TextProcessor
from request import Request, Replace, Time


class BaseForm:

    def __init__(self):
        config.init_log()
        self.db = sql_db.DataBase(config.sql)
        self.login = ''
        self.__index = 0


    def is_admin(self):
        return False

    def odd(self, index = None):
        if index != None:
            self.__index = index
        else:
            self.__index += 1
        if self.__index % 2:
            odd_even = 'odd'
        else:
            odd_even = 'even'
        return 'class="%s"'%odd_even

    def escape(self, value):
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            }
        return "".join(html_escape_table.get(c,c) for c in value)

    def unescape(self, value):
        s = value.replace("&lt;", "<")
        s = s.replace("&gt;", ">")
        # this has to be last:
        s = s.replace("&amp;", "&")
        return s

    def getvalue(self, value_name, _type = str):
        value = self.f.getvalue(value_name)
        try:
            value = self.escape(value)
            value = _type(value)
        except:
            value = _type(0)
        return value

    def validate_ip(self, ip, redirect_to):
        ip_re = re.compile(r'(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        m = ip_re.match(ip)
        is_ip_ok = True
        if m != None:
            for i in m.groups():
                if (int(i) > 255):
                    is_ip_ok = False
        else:
            is_ip_ok = False
        if not is_ip_ok:
            msg = '$INCORRECT_IP: %s'%ip
            self.on_fail(msg, redirect_to)
            sys.exit(0)

    def validate_mac(self, mac, redirect_to):
        mac_re = re.compile(r'[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}$')
        if not mac_re.match(mac):
            msg = '$INCORRECT_MAC: %s'%mac
            self.on_fail(msg, redirect_to)
            sys.exit(0)



    def on_fail(self, msg, redirect_to = None):
        f = file("template/err.html")
        html = f.read()
        html = html.replace('$error', msg)
        if redirect_to == None:
            redirect_to = self.get_redirect()
        html = html.replace('$redirect_to', redirect_to)
        html = Replace(html).run(self.r, self.text)
        print "Content-Type: text/html\n\n"
        print html

    def on_success(self):
        html = file(self.get_base_template()).read()

        self.before_process()
        self.r.derived = self.process()

        html = Replace(html).run(self.r, self.text)
        print "Content-Type: text/html\n\n"
        print html

    def run(self):
        self.form = cgi.FieldStorage()
        self.f = self.form
        self.r = Request()
        self.text = TextProcessor().get_language(config.language)

        if self.authorize() != None:
            self.on_success()
        else:
            self.on_fail("Access denied!")
            sys.exit(0)

class BaseClientForm(BaseForm):
    def get_base_template(self):
        return 'template/client_base.html'
    def get_redirect(self):
        return '/index.html'
    def before_process(self):
        self.r.title = 'Internet Gateway. Client'
    def authorize(self):
        return True


class BaseAdminForm(BaseForm):
    def get_base_template(self):
        return 'template/admin_base.html'
    def get_redirect(self):
        return '/admin/index.html'
    def before_process(self):
        self.r.title = 'Internet Gateway. Admin'
    def authorize(self):
        ip = os.environ["REMOTE_ADDR"]
        sessionMan = Session(is_admin = True)
        uid, sessionid = sessionMan.validate(self.db, self.form, ip)
        sessionMan.inject(self.r, sessionid)
        self.login = uid
        return uid != None




class Calendar:

    def __init__(self, form):
        if "year" in form and "month" in form and "month_count" in form:
            self.year = int(form.getvalue("year"))
            self.month = int(form.getvalue("month"))
            self.count = int(form.getvalue("month_count"))
        else:
            self.year = datetime.datetime.today().year
            self.month = datetime.datetime.today().month
            self.count = 1

    def ___show_years(self, year):
        out = ''
        current = datetime.datetime.today().year
        year_list = range(current - 3, current + 4)
        for name in year_list:
            if year == name:
                selected = 'selected'
            else:
                selected = ''
            out += '<option value="%d" %s>%s</option>'%(name, selected, name)
        return out

    def ___show_months(self, month):
        out = ''
        month_list = 'Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split()
        for i, name in enumerate(month_list):
            if month == i+1:
                selected = 'selected'
            else:
                selected = ''
            out += '<option value="%d" %s>%s</option>'%(i+1, selected, name)
        return out

    def select_month(self):
        out = '<select name=year style="font-size:12pt">'
        out += self.___show_years(self.year)
        out += '</select>'
        out += '<select name=month style="font-size:12pt">'
        out += self.___show_months(self.month)
        out += '</select>*'
        out += '<input name=month_count value="%s" size=1 style="font-size:12pt">'%self.count
        out += '<input type="submit" name=month_update value="OK" style="font-size:12pt">'
        return out

    def get_time_range(self):
        return Time().str_month_range(year = self.year, month = self.month, count = self.count)

if __name__ == '__main__':
    print BaseForm().escape('22')
