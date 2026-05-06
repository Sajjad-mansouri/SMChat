from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from chat.models import Conversation, Chat, ConversationMember, BlockList

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	group_type = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()
	blocklist_id = serializers.SerializerMethodField()



	class Meta:
		model = UserModel
		fields = ["id", "username", "conversation_name", "conversation_image", "group_type", "bio", "blocklist_id"]
	def get_conversation_name(self, obj):
			return obj.username

	def get_conversation_image(self, obj):
			return obj.profile.get_image()

	def get_group_type(self, obj):
		return "direct"

	def get_bio(self, obj):
		return obj.profile.bio

	def get_blocklist_id(self, obj):
		request = self.context["request"]
		try:
			return BlockList.objects.get(user=request.user, blocked_user=obj).id
		except BlockList.DoesNotExist:
			return None
class MessageSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	reply_to = serializers.SerializerMethodField()
	class Meta:
		model = Chat
		fields = ["id", "user", "text", "file", "image", "created", "reply_to"]

	def get_reply_to(self,obj):
		if obj.reply_to:
			return {
					"user_username":obj.reply_to.user.username, 
					"id":obj.reply_to.id, 
					"text":obj.reply_to.text,
					"file":obj.reply_to.file if obj.reply_to.file else None,
					"image":obj.reply_to.image if obj.reply_to.image else None,
					"created":obj.reply_to.created
					}
		else:
			return None

class ConversationSerializer(serializers.ModelSerializer):
	conversation_id = serializers.SerializerMethodField()
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	last_message = serializers.SerializerMethodField()
	current_user = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()


	class Meta:
		model = Conversation
		fields = ["conversation_id", "current_user", "name","conversation_name", "bio", "conversation_image","last_message","created_by", "group_type", "group_chats"]
		read_only_fields = ["conversation_id", "bio","conversation_image", "last_message","created_by"]

	def get_conversation_name(self, obj):

		if obj.group_type == "direct":
			
			obj = self.add_member(obj)
			return [other_user.email for other_user in obj.other_users]

		else:
			return obj.name

	def get_conversation_image(self, obj):
		if obj.group_type == "direct":
			obj = self.add_member(obj)

			return [other_user.profile.get_image() for other_user in obj.other_users][0]
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

	def get_bio(self, obj):
		if obj.group_type == "direct":
			obj = self.add_member(obj)

			return [other_user.profile.bio for other_user in obj.other_users][0]
		else:
			return obj.bio

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


class ConversationProfileSerializer(serializers.ModelSerializer):
	current_user = serializers.SerializerMethodField()
	conversation_name = serializers.SerializerMethodField()
	conversation_id = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()
	members = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	blocklist_id = serializers.SerializerMethodField()


	class Meta:
		model = Conversation
		fields = [
		"created_by", "group_type", "bio","members","blocklist_id",
		"name", "conversation_image", "current_user", 
		"conversation_id", "conversation_name"]

	def get_current_user(self, obj):
		request = self.context["request"]
		return request.user.id

	def get_conversation_name(self, obj):
		if obj.group_type == "direct":
			if isinstance(obj, UserModel):
				return obj.username

			other_user = self.get_direct_other_user(obj)
			if other_user:

				return other_user.username
		else:
			return obj.name

	def get_direct_other_user(self, obj):
		request = self.context["request"]

		if obj.members.exclude(user=request.user).exists():
			return obj.members.exclude(user=request.user)[0].user
		else:
			return None


	def get_conversation_id(self, obj):
		return obj.id

	def get_bio(self, obj):
		if obj.group_type == "direct":
			other_user = self.get_direct_other_user(obj)

			return other_user.profile.bio
		else:
			return obj.bio

	def get_members(self, obj):
		return obj.members.count()


	def get_conversation_image(self, obj):
		if obj.group_type == "direct":
			other_user = self.get_direct_other_user(obj)

			return other_user.profile.get_image()
		else:
			return obj.get_image()

	def get_blocklist_id(self, obj):
		request = self.context["request"]
		try:
			return BlockList.objects.get(user=request.user, conversation=obj).id
		except BlockList.DoesNotExist:
			return None

class ConversationWithMessageSerializer(ConversationProfileSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)

	class Meta(ConversationProfileSerializer.Meta):
		model = Conversation
		fields = [
		"created_by", "group_type", "bio","blocklist_id",
		"group_chats", "name", "current_user", 
		"conversation_id", "conversation_name"]

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

class BlockListSerializer(serializers.ModelSerializer):
	class Meta:
		model = BlockList
		fields = ["conversation", "blocked_user"]

	def to_internal_value(self, data):
		data = data.copy()
		request = self.context["request"]
		data["user"] = request.user
		return data


	def create(self, validated_data):

		print(validated_data)
		user = validated_data["user"]
		if "conversation" in validated_data:
			conversation_id = validated_data.pop('conversation')
			conversation = get_object_or_404(Conversation, id=int(conversation_id))
			block_list = BlockList.objects.create(user=user, conversation=conversation)
		elif "blocked_user" in validated_data:
			blocked_user_id = validated_data.pop('blocked_user')
			blocked_user = get_object_or_404(UserModel, id=int(blocked_user_id))
			block_list = BlockList.objects.create(user=user, blocked_user=blocked_user)

		return block_list