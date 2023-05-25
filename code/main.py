#!/usr/bin/python3
user_name = '건호'
import os
import sys
import time
import re
import random
import string
import speech_recognition as sr
import requests
import json

# openpibo module
import openpibo
from openpibo.device import Device
from openpibo.speech import Speech
from openpibo.audio import Audio
from openpibo.vision import Camera
from openpibo.oled import Oled

# path
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))))))

from text_to_speech import TextToSpeech
from src.data import behavior_list
from src.NLP import NLP, Dictionary
import src.data.eye_list as eye
from openpibo.motion import Motion
m = Motion()

m.set_profile("/home/pi/test/motion_db.json")
client_id = "zq90hxu84o" # naver cloud platform - clova sentiment client id
client_secret = "B6jHEYSIrkCK4kTVbK8l1NXclQAUcnBu7bRXcEoo" # clova sentiment client password
url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze" # naver sentiment url

# naver clova sentiment header
headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret,
    "Content-Type": "application/json" # json 형식
}


NLP = NLP()
Dic = Dictionary()
tts = TextToSpeech()
device_obj = Device()
camera = Camera()
oled = Oled()

r = sr.Recognizer()
r.energy_threshold = 300
mic = sr.Microphone()
biblefile = "/home/pi/AI_pibo2/src/data/bible.json"
with open(biblefile, encoding='utf-8') as f:
    bible = json.load(f)


def text_to_speech(text):
    filename = "tts.wav"
    print("\n" + text + "\n")
    # tts 파일 생성 (*break time: 문장 간 쉬는 시간)
    tts.tts_connection(text, filename)
    tts.play(filename, 'local', '-1500', False)     # tts 파일 재생

def bible_to_speech(text):
    filename = "tts.wav"
    print("\n" + text + "\n")
    # tts 파일 생성 (*break time: 문장 간 쉬는 시간)
    tts.second_connection(text, filename)
    tts.play(filename, 'local', '-1500', False)     # tts 파일 재생


def ends_with_jong(kstr):
    m = re.search("[가-힣]+", kstr)
    if m:
        k = m.group()[-1]
        return (ord(k) - ord("가")) % 28 > 0
    else:
        return


def lee(kstr):
    josa = "이" if ends_with_jong(kstr) else ""
    return josa


def aa(kstr):
    josa = "아" if ends_with_jong(kstr) else "야"
    return josa


def wait_for(item):
    while True:
        print(f"{item} 기다리는 중")
        break

def verse(feel):
    ran = random.randrange(0,len(bible[feel]))
    print(len(bible[feel]))
    print(bible[feel])
    result=bible[feel][ran]

    oled.draw_image("/home/pi/AI_pibo2/src/data/icon/화면_default1.png")
    oled.show()
    m.set_speeds([20, 20, 20, 20, 20, 20, 20, 20, 20, 20])
    text_to_speech(f"{result['verse']} 말씀이야!")
    time.sleep(1)
    bible_to_speech(f"{result['text']}")
    time.sleep(1)
    text_to_speech(f"{result['comment']}")
    time.sleep(1)
    text_to_speech("오늘 말해줘서 고마워. 마지막으로 악수 하자!")
    m.set_motors([0,0,-70,-25,0,0,0,0,25,25])
    time.sleep(1)
    text_to_speech("남은 하루도 행복하기를 바랄게")
    time.sleep(4)
    m.set_motors([0,0,-70,-25,0,0,0,0,70,25])


def heart_scenario():
    text_to_speech(
        f"{user_name}{aa(user_name)}!! 너가 좋아하니 내가 너무 신나!! 내 심장소리 들려!?")
    tts.play(filename="/home/pi/audio/기타/심장박동.mp3", out='local', volume=-100, background=False)
    text_to_speech(f"안 들린다면 내 가슴쪽을 봐줘!!")
    oled.set_font(size=50)

    for a in range(20):
        num= random.randrange(150,181)
        oled.draw_text((0, 0), str(num))  # (0,0)에 문자열 출력
        oled.show()  # 화면에 표시
        time.sleep(0.1)
        oled.clear()

    text_to_speech(f"내 심장이 너무 빨리 뛰어!! 진심으로 기뻐 {user_name}{aa(user_name)}!")
    time.sleep(1)
    text_to_speech("너도 이만큼 기쁘다면 내 머리를 쓰담아줘.")
    if touch_test():
        oled.draw_image("/home/pi/AI_pibo2/src/data/icon/heart3.png")
        oled.show()
        text_to_speech("너도 그렇게 느꼈다니 너무 좋아!")   
    
    else:
        text_to_speech("별로 쓰담아주고 싶지는 않구나! 그럴 수 있지.")

def recording(expect, response):
    
    while True:
        with mic as source:
   