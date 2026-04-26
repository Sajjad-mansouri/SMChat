from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from chat.models import Conversation, ConversationMember, Chat
from django.db.models import Q, Value
from .serializers import ConversationSerializer, ConversationWithMessageSerializer

class Conversations(ListAPIView):
	serializer_class = ConversationSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		print('user',self.request.user)
		conversation_type = self.kwargs.get("conversation_type", "direct")
		q = Q(group_type=conversation_type) & Q(members__user=self.request.user) 
		qs = Conversation.objects.filter(q).prefetch_related("members__user")
		for conversation in qs:

			other_members = conversation.members.exclude(user=self.request.user)

			conversation.other_users = [other_member.user for other_member in other_members]
			# conversation.last_message = conversation.chats.first()
			if Chat.objects.filter(conversation=conversation).exists():
				conversation.last_message = Chat.objects.filter(conversation=conversation).last().text

		return qs

	def get_serializer_context(self, *args, **kwargs):
		context = super().get_serializer_context()
		context["blah"] = "blah"
		return context


class ConversationDetail(RetrieveAPIView):
	serializer_class = ConversationWithMessageSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		print(self.request.user)
		qs = Conversation.objects.filter(group_type="direct")

		return qs

	def get_object(self):
		obj = super().get_object()

		obj.member = obj.members.exclude(user=self.request.user).distinct()[0].user
		members = obj.members.exclude(user=self.request.user).distinct()
		if members:
			obj.member = members[0].user
		return obj