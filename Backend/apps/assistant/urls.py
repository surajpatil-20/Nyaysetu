"""
URL configuration for NYAYASETU Assistant app.
"""
from django.urls import path
from apps.assistant.views import AssistantChatView

urlpatterns = [
    path("", AssistantChatView.as_view(), name="assistant_chat"),
    path("ask/", AssistantChatView.as_view(), name="assistant_ask"),
]

