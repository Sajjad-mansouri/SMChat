from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from chat.models import Conversation, Chat, ConversationMember

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	group_type = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()



	class Meta:
		model = UserModel
		fields = ["id", "username", "conversation_name", "conversation_image", "group_type", "bio",]
	def get_conversation_name(self, obj):
			return obj.username

	def get_conversation_image(self, obj):
			return obj.profile.get_image()

	def get_group_type(self, obj):
		return "direct"

	def get_bio(self, obj):
		return obj.profile.bio

class MessageSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	class Meta:
		model = Chat
		fields = ["id", "user", "text", "created"]

class ConversationSerializer(serializers.ModelSerializer):
	conversation_id = serializers.SerializerMethodField()
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()
	current_user = serializers.SerializerMethodField()


	class Meta:
		model = Conversation
		fields = ["conversation_id", "current_user", "name","conversation_name", "bio", "conversation_image","last_message","created_by", "group_type", "group_chats"]
		read_only_fields = ["conversation_id", "bio","conversation_image", "last_message", "group_chats","created_by"]

	def get_conversation_name(self, obj):

		if obj.group_type == "direct":
			
			obj = self.add_member(obj)
			return [other_user.email for other_user in obj.other_users]

		else:
			return obj.name

	def get_conversation_image(self, obj):
		if obj.group_type == "direct":
			obj = self.add_member(obj)

			return [other_user.profile.get_image() for other_user in obj.other_users]
		else:
			return obj.get_image()

	def add_member(self, obj):
			request = self.context["request"]
			other_members = obj.members.exclude(user=request.user)
			obj.other_users = [other_member.user for other_member in other_members]
			return obj	
	def get_last_message(self, obj):
		if hasattr(obj, 'last_message'):
			return obj.last_message
		return

	def get_conversation_id(self, obj):

			return obj.id

	def get_current_user(self, obj):
		request = self.context["request"]
		return request.user.id

	def to_internal_value(self, data):
		data = data.copy()
		request = self.context["request"]
		data["created_by"] = request.user
		return data

	def create(self, validated_data):

		member_users = [validated_data["created_by"]]
		try:
			user_id = validated_data.pop('member_user')
			if user_id:
				user = get_object_or_404(UserModel, id=user_id)
				member_users.append(user)

		except KeyError:
			pass

		conversation = Conversation.objects.create(**validated_data)
		conversations = []
		for user in member_users:
			conversations.append(ConversationMember(conversation=conversation, user=user))
		ConversationMember.objects.bulk_create(conversations)
		return conversation

class ConversationWithMessageSerializer(serializers.ModelSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)
	current_user = serializers.SerializerMethodField()
	conversation_name = serializers.SerializerMethodField()
	conversation_id = serializers.SerializerMethodField()



	class Meta:
		model = Conversation
		fields = [
		"created_by", "group_type", "bio",
		"group_chats", "name", "current_user", 
		"conversation_id", "conversation_name"]


	def get_current_user(self, obj):
		request = self.context["request"]
		return request.user.id

	def get_conversation_name(self, obj):
		if obj.group_type == "direct":
			if isinstance(obj, UserModel):
				return obj.username
			return obj.member.username
		else:
			return obj.name


	def get_conversation_id(self, obj):
		return obj.id

class ConversationMemberSerializer(serializers.ModelSerializer):
	class Meta:
		model = ConversationMember
		fields = ["conversation", "user", "accepted"]
		read_only_fields = ["accepted"]

	def to_internal_value(self, data):
		data = data.copy()
		request = self.context["request"]
		data["conversation"] = get_object_or_404(Conversation, id=data.pop("conversation"))
		data["user"] = request.user
		return data