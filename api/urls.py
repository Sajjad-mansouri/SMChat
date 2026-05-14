from django.urls import path
from rest_framework_simplejwt.views import (
		TokenObtainPairView,
		TokenRefreshView,
		TokenVerifyView
	)
from . import views

app_name = "api"
urlpatterns = [
	path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
	path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
	path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),


	path("search/", views.SearchView.as_view(), name="search"),
	path("conversations/<slug:conversation_type>/", views.Conversations.as_view(), name="Index"),
	path("conversation/<slug:conversation_type>/<int:conversation_id>/", views.ConversationDetail.as_view(), name="conversation"),
	path("conversation/<slug:conversation_type>/user/<int:user_id>/", views.ConversationDetail.as_view(), name="new_user"),

	path("conversation/<slug:conversation_type>/profile/<int:conversation_id>/", views.ConversationProfile.as_view(), name="conversation_profile"),
	path("conversation/<slug:conversation_type>/user/<int:user_id>/profile/", views.ConversationDetail.as_view(), name="new_user_profile"),





	path("conversation/create/", views.ConversationCreateView.as_view(), name="create_conversation"),
	path("conversation/<int:pk>/update/", views.ConversationUpdateView.as_view(), name="update_conversation"),
	path("conversation/<int:pk>/setting/", views.ConversationSettingView.as_view(), name="conversation_setting"),


	path("membership/add/", views.MembershipCreateView.as_view(), name="add_member"),




	path("blocklist/toggle/", views.BlockUnblockView.as_view(), name="create_blocklist"),
	path("blocklist/toggle/<int:pk>/", views.BlockUnblockView.as_view(), name="delete_blocklist"),



	path("login/", views.LoginApiView.as_view(), name="login"),

	 path("update-account/", views.ProfileUpdateView.as_view(), name="update_profile"),
]