from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CaseCategory(models.Model):
    c_name = models.CharField(max_length=255)
    c_image=models.FileField()
    c_disc=models.TextField()

class Agent(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    name=models.CharField(max_length=50)
    email=models.EmailField()
    password=models.TextField()

class Case(models.Model):
    case_detail = models.TextField()
    evidence = models.FileField(upload_to='evidence/', null=True, blank=True)
    evidence_details = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('closed', 'Closed'),
        ],
        default='open'
    )
    date_and_time = models.DateTimeField(auto_now_add=True)
    case_category = models.ForeignKey(CaseCategory, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_no = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

class ChatMessage(models.Model):
    case = models.ForeignKey('Case', on_delete=models.CASCADE, related_name='chat_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    name=models.TextField()
    email=models.EmailField()
    message=models.TextField()