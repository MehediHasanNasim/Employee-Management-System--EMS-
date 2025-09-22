from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import BaseModel
from core.choices import Status

class UserRole(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    def __str__(self):
        return self.name

class Team(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    team_lead = models.ForeignKey(
        'User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='led_teams'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    def __str__(self):
        return self.name

class User(AbstractUser, BaseModel):
    email = models.EmailField(unique=True)
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, related_name='users', null=True, blank=True)
    team = models.ForeignKey(
        Team, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='members'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return f"{self.email} - {self.username}"
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'