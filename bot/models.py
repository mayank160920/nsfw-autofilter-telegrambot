from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

def UniqueId(length=10):
    source = "abcdefghijklmnopqrstuvwsyzABCDEFGHIJKLMNOPQRSTUVWSYZ123456789"
    unique = ""
    for _ in range(length):
        unique += random.choice(source)
    return unique

class GroupChat(models.Model):
    unique_id = models.CharField(max_length=10, default=UniqueId, editable=False)
    chat_id = models.IntegerField(default=0)
    title = models.CharField(max_length=200, default="")
    remove_sexual_content = models.BooleanField(default=True)
    remove_links = models.BooleanField(default=False)
    remove_documetns = models.BooleanField(default=False)
    remove_audios = models.BooleanField(default=False)
    remove_voices = models.BooleanField(default=False)
    remove_videos = models.BooleanField(default=False)
    remove_stickers = models.BooleanField(default=False)

class BotMember(models.Model):
    user_id = models.IntegerField(default=0)
    chat_id = models.IntegerField(default=0)
    username = models.CharField(max_length=100, default="")
    keyboard_status = models.IntegerField(default=0)
    temp_data = models.CharField(max_length=100, default="")
    language_code = models.CharField(max_length=10, default="")
    groupchats = models.ManyToManyField(GroupChat)
    date_created = models.DateTimeField(default=timezone.now)


