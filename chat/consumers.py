from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core import serializers

from asgiref.sync import sync_to_async
import json

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

		message["user_id"] = self.user.id
		message["username"] = self.user.username

		message["created_at"] = timestamp = timezone.now().isoformat()
		date_str=message['timestamp']
		content=message['message']
		# receiver=message['receiver']

		

		await self.channel_layer.group_send(
			self.group_name,{
			'type':'send.message',
			'message':message
			}
		)

	async def send_message(self,event):
		# {'type': 'send_message', 'message': {'message': '12'}}
		await self.send(text_data=json.dumps(event['message']))