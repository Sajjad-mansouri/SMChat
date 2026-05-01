from django.contrib import admin
from .models import Conversation, Chat, ConversationMember

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ["name", "id", "created_by"]
admin.site.register(Chat)
admin.site.register(ConversationMember)


