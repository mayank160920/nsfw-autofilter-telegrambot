from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
import json
from bot.modules.event_handler import EventHandler
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
@csrf_exempt
def event(request):
    data = json.loads(request.body)
    # print(request.body)
    EventHandler(data)
    return HttpResponse()
    