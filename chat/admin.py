from django.contrib import admin
from .models import Conversation, Chat, ConversationMember, BlockList

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ["name", "id", "created_by"]
admin.site.register(Chat)

@admin.register(ConversationMember)
class ConversationMemberAdmin(admin.ModelAdmin):
	list_display = ["user", "id","conversation", "joined_at"]

@admin.register(BlockList)
class ConversationAdmin(admin.ModelAdmin):
	list_display = ["user", "conversation", "created"]



