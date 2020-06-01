from django.contrib import admin
from bot.models import BotMember, GroupChat

# Register your models here.
admin.site.register(BotMember)
admin.site.register(GroupChat)