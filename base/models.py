from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
  name = models.CharField(max_length=50)

  def __str__(self):
    return self.name

class Room(models.Model):
  name = models.CharField(max_length=200)
  host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
  description = models.TextField(null=True, blank=True)
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  class Meta:
    ordering = ['-updated', '-created'] # - is equivalent to reverse

  def __str__(self) -> str:
    return self.name
  
class Message(models.Model):
  PREVIEW_LENGTH = 50
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  room = models.ForeignKey(Room, on_delete=models.CASCADE)
  content = models.TextField()
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.content[Message.PREVIEW_LENGTH]