from rest_framework import serializers
from django.contrib.auth import get_user_model
from chat.models import Conversation, Chat

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()

	class Meta:
		model = UserModel
		fields = ["id", "username", "conversation_name", "conversation_image"]
	def get_conversation_name(self, obj):
			return obj.username

	def get_conversation_image(self, obj):

			return obj.profile.get_image()

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
		data["created_by"] = request.user.id
		return data


class ConversationWithMessageSerializer(serializers.ModelSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)
	current_user = serializers.SerializerMethodField()
	profile_id = serializers.SerializerMethodField()
	profile_username = serializers.SerializerMethodField()
	profile_full_name = serializers.SerializerMethodField()


	class Meta:
		model = Conversation
		fields = ["id", "created_by", "group_type", "group_chats", "name", "current_user", "profile_id", "profile_username", "profile_full_name"]


	def get_current_user(self, obj):
		request = self.context["request"]
		return request.user.id

	def get_profile_username(self, obj):
		if obj.group_type == "direct":
			return obj.member.username
		else:
			return obj.name

	def get_profile_id(self, obj):
		if obj.group_type == "direct":
			return obj.member.id
		else:
			return obj.name

	def get_profile_full_name(self, obj):
		if obj.group_type == "direct":
			return obj.member.get_full_name()
		else:
			return ""