from rest_framework import serializers
from django.contrib.auth import get_user_model
from chat.models import Conversation, Chat

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserModel
		fields = ["id", "username"]

class MessageSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	class Meta:
		model = Chat
		fields = ["id", "user", "text", "created"]

class ConversationSerializer(serializers.ModelSerializer):
	

	class Meta:
		model = Conversation
		fields = ["id", "created_by", "group_type", "group_chats"]

	def to_representation(self, instance):
		request = self.context["request"]
		ret = super().to_representation(instance)
		print(ret)
		if instance.group_type == "direct":
			ret["conversation_name"] = [other_user.email for other_user in instance.other_users]
			ret["conversation_image"] = [other_user.profile.get_image() for other_user in instance.other_users]
		else:
			ret["conversation_name"] = instance.name
			ret["conversation_image"] = instance.get_image()

		ret["last_message"] = instance.last_message

		return ret



class ConversationWithMessageSerializer(serializers.ModelSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)

	class Meta:
		model = Conversation
		fields = ["id", "created_by", "group_type", "group_chats"]

	def to_representation(self, instance):
		ret = super().to_representation(instance)
		request = self.context["request"]
		ret["current_user"] = request.user.id
		return ret