from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core import serializers
from django.shortcuts import aget_object_or_404, get_object_or_404

from asgiref.sync import sync_to_async
import json
from .models import Chat, Conversation

User=get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
	async def connect(self):

		self.room_name=self.scope['url_route']['kwargs']['room_name']
		self.group_name=f'chat_{self.room_name}'
		self.user=self.scope['user']

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
		message=json.loads(text_data)

		conversation_id = message['conversationId']

		conversation = await aget_object_or_404(Conversation, id=conversation_id)
		condition = await sync_to_async(self.get_message_condition)(conversation)
		if condition:
			msg_obj = await self.create_message(message)

			message = await self.add_extra_value(message, msg_obj)

			group_name = f"chat_{message['conversationId']}"

			print("group name ",group_name)
			await self.channel_layer.group_send(
				group_name,{
				'type':'send.message',
				'message':message
				}
			)

	async def create_message(self, message):
		self.reply_to = None
		if message.get("messageType") == "message":
			content=message['message']
			self.reply_to = message.get("replyTo")

			conversation = await aget_object_or_404(Conversation, id=self.room_name)
			if self.reply_to:
				self.reply_to_obj = await sync_to_async(self.get_reply_to)(int(self.reply_to))
				return await Chat.objects.acreate(user=self.user, conversation=conversation, text=content, reply_to=self.reply_to_obj)
			else:
				return await Chat.objects.acreate(user=self.user, conversation=conversation, text=content)

	def get_message_condition(self, conversation):

		return (conversation.group_type == "channel" and conversation.created_by==self.user) or conversation.group_type in ["group", "direct"]

	async def add_extra_value(self, message, msg_obj):

		if self.reply_to:
			message = await sync_to_async(self.add_reply)(message)

		#add extra info to messages that user send and send with these extra info to group
		if msg_obj:
			message["msg_id"] = msg_obj.id
		message["sender_id"] = self.user.id
		message["sender_username"] = self.user.username
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