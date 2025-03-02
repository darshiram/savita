import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from openai import OpenAI
from playsound import playsound
import eel
import pyaudio
import pyautogui
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

con = sqlite3.connect("savita.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":

        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(3)
    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)

# chat bot 
# def chatBot(query):
#     user_input = query.lower()
#     chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
#     id = chatbot.new_conversation()
#     chatbot.change_conversation(id)
#     response =  chatbot.chat(user_input)
#     print(response)
#     speak(response)
#     return response



# def chatBot(query):
    
#     base_url = "https://api.aimlapi.com/v1"
#     api_key = ""
#     system_prompt = "you are a Virtual assistant named SAVITA , which means Smart Artificial Virtual Assistant to Assist."
#     user_prompt = query.lower()
#     api = OpenAI(api_key=api_key, base_url=base_url)
#     completion = api.chat.completions.create(
#         model="mistralai/Mistral-7B-Instruct-v0.2",
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         temperature=0.7,
#         max_tokens=256,
#     )

#     response = completion.choices[0].message.content

#     print("User:", user_prompt)
#     print("AI:", response)
#     speak(response)
#     return(response)




def chatBot(query):
    base_url = "https://api.aimlapi.com/v1"
    api_keys = [
        "8330b24a7c01482a8ae2543200420c2a",  # Primary API key
        "a33fab4d12a24d66a1cea19b8dc7010a",  # Backup API key
        "74fa7856dd49430f8d0ab436c4eb2a90",
        "d9958a94587d4b4a9f6d8ed06d8bb329",
        "ee7f24e36ce043b6bceac50576245304",
        "a0d49c9c9b164633abc7d2bdbe46dc9f"
              
        
    ]
    
    system_prompt = "You are a Virtual Assistant named SAVITA (Smart Artificial Virtual Assistant To Assist)devloped by Team GlitchCoders whose members are 'Darshi' 'Daksh' 'Arshpreet' 'Abhinav', "
    user_prompt = query.lower()

    for api_key in api_keys:
        try:
            api = OpenAI(api_key=api_key, base_url=base_url)
            completion = api.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,
                max_tokens=256,
            )

            response = completion.choices[0].message.content

            # Check for limitation error (modify based on actual API responses)
            if "rate limit" in response.lower() or "quota exceeded" in response.lower():
                print(f"API Key {api_key} has limitations. Trying another key...")
                continue  # Try the next key

            print("User:", user_prompt)
            print("AI:", response)
            speak(response)
            return response  # Exit after a successful response

        except Exception as e:
            print(f"Error using API Key {api_key}: {e}")
            continue  # Try the next key if an error occurs

    print("All API keys failed. Please check your API limits or credentials.")
    apiNotWorking = "backend api is not responsing"
    response = apiNotWorking
    speak(response)
    return response  # If no keys work,

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(253, 2228)
    #start chat
    tapEvents(825, 2237)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(645, 500)
    # tap on input
    tapEvents(473, 2307)
    #message
    adbInput(message)
    #send
    tapEvents(969, 1305)
    speak("message send successfully to "+name)