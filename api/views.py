from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Value
from django.contrib.auth import get_user_model
from .serializers import ConversationSerializer, ConversationWithMessageSerializer, UserSerializer, ConversationMemberSerializer, ConversationProfileSerializer, BlockListSerializer
from chat.models import Conversation, ConversationMember, Chat, BlockList
from .permissions import IsMember


UserModel = get_user_model()
class Conversations(ListAPIView):
	serializer_class = ConversationSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		conversation_type = self.kwargs.get("conversation_type")
		q1 = Q(created_by=self.request.user) & Q(group_type=conversation_type)
		q2 = Q(members__user=self.request.user) & Q(group_type=conversation_type)
		q = q1|q2
		qs = Conversation.objects.filter(q).distinct().prefetch_related("members__user")
		for conversation in qs:
			# conversation.last_message = conversation.chats.first()
			if Chat.objects.filter(conversation=conversation).exists():
				conversation.last_message = Chat.objects.filter(conversation=conversation).last().text
			else:
				conversation.last_message = ""

		return qs


class ConversationDetail(RetrieveAPIView):
	serializer_class = ConversationWithMessageSerializer
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
			return UserSerializer
		else:
			return ConversationWithMessageSerializer

class ConversationProfile(ConversationDetail):
	def get_serializer_class(self):
		if isinstance(self.obj, UserModel):
			return UserSerializer
		else:
			return ConversationProfileSerializer	

class ConversationCreateView(CreateAPIView):
	serializer_class = ConversationSerializer
	permission_classes = [IsAuthenticated]

class SearchView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		user_qs, conversation_qs = self.get_queryset()
		conversation_serializer, user_serializer = self.get_serializer(user_qs, conversation_qs)
		return Response({"users":user_serializer.data, "conversations":conversation_serializer.data})

	def get_queryset(self):
		search_param = self.request.query_params.get("search")
		user_q = Q(username__icontains=search_param) & ~Q(conversation_members__conversation__members__user=self.request.user)
		exclude_q = Q(user_block_list__blocked_user=self.request.user)
		users = UserModel.objects.filter(user_q).exclude(exclude_q).distinct()


		conversation_q = Q(status="public") & Q(name__icontains=search_param) & Q(group_type__in=["channel", "group"])
		exclude_conversation_q = Q(blocklist__user=self.request.user) 
		conversations = Conversation.objects.filter(conversation_q).exclude(exclude_conversation_q)

		return users, conversations

	def get_serializer(self, user_qs, conversation_qs):
		conversation_serializer = ConversationSerializer(
			conversation_qs, 
			many=True, 
			context={'request': self.request}
		)

		user_serializer = UserSerializer(
			user_qs,
			many=True, 
			context={'request': self.request}
			)

		return conversation_serializer, user_serializer

class MembershipCreateView(CreateAPIView):
	serializer_class = ConversationMemberSerializer
	permission_classes = [IsAuthenticated]



class BlockListCreateView(CreateAPIView):
	serializer_class = BlockListSerializer
	permission_classes = [IsAuthenticated]


class BlockUnblockView(
						mixins.CreateModelMixin,
						mixins.DestroyModelMixin,
						GenericAPIView
						):

	serializer_class = BlockListSerializer
	permission_classes = [IsAuthenticated]
	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)

	def get_queryset(self):
		return BlockList.objects.all()

