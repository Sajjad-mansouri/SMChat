from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core import serializers
from django.shortcuts import aget_object_or_404

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
		print(conversation_id)
		conversation = await aget_object_or_404(Conversation, id=conversation_id)
		condition = await sync_to_async(self.get_message_condition)(conversation)
		if condition:
			await self.create_message(message)
			message = await self.add_extra_value(message)

			group_name = f"chat_{message['conversationId']}"
			await self.channel_layer.group_send(
				group_name,{
				'type':'send.message',
				'message':message
				}
			)

	async def create_message(self, message):
		if message.get("messageType") == "message":
			content=message['message']
			
			conversation = await aget_object_or_404(Conversation, id=self.room_name)
			await Chat.objects.acreate(user=self.user, conversation=conversation, text=content)

	def get_message_condition(self, conversation):
		print(conversation.group_type, conversation.created_by)
		return (conversation.group_type == "channel" and conversation.created_by==self.user) or conversation.group_type in ["group", "direct"]

	async def add_extra_value(self, message):
		#add extra info to messages that user send and send with these extra info to group
		message["sender_id"] = self.user.id
		message["sender_username"] = self.user.username
		message["created_at"] = timestamp = timezone.now().isoformat()

		return message

	async def send_message(self,event):
		# {'type': 'send_message', 'message': {'message': '12'}}
		await self.send(text_data=json.dumps(event['message']))