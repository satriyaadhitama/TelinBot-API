from rest_framework import permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from http import HTTPMethod
from django.utils import timezone
from django.shortcuts import get_object_or_404

from apps.user_auth.models import User
from .models import ChatSession, ChatHistory
from .serializers import ChatHistorySerializer, ChatSessionSerializer

from faker import Faker

import logging

# Configure logger
logger = logging.getLogger(__name__)


from .utils import get_bot_reply_message


# Create your views here.
class ChatbotViewSet(viewsets.ViewSet):
    @action(detail=False, methods=[HTTPMethod.GET])
    def get_all_history(self, request, user_id):
        try:
            # Attempt to retrieve chat sessions based on user_id and order by last_activity
            sessions = ChatSession.objects.order_by("-last_activity").filter(
                user_id=user_id
            )
            serializer = ChatSessionSerializer(sessions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle any exceptions that might occur
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=[HTTPMethod.POST])
    def create_chat_session(self, request, user_id):
        try:
            # Using get_object_or_404 ensures that a 404 response is automatically returned if the user is not found.
            user = get_object_or_404(User, id=user_id)

            # Create a new chat session for the user
            session = ChatSession.objects.create(user=user, title="New Chat")

            # Return a success response
            return Response(
                {
                    "message": "Successfully created chat session",
                    "detail": {"session_id": session.id},
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            # This block will actually never be executed because get_object_or_404 handles the DoesNotExist exception.
            logger.error(f"User with ID {user_id} does not exist.")
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Catch all other exceptions to prevent the API from returning 500 Internal Server Error without logging
            logger.exception(
                "An unexpected error occurred while creating a chat session."
            )
            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=[HTTPMethod.POST])
    def send_message(self, request, session_id):
        data = request.data
        message = data["message"]

        try:
            session = get_object_or_404(ChatSession, id=session_id)

            # Send new message from user
            ChatHistory.objects.create(session=session, sender=1, message=message)

            # Generate a dummy reply message using Faker for now
            # reply_message = Faker().paragraph(nb_sentences=7)
            reply_message = get_bot_reply_message(message)
            bot_message = ChatHistory.objects.create(
                session=session, sender=0, message=reply_message
            )

            # Update session activity time
            session.last_activity = timezone.now()
            session.save()

            # Successful response
            return Response(
                {
                    "message": "Successfully created chat session",
                    "detail": {
                        "reply": {
                            "id": bot_message.id,
                            "sender": bot_message.sender,
                            "message": bot_message.message,
                            "created_at": bot_message.created_at,
                        },
                    },
                },
                status=status.HTTP_200_OK,
            )

        except ChatSession.DoesNotExist:
            logger.error(f"ChatSession with ID {session_id} does not exist.")
            return Response(
                {"error": "Chat session not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("An error occurred during chat interaction.")
            return Response(
                {"error": "An internal server error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=[HTTPMethod.GET])
    def get_message_history(self, request, session_id):
        try:
            # Attempt to retrieve the session
            session = ChatSession.objects.get(id=session_id)
        except ChatSession.DoesNotExist:
            # If the session does not exist, return a 404 Not Found response
            return Response(
                {"error": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            # Handle other possible exceptions, such as database errors
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # Retrieve and serialize the chat history associated with the session
            history = ChatHistory.objects.order_by("created_at").filter(session=session)
            serializer = ChatHistorySerializer(history, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle unexpected errors during the query or serialization process
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=[HTTPMethod.PATCH])
    def update_title(self, request, session_id):
        try:
            new_title = request.data.get("new_title")
            if not new_title:
                return Response(
                    {"error": "The new_title field is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            ChatSession.objects.filter(id=session_id).update(title=new_title)

            return Response(
                {"message": "Successfully updated chat session title"},
                status=status.HTTP_200_OK,
            )
        except ChatSession.DoesNotExist:
            return Response(
                {"error": "Chat session not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=[HTTPMethod.DELETE])
    def delete_session(self, request, session_id=None):
        try:
            chat_session = get_object_or_404(ChatSession, id=session_id)
            chat_session.delete()
            return Response(
                {"message": "Successfully deleted chat session"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except ChatSession.DoesNotExist:
            logger.error(f"ChatSession with id: {session_id} not found.")
            return Response(
                {"error": "Chat session not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(
                f"An error occurred while deleting ChatSession id: {session_id}: {str(e)}"
            )
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
