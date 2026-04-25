from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from chat.models import Conversation
from .serializers import ChatGroupSerializer

class Index(ListAPIView):
	serializer_class = ChatGroupSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		return Conversation.objects.filter(created_by=self.request.user)
