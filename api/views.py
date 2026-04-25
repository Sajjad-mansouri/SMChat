from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from chat.models import ChatGroup
from .serializers import ChatGroupSerializer

class Index(ListAPIView):
	serializer_class = ChatGroupSerializer
	permission_classes = [IsAuthenticated]
	def get_queryset(self):
		return ChatGroup.objects.filter(user=self.request.user)
