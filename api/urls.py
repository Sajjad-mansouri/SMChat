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


	path("search/", views.SearchView.as_view(), name="search"),
	path("conversations/<slug:conversation_type>/", views.Conversations.as_view(), name="Index"),
	path("conversation/<slug:conversation_type>/<int:conversation_id>/", views.ConversationDetail.as_view(), name="conversation"),
	path("conversation/<slug:conversation_type>/user/<int:user_id>/", views.ConversationDetail.as_view(), name="new_user"),



	path("conversation/create/", views.ConversationCreateView.as_view(), name="create_conversation"),






]