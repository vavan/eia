#!/usr/bin/python

import sys, os
import logging
from web_base import BaseAdminForm
from web_base_msg import BaseMsg


class Form(BaseAdminForm, BaseMsg):

	def get_name(self):
		return os.path.basename(__file__)
		
	def can_delete(self, sender):
		return True
		
	def get_visited(self):
		return self.db.get_admin_time(self.login)

	def set_visited(self, time):
		self.db.set_admin_time(self.login, time)

	def get_sender(self):
		return self.MSG_ADMIN[0]
		
	def get_messages(self):
		messages = self.db.get_all_messages()
		return messages
	
	def get_receivers(self):
		clients = map(lambda x: (x.id, x.name), self.clients)
		clients.sort(key = lambda x : x[0])
		return [self.MSG_ALL, self.MSG_ADMIN] + clients

Form().run()