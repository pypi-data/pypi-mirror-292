# -*- coding: utf-8 -*-

"""Всякие утилиты для работы с ИИ и RCON!"""
import g4f.client
from mcrcon import MCRcon
from g4f.Provider import Bing
from MukeshAPI import api
import g4f, segno
import requests
from typing import Union, Any
import time, pyautogui
import googletrans
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pywebio.output import put_html
from pywebio import start_server
import mcstatus, pyjokes, art
import mouse
import string, random, requests
from tqdm import tqdm
from .working_api import VK, Discord, get_youtube_channel_details
from pytubefix import YouTube

def ai_text(prompt: str) -> str:
    """Попросите ИИ написать Вам любой текст на Ваш вкус по запросу."""
    response = g4f.client.Client().chat.completions.create(model='gpt-4o', messages=[{"role": "user", "content": prompt}], provider=Bing)
    return response.choices[0].message.content

def ai_image(prompt: str) -> bytes:
    """Попросите ИИ нарисовать картинку по Вашему запросу.\n\nВНИМАНИЕ! МОГУТ БЫТЬ НЕТОЧНОСТИ, ЖЕЛАТЕЛЬНО ВВОДИТЬ СВОЙ ЗАПРОС НА АНГЛИЙСКОМ ЯЗЫКЕ.\nФункция возвращает тип `bytes`.\nВот примерчик использования: ```with open('file.png', 'rb') as file:\nfile.write(ai_image('Draw a car.'))\nfile.close()```"""
    return api.ai_image(prompt)

def rcon_connect(host: str, passwd: str, port: int, command: str):
    """Взаимодействуйте с RCON с помощью данной функции.\nhost: IP/Домен сервера.\npasswd: RCON пароль сервера.\ncommand: Команда, которую надо прописать. Пример: tp FlorestDev Dima (команда пишется без слэша)."""
    try:
        with MCRcon(host, passwd, port) as server:
            server.connect()
            answear = server.command(command)
            server.disconnect()
            return {
                "status": 'success',
                "answear": answear
            }
    except:
        return {"status":"failed", "answear":None}
    

def ip_deanon(ip: str) -> Union[list, str]:
    """Пробейте IP с помощью данной функции.\nВозвращает `list` при удачной завершении операции."""
    response = requests.get(f"http://ip-api.com/json/{ip}?lang=ru")
    if response.status_code == 404:
        return f'Произошла ошибка 404. Возможно, это проблема с сайтом, которую мы используем для пробива.'
    results = response.json()
    if results['status'] == 'fail':
        return f'Не удалось пробить IP адрес, который был введен в аргумент `ip`.'
    record = []
    for key, value in results.items():
        record.append(f"[{key.title()}]: {value}")
    return record

def spamer(text: Union[str, list], time1: float = 5):
    """Спамер на Python, которого можно юзать в различных мессенджерах.\ntext: текст, которым будет спамить спамер. Или даже список.\ntime: время, через которое начинается исполнение программы после запуска в секундах. По умолчанию, 5 секунд."""
    if isinstance(text, str):
        time.sleep(time1)
        while True:
            pyautogui.write(text)
            pyautogui.press('enter')
    if isinstance(text, list):
        time.sleep(time1)
        while True:
            for _ in text:
                pyautogui.write(_)
                pyautogui.press('enter')
            print(f'Мы перебрали {str(len(text))} элементов из списка. Повторяем...')

def translate(text: Union[str, list], lang: str) -> Union[str, list]:
    """Перевести текст, или список текстов на какой-либо язык.\ntext: текст, или список текстов, который пренадлежит к переводу.\nlang: язык, на который надо перевести текст, или список текстов."""
    if isinstance(text, str):
        trans_result = googletrans.Translator().translate(text, lang).text
        return trans_result
    if isinstance(text, list):
        results = []
        for _ in text:
            trans_result_one = googletrans.Translator().translate(_, lang).text
            results.append(trans_result_one)
        return results
    
def send_email(login: str, passwd: str, title: str, text: str, to_addr: str) -> bool:
    """Отправьте письмо, используя MAIL.RU API.\nlogin: адрес вашей электронной электронной почты на MAIL.RU (это ваш логин).\npasswd: токен от MAIL.RU API. [Подробнее...](https://api.mail.ru/docs/)\ntitle: заголовок письма.\ntext: остальная часть письма.\nto_addr: адрес электронной почты получателя."""
    msg = MIMEMultipart()
 
    msg["From"] = login
    msg["To"] = to_addr
    msg["Subject"] = title
 
    msg.attach(MIMEText(text, "plain"))
    with smtplib.SMTP('smtp.mail.ru', 465) as server:
        server.login(login, passwd)
        server.sendmail(login, to_addr, msg.as_string())
        server.quit()
        return True

def html_make(html: str):
    """Служебная функция, которая пренадлежит `run_html`."""
    put_html(html)

def run_html(html: str, port: int = 50125):
    """Запустите HTML код на сервере.\nhtml: ваш HTML код.\nport: порт сервера.\nСервер будет запускаться на `localhost:<порт сервера>`."""
    if __name__ == '__main__':
        start_server(html_make(html), port)

def get_py_joke():
    """Рандомная шутка на английском языке."""
    return pyjokes.get_joke()

def info_about_java_server(ip: str) -> dict:
    """Информация о Java сервере Minecraft.\nip: ip адрес сервера. (Желательно с портом.)"""
    server = mcstatus.JavaServer.lookup(ip)
    status = server.status()
    query = server.query()
    return {
        'online': status.players.online,
        'max_online': status.players.max,
        'ping': status.latency,
        'players_name': query.players.names

    }

def create_qr(url: str, name: str = 'qr.png') -> bool:
    """Создает QR-код для Вашей ссылки.\nurl: ссылка, под которую надо делать QR.\nname: имя QR кода. По умолчанию: `qr.png`.\nВозвращает True."""
    qr = segno.make_qr(url)
    qr.save(name, scale=10)
    return True

def cool_text(text: str) -> str:
    """Данная функция делает текст более красивым и эффектным. Желательно использовать для заголовков и названий чего-либо\ntext: введи текст, который ты хочешь преобрезовать.\nВозвращает `str`."""
    return art.text2art(text)

def auto_clicker(time_: float):
    """Автокликер, написанный Флорестом!\ntime_: задержка, перед следующим кликом."""
    while True:
        mouse.click('left')
        time.sleep(time_)

def generate_password(symbols_amount: int, use_special_symbol: bool = False) -> str:
    """Сгенирировать уникальный пароль специально для Вас!\nsymbols_amount: количество символов в пароле.\nuse_special_symbol: использовать спецсимвол?\nВозвращает `str`."""
    if not use_special_symbol:
        symbols = list(string.ascii_letters + string.digits)
        random.shuffle(symbols)
        return ''.join(symbols[:symbols_amount])
    else:
        special_symbols1 = ['!', '*', '&', '?', '%', '$', '#', '@']
        symbols1 = list(string.ascii_letters + string.digits)
        random.shuffle(symbols1)
        psw = ''.join(symbols1[:symbols_amount])
        return psw + random.choice(special_symbols1)

def calculate(one: float, symbol: str, two: float) -> Union[float, bool]:
    """Калькулятор в Python.\none: первое число.\nsymbol: знак действия. (+, -, *, /)\ntwo: второе число.\nВозвращает `float` при удачном завершении операции."""
    if symbol not in ['+', '-', '/', '*']:
        return False
    else:
        if symbol == '+':
            return one + two
        if symbol == '-':
            return one - two
        if symbol == '*':
            return one * two
        if symbol == '/':
            return one / two

def fact_about_cat() -> str:
    """Интереснейшний факт о кошках с помощью Python))).\nНа русском, конечно же. А ты как думал, епт?)\nВозвращает `str`."""
    return googletrans.Translator().translate(eval(requests.get('https://catfact.ninja/fact').text)['fact'], 'ru').text

def progress_bar(object: int) -> int:
    """Прогресс бар, который будет считать то, что Вы написали в аргумент `object`.\nobject: объект для подсчета."""
    count = 10
    for _ in tqdm(range(object), 'Объекты считаются, эщкере', ncols=70, colour='#009FBD'):
        count += 1
        time.sleep(0.1)
    return count

from bs4 import BeautifulSoup 
import requests 
 
 
def weather_check(city: str): 
    """Функция для проверки погоды.\ncity: ваш населенный пункт."""
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid=79d1ca96933b0328e1c7e3e7a26cb347', headers={"User-Agent": "(Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36)"}, verify=False).text
        temperature = eval(response)['main']['temp']
        wind = eval(response)['wind']['speed']
        description = eval(response)['weather'][0]['description']
        return {
            "status": "success",
            "temp": temperature,
            "wind": wind,
            "desc": description
        }
    except:
        return {
            "status": 'failed',
            "temp": None,
            "wind": None,
            "desc": None
        }

class AllServices:
    """Класс для работы со всеми сервисами.\nkwargs: параметры."""
    def __init__(self, **kwargs):
        """Класс для работы со всеми сервисами.\nkwargs: параметры."""
        self.parameters = kwargs
    def discord_return(self) -> Discord.WebhookSender:
        """Функция, которая возвращает WebhookSender."""
        if self.parameters['webhook_url']:
            return Discord.WebhookSender(self.parameters['webhook_url'])
        else:
            return f'Не был указан параметр `webhook_url`.'
    def vk_return(self) -> VK:
        if self.parameters['vk_token'] and self.parameters['vk_id']:
            return VK(self.parameters['vk_token'], self.parameters['vk_id'])
        else:
            return f'Не был обнаружен параметр `vk_token`, или параметр `vk_id`.'
    def yt_info(self) -> dict:
        if self.parameters['yt_token'] and self.parameters['channel_id']:
            return get_youtube_channel_details(self.parameters['yt_token'], self.parameters['channel_id'])
        else:
            return f'Не был обнаружен параметр `yt_token`, или параметр `channel_id`.'
        
def youtube_video_download(url: str, filename: str = 'video.mp4', path: str = None) -> str:
    """Скачать видео с помощью Python. Не советуется скачивать длинные видео.\nurl: ссылка на видео.\nfilename: имя файла. По умолчанию, `video.mp4`.\npath: путь, куда будет сохранен файл. По умолчанию, папка, где запущен файл с кодом."""
    try:
        youtube = YouTube(url)
        video = youtube.streams.get_highest_resolution()
        video.download(path, filename)
        return 'Готово!'
    except:
        return 'Ошибка...'

def find_proxy() -> list:
    """Данная функция возвращает HTTPS прокси (бесплатные), которые были найдены путем парсинга.\nВозвращает `list`."""
    url = "https://free-proxy-list.net/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    proxies = soup.textarea.text.split('\n')[3:-1]

    print(f'Обнаружено бесплатных прокси - {len(proxies)}:')
    proxies_ = []
    for prox in proxies:
        try:
            req = requests.get('https://ip.beget.ru/', proxies={"http":f'http://{prox}', 'https':f'http://{prox}'}, timeout=0.5)
            if req.status_code == 200:
                print(f'Доступный прокси: {prox}')
                proxies_.append(prox)
            else:
                print(f'{prox} недоступен.')
        except:
            print(f'{prox} недоступен.')
    return proxies_


