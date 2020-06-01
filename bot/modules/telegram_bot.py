import requests
import json


class TelegramBot():
    def __init__(self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot{0}/".format(token)
    
    def sendMessage(self, chat_id, text, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        data = {'chat_id': chat_id, 'text': text, 'parse_mode': parse_mode, 'disable_web_page_preview': disable_web_page_preview, 'disable_notification': disable_notification, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        response = requests.post(self.url + "sendMessage", data=data)
        return response.content

    def deleteMessage(self, chat_id, message_id):
        data = {'chat_id': chat_id, 'message_id': message_id}
        response = requests.post(self.url + "deleteMessage", data=data)
        return response.content

    def editMessageText(self, chat_id=None, message_id=None, inline_message_id=None, text=None, parse_mode=None, disable_web_page_preview=None, disable_notification=None, reply_to_message_id=None, reply_markup=None):
        data = {'chat_id': chat_id, 'message_id': message_id, 'inline_message_id': inline_message_id, 'text': text, 'parse_mode': parse_mode, 'disable_web_page_preview': disable_web_page_preview, 'disable_notification': disable_notification, 'reply_to_message_id': reply_to_message_id, 'reply_markup': reply_markup}
        response = requests.post(self.url + "editMessageText", data=data)
        return response.content

    def answerCallbackQuery(self, callback_query_id, text=None, show_alert=None, url=None, cache_time=None):
        data = {'callback_query_id': callback_query_id, 'text': text, 'show_alert': show_alert, 'url': url, 'cache_time': cache_time}
        response = requests.post(self.url + "answerCallbackQuery", data=data)
        return response.content

    def getChatMember(self, chat_id, user_id):
        data = {'chat_id': chat_id, 'user_id': user_id}
        response = requests.post(self.url + "getChatMember", data=data)
        content = json.loads(response.content)
        return content['result']

    def getFile(self, file_id):
        data = {'file_id': file_id}
        response = requests.post(self.url + "getFile", data=data)
        content = json.loads(response.content)
        return content['result']['file_path']