from rest_framework.serializers import ModelSerializer
from chat.models import Conversation



class ConversationSerializer(ModelSerializer):
	def __int__(self, *args, **kwargs):
		print('init',kwargs, args)
		super().__init__(*args, **kwargs)
	class Meta:
		model = Conversation
		fields = "__all__"

	def to_representation(self, instance):
		request = self.context["request"]
		ret = super().to_representation(instance)
		if instance.group_type == "direct":
			ret["conversation_name"] = [other_user.email for other_user in instance.other_users]
			ret["conversation_image"] = [other_user.profile.get_image() for other_user in instance.other_users]
		else:
			ret["conversation_name"] = instance.name
			ret["conversation_image"] = instance.get_image()

		ret["last_message"] = instance.last_message


		return ret