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

openai.api_key = "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"

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


def text_to_speech(text):
    filename = "tts.wav"
    print("\n" + text + "\n")
    # tts 파일 생성 (*break time: 문장 간 쉬는 시간)
    tts.tts_connection(text, filename)
    tts.play(filename, 'local', '-2000', False)     # tts 파일 재생


def bible_to_speech(text):
    filename = "tts.wav"
    print("\n" + text + "\n")
    # tts 파일 생성 (*break time: 문장 간 쉬는 시간)
    tts.second_connection(text, filename)
    tts.play(filename, 'local', '-1500', False)     # tts 파일 재생


def wait_for(item):
    while True:
        print(f"{item} 기다리는 중")
        break


def recording(expect, response):
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
            except sr.UnknownValueError:
                print("say again plz\n")
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue

        # stt 결과 처리 (NLP.py 참고)
        answer = NLP.nlp_answer(user_said=text, dic=Dic)

        if answer == expect:

            while True:
                text_to_speech(response)
                time.sleep(1)
                break
        else:

            wait_for(expect)    # DONE 답변 들어올 때까지 stt open 반복
            continue
        break


def touch_test():
    print(f"touch test")
    total = 0
    for i in range(3):
        time.sleep(1)
        data = device_obj.send_cmd(Device.code_list['SYSTEM']).split(':')[1].split('-')
        _touch = data[1] if data[1] else "No signal"
        if _touch == 'touch':
            total = total + 1
    return total


def recommend_praise_scenario():
    oled.draw_image("/home/pi/AI_pibo2/src/data/icon/화면_음표1.png")
    oled.show()
    tts.play(filename="/home/pi/AI_pibo2/src/data/audio/물음표소리1.wav",
             out='local', volume=-1000, background=False)
    text_to_speech("Hey friend, do you want me to recommend a praise? Pat me on the forehead if you want!")
    text_to_speech(f"친구야, 내가 찬양 하나 추천해줄까? 원하면 내 이마를 쓰다듬어줘!")
    
    touched = touch_test()
    
    if touched > 1:
        device_obj.send_cmd(20, '0,0,255')
        text_to_speech("Thank you for stroking me! I'll recommend praise.")
        text_to_speech(f"쓰다듬어줘서 고마워! 찬양을 추천해줄게.")

        songlist = ["/home/pi/HCI/audio/hosanna.mp3", "/home/pi/HCI/audio/꽃들도.mp3", "/home/pi/HCI/audio/내주를가까이.mp3","/home/pi/HCI/audio/은혜.mp3","/home/pi/HCI/audio/주님의마음있는곳.mp3"]
        ran = random.randrange(0, len(songlist))
        tts.play(filename=songlist[ran], out='local', volume=-2000, background=False)
        text_to_speech(f"It's over!")
        text_to_speech(f"끝났어!")
    else:
        text_to_speech("Okay. I'll recommend praise next time!")
        text_to_speech(f"알겠어. 찬양은 다음에 추천해줄게!")


def bible_recommend():
    oled.draw_image("/home/pi/AI_pibo2/src/data/icon/화면_음표1.png")
    oled.show()
    tts.play(filename="/home/pi/AI_pibo2/src/data/audio/물음표소리1.wav",
             out='local', volume=-1000, background=False)
    text_to_speech("Do you want me to recommend a Bible verse, my friend? Pat me on the forehead if you want!")
    text_to_speech(f"친구야, 내가 성경구절 하나 추천해줄까? 원하면 내 이마를 쓰다듬어줘!")
    
    touched = touch_test()
    
    if touched > 1:
        device_obj.send_cmd(20, '0,0,255')
        text_to_speech("Thank you for stroking me! I'll recommend a Bible verse.")
        text_to_speech(f"쓰다듬어줘서 고마워! 성경구절을 추천해줄게.")
        
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
        rule9 = "9) 영어로 말해줘."

        # Generate text using the GPT model
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            n=1,
            messages=[
                {"role": "system", "content": pre + rule1 + rule2 + rule3 + rule4 + rule5 + rule6 + ex + rule7 + rule8 + rule9},
                # {"role": "system", "content": pre + rule1 + rule2 + rule3 + rule4 + rule5 + rule6 + ex + rule7 + rule8},
                {"role": "user", "content": ""},
            ])
        message = response.choices[0]['message']
        print("{}: {}".format(message['role'], message['content']))
        abc = message['content'].split("**")
        text_to_speech(abc[0])
        
    else:
        text_to_speech("Okay. I'll recommend a Bible verse next time!")
        text_to_speech(f"알겠어. 성경구절은 다음에 추천해줄게!")


def healthCheck():
    text_to_speech("Let me check your health!")
    text_to_speech("너의 건강을 확인해줄게!")
    text_to_speech("How are you feeling these days?")
    text_to_speech("요즘 상태가 어때?")
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
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
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
            {"role": "system", "content": "3 문장 내로 영어로 대답해"+ gptResponse + text},
            # {"role": "system", "content": "3 문장 내로 대답해"+ gptResponse + text},
            {"role": "user", "content": text},
        ]
    )
    message = response.choices[0]['message']
    print("{}: {}".format(message['role'], message['content']))
    abc = message['content'].split("**")
    text_to_speech(abc[0])
    return abc[0]


def freeTalking():
    text_to_speech("What do you want to talk to me about?")
    text_to_speech("나랑 무슨 대화 하고싶어?")
    
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
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
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
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
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
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
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
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
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
            text_to_speech("if you opened your index finger")
            text_to_speech("You value the pride and freedom of your partner. \
                            You're the type to pursue a chill and cool relationship.​")
            break

        elif answer == "3":
            text_to_speech("if you opened one's middle finger")
            text_to_speech("Your love has a strong personality and is very charming.\
                            You could be someone who prioritizes pleasure and fun while dating​​.")
            break

        elif answer == "4":
            text_to_speech("if you opened your ring finger")
            text_to_speech("You might have difficulty in your love life, \
                            maybe you have a crush or are in a long distance relationship. You have an unusual love. Cheer up.")
            break

        elif answer == "5":
            text_to_speech("if you opened your baby finger or pinky finger")
            text_to_speech("You tend to pursue pure love. You love like it is your first love and last love. That's so cool")
            break
        
        else:
            text_to_speech('Please choose the number from one to five')
            continue


def Start():
    device_obj.send_cmd(20, '0,0,0') # 20 = eye, 0,0,0 = color rgb
    #device_obj.send_cmd(25, '2') 

    # name recognition
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)

            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
                answer = NLP.nlp_answer(user_said=text, dic=Dic)

                if answer == 'EXIT':
                    text_to_speech('Okay... Bye!')
                    exit(0)
                if answer == 'EVE':
                    break
                else:
                    # 해당 안 될 경우
                    pass
            except sr.UnknownValueError:
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue
    
    behavior_list.do_question_S()
    text_to_speech('Hello? My name is Eve. Great to see you!')
    text_to_speech('안녕? 내 이름은 이브야. 만나서 반가워!')
    text_to_speech(f"Hey friend, How are you today?")
    text_to_speech(f"친구야, 오늘 기분이 어때?")

    # 기분 파악
    while True:
        with mic as source:
            print("say something\n")
            audio = r.listen(source, timeout=0, phrase_time_limit=5)
            try:
                text = r.recognize_google(audio_data=audio, language="ko-KR")
                answer = NLP.nlp_answer(user_said=text, dic=Dic)

                if answer == 'EXIT':
                    text_to_speech('Okay... Bye!')
                    exit(0)
                
            except sr.UnknownValueError:
                text_to_speech("I can't not understand what you said. Can you say again?")
                text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
                continue
            except sr.RequestError:
                print("speech service down\n")
                continue
            break

    # 감정 분류
    data = {
        "content": text
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    parse = response.json().get('document').get('sentiment')
    print(parse)

    # 부정일 경우, 위로의 말 후 랜덤 선택
    if parse == 'negative':
        text_to_speech('You\'re in a bad mood. Let\'s do an activity with me!')
        text_to_speech('기분이 안좋구나 ㅠㅠ 나랑 활동 하나 하자!')
        funcs = [recommend_praise_scenario, bible_recommend, healthCheck, games] #
        ran = random.randrange(0, len(funcs)) # 0이상 3미만의 난수

        if ran == 0:
            pass
        if ran == 1:
            pass
        if ran == 2:
            pass
        if ran == 3:
            pass
        
        funcs[ran]()
    
    # 부정이 아닐 경우, 직접 선택
    else:
        text_to_speech('Activities that I can do include praise recommendation, Bible recommendation, health check, psychological test, and free conversation.')
        text_to_speech("내가 할 수 있는 활동에는 찬양추천, 성경추천, 건강체크, 심리테스트, 자유대화가 있어.")
        text_to_speech('Is there any activity you want to do?')
        text_to_speech('혹시 하고 싶은 활동 있어?')
        num = 0

        while True:
            with mic as source:
                print("say something\n")
                audio = r.listen(source, timeout=0, phrase_time_limit=5)
                try:
                    text = r.recognize_google(audio_data=audio, language="ko-KR")
                    answer = NLP.nlp_answer(user_said=text, dic=Dic)

                    if answer in ['EXIT', 'NO']:
                        text_to_speech('Okay... Bye!')
                        exit(0)
                    if answer == 'PRAISE':
                        num = 0
                        break
                    if answer == 'BIBLE':
                        num = 1
                        break
                    if answer == 'HEALTH':
                        num = 2
                        break
                    if answer == 'PSYCHOLOGY':
                        num = 3
                        break
                    if answer == 'TALKING':
                        num = 4
                        break
                    
                    # 해당 안 될 경우
                    text_to_speech("Please choose between praise recommendation, Bible recommendation, health check, psychological test, and free conversation!")
                    text_to_speech("찬양추천, 성경추천, 건강체크, 심리테스트, 자유대화 중에 선택해줘!")

                except sr.UnknownValueError:
                    text_to_speech("I can't not understand what you said. Can you say again?")
                    text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
                    continue
                except sr.RequestError:
                    print("speech service down\n")
                    continue

        funcs = [recommend_praise_scenario, bible_recommend, healthCheck, games, freeTalking]
        ran = random.randrange(0, len(funcs))
        funcs[num]()
    
    # 이후로는 반복 진행
    while(True):
        text_to_speech('Is there anything else you want to do?')
        text_to_speech('혹시 더 하고 싶은 활동이 있어?')
        num = 0

        while True:
            with mic as source:
                print("say something\n")
                audio = r.listen(source, timeout=0, phrase_time_limit=5)
                try:
                    text = r.recognize_google(audio_data=audio, language="ko-KR")
                    answer = NLP.nlp_answer(user_said=text, dic=Dic)

                    if answer == 'EXIT':
                        text_to_speech('Okay... Bye!')
                        exit(0)
                    if answer == 'PRAISE':
                        num = 0
                        break
                    if answer == 'BIBLE':
                        num = 1
                        break
                    if answer == 'HEALTH':
                        num = 2
                        break
                    if answer == 'PSYCHOLOGY':
                        num = 3
                        break
                    if answer == 'TALKING':
                        num = 4
                        break
                    
                    # 해당 안 될 경우
                    text_to_speech("Please choose between praise recommendation, Bible recommendation, health check, psychological test, and free conversation!")
                    text_to_speech("찬양추천, 성경추천, 건강체크, 심리테스트, 자유대화 중에 선택해줘!")

                except sr.UnknownValueError:
                    text_to_speech("I can't not understand what you said. Can you say again?")
                    text_to_speech("잘 못 알아들었어. 다시 한 번 얘기해줄래?")
                    continue
                except sr.RequestError:
                    print("speech service down\n")
                    continue

        funcs = [recommend_praise_scenario, bible_recommend, healthCheck, games, freeTalking]
        ran = random.randrange(0, len(funcs))
        funcs[num]()

Start()