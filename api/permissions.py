from rest_framework import permissions

class IsMember(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		if hasattr(obj, "group_type"):
			if request.user.id in obj.members.values_list("user", flat=True):
				return True
			return False
		else:
			return True