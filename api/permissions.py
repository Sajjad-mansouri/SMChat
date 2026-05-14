from rest_framework import permissions
from chat.models import Conversation,ConversationMember

class IsMember(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		if hasattr(obj, "group_type"):
			if request.user.id in obj.members.values_list("user", flat=True):
				return True
			return False
		else:
			return True


class IsConversationOwner(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if isinstance(obj, Conversation):
			return  obj.created_by == request.user
		elif isinstance(obj, ConversationMember):
			return obj.conversation.created_by == request.user

