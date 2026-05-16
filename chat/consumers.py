from tempfile import SpooledTemporaryFile, TemporaryFile
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core import serializers
from django.core.files.base import File
from django.shortcuts import aget_object_or_404, get_object_or_404

from asgiref.sync import sync_to_async
import json
from .models import Chat, Conversation,BlockList
import time

User=get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):

		self.room_name=self.scope['url_route']['kwargs']['room_name']
		self.group_name=f'chat_{self.room_name}'
		self.user=self.scope['user']
		self.file = None

		self.MAX_SIZE = 50 * 1024 * 1024  # < 50MB
		

		await self.channel_layer.group_add(
			self.group_name,
			self.channel_name)

		await self.accept()

	async def disconnect(self, code):
		await self.channel_layer.group_discard(
			self.group_name,
			self.channel_name		
			)

	async def receive(self, text_data=None, bytes_data=None):
		if text_data:
			condition = True
			message=json.loads(text_data)
			if message.get("messageType") == "cancellation":
				self.cancel_uploading()
			elif message.get("messageType") == "status_notif":
				await self.send_group_message(message)
			else:
				await self.send_message_to_coversation(message)

		elif bytes_data:

			if self.temp_file:
				self.temp_file.write(bytes_data)

				self.total_bytes_received += len(bytes_data)

				current_progress = (self.total_bytes_received/self.file_size) * 100
				await self.channel_layer.group_send(
					self.group_name,{
					'type':'send.message',
					'message':{"progress":True, "received":self.total_bytes_received, "file_size":self.file_size, "percentage":current_progress}
					}
				)

	async def send_message_to_coversation(self, message):
				conversation_id = message['conversationId']
				conversation = await aget_object_or_404(Conversation, id=conversation_id)
				condition = await sync_to_async(self.get_message_condition)(conversation)

				if condition:
					message, msg_obj = await self.create_message(message)

					message = await self.add_extra_value(message, msg_obj)

					await self.send_group_message(message)
	async def send_group_message(self, message):
			message["sender_id"] = self.user.id
			message["sender_username"] = self.user.username

			self.group_name = f"chat_{message['conversationId']}"
			await self.channel_layer.group_send(
				self.group_name,{
				'type':'send.message',
				'message':message
				}
			)
	async def create_message(self, message):
		self.reply_to = None
		msg_obj = None
		if message.get("messageType") == "message":
			msg_obj = await self.create_message_object(message)
		elif message.get("messageType") == "file":
			file_position = message.get("position")
			if file_position == "start":
				self.total_bytes_received = 0
				self.file_size = 0
				self.last_progress_sent = 0
				self.file_name = message["name"]
				self.file_size = message["size"]
				if self.file_size < self.MAX_SIZE:  # < 50MB
					self.temp_file = SpooledTemporaryFile(max_size=self.file_size )
				else:
					self.temp_file = TemporaryFile()
				message["progress"] = True

			elif file_position == "end":
				if self.temp_file:

					self.temp_file.seek(0)
					django_file = File(self.temp_file, self.file_name)
					if message["content_type"]=="image/png":
						msg_obj = await self.create_message_object(message, image=django_file, file=None)
					else:
						msg_obj = await self.create_message_object(message, image=None, file=django_file)

					self.temp_file.close()
					self.temp_file = None

		return message, msg_obj

	def cancel_uploading(self):
		if self.temp_file and not self.temp_file.closed:
			self.temp_file.close()
			self.temp_file = None

	async def create_message_object(self, message, image=None, file=None):
			content=message['message']
			self.reply_to = message.get("replyTo")

			conversation = await aget_object_or_404(Conversation, id=self.room_name)
			if self.reply_to:
				self.reply_to_obj = await sync_to_async(self.get_reply_to)(int(self.reply_to))

				return await Chat.objects.acreate(
					user=self.user, 
					conversation=conversation, 
					text=content, 
					image=image,
					file=file,
					reply_to=self.reply_to_obj)
			else:

				return await Chat.objects.acreate(
					user=self.user, 
					conversation=conversation, 
					text=content,
					image=image,
					file=file,
					)



	def get_message_condition(self, conversation):
		q = (conversation.group_type == "channel" and conversation.created_by==self.user) or conversation.group_type in ["group", "direct"]
		if conversation.group_type == "direct":
			user1,user2 = self.get_conversation_users(conversation)

			is_conversation_blocked = not conversation.blocklist_set.exists()
			q_users = (Q(user_id=user1) & Q(blocked_user_id=user2))|(Q(user_id=user2) & Q(blocked_user_id=user1))
			are_users_blocked = not BlockList.objects.filter(q_users).exists()
			

			q = is_conversation_blocked and are_users_blocked and q
		return q

	def get_conversation_users(self, conversation):
		return conversation.members.values_list("user", flat=True)
	async def add_extra_value(self, message, msg_obj):

		if self.reply_to:
			message = await sync_to_async(self.add_reply)(message)

		#add extra info to messages that user send and send with these extra info to group
		if msg_obj:
			message["msg_id"] = msg_obj.id
			message["image"] = msg_obj.image.url if msg_obj.image else None

			message["file"] = msg_obj.file.url if msg_obj.file else None


		message["created_at"] = timestamp = timezone.now().isoformat()

		return message

	def add_reply(self, message):
			message["reply_to"] = {"user_username":self.reply_to_obj.user.username, "text":self.reply_to_obj.text}
			return message

	def get_reply_to(self, reply_to):
		chat = get_object_or_404(Chat, id=reply_to)
		return chat

	async def send_message(self,event):
		# {'type': 'send_message', 'message': {'message': '12'}}
		await self.send(text_data=json.dumps(event['message']))