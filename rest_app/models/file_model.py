# models/file_model.py (Modified)
from django.db import models
from .user_model import Account
from .prompt_model import Prompt
from .model import SupabaseModelMixin

class CloudinaryFile(models.Model, SupabaseModelMixin):
    table_name = 'files'

    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='files')
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    public_id = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    url = models.URLField()
    resource_type = models.CharField(max_length=50)
    format = models.CharField(max_length=20, blank=True, null=True)
    folder = models.CharField(max_length=255, blank=True, null=True)
    
    step_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., object_detection, segmentation, inpainting
    step_index = models.IntegerField(default=0)

    def __str__(self):
        return self.filename