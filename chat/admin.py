from django.contrib import admin
from .models import Conversation, Chat, ConversationMember


admin.site.register(Conversation)
admin.site.register(Chat)
admin.site.register(ConversationMember)


