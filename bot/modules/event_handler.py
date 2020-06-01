from bot.modules.telegram_bot import TelegramBot
from ndproject import config
import cv2
from skimage import io
import numpy as np
import json
from bot.modules.nudity_detection.predict import NudityDetection
from bot.models import BotMember, GroupChat

API_TOKEN = config.API_TOKEN
BOT_USERNAME = config.BOT_USERNAME
bot = TelegramBot(API_TOKEN)

class EventHandler():
    def __init__(self, data):
        self.data = data
        callback_query = data.get("callback_query", None)
        if callback_query:
            # Extract Query
            self.query = data['callback_query']

            # Extract Message
            self.message = self.query['message']
            self.message_id = self.message['message_id']
            
            # Extart Sender User
            self.user = self.query['from']
            self.user_id = self.user['id']

            self.reply_markup = self.data
        else:
            # Extract Message
            self.message = data['message']
            self.message_id = data['message']['message_id']
            
            # Extart Sender User
            self.user = self.message['from']
            self.user_id = self.user['id']

        # Extract Chat Data
        self.chat = self.message['chat']
        self.chat_id = self.chat['id']
        self.chat_type = self.chat['type']

        # Save and Update User
        if not self.userExists():
            if self.chat_type == "private": self.user_obj = BotMember.objects.create(user_id=self.user_id, chat_id=self.chat_id, language_code=self.user['language_code'])
        else:
            self.user_obj = BotMember.objects.get(user_id=self.user_id)

        if callback_query:
            self.handle_query()
        else:
            self.handle_message()

    def handle_message(self):
        text = self.message.get('text', None)
        entities = self.message.get('entities', None)
        caption_entities = self.message.get('caption_entities', None)
        photo = self.message.get('photo', None)
        audio = self.message.get('audio', None)
        video = self.message.get('video', None)
        document = self.message.get('document', None)
        animation = self.message.get('animation', None)
        videonote = self.message.get('videonote', None)
        voice = self.message.get('voice', None)
        sticker = self.message.get('sticker', None)
        new_chat_members = self.message.get('new_chat_members', None)

        if text:
            if text.startswith('/'):
                if self.chat_type == "private":
                    self.private_command_handler(text)
                elif self.chat_type == "group" or self.chat_type == "supergroup":
                    self.group_command_handler(text)
            elif entities:
                self.entities_handler(entities)
            else:
                self.message_handler(text)
        elif caption_entities:
            self.entities_handler(caption_entities)
        elif photo:
            self.photo_handler(photo)
        elif video:
            self.video_handler([video.get("thumb", None)])
        elif animation:
            self.photo_handler([animation.get("thumb", None)])
        elif videonote:
            self.photo_handler([videonote.get("thumb", None)])
        elif audio:
            self.audio_handler(audio)
        elif voice:
            self.voice_handler(voice)
        elif sticker:
            self.sticker_handler([sticker.get("thumb", None)])
        elif document:
            self.document_handler([document.get("thumb", None)])
        elif new_chat_members:
            self.new_chat_member_handler(new_chat_members)
            
    def handle_query(self):
        callback_data = self.query.get('data', None)
        if callback_data.startswith('option'): 
            if callback_data == "option_0":
                buttons = []
                for item in self.user_obj.groupchats.all():
                    buttons.append([{"text":item.title, "callback_data": f"group_{item.id}"}])
                    keyboard = json.dumps({"inline_keyboard":buttons})
                    bot.editMessageText(self.chat_id, self.message_id, text=f"There is a list of the groups you have created. Choose one to manage settings:", reply_markup=keyboard)
                    bot.answerCallbackQuery(self.query['id'])
                    return 

            chat = self.getGroupById(int(self.user_obj.temp_data)) 
            if not chat:
                bot.answerCallbackQuery(self.query['id'], text="Chat doesn't exist!")
                return

            if callback_data == "option_1": chat.remove_sexual_content = False
            if callback_data == "option_2": chat.remove_sexual_content = True
            if callback_data == "option_3": chat.remove_links = False
            if callback_data == "option_4": chat.remove_links = True
            if callback_data == "option_5": chat.remove_documetns = False
            if callback_data == "option_6": chat.remove_documetns = True
            if callback_data == "option_7": chat.remove_audios = False
            if callback_data == "option_8": chat.remove_audios = True
            if callback_data == "option_9": chat.remove_voices = False
            if callback_data == "option_10": chat.remove_voices = True
            if callback_data == "option_11": chat.remove_videos = False
            if callback_data == "option_12": chat.remove_videos = True
            if callback_data == "option_13": chat.remove_stickers = False
            if callback_data == "option_14": chat.remove_stickers = True
            chat.save()
            buttons = self.get_options_list(chat)
            keyboard = json.dumps({"inline_keyboard":buttons})
            bot.editMessageText(self.chat_id, self.message_id, text=f"Here it is: {chat.title}\nWhat do you want to do with the group?", reply_markup=keyboard)
            bot.answerCallbackQuery(self.query['id'])

        if callback_data.startswith('group'): 
            chat_id = int(callback_data.split("_")[1])
            chat = self.getGroupById(chat_id)
            buttons = self.get_options_list(chat)
            keyboard = json.dumps({"inline_keyboard":buttons})
            bot.editMessageText(self.chat_id, self.message_id, text=f"Here it is: {chat.title}\nWhat do you want to do with the group?", reply_markup=keyboard)
            self.updateTempData(chat_id)
            bot.answerCallbackQuery(self.query['id'])

    def private_command_handler(self, command):
        command = command[1:]
        if command == "start":
            bot.sendMessage(self.chat_id, f"Hello {self.user['first_name']}\nWelcome to our bot!")
            bot.sendMessage(self.chat_id, f"If you want to enable this bot in your group you should add this bot to your group and make it admin.\nAdd {config.BOT_NAME} bot to your group from [here](https://telegram.me/{BOT_USERNAME}?startgroup=true).", parse_mode="Markdown")
        elif command.startswith("start"):
            target_chat_id = int(command.split()[1])
            if self.user_obj.groupchats.filter(chat_id=target_chat_id).count() > 0:
                chat = self.getGroupByChatId(target_chat_id)
                buttons = self.get_options_list(chat)
                keyboard = json.dumps({"inline_keyboard":buttons})
                bot.sendMessage(self.chat_id, f"Here it is: {chat.title}\nWhat do you want to do with the group?", reply_markup=keyboard)
                self.updateTempData(target_chat_id)
            else:
                bot.sendMessage(self.chat_id, f"You haven't access to manage the group you have chosen.")

        elif command == "help":
            pass

        elif command == "panel":
            buttons = []
            for item in self.user_obj.groupchats.all():
                buttons.append([{"text":item.title, "callback_data":item.id}])
            keyboard = json.dumps({"inline_keyboard":buttons})
            bot.sendMessage(self.chat_id, f"There is a list of the groups you have created. Choose one to manage settings:", reply_markup=keyboard)

    def group_command_handler(self, command):
        command = command[1:]
        chat_member = bot.getChatMember(self.chat_id, self.user_id)
        if chat_member['status'] == "creator" and self.userExists():
            if command == f"start@{BOT_USERNAME} true" or command == f"start@{BOT_USERNAME}":
                if not self.chatExists():
                    self.user_obj.groupchats.create(chat_id=self.chat_id, title=self.chat['title'])
                    bot.sendMessage(self.chat_id, f"Dear @{self.user['username']}\n{config.BOT_NAME} control panel was enabled for you. You can change settings from [here](t.me/{BOT_USERNAME}?start={self.chat_id}).", parse_mode="Markdown")
                else:
                    bot.sendMessage(self.chat_id, f"Dear @{self.user['username']}\n{config.BOT_NAME} control panel is already enabled for you. You can change settings from [here](t.me/{BOT_USERNAME}?start={self.chat_id}).", parse_mode="Markdown")
            elif command == "hello":
                pass

    def message_handler(self, text):
        if text == "hi":
            bot.sendMessage(self.chat_id, f"Hello {self.user['first_name']}")
        elif text == "bye":
            bot.sendMessage(self.chat_id, f"Goodbye {self.user['first_name']}")

    def entities_handler(self, entities):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private" or (self.is_group_chat() and chat.remove_links):
            for en in entities:
                if en['type'] == "url" or en['type'] == "text_link":
                    bot.deleteMessage(self.chat_id, self.message_id)
                    warning_msg = f"Dear @{self.user['username']}\nSending links is not legal in this chat."
                    bot.sendMessage(self.chat_id, warning_msg)
                    break

    def photo_handler(self, photo):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private":
            self.delete_sexual_content(photo)
        elif self.is_group_chat() and chat.remove_sexual_content:
            self.delete_sexual_content(photo)

    def video_handler(self, photo):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private":
            self.delete_sexual_content(photo)
        elif self.is_group_chat():
            if chat.remove_videos:
                bot.deleteMessage(self.chat_id, self.message_id)
            elif chat.remove_sexual_content:
                self.delete_sexual_content(photo)
    
    def sticker_handler(self, photo):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private":
            self.delete_sexual_content(photo)
        elif self.is_group_chat():
            if chat.remove_stickers:
                bot.deleteMessage(self.chat_id, self.message_id)
                warning_msg = f"Dear @{self.user['username']}\nSending stickers is not legal in this chat."
                bot.sendMessage(self.chat_id, warning_msg)
            elif chat.remove_sexual_content:
                self.delete_sexual_content(photo)

    def document_handler(self, photo):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private":
            self.delete_sexual_content(photo)
        elif self.is_group_chat():
            if chat.remove_documetns:
                bot.deleteMessage(self.chat_id, self.message_id)
                warning_msg = f"Dear @{self.user['username']}\nSending documents is not legal in this chat."
                bot.sendMessage(self.chat_id, warning_msg)
            elif chat.remove_sexual_content:
                self.delete_sexual_content(photo)
            
    def audio_handler(self, audio):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private" or (self.is_group_chat() and chat.remove_audios):
            bot.deleteMessage(self.chat_id, self.message_id)
            warning_msg = f"Dear @{self.user['username']}\nSending audios is not legal in this chat."
            bot.sendMessage(self.chat_id, warning_msg)

    def voice_handler(self, audio):
        chat = self.getGroupByChatId(self.chat_id)
        if self.chat_type == "private" or (self.is_group_chat() and chat.remove_voices):
            bot.deleteMessage(self.chat_id, self.message_id)
            warning_msg = f"Dear @{self.user['username']}\nSending voices is not legal in this chat."
            bot.sendMessage(self.chat_id, warning_msg)

    def new_chat_member_handler(self, members):
        first_member = members[0]
        # if first_member['username'] = "{BOT_USERNAME}":

    # Deep Methods
    def delete_sexual_content(self, photo):
        pic = photo[0]
        file_id = pic['file_id']
        file_path = bot.getFile(file_id)
        file_url = "https://api.telegram.org/file/bot{0}/{1}".format(API_TOKEN, file_path)
    
        image = io.imread(file_url)
        label, _ = NudityDetection().detect(image)

        if label == "nsfw":
            bot.deleteMessage(self.chat_id, self.message_id)
            warning_msg = f"Dear @{self.user['username']}\nSexual content is not legal in this chat."
            bot.sendMessage(self.chat_id, warning_msg)

    # Checker Methodes
    def is_group_chat(self):
        return self.chat_type == "group" or self.chat_type == "supergroup"

    # Database
    def userExists(self):
        return BotMember.objects.filter(user_id=self.user_id).count() > 0

    def chatExists(self):
        return GroupChat.objects.filter(chat_id=self.chat_id).count() > 0

    def getGroupById(self, pk):
        try:
            return GroupChat.objects.get(pk=pk)
        except GroupChat.DoesNotExist:
            return None

    def getGroupByChatId(self, chat_id):
        try:
            return GroupChat.objects.get(chat_id=chat_id)
        except GroupChat.DoesNotExist:
            return None

    def updateTempData(self, temp):
        BotMember.objects.filter(user_id=self.user_id).update(temp_data=temp)

    # Keyboard Generator
    def get_options_list(self, chat):
        buttons = []
        if chat.remove_sexual_content: 
            buttons.append([{"text":"Disable Filtering Sexual Content", "callback_data":"option_1"}])
        else:
            buttons.append([{"text":"Enable Filtering Sexual Content", "callback_data":"option_2"}])

        if chat.remove_links: 
            buttons.append([{"text":"Disable Filtering Links", "callback_data":"option_3"}])
        else:
            buttons.append([{"text":"Enable Filtering Links", "callback_data":"option_4"}])

        if chat.remove_documetns: 
            buttons.append([{"text":"Disable Filtering Documents", "callback_data":"option_5"}])
        else:
            buttons.append([{"text":"Enable Filtering Documents", "callback_data":"option_6"}])

        if chat.remove_audios: 
            buttons.append([{"text":"Disable Filtering Audios", "callback_data":"option_7"}])
        else:
            buttons.append([{"text":"Enable Filtering Audios", "callback_data":"option_8"}])

        if chat.remove_voices: 
            buttons.append([{"text":"Disable Filtering Voices", "callback_data":"option_9"}])
        else:
            buttons.append([{"text":"Enable Filtering Voices", "callback_data":"option_10"}])

        if chat.remove_videos: 
            buttons.append([{"text":"Disable Filtering Videos", "callback_data":"option_11"}])
        else:
            buttons.append([{"text":"Enable Filtering Videos", "callback_data":"option_12"}])

        if chat.remove_stickers: 
            buttons.append([{"text":"Disable Filtering Stickers", "callback_data":"option_13"}])
        else:
            buttons.append([{"text":"Enable Filtering Stickers", "callback_data":"option_14"}])

        buttons.append([{"text":"« Back to Groups List", "callback_data":"option_0"}])

        return buttons


            
            
            
    





        




    