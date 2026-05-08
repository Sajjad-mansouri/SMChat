from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Conversation


class Index(LoginRequiredMixin, TemplateView):
	template_name='chat/main.html'