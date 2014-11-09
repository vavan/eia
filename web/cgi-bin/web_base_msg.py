#!/usr/bin/python

import sys, os
import datetime
import logging
from web_base import BaseAdminForm
sys.path.append(os.path.join(os.path.dirname(sys.argv[0]), '../../bin'))
from request import Time


class BaseMsg:
	MSG_ALL = ('*', '$MSG_ALL')
	MSG_ADMIN = ('A', '$MSG_ADMIN')

	
	def decode_id(self, the_id):
		out = ''
		for id, text in (self.MSG_ALL, self.MSG_ADMIN):
			if the_id == id:
				out = text
				break
		else:
			try:
				out = self.client_map[int(the_id)].name
			except:
				out = '$MSG_CLIENT_DELETED'
		return out
	
	def decode_messages(self, messages):
		out_messages = []
		for msgid, data, senderid, recieverid, text, time in messages:
			sender = self.decode_id(senderid)
			reciever = self.decode_id(recieverid)
			out_messages.append( (msgid, data, senderid, sender, reciever, text, time) )
		return out_messages
	
	def show_messages(self, messages, visited):
		t = Time()
		visited = t.create(visited)
		self.odd(0)
		out = ''
		for msgid, data, senderid, sender, reciever, text, time in messages:
			if t.create(time) > visited:
				unread = 'class="selected"'
			else:
				unread = ''
			out += '<tr %s>'%self.odd()
			if self.can_delete(senderid):
				out += '<td class="first"><a href="%s?$session_link&delete=%s">Delete</a></td>'%(self.get_name(), msgid)
			else:
				out += '<td class="first">&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</td>'
			out += '<td %s>%s</td>'%(unread, data[:-9])
			out += '<td %s>%s</td>'%(unread, sender)
			out += '<td %s>%s</td>'%(unread, reciever)
			out += '<td %s>%s</td>'%(unread, text)
			out += '</tr>\n'         
		return out
	
	def show_receivers(self, receivers):
		out = ''
		for k, v in receivers:
			out += '<option value="%s">%s</option>\n'%(k, v)
		return out

	def process(self):
		self.clients = self.db.get_clients()
		self.client_map = dict(map(lambda x: (int(x.id), x), self.clients))

		if 'add' in self.f:
			sender = self.get_sender()
			reciever = self.getvalue("reciever")
			msg = self.getvalue("msg")
			if len(msg.strip()) != 0:
				self.db.add_message(sender, reciever, msg, Time().str())
		elif 'delete' in self.f:
			record_id = self.getvalue("delete", int)
			self.db.delete_message(record_id)

		receivers = self.get_receivers()
		self.r.receivers_list = self.show_receivers(receivers)
		messages = self.get_messages()
		messages = self.decode_messages(messages)
		visited = self.get_visited()
		self.r.msg_list = self.show_messages(messages, visited)
		self.set_visited(Time().str())
		
		f = file("template/base_msg.html")
		html = f.read()
		return html
