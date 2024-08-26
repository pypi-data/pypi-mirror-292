# -*- coding: utf-8 -*-

"""Модуль для работы с API разных соц. сетей (VK, Discord)"""
import vk_api, discord, pypresence, time
from googleapiclient.discovery import build

import vk_api.longpoll

class Discord():
    """Класс для работы с Discord."""
    def presence(id: str, title: str, title2: str, btns: dict, is_time_shared: bool = False):
        """Создайте кастомную активность с кнопками с помощью данной функции.\nid: ID приложения на портале разрабов.\ntitle: первый заголовок.\ntitle2: заголовок ниже первого.\nbtns: кнопки. Пример: {'VK':'https://vk.com', 'YouTube':'https://youtube.com/'}\nis_time_shared: распостранять ли время запуска активности? По умолчанию, False."""
        if is_time_shared:
            profile = pypresence.Presence(id)
            profile.connect()
            profile.update(details=title, state=title2, buttons=btns, start=time.time())
        else:
            profile = pypresence.Presence(id)
            profile.connect()
            profile.update(details=title, state=title2, buttons=btns)
    class WebhookSender:
        """Класс, руководящий вебхуками.\nurl: URL вебхука."""
        def __init__(self, url: str):
            self.webhook = discord.SyncWebhook.from_url(url)
        def send(self, message: str):
            """Отправьте текст с помощью вебхука.\nmessage: текст сообщения."""
            self.webhook.send(message)
        def send_embed(self, embed: discord.Embed):
            """Отправьте эмбед с помощью вебхука.\nembed: ваш эмбед."""
            self.webhook.send(embed=embed)
        def send_picture(self, directory: str, spoiler: bool = False, title: str = None):
            """Отправьте картинку с помощью вебхука.\ndirectory: директория твоей картинки.\nspoiler: нужно-ли поместить картинку в спойлер? По умолчанию, False.\ntitle: надпись, которая будет выше твоей картинки. По умолчанию, None."""
            self.webhook.send(title, file=discord.File(directory, spoiler=spoiler))
class VK:
    """Класс для работы с VK API.\ntoken: токен твоего приложение, которое привязано к сообществу.\nid: id твоего сообщества, которое привязано к сообществу. Пригодится в большинстве случаев."""
    def __init__(self, token: str, id: int):
        self.vk_session = vk_api.VkApi(token=token)
        self.id = id
    def inspect_messages(self):
        """Отслеживайте все сообщения из сообщества."""
        for event in vk_api.longpoll.VkLongPoll(self.vk_session).listen():
                if event.type == vk_api.longpoll.VkEventType.MESSAGE_NEW:
                    if event.to_me == True:
                        user = self.vk_session.method("users.get", {"user_ids": event.user_id})
                        fullname = user[0]['first_name'] +  ' ' + user[0]['last_name']
                        print(f'{fullname} написал(а) сообщение: {event.message}')
    def get_subs(self):
        """Узнать количество подписчиков на сообществе на данный момент."""
        members = self.vk_session.method('groups.getMembers', {'group_id': self.id})
        return len(members['items'])
    def inspect_new_subs(self, text: str, time1: float = 5):
        """Приветствовать новых участников.\ntext: текст, который мы будем отправлять новым подписчикам.\ntime: время, раз в которое начинается следующая проверка. По умолчанию, раз в 5 секунд."""
        previous_followers = self.vk_session.method('groups.getMembers', {'group_id': self.id})['items']
        while True:
        # Проверяем наличие новых подписчиков
            current_followers = self.vk_session.method('groups.getMembers', {'group_id': self.id})['items']
            new_followers = list(set(current_followers) - set(previous_followers))
    
            # Если есть новые подписчики, отправляем им сообщение
            for follower_id in new_followers:
                self.vk_session.method('messages.send', {"user_id":follower_id, "message":text, "random_id":0})

            # Обновляем список подписчиков
            previous_followers = current_followers
    
            # Пауза перед следующей проверкой
            time.sleep(time1)
def get_youtube_channel_details(developer_key: str, id: str):
    """Информация о YouTube канале.\ndeveloper_key: ваш ключ разработчика для сервисов Google.\nid: id канала на YouTube. (Пример: `UCoBDcBK9tz9HyI2o_sV6o8Q`).\nВозвращает `dict`."""
    youtube = build('youtube', 'v3', developerKey=developer_key)
    request = youtube.channels().list(part='snippet,statistics', id=id)
    response = request.execute()
    return dict(response['items'][0]['snippet'])
