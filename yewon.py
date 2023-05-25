#!/usr/bin/python3
user_name = '친구'
import os
import sys
import time
import re
import random
import string
import speech_recognition as sr
import requests
import json
import openai

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

m.set_profile("/home/pi/HCI/src/motion_db.json")
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

openai.api_key = "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"
def text_to_speech(text):
    filename = "tts.wav"
    print("\n" + text + "\n")
    # tts 파일 생성 (*break time: 문장 간 쉬는 시간)
    tts.tts_connection(text, filename)
    tts.play(filename, 'local', '-1500', False)     # tts 파일 재생


def BibleRecommed():
    pre = "나에게 성경구절 하나를 추천해 줘. 너는 대답을 이런 형식으로 해야해."
    rule1 = "1) 반말(~야)을 사용해줘. 친구에게 말을 하듯이 대답해줘."
    rule2 = "2) 대답을 시작할 때, 말씀의 제목을 먼저 말해줘. 예를 들어 '이사야 5장 5절이야'와 같은 형태로 대답을 시작해줘."
    rule3 = "3) 성경 구절은 따로 문단을 나눠 대답을 해줘, 마지막에는 한 문장으로 위로를 해줘"
    rule4 = "4) 나를 부를 때는 '너' 라고 불러줘."
    rule5 = "5) 질문은 하지 마."
    rule6 = "6) 시편 같은 경우에는 장이 아니라 편이야 위에와 같은 형식으로 꼭 대답을 해."
    ex = "아래는 예시를 보여줄게. 같은 형식으로 대답을 해야해. [(창세기 28장 15절)이야. \"보라, 나는 너와 함께 있어서 네가 가는 모든 길에서 너를 지키리니 이르기를 내가 너를 보내지 아니하고 네게 허락한 땅으로 돌아가게 하리라 할 때까지\" 너가 잃어버린 것이 얼마나 아까워서 불안하고 슬프겠지만, 하나님은 네가 가는 길에서 너를 지키시며, 네가 돌아가는 땅까지 너를 인도해주시리라 믿어봐.] 위의 예시처럼 대답을 해줘."
    rule7 = "7) 대답을 할 때 존댓말을 절대 사용하지마."
    rule8 = "8) 말씀 주소와 말씀을 먼저 말해줘."

    # Generate text using the GPT model
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        n=1,
        messages=[
            {"role": "system", "content": pre + rule1 + rule2 + rule3 + rule4 + rule5 + rule6 + ex + rule7 + rule8},
            {"role": "user", "content": ""},
        ])
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))
    abc = message['content'].split("**")
    text_to_speech(abc[0])


def healthCheck():
    text_to_speech("How are you feeling these days?")
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=3)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
                chatGPTforHealthCheck(text)
                # text_to_speech(text)
                break
            except sr.UnknownValueError:
                print("I can't understand. Could you say that again?\n")
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue

def chatGPTforHealthCheck(text):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        n=1,
        messages=[
            {"role": "system", "content": text + "You're a program that advises you on your health. \
                Please give me some simple consolation and advice on the \"bottom stomach hurts\" comment within 80 characters.\
                1) For example, regarding the comment, \"My throat hurts often these days,\", you can answer as \"I\'m worried that my throat hurts.. \
                There is a possibility that a sore throat is a cold or fine dust. Drink a lot of water and wear a mask! \
                If it gets worse, go to the hospital.\"\
                2) You have to answer in a friendly way like a friend \
                3) Don't say hello like 'hello' and answer me right away."},
            {"role": "user", "content": text},
        ]
    )
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))
    abc = message['content'].split("**")
    text_to_speech(abc[0])


def freeTalkingChatGpt(gptResponse, text):    
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        n=1,
        messages=[
            {"role": "system", "content": "3 문장 내로 대답해"+ gptResponse + text},
            {"role": "user", "content": text},
        ]
    )
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))
    abc = message['content'].split("**")
    text_to_speech(abc[0])
    return abc[0]


def freeTalking():
    gptResponse = ""
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=3)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
                answer = NLP.nlp_answer(user_said=text, dic=Dic)
                if answer == "END":
                    break
                else :
                    gptResponse = freeTalkingChatGpt(gptResponse, text)
                
            except sr.UnknownValueError:
                print("I can't understand. Could you say that again?\n")
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue
    

def games():
    psychological_test = [test1, test2, test3]
    random.choice(psychological_test)()

def test1():
    text_to_speech("There is your favorite cake in front of you. But you can't eat it. You are just holding back. Guess why?")
    text_to_speech("1. because you are on a diet")
    text_to_speech("2. because you have diabetes")
    text_to_speech("3. because the cake is not yours.")

    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
            except sr.UnknownValueError:
                text_to_speech('Well, I don\'t understand. Can you say that again?')
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue
            
        answer = NLP.nlp_answer(user_said=text, dic=Dic)

        if answer == "1":
            text_to_speech("You chose the first one.")
            text_to_speech("You responded it's because you are on a diet, \
                            but it actually reflects a desire to be recognized by others for your self-discipline.\
                            You prioritize social success over love, and you may be the type of person who sacrifices both family and romantic relationships when things don't go well")
            break

        elif answer == "2":
            text_to_speech("You chose the second one.")
            text_to_speech("You responded that it's because of diabetes.\
                             It reflects a strong stubbornness. You consider it a waste of time or money to spend it for the sake of love. \
                             In other words, you may be seen as selfish.")
            break

        elif answer == "3":
            text_to_speech("You chose the third one.")
            text_to_speech("You are the type of person who values human relationships more than love. \
            This can also be described as a moral consciousness that is conscious of other people's perspectives.\
            No matter how much you love someone, it won't work out if it doesn't make logical sense.")
            break
        
        else:
            text_to_speech('Please choose the number from one to three')
            continue

def test2():
    text_to_speech("There is an old wardrobe that someone has discarded in front of you right now.\
                    You open a drawer inside the wardrobe and find something inside. What is in the drawer?")
    text_to_speech("1. a broken toy")
    text_to_speech("2. a picture")
    text_to_speech("3. a candle")
    text_to_speech("4. an id card")

    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
            except sr.UnknownValueError:
                text_to_speech('Well, I don\'t understand. Can you say that again?')
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue
                
        answer = NLP.nlp_answer(user_said=text, dic=Dic)

        if answer == "1":
            text_to_speech("You choose the first answer")
            text_to_speech("Choosing the broken toy suggests that you want to hide a lack of sociability.\
                            Although you don't show it outwardly, your true nature is to be reserved around people you don't know well or with whom you don't click,\
                            and you may feel uncomfortable in social situations with them.")
            break

        elif answer == "2":
            text_to_speech("You choose the second answer")
            text_to_speech("Choosing the photograph suggests that you may be having some trouble with your current lover or spouse. \
                            In such situations, you could talk to a close friend for advice or to confide in them, \
                            but you tend to be someone who doesn't want to talk about personal matters related to your relationships or family.")
            break
        elif answer == "3":
            text_to_speech("You choose the third answer")
            text_to_speech("Having chosen a candle, you have a hobby that you can't tell anyone,\
                            and you don't want to reveal it to others.\
                            This is because you think that others will judge you and you might be placed in an awkward situation. ")
            break

        elif answer == "4":
            text_to_speech("You choose the fourth answer")
            text_to_speech("If you chose the ID card, you are recognized by people around you as a popular person.\
                            However, you know that it is a hollow emotion. you get very upset when you think you're behind someone while working.\
                            So your afraid that people will leave you when they see that you don’t have skills.")
            break

        else:
            text_to_speech('Please choose the number from one to four')
            continue

def test3():
    text_to_speech("I'll give you a psychological test.\
                    Make a fist first.\
                    If you're done, can you stretch out one of your fingers?")

    text_to_speech("I'll show you your dating style with the finger that you opened.\
                    Thumb, index finger, middle (middle), ring finger, baby finger, where did you open?\
                    the thumb is the first finger")
            
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
            except sr.UnknownValueError:
                text_to_speech('Well, I don\'t understand. Can you say that again?')
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue

        answer = NLP.nlp_answer(user_said=text, dic=Dic)

        if answer == "1":
            text_to_speech("If you opened your thumb")
            text_to_speech("You are a person that has a lot of love to give. \
                            You are good to your loved ones and passionate.​")
            break

        elif answer == "2":
            text_to_speech("If you opened your index finger")
            text_to_speech("You value the pride and freedom of your partner. \
                            You're the type to pursue a chill and cool relationship.​")
            break

        elif answer == "3":
            text_to_speech("If you opened one's middle finger")
            text_to_speech("Your love has a strong personality and is very charming.\
                            You could be someone who prioritizes pleasure and fun while dating​​.")
            break

        elif answer == "4":
            text_to_speech("If you opened your ring finger")
            text_to_speech("You might have difficulty in your love life, \
                            maybe you have a crush or are in a long distance relationship. You have an unusual love. Cheer up.")
            break

        elif answer == "5":
            text_to_speech("If you opened your baby finger or pinky finger")
            text_to_speech("You tend to pursue pure love. You love like it is your first love and last love. That's so cool")
            break
        
        else:
            text_to_speech('Please choose the number from one to five')
            continue


# psychological_test = [test1, test2, test3]
# random.choice(psychological_test)()

freeTalking()