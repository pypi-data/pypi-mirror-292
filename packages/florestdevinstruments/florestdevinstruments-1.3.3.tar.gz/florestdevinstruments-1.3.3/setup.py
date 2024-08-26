# -*- coding: utf-8 -*-

from setuptools import setup

def read_file():
    with open('README.md', 'r') as file:
        return file.read()


setup(name='florestdevinstruments', version='1.3.3', description='Личная библиотека Флореста, написанная на Python.', long_description=read_file(), long_description_content_type='text/markdown', packages=['florestdevinstruments'], author='FlorestDevelopment', author_email='florestone4185@internet.ru', install_requires=['g4f', 'MukeshAPI', 'pypresence', 'curl_cffi', 'pygame', 'pygame_gui', 'vk_api', 'pyautogui', 'googletrans', 'rcon', 'discord', 'pywebio', 'mcstatus', 'pyjokes', 'google-api-python-client', 'segno', 'art', 'keyboard', 'mouse', 'requests', 'tqdm', 'bs4', 'mcrcon', 'pytubefix'], url='https://taplink.cc/florestone4185', python_requires='>=3.8.9',project_urls={"Florest's Resources": 'https://taplink.cc/florestone4185', 'GitHub':"https://github.com/florestdev/florestdevinstruments"})