from django.db import models
from apps.user_auth.models import User
import uuid


# Create your models here.
class ChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    last_activity = models.DateTimeField(auto_now_add=True, null=True)


class ChatHistory(models.Model):
    SENDER_OPTIONS = [(1, "User"), (0, "Bot")]
    sender = models.IntegerField(choices=SENDER_OPTIONS, default=0)
    message = models.TextField()
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
