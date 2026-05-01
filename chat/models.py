from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
UserModel = get_user_model()

def group_file_path(instance, file_name):
	return "group/profile/{conversation_id}/{year}/{month}/{day}/{file_name}".format(
										conversation_id=instance.id, 
										year = instance.updated.year,
										month = instance.updated.month,
										day = instance.updated.day,
										file_name = file_name)

class Conversation(models.Model):
	GROUP_TYPE = [
		("channel", "Channel"),
		("group", "Group"),
		("direct", "Direct")
	]

	STATUS_CHOICES = [
		("public", "Public"),
		("private", "Private")
	]
	created_by = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name="chat_groups", verbose_name=_("created by"))
	bio = models.CharField(_("bio"), max_length=250, blank=True)
	name = models.CharField(_("name"), max_length=150, blank=True)


	status = models.CharField(_("status"), choices=STATUS_CHOICES, max_length=10, default="private")
	group_type = models.CharField(_("group type"), choices=GROUP_TYPE, max_length=10)
	image = models.ImageField(_("image"), upload_to=group_file_path, null=True, blank=True)
	is_active = models.BooleanField(default=True)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	def __str__(self):
		if self.group_type == "direct":
			return f"direct by {self.created_by}{self.id}"
		return f"{self.id}{self.group_type}:{self.name}"

	def get_image(self):
		if self.image:
			return self.image.url

		else:
			return ""



class ConversationMember(models.Model):
	MEMBER_ROLES = (
		('owner', 'Owner'),
		('admin', 'Admin'),
		('member', 'Member'),
	)
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='members', verbose_name=_("conversation"))
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='conversations',verbose_name= _("user"))
	role = models.CharField(_("role"), max_length=20, choices=MEMBER_ROLES, default='member')
	joined_at = models.DateTimeField(auto_now_add=True)
	accepted = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.user} in {self.conversation}"

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=['conversation', 'user'],
				name='unique_membership'
			)
		]
def file_path(instance, file_name):
	return "chat/{user_id}/{group_id}/{year}/{month}/{day}/{file_name}".format(
										user_id=instance.user.id,
										group_id=instance.group.id, 
										year = instance.updated.year,
										month = instance.updated.month,
										day = instance.updated.day,
										file_name = file_name)


class Chat(models.Model):
	user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, related_name="chats", verbose_name=_("user"))
	conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True, related_name="group_chats", verbose_name=_("group"))
	reply_to = models.ForeignKey(UserModel, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_("reply to"))
	text = models.TextField(_("text"), blank=True)
	file = models.FileField(_("file"), upload_to=file_path, null=True, blank=True)
	image = models.FileField(_("image"), upload_to=file_path, null=True, blank=True)

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)



class MessageRead(models.Model):
	message = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='read_by', verbose_name=_("message"))
	user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name=_("user"))
	read_at = models.DateTimeField(auto_now_add=True)
	
