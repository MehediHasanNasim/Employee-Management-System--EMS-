import uuid
from django.db import models

class BaseModel(models.Model):
    alias = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True