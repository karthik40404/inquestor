from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

class Case(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Under Investigation', 'Under Investigation'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Open')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    assigned_agent = models.ForeignKey(
        User, limit_choices_to={'is_staff': True}, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

class Evidence(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    file = models.FileField(upload_to='evidence/')
    description = models.TextField(blank=True)

class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="agent_profile")
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

class CaseCategory(models.Model):
    c_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)