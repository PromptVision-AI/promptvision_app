# models/prompt_model.py
from django.db import models
from .conversation_model import Conversation
from .model import SupabaseModelMixin

class Prompt(models.Model, SupabaseModelMixin):
    table_name = 'prompts'

    # id = models.UUIDField(primary_key=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='prompts')
    text = models.TextField()
    response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.text[:30]