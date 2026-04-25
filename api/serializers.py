from rest_framework.serializers import ModelSerializer
from chat.models import ChatGroup



class ChatGroupSerializer(ModelSerializer):
	def __int__(self, *args, **kwargs):
		print('init',kwargs, args)
		super().__init__(*args, **kwargs)
	class Meta:
		model = ChatGroup
		fields = "__all__"