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


	path("conversations/<slug:conversation_type>/", views.Conversations.as_view(), name="Index"),
	path("conversation/<int:pk>/", views.ConversationDetail.as_view(), name="conversation"),





]