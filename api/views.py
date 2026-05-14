from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Value
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import FormParser, MultiPartParser
from . import serializers
from chat.models import Conversation, ConversationMember, Chat, BlockList
from account.models import Profile
from .permissions import IsMember, IsConversationOwner


UserModel = get_user_model()
class Conversations(ListAPIView):
	serializer_class = serializers.ConversationSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		conversation_type = self.kwargs.get("conversation_type")
		q_user = Q(group_type="direct")
		q_group_channel = (~Q(group_type="direct") & Q(members__accepted=True) & Q(status="private")) | Q(status="public")
		q_general = Q(members__user=self.request.user) 
		g_total = ((q_user & q_general) | (q_group_channel & q_general) | Q(created_by=self.request.user))& Q(group_type=conversation_type)

		qs = Conversation.objects.filter(g_total).distinct().prefetch_related("members__user")
		for conversation in qs:
			# conversation.last_message = conversation.chats.first()
			if Chat.objects.filter(conversation=conversation).exists():
				conversation.last_message = Chat.objects.filter(conversation=conversation).last().text
			else:
				conversation.last_message = ""

		return qs


class ConversationDetail(RetrieveAPIView):
	serializer_class = serializers.ConversationWithMessageSerializer
	permission_classes = [IsAuthenticated, IsMember]
	def get_queryset(self):
		self.conversation_id = self.kwargs.get("conversation_id")
		self.user_id = self.kwargs.get("user_id")
		self.conversation_type = self.kwargs.get("conversation_type")


		if self.conversation_type == "direct" and self.user_id:
				self.lookup_url_kwarg = "user_id"
				return UserModel.objects.all()
		else:
			self.lookup_url_kwarg = "conversation_id"
			return Conversation.objects.all()



	def get_object(self):
		self.obj = super().get_object()

		if self.conversation_type == "direct":
			if self.conversation_id:
				members = self.obj.members.exclude(user=self.request.user).distinct()
				self.obj.member = members[0].user

		return self.obj

	def get_serializer_class(self):
		if isinstance(self.obj, UserModel):
			return serializers.UserSerializer
		else:
			return serializers.ConversationWithMessageSerializer

class ConversationProfile(ConversationDetail):
	def get_serializer_class(self):
		if isinstance(self.obj, UserModel):
			return serializers.UserSerializer
		else:
			return serializers.ConversationProfileSerializer	

class ConversationCreateView(CreateAPIView):
	serializer_class = serializers.ConversationSerializer
	permission_classes = [IsAuthenticated]

class ConversationSettingView(RetrieveAPIView):
	serializer_class = serializers.ConversationSettingSerializer
	permission_classes = [IsAuthenticated, IsConversationOwner]
	def get_queryset(self):
		return Conversation.objects.filter(group_type__in=["group", "channel"])

class SearchView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		user_qs, conversation_qs = self.get_queryset()
		conversation_serializer, user_serializer = self.get_serializer(user_qs, conversation_qs)
		return Response({"users":user_serializer.data, "conversations":conversation_serializer.data})

	def get_queryset(self):
		search_param = self.request.query_params.get("search")
		user_q = Q(username__icontains=search_param) 
		exclude_q = Q(user_block_list__blocked_user=self.request.user)
		users = UserModel.objects.filter(user_q).exclude(exclude_q).distinct()


		conversation_q = Q(status="public") & Q(name__icontains=search_param) & Q(group_type__in=["channel", "group"])
		exclude_conversation_q = Q(blocklist__user=self.request.user) 
		conversations = Conversation.objects.filter(conversation_q).exclude(exclude_conversation_q)
		print("search param",search_param,users, conversations)
		return users, conversations

	def get_serializer(self, user_qs, conversation_qs):
		conversation_serializer = serializers.ConversationSerializer(
			conversation_qs, 
			many=True, 
			context={'request': self.request}
		)

		user_serializer = serializers.UserSerializer(
			user_qs,
			many=True, 
			context={'request': self.request}
			)

		return conversation_serializer, user_serializer

class MembershipCreateView(CreateAPIView):
	serializer_class = serializers.ConversationMemberSerializer
	permission_classes = [IsAuthenticated]



class BlockListCreateView(CreateAPIView):
	serializer_class = serializers.BlockListSerializer
	permission_classes = [IsAuthenticated]


class BlockUnblockView(
						mixins.CreateModelMixin,
						mixins.DestroyModelMixin,
						GenericAPIView
						):

	serializer_class = serializers.BlockListSerializer
	permission_classes = [IsAuthenticated]
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	def get_queryset(self):
		return BlockList.objects.all()



class LoginApiView(APIView):
	permission_classes = []
	def post(self, request, *args, **kwargs):

		username = request.data.get("email")
		password = request.data.get("password")
		user = authenticate(username=username, password=password)
		if not user:
			return Response({"error":"Invalid Credentials"}, status=401)

		login(request, user)
		refresh = RefreshToken.for_user(user)

		return Response({
			"access": str(refresh.access_token),
			"refresh": str(refresh)
			})

class ProfileUpdateView(UpdateAPIView):
	serializer_class = serializers.AccountProfileSerializer
	permission_classes = [IsAuthenticated]
	parser_classes = [FormParser, MultiPartParser]
	def get_object(self):
		return self.request.user.profile



class ConversationUpdateView(UpdateAPIView):
	serializer_class = serializers.ConversationSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		return Conversation.objects.filter(created_by=self.request.user)