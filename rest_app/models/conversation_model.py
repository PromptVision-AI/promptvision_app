# models/conversation_model.py
from django.db import models
from .user_model import Account
from .model import SupabaseModelMixin

class Conversation(models.Model, SupabaseModelMixin):
    table_name = 'conversations'

    # id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.title