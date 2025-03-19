from django.db import models
from .user_model import CustomUser

class CloudinaryFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='files')
    public_id = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    url = models.URLField()
    resource_type = models.CharField(max_length=50)
    format = models.CharField(max_length=20, blank=True, null=True)
    folder = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.filename
    
    class Meta:
        ordering = ['-updated_at'] 