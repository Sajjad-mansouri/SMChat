from django.shortcuts import render
from django.views.generic.base import TemplateView
from .models import Conversation

class Index(TemplateView):
	template_name='chat/main.html'