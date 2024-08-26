# -*- coding: utf-8 -*-

"""Работайте с документами с помощью данного модуля!"""

import googletrans

class WorkingWithTXT:
    """Класс для работы с TXT документами. Очень много функций.\npath: путь к файлу. Пример: E:\Кирилл\Florest\Программирование\Python\h.txt"""
    def __init__(self, path: str):
        """Класс для работы с TXT документами. Очень много функций.\npath: путь к файлу. Пример: E:\Кирилл\Florest\Программирование\Python\h.txt"""
        self.path = path

    def read_txtfile(self) -> str:
        """Прочтите файл с помощью данной функции."""
        file = open(self.path, 'r')
        text = file.read()
        return text
    def write_to_txtfile(self, text: str) -> bool:
        """Напишите что-нибудь в файл с помощью данной функции.\ntext: текст, который надо написать в файл."""
        with open(self.path, 'w') as txt:
            txt.write(text)
            txt.close()
        return True
    
    def translate_of_txtfile(self, lang: str = 'ru') -> str:
        """Данная функция без проблем переведет Ваш текстовый документ на любой язык!\nlang: язык, на который надо перевести файл. Пример: ru, eng"""
        with open(self.path, 'r') as file:
            text = file.read()
            return googletrans.Translator().translate(text, lang).text