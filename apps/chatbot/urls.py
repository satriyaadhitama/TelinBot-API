from django.urls import path
from .views import ChatbotViewSet

urlpatterns = [
    path(
        "chatbot/session/<int:user_id>",
        ChatbotViewSet.as_view(
            {"post": "create_chat_session", "get": "get_all_history"}
        ),
        name="chat-session-list",
    ),
    path(
        "chatbot/<str:session_id>",
        ChatbotViewSet.as_view({"post": "send_message", "get": "get_message_history"}),
        name="message-history-list",
    ),
]
