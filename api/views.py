from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Value
from .serializers import ConversationSerializer, ConversationWithMessageSerializer, UserSerializer
from chat.models import Conversation, ConversationMember, Chat
from django.contrib.auth import get_user_model


UserModel = get_user_model()
class Conversations(ListAPIView):
	serializer_class = ConversationSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		conversation_type = self.kwargs.get("conversation_type")
		q = Q(created_by=self.request.user) & Q(group_type=conversation_type)
		qs = Conversation.objects.filter(q).prefetch_related("members__user")
		for conversation in qs:

			other_members = conversation.members.exclude(user=self.request.user)

			conversation.other_users = [other_member.user for other_member in other_members]
			# conversation.last_message = conversation.chats.first()
			if Chat.objects.filter(conversation=conversation).exists():
				print(Chat.objects.filter(conversation=conversation).exists(), Chat.objects.filter(conversation=conversation))
				conversation.last_message = Chat.objects.filter(conversation=conversation).last().text
			else:
				conversation.last_message = ""

		return qs




class ConversationDetail(RetrieveAPIView):
	serializer_class = ConversationWithMessageSerializer
	# permission_classes = [IsAuthenticated]
	def get_queryset(self):
		pk = self.kwargs.get("pk")
		qs = Conversation.objects.filter(pk=pk)

		return qs

	def get_object(self):
		obj = super().get_object()
		if obj.group_type == "direct":
			obj.member = obj.members.exclude(user=self.request.user).distinct()[0].user
			members = obj.members.exclude(user=self.request.user).distinct()
			if members:
				obj.member = members[0].user
		return obj

class ConversationCreateView(CreateAPIView):
	serializer_class = ConversationSerializer
	# permission_classes = [IsAuthenticated]

class SearchView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		user_qs, conversation_qs = self.get_queryset()
		conversation_serializer, user_serializer = self.get_serializer(user_qs, conversation_qs)
		return Response({"users":user_serializer.data, "conversations":conversation_serializer.data})

	def get_queryset(self):
		search_param = self.request.query_params.get("search")
		user_q = Q(username__icontains=search_param)
		users = UserModel.objects.filter(user_q)

		conversation_q = Q(status="public") & Q(name__icontains=search_param) & Q(group_type__in=["channel", "group"])
		conversations = Conversation.objects.filter(conversation_q)

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