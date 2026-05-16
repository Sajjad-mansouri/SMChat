from django.db import models
from django.db.models import UniqueConstraint, Q
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	email = models.EmailField(_("email address"), blank=True, unique=True)
	username = models.CharField(_("username"), max_length=150)
	



	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username"]

	class Meta(AbstractUser.Meta):
		ordering = ["-date_joined"]
		constraints = [
			UniqueConstraint(
					fields = ["username"],
					condition=~Q(username=""),
					name="unique_username"
				)
		]

	def get_display_name(self):
		if self.first_name or self.last_name:
			return self.get_full_name()
		elif self.username:
			return self.username
		else:
			return self.email

class Profile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE ,verbose_name=_("User"))
	profile_image = models.ImageField(_("Profile Image"), upload_to="users", null=True)
	birth_day = models.DateTimeField(_("Birth Day"), null=True, blank=True)
	bio = models.CharField(_("Bio"), max_length=200, blank=True)
	
	def __str__(self):
		return f'{self.user.username}-"{self.user.get_full_name()}" profile'


	class Meta:
		verbose_name = _("Profile")
		verbose_name_plural = _("Profiles")

	def get_image(self):
		if self.profile_image:
			return self.profile_image.url
		else:
			return ""

	def save(self, *args, **kwargs):
		if not self.profile_image:
			self.profile_image = '/default/default_user.jpeg'

		super().save(*args, **kwargs)