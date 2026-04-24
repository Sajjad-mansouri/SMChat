from django.urls import path, include
from . import views

app_name = "account"
urlpatterns = [
	path("register/<uidb64>/<token>/", views.RegistrationConfirmView.as_view(), name="register-confirm"),
	path("register/", views.RegistrationView.as_view(), name="register"),
	path("register/registration_done/", views.RegistrationDoneView.as_view(), name="registration_done"),
]