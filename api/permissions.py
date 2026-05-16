from rest_framework import permissions
from django.db.models import Q
from chat.models import Conversation,ConversationMember

class IsMember(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		if hasattr(obj, "group_type"):
			if request.user.id in obj.members.values_list("user", flat=True):
				return True
			return False
		else:
			return True


class RemoveMembershipPermission(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):

		return obj.conversation.created_by == request.user or obj.user == request.user

class IsConversationOwner(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if isinstance(obj, Conversation):
			return  obj.created_by == request.user
		elif isinstance(obj, ConversationMember):
			return obj.conversation.created_by == request.user


class isAcceptedUser(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if hasattr(obj, "group_type"):
			if obj.join_request and obj.status=="public":
				q1 = Q(user=request.user)
				q2 = Q(accepted=True)
				q = (q1 & q2) 
				if obj.created_by == request.user :
					return True
				else:
					if request.user.id in obj.members.values_list("user", flat=True):
						self.message = {
						    'detail': 'Permission required',
						    'status': 'pending'
						}
					else:
						self.message = {
						    'detail': 'Permission required',
						    'status': 'not accepted'
						}	
					return obj.members.filter(q).exists()
		
		return True