import os, logging
from datetime import datetime, time, timedelta
from string import Template
from main import VERSION

class Replace(Template):
	def __init__(self, text):
		Template.__init__(self, text)
		self.text = text
	def __run(self, text, values):
		for k, v in values:
			text = text.replace('$%s'%k, str(v))
			#logging.debug('*** [%s] -- %s'%(k, str(v)))
		return text #self.safe_substitute(values)
	def run(self, *var_map):
		values = {}
		for i in var_map:
			values.update(i.__dict__)
		text = self.text
		values = values.items()
		values.sort( key = lambda x: x[0], reverse = True )
		while(1):
			updated = self.__run(text, values)
			if updated == text:
				break
			text = updated
		return updated
			
		

class Request:

	def create_session_http(self, sessionid):
		return '<input type="hidden" name="session" value="%s">'%sessionid
		
	def create_session_link(self, sessionid):
		return 'session=%s'%sessionid       

	def __init__(self, sessionid):
		self.script = os.environ['SCRIPT_NAME']
		self.session = self.create_session_http(sessionid)
		self.session_link = self.create_session_link(sessionid)
		self.version = VERSION
		

	
class Time:
	def __init__(self):
		self.now = datetime.today()
		self.__fmt = '%Y-%m-%d %H:%M:%S'
		
	def create(self, _time):
		try:
			return datetime.strptime(_time, self.__fmt)
		except:
			return datetime.min
		
	def str(self, _time = None):
		if _time == None:
			_time = datetime.now()
		return _time.strftime(self.__fmt)
		
	def period(self, before):
		if isinstance(before, timedelta):
			start = self.now - before
			end = self.now + timedelta(seconds = 1)
			return self.str(start), self.str(end)
		
		
	def current_day(self):
		start = datetime.combine(self.now, time.min)
		end = datetime.combine(self.now, time.max)
		return start, end
		
	def str_current_day(self):
		start, end = self.current_day()
		return self.str(start), self.str(end)
	
	def month_range(self, year = None, month = None, count = 1):
		start = datetime.combine(self.now, time.min).replace(day = 1)
		if month != None:
			start = start.replace(month = month)
		if year != None:
			start = start.replace(year = year)
		end = start + timedelta(days = count*31)
		end = end.replace(day = 1, hour = 0, minute = 0, second = 0)
		end = end - timedelta(seconds = 1)
		return start, end

	def str_month_range(self, year = None, month = None, count = 1):
		start, end = self.month_range(year, month, count)
		return self.str(start), self.str(end)


if __name__ == "__main__":
	print Time().current_day()
	print Time().month_range()
	print Time().month_range(month = 10)
	print Time().month_range(month = 9, count = 2)
	print Time().month_range(month = 9, count = 6)
	print Time().month_range(year = 2007, month = 9, count = 6)
