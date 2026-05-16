from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from chat.models import Conversation, Chat, ConversationMember, BlockList
from account.models import Profile

UserModel = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	conversation_name = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	group_type = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()
	blocklist_id = serializers.SerializerMethodField()



	class Meta:
		model = UserModel
		fields = [
		"id", "username", "email", "first_name", "last_name", 
		"conversation_name", "conversation_image", "group_type", 
		"bio", "blocklist_id"
		]
		extra_kwargs = {
			"username" : {"validators":[]},
			"email" : {"validators":[]},

		}
	def get_conversation_name(self, obj):
			if obj.first_name:
				return obj.get_full_name()
			elif obj.username:
				return obj.username
			else:
				return obj.email

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

	def validate_username(self, value):
		user = self.context["request"].user
		if UserModel.objects.exclude(pk=user.pk if user else None).filter(username=value).exists():
			raise serializers.ValidationError("**This username already exists.")

		return value

	def validate_email(self, value):
		user = self.context["request"].user

		if UserModel.objects.exclude(pk=user.pk if user else None).filter(email=value).exists():
			raise serializers.ValidationError("--This username already exists.")

		return value

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
					"file":obj.reply_to.file.url if obj.reply_to.file else None,
					"image":obj.reply_to.image.url if obj.reply_to.image else None,
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
	blocklist_id = serializers.SerializerMethodField()
	

	class Meta:
		model = Conversation
		fields = [
		"conversation_id", "current_user", "image", 
		"created_by" ,"name","conversation_name", "bio", 
		"status", "conversation_image","last_message","created_by", 
		"group_type", "blocklist_id", "join_request"]
		read_only_fields = ["conversation_id","conversation_image", "last_message", "blocklist_id"]

	def get_conversation_name(self, obj):

		if obj.group_type == "direct":
			
			obj = self.add_member(obj)
			for other_user in obj.other_users:
				if other_user.first_name:
					return other_user.get_full_name()
				elif other_user.username:
					return other_user.username
				else:
					return other_user.email


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


	def get_bio(self, obj):
		if obj.group_type == "direct":
			obj = self.add_member(obj)

			return [other_user.profile.bio for other_user in obj.other_users]
		else:
			return obj.bio
			
	def get_direct_other_user(self, obj):
		request = self.context["request"]

		if obj.members.exclude(user=request.user).exists():
			return obj.members.exclude(user=request.user)[0].user
		else:
			return None
	def get_blocklist_id(self, obj):
		request = self.context["request"]
		try:
			other_user = self.get_direct_other_user(obj)

			q = (Q(user=request.user) & Q(conversation=obj))|(Q(user=request.user) & Q(blocked_user=other_user) & Q(conversation=None))
			return BlockList.objects.get(q).id
		except BlockList.DoesNotExist:
			return None

	def to_internal_value(self, data):
		data = data.copy()
		request = self.context["request"]
		data["created_by"] = request.user.id
		data["join_request"] =  True if data.get("join_request") == "true" else False

		return super().to_internal_value(data)

		return validated
	def is_valid(self, *, raise_exception=False):
		boolean = super().is_valid(raise_exception=False)
		
		return boolean
	def create(self, validated_data):
		validated_data["bio"] = self.initial_data.get("bio")
		request = self.context["request"]
		member_users = [validated_data["created_by"]]
		try:
			user_id = self.initial_data.get('member_user')
			if user_id:
				user = get_object_or_404(UserModel, id=user_id)
				member_users.append(user)

		except KeyError:
			pass

		conversation = Conversation.objects.create(**validated_data)
		conversations = []
		for user in member_users:
			c = ConversationMember(conversation=conversation, user=user)
			if user == request.user:
				c = ConversationMember(conversation=conversation, user=user, accepted=True)
			conversations.append(c)
		ConversationMember.objects.bulk_create(conversations)
		return conversation

	def update(self, instance, validated_data):
		instance.bio = self.initial_data.get("bio", instance.bio)

		return super().update(instance, validated_data)

	def validate(self, data):
		if self.instance is None:
			request = self.context["request"]
			member_user = self.initial_data.get("member_user")
			q1 = Q(user_id=data["created_by"]) & Q(blocked_user_id=member_user)
			q2 = Q(user_id=member_user) & Q(blocked_user_id=data["created_by"])
			if BlockList.objects.filter(q1 | q2).exists():
				raise serializers.ValidationError("can not create conversation for users that block each other")
		return data

class ConversationProfileSerializer(serializers.ModelSerializer):
	current_user = serializers.SerializerMethodField()
	conversation_name = serializers.SerializerMethodField()
	username = serializers.SerializerMethodField()

	conversation_id = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()
	members = serializers.SerializerMethodField()
	conversation_image = serializers.SerializerMethodField()
	blocklist_id = serializers.SerializerMethodField()
	current_user_member_id = serializers.SerializerMethodField()

	class Meta:
		model = Conversation
		fields = [
		"created_by", "group_type", "bio","members","blocklist_id",
		"name", "conversation_image", "current_user", 
		"conversation_id", "conversation_name", "current_user_member_id",
		"username"
		]

	def get_current_user(self, obj):
		request = self.context["request"]
		return request.user.id

	def get_conversation_name(self, obj):
		if obj.group_type == "direct":
			other_user = self.get_direct_other_user(obj)
			if other_user:
				if other_user.first_name:
					return other_user.get_full_name()
				elif other_user.username:
					return other_user.username
				else:
					return other_user.email
		else:
			return obj.name

	def get_username(self, obj):
		if obj.group_type == "direct":
			other_user = self.get_direct_other_user(obj)
			if other_user.first_name:
				return other_user.username
			else:
				return ""
		else:
			return ""
	def get_current_user_member_id(self, obj):
		request = self.context["request"]
		if ConversationMember.objects.filter(conversation=obj, user=request.user).exists():
			return ConversationMember.objects.get(conversation=obj, user=request.user).id
		else:
			return ""

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
			other_user = self.get_direct_other_user(obj)
			q = (Q(user=request.user) & Q(conversation=obj))|(Q(user=request.user) & Q(blocked_user=other_user) & Q(conversation=None))
			return BlockList.objects.get(q).id
		except BlockList.DoesNotExist:
			return None

class ConversationWithMessageSerializer(ConversationProfileSerializer):
	group_chats = MessageSerializer(many=True, read_only=True)

	class Meta(ConversationProfileSerializer.Meta):
		model = Conversation
		fields = [
		"created_by", "group_type", "bio","blocklist_id","conversation_image",
		"group_chats", "name", "current_user", 
		"conversation_id", "conversation_name"]

class ConversationMemberSerializer(serializers.ModelSerializer):
	user = UserSerializer(read_only=True)
	conversation_status = serializers.SerializerMethodField()
	class Meta:
		model = ConversationMember
		fields = ["id","conversation", "accepted", "user", "conversation_status"]


	def create(self, validated_data):
		request = self.context["request"]
		validated_data["user"] = request.user
		return super().create(validated_data)

	def get_conversation_status(self, obj):
		return obj.conversation.status


class ConversationSettingSerializer(serializers.ModelSerializer):

	members = ConversationMemberSerializer(many=True)

	class Meta:
		model = Conversation
		fields = ["id","name", "status", "members", "created_by", "join_request", "bio"]


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

		
		user = validated_data["user"]
		if "conversation" in validated_data:
			#add conversation and user in blocklist
			request = self.context["request"]
			conversation_id = validated_data.pop('conversation')
			conversation = get_object_or_404(Conversation, id=int(conversation_id))
			other_user = ConversationMember.objects.filter(conversation=conversation).exclude(user=request.user)[0].user
			block_list = BlockList.objects.create(user=user, conversation=conversation, blocked_user=other_user)
		elif "blocked_user" in validated_data:
			blocked_user_id = validated_data.pop('blocked_user')
			blocked_user = get_object_or_404(UserModel, id=int(blocked_user_id))
			block_list = BlockList.objects.create(user=user, blocked_user=blocked_user)

		return block_list




class AccountProfileSerializer(serializers.ModelSerializer):
	user = UserSerializer()
	class Meta:
		model = Profile
		fields = ["user", "profile_image", "birth_day", "bio"]

	def update(self, instance, validated_data):
		user_data = validated_data.pop("user", None)
		if user_data:
			user = instance.user
			for attr, value in user_data.items():
				setattr(user, attr, value)
			user.save()

		return super().update(instance, validated_data)

