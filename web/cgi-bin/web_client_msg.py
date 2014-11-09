#!/usr/bin/python

import sys, os
import logging
from web_base import BaseClientForm
from web_base_msg import BaseMsg


class Form(BaseClientForm, BaseMsg):

	def get_name(self):
		return os.path.basename(__file__)

	def can_delete(self, sender):
		return str(sender) == str(self.login)

	def get_visited(self):
		return self.db.get_client_time(self.login)

	def set_visited(self, time):
		self.db.set_client_time(self.login, time)

	def get_sender(self):
		return self.login		

	def get_messages(self):
		messages = self.db.get_message_forclient(self.login)
		return messages
	
	def get_receivers(self):
		return [self.MSG_ALL, self.MSG_ADMIN]

Form().run()