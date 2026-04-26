from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
	email = models.EmailField(_("email address"), blank=True, unique=True)
	username = models.EmailField(_("username"), blank=True, null=True)



	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username"]

	class Meta(AbstractUser.Meta):
		ordering = ["-date_joined"]

class Profile(models.Model):

	user = models.OneToOneField(User, on_delete=models.CASCADE ,verbose_name=_("User"))
	profile_image = models.ImageField(_("Profile Image"), upload_to="users", null=True)
	birth_day = models.DateTimeField(_("Birth Day"), null=True, blank=True)
	
	def __str__(self):
		return f'"{self.user.get_full_name()}" profile'


	class Meta:
		verbose_name = _("Profile")
		verbose_name_plural = _("Profiles")

	def get_image(self):
		if self.profile_image:
			return self.profile_image.url
		else:
			return ""