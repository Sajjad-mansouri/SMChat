from django.urls import path
from rest_framework_simplejwt.views import (
		TokenObtainPairView,
		TokenRefreshView,
		TokenVerifyView
	)
from . import views

urlpatterns = [
	path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
	path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),


	path("conversation/<slug:conversation_type>/", views.Index.as_view(), name="Index"),




]