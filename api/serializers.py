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
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()

	class Meta:
		model = Conversation
		fields = ["id", "name","conversation_name", "conversation_image","last_message","created_by", "group_type", "group_chats"]
		read_only_fields = ["id", "conversation_image", "last_message", "group_chats","created_by"]

	def get_conversation_name(self, obj):
		if obj.group_type == "direct":
			return [other_user.email for other_user in obj.other_users]
		else:
			return obj.name

	def get_conversation_image(self, obj):
		if obj.group_type == "direct":
			return [other_user.profile.get_image() for other_user in obj.other_users]
		else:
			return obj.get_image()

	def get_last_message(self, obj):
		if hasattr(obj, 'last_message'):
			return obj.last_message
		return

	def to_internal_value(self, data):
		request = self.context["request"]
		data = data.copy()
		data["created_by"] = request.user
		return data


class ConversationWithMessageSerializer(serializers.ModelSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)

	class Meta:
		model = Conversation
		fields = ["id", "created_by", "group_type", "group_chats"]

	def to_representation(self, instance):
		ret = super().to_representation(instance)
		request = self.context["request"]
		ret["current_user"] = request.user.id
		ret["profile_id"] = instance.member.id
		ret["profile_username"] = instance.member.username
		ret["profile_full_name"] = instance.member.get_full_name()


		return ret